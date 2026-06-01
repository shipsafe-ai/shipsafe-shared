"""
shipsafe_shared.instrumentation.telemetry
==========================================
Single OTel init function that fans out to Phoenix Cloud and/or Dynatrace
from one trace stream.  Called once at agent startup:

    from shipsafe_shared.instrumentation.telemetry import init_telemetry
    tracer_provider = init_telemetry("routeforge")

Environment variables drive which exporters are active — no config files,
no hardcoded values.

Phoenix fan-out:
    PHOENIX_API_KEY               → enables Phoenix exporter
    PHOENIX_COLLECTOR_ENDPOINT    → optional override (defaults to Phoenix Cloud)

Dynatrace fan-out (all four must be present to avoid silent-fail traps):
    DT_ENVIRONMENT                → https://<env-id>.live.dynatrace.com
    DT_OTLP_TOKEN                 → API token with openTelemetryTrace.ingest scope

    _add_dynatrace_exporter() sets the four required OTel env vars:
      OTEL_EXPORTER_OTLP_PROTOCOL                      = http/protobuf
      OTEL_EXPORTER_OTLP_ENDPOINT                      = <DT_ENVIRONMENT>/api/v2/otlp
      OTEL_EXPORTER_OTLP_HEADERS                       = Authorization=Api-Token <token>
      OTEL_EXPORTER_OTLP_METRICS_TEMPORALITY_PREFERENCE = delta

    See PARTNER-INTEGRATION.md §6 for the four silent-fail traps this addresses.

Architecture note — provider ownership and Phoenix's add_span_processor:
    phoenix.otel.register() creates a _TracerProvider (Phoenix subclass) with
    a default SimpleSpanProcessor, sets it as the OTel global, and marks
    provider._default_processor = True.

    Phoenix's _TracerProvider.add_span_processor() has a side effect:
    when _default_processor is True, it calls shutdown() on the existing
    multi-processor before clearing it — then adds the new processor via
    super().add_span_processor(). This means DT's BatchSpanProcessor is
    added to an already-shutdown SynchronousMultiSpanProcessor, so
    force_flush() returns True trivially but exports nothing.

    Fix: pass replace_default_processor=False to Phoenix's add_span_processor.
    This adds DT's BSP alongside Phoenix's (no shutdown, no replacement).
    For non-Phoenix providers that don't accept this kwarg, fall back to
    the standard call via try/except TypeError.
"""

from __future__ import annotations

import logging
import os

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

logger = logging.getLogger(__name__)


def init_telemetry(project_name: str) -> TracerProvider:
    """
    Initialize OTel tracing for an agent.  Returns the configured TracerProvider.

    Call order matters:
    1. Phoenix register() runs first — it creates and sets the global provider.
    2. Dynatrace exporter is added to the provider register() returned.
    This guarantees both exporters share one provider, which is the global one.

    Exporters activated by env vars:
    - Always: console exporter (dev visibility, no-op if Phoenix is active)
    - If PHOENIX_API_KEY: Phoenix Cloud via arize-phoenix-otel
    - If DT_ENVIRONMENT + DT_OTLP_TOKEN: Dynatrace OTLP HTTP/protobuf

    Args:
        project_name: agent identifier, e.g. "routeforge". Passed to Phoenix
                      as the project name and used in log messages.
    """
    # Resource service.name enables Dynatrace service filtering and Phoenix project grouping.
    resource = Resource.create({"service.name": project_name})

    if os.environ.get("PHOENIX_API_KEY"):
        # Phoenix creates and sets the global provider; capture it.
        provider = _register_phoenix(project_name, resource)
    else:
        provider = TracerProvider(resource=resource)
        provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
        trace.set_tracer_provider(provider)

    if os.environ.get("DT_ENVIRONMENT") and os.environ.get("DT_OTLP_TOKEN"):
        # Add to the same provider that is already global.
        _add_dynatrace_exporter(provider)
    elif os.environ.get("DT_ENVIRONMENT") and not os.environ.get("DT_OTLP_TOKEN"):
        logger.warning(
            "DT_ENVIRONMENT is set but DT_OTLP_TOKEN is missing — "
            "Dynatrace exporter skipped. Set DT_OTLP_TOKEN with "
            "openTelemetryTrace.ingest scope."
        )

    return provider


def _register_phoenix(project_name: str, resource: Resource | None = None) -> TracerProvider:
    """
    Register Phoenix Cloud as an OTel destination.

    phoenix.otel.register() auto-detects every installed OpenInference
    instrumentor, creates a TracerProvider wired to Phoenix, sets it as
    the OTel global, and returns it.  We capture the return value so the
    caller can add additional exporters (e.g. Dynatrace) to the same provider.

    On failure: logs exception, creates a fallback TracerProvider with a
    console exporter, sets it as global, and returns it.  Callers always
    receive a usable provider regardless of Phoenix availability.

    Reads from env:
        PHOENIX_API_KEY               required
        PHOENIX_COLLECTOR_ENDPOINT    optional — defaults to Phoenix Cloud
    """
    try:
        from phoenix.otel import register  # type: ignore[import-untyped]

        kwargs: dict = {"project_name": project_name, "auto_instrument": True}
        if resource is not None:
            kwargs["resource"] = resource
        provider = register(**kwargs)
        logger.info("Phoenix exporter registered for project '%s'", project_name)
        return provider
    except Exception:
        logger.exception(
            "Phoenix exporter registration failed — traces will not reach Phoenix"
        )
        fallback = TracerProvider(resource=resource or Resource.create({}))
        fallback.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
        trace.set_tracer_provider(fallback)
        return fallback


def _add_dynatrace_exporter(provider: TracerProvider) -> None:
    """
    Add a Dynatrace OTLP exporter to an existing TracerProvider.

    Sets the four env vars required by Dynatrace before constructing the
    exporter.  All four are documented in PARTNER-INTEGRATION.md §6 as
    silent-fail traps:

    1. OTEL_EXPORTER_OTLP_PROTOCOL = http/protobuf
       OTel SDK defaults to gRPC; Dynatrace only accepts HTTP/protobuf.

    2. OTEL_EXPORTER_OTLP_ENDPOINT = <DT_ENVIRONMENT>/api/v2/otlp
       Base URL without signal suffix — kept here for SDK-level metric/log
       discovery.  The span exporter receives the explicit /v1/traces URL
       in its constructor so it does not rely on env-var signal-path appending.

    3. OTEL_EXPORTER_OTLP_HEADERS = Authorization=Api-Token <token>
       Must use "Api-Token" prefix (not "Bearer").
       Token needs openTelemetryTrace.ingest scope — wrong scope → silent 401.

    4. OTEL_EXPORTER_OTLP_METRICS_TEMPORALITY_PREFERENCE = delta
       Dynatrace requires delta; OTel default is cumulative.
       Without this, metrics ingest but counters behave unexpectedly.

    Reads from env:
        DT_ENVIRONMENT    https://<env-id>.live.dynatrace.com
        DT_OTLP_TOKEN     API token with openTelemetryTrace.ingest scope
    """
    dt_env = os.environ["DT_ENVIRONMENT"].rstrip("/")
    dt_token = os.environ["DT_OTLP_TOKEN"]

    base_endpoint = f"{dt_env}/api/v2/otlp"
    trace_endpoint = f"{base_endpoint}/v1/traces"

    os.environ["OTEL_EXPORTER_OTLP_PROTOCOL"] = "http/protobuf"
    os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"] = base_endpoint
    os.environ["OTEL_EXPORTER_OTLP_HEADERS"] = f"Authorization=Api-Token {dt_token}"
    os.environ["OTEL_EXPORTER_OTLP_METRICS_TEMPORALITY_PREFERENCE"] = "delta"

    exporter = OTLPSpanExporter(
        endpoint=trace_endpoint,
        headers={"Authorization": f"Api-Token {dt_token}"},
    )
    bsp = BatchSpanProcessor(exporter)

    # Phoenix's _TracerProvider.add_span_processor() accepts replace_default_processor=False
    # to ADD alongside the existing Phoenix processor rather than shutting it down first.
    # Standard OTel TracerProvider.add_span_processor() does not accept this kwarg,
    # so we fall back to the plain call if TypeError is raised.
    try:
        provider.add_span_processor(bsp, replace_default_processor=False)  # type: ignore[call-arg]
    except TypeError:
        provider.add_span_processor(bsp)

    logger.info("Dynatrace OTLP exporter registered → %s", trace_endpoint)
