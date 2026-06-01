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

Architecture note — provider ownership:
    phoenix.otel.register() calls trace.set_tracer_provider() internally,
    replacing whatever was previously the global.  To ensure Dynatrace's
    BatchSpanProcessor lands on the SAME provider that becomes global,
    _register_phoenix() must run FIRST and return that provider.  Dynatrace
    is then added to the returned object.  If Phoenix is not active we create
    our own provider, set it as global, then optionally add Dynatrace.
"""

from __future__ import annotations

import logging
import os

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
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
    if os.environ.get("PHOENIX_API_KEY"):
        # Phoenix creates and sets the global provider; capture it.
        provider = _register_phoenix(project_name)
    else:
        provider = TracerProvider()
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


def _register_phoenix(project_name: str) -> TracerProvider:
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

        provider = register(
            project_name=project_name,
            auto_instrument=True,
        )
        logger.info("Phoenix exporter registered for project '%s'", project_name)
        return provider
    except Exception:
        logger.exception(
            "Phoenix exporter registration failed — traces will not reach Phoenix"
        )
        fallback = TracerProvider()
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
    provider.add_span_processor(BatchSpanProcessor(exporter))

    logger.info("Dynatrace OTLP exporter registered → %s", trace_endpoint)
