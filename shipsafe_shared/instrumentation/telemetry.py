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
"""

from __future__ import annotations

import logging
import os

from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

logger = logging.getLogger(__name__)


def init_telemetry(project_name: str) -> TracerProvider:
    """
    Initialize OTel tracing for an agent.  Returns the configured TracerProvider.

    Exporters are added based on env vars:
    - Always: console exporter (dev visibility)
    - If PHOENIX_API_KEY: Phoenix Cloud exporter via arize-phoenix-otel
    - If DT_ENVIRONMENT + DT_OTLP_TOKEN: Dynatrace OTLP exporter

    Args:
        project_name: agent identifier, e.g. "routeforge". Passed to Phoenix
                      as the project name and used in log messages.
    """
    provider = TracerProvider()

    provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))

    if os.environ.get("PHOENIX_API_KEY"):
        _register_phoenix(project_name)

    if os.environ.get("DT_ENVIRONMENT") and os.environ.get("DT_OTLP_TOKEN"):
        _add_dynatrace_exporter(provider)
    elif os.environ.get("DT_ENVIRONMENT") and not os.environ.get("DT_OTLP_TOKEN"):
        logger.warning(
            "DT_ENVIRONMENT is set but DT_OTLP_TOKEN is missing — "
            "Dynatrace exporter skipped. Set DT_OTLP_TOKEN with "
            "openTelemetryTrace.ingest scope."
        )

    return provider


def _register_phoenix(project_name: str) -> None:
    """
    Register Phoenix Cloud as an OTel destination.

    Uses arize-phoenix-otel's register() which auto-detects every installed
    OpenInference instrumentor (ADK, Vertex AI, etc.) and configures the
    global tracer provider to export to Phoenix.

    Reads from env:
        PHOENIX_API_KEY               required
        PHOENIX_COLLECTOR_ENDPOINT    optional — defaults to Phoenix Cloud
    """
    try:
        from phoenix.otel import register  # type: ignore[import-untyped]

        register(
            project_name=project_name,
            auto_instrument=True,
        )
        logger.info("Phoenix exporter registered for project '%s'", project_name)
    except Exception:
        logger.exception("Phoenix exporter registration failed — traces will not reach Phoenix")


def _add_dynatrace_exporter(provider: TracerProvider) -> None:
    """
    Add a Dynatrace OTLP exporter to an existing TracerProvider.

    Sets the four env vars required by Dynatrace before constructing the
    exporter.  All four are documented in PARTNER-INTEGRATION.md §6 as
    silent-fail traps:

    1. OTEL_EXPORTER_OTLP_PROTOCOL = http/protobuf
       OTel SDK defaults to gRPC; Dynatrace only accepts HTTP/protobuf.

    2. OTEL_EXPORTER_OTLP_ENDPOINT = <DT_ENVIRONMENT>/api/v2/otlp
       Base URL, no signal suffix — the SDK appends /v1/traces etc.
       Including the suffix manually → 404.

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

    endpoint = f"{dt_env}/api/v2/otlp"

    os.environ["OTEL_EXPORTER_OTLP_PROTOCOL"] = "http/protobuf"
    os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"] = endpoint
    os.environ["OTEL_EXPORTER_OTLP_HEADERS"] = f"Authorization=Api-Token {dt_token}"
    os.environ["OTEL_EXPORTER_OTLP_METRICS_TEMPORALITY_PREFERENCE"] = "delta"

    exporter = OTLPSpanExporter(endpoint=endpoint)
    provider.add_span_processor(BatchSpanProcessor(exporter))

    logger.info("Dynatrace OTLP exporter registered → %s", endpoint)
