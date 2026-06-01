#!/usr/bin/env python3
"""
Smoke test: verify shipsafe_shared.instrumentation.telemetry fans out
BOTH Phoenix Cloud and Dynatrace from a single OTel trace stream.

Day 2 exit gate — both UIs must show the trace before moving to Phase 1.

Required env vars:
    PHOENIX_API_KEY         Phoenix Cloud API key (from app.phoenix.arize.com)
    DT_ENVIRONMENT          https://<env-id>.live.dynatrace.com
    DT_OTLP_TOKEN           API token with openTelemetryTrace.ingest scope

Run:
    python scripts/smoke_test_instrumentation.py

Verify within 60s:
    Phoenix:   https://app.phoenix.arize.com
               → Projects → smoke-test → Traces
               → Should see "hormuz-crisis-smoke-test" span

    Dynatrace: https://<env-id>.apps.dynatrace.com
               → Distributed Tracing → Spans
               → Filter: service.name = "shipsafe-smoke-test"
               → Should see "hormuz-crisis-smoke-test" span

If Dynatrace shows nothing after 60s, work through the four-trap
diagnostic printed at the end of this script.
"""

from __future__ import annotations

import os
import sys
import time


# ---------------------------------------------------------------------------
# Pre-flight: validate env vars
# ---------------------------------------------------------------------------

def _check_env() -> bool:
    required = {
        "PHOENIX_API_KEY": "Phoenix Cloud API key",
        "DT_ENVIRONMENT": "Dynatrace environment URL (https://<env-id>.live.dynatrace.com)",
        "DT_OTLP_TOKEN": "Dynatrace API token with openTelemetryTrace.ingest scope",
    }
    missing = {k: v for k, v in required.items() if not os.environ.get(k)}
    if missing:
        print("FAIL — missing env vars:")
        for var, desc in missing.items():
            print(f"  {var}  ({desc})")
        return False

    dt_env = os.environ["DT_ENVIRONMENT"]
    if not dt_env.startswith("https://") or "live.dynatrace.com" not in dt_env:
        print(f"FAIL — DT_ENVIRONMENT looks wrong: {dt_env!r}")
        print("  Expected: https://<env-id>.live.dynatrace.com")
        return False

    return True


# ---------------------------------------------------------------------------
# Processor inspection helper
# ---------------------------------------------------------------------------

def _count_batch_processors(provider: object) -> int:
    """
    Best-effort count of BatchSpanProcessors on the provider.
    Uses OTel SDK internals — diagnostic only, not load-bearing.
    """
    from opentelemetry.sdk.trace.export import BatchSpanProcessor

    try:
        active = getattr(provider, "_active_span_processor", None)
        if active is None:
            return 0
        procs = getattr(active, "_span_processors", [])
        return sum(1 for p in procs if isinstance(p, BatchSpanProcessor))
    except Exception:
        return -1  # couldn't inspect


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    print("=" * 60)
    print("ShipSafe instrumentation smoke test")
    print("=" * 60)

    if not _check_env():
        return 1

    dt_env = os.environ["DT_ENVIRONMENT"].rstrip("/")
    print(f"\nPhoenix project : smoke-test")
    print(f"Dynatrace env   : {dt_env}")
    print()

    # ------------------------------------------------------------------ #
    # 1. Initialize telemetry                                              #
    # ------------------------------------------------------------------ #
    print("[1/4] Initializing telemetry ...")
    from shipsafe_shared.instrumentation.telemetry import init_telemetry

    provider = init_telemetry("smoke-test")

    from opentelemetry import trace as otel_trace
    global_provider = otel_trace.get_tracer_provider()

    print(f"      Provider type : {type(provider).__name__}")
    print(f"      Global type   : {type(global_provider).__name__}")

    batch_count = _count_batch_processors(provider)
    if batch_count >= 0:
        print(f"      BatchSpanProcessors on provider: {batch_count}")
        # Phoenix uses SimpleSpanProcessor (not BatchSpanProcessor) so expected count is 1 (DT only).
        # If 0: DT exporter was not attached. If >= 1: DT is attached correctly.
        if batch_count == 0:
            print("  ERROR: Dynatrace BatchSpanProcessor not found — DT exporter not attached")
        else:
            print(f"  OK: Dynatrace exporter attached (Phoenix uses SimpleSpanProcessor)")
    else:
        print("      (processor count unavailable — SDK internals changed)")

    # ------------------------------------------------------------------ #
    # 2. Emit test spans                                                   #
    # ------------------------------------------------------------------ #
    print("\n[2/4] Emitting test spans ...")
    tracer = otel_trace.get_tracer("shipsafe.smoke-test")

    with tracer.start_as_current_span("hormuz-crisis-smoke-test") as root:
        root.set_attribute("shipsafe.agent", "smoke-test")
        root.set_attribute("shipsafe.scenario", "hormuz-crisis")
        root.set_attribute("shipsafe.version", "0.1.0")
        root.set_attribute("service.name", "shipsafe-smoke-test")
        root.set_attribute("smoke_test.timestamp", time.time())

        with tracer.start_as_current_span("cargodb.memory_recall") as span1:
            span1.set_attribute("db.system", "mongodb")
            span1.set_attribute("db.operation", "vectorSearch")
            span1.set_attribute("cargodb.conflict_count", 23)
            span1.set_attribute("cargodb.similarity_score", 0.89)
            time.sleep(0.05)

        with tracer.start_as_current_span("naviguard.quality_gate") as span2:
            span2.set_attribute("naviguard.model_id", "routing-avoidance-v3.2")
            span2.set_attribute("naviguard.baseline_pct", 72)
            span2.set_attribute("naviguard.current_pct", 31)
            span2.set_attribute("naviguard.verdict", "BLOCK")
            time.sleep(0.05)

    print("      3 spans emitted (root + 2 child spans)")

    # ------------------------------------------------------------------ #
    # 3. Force-flush                                                        #
    # ------------------------------------------------------------------ #
    print("\n[3/4] Force-flushing exporters (30s timeout) ...")
    flushed = provider.force_flush(timeout_millis=30_000)
    if flushed:
        print("      Flush succeeded")
    else:
        print("      WARNING: flush timed out or reported failure")
        print("      Spans may still export async — wait 60s before concluding failure")

    # ------------------------------------------------------------------ #
    # 4. Verification instructions + diagnostic                            #
    # ------------------------------------------------------------------ #
    print("\n[4/4] Verification")
    print("-" * 60)
    print("\nPhoenix Cloud:")
    print("  https://app.phoenix.arize.com")
    print("  → Projects → smoke-test → Traces")
    print("  → span name: hormuz-crisis-smoke-test")

    apps_url = dt_env.replace(".live.dynatrace.com", ".apps.dynatrace.com")
    print(f"\nDynatrace:")
    print(f"  {apps_url}")
    print("  → Distributed Tracing → Spans")
    print("  → filter: service.name = shipsafe-smoke-test")
    print("  → span name: hormuz-crisis-smoke-test")

    print("\n" + "=" * 60)
    print("Dynatrace not showing traces after 60s? Diagnose in order:\n")

    protocol = os.environ.get("OTEL_EXPORTER_OTLP_PROTOCOL", "(not set)")
    endpoint = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT", "(not set)")
    headers  = os.environ.get("OTEL_EXPORTER_OTLP_HEADERS", "(not set)")
    trace_ep = f"{dt_env}/api/v2/otlp/v1/traces"

    print(f"  1. Protocol  : {protocol!r}")
    print(f"     Must be 'http/protobuf'")
    print()
    print(f"  2. Endpoint  : env var = {endpoint!r}")
    print(f"                 exporter  = {trace_ep!r}")
    print(f"     Verify:  curl -s -o /dev/null -w '%{{http_code}}' \\")
    print(f"       -X POST {trace_ep} \\")
    print(f"       -H 'Authorization: Api-Token $DT_OTLP_TOKEN' \\")
    print(f"       -H 'Content-Type: application/x-protobuf' --data-binary ''")
    print(f"     Must return 200 or 400 (not 401/403/404)")
    print()
    print(f"  3. Token     : {headers!r}")
    print(f"     Must contain 'Api-Token', not 'Bearer'")
    print(f"     Token must have openTelemetryTrace.ingest scope")
    print()
    print(f"  4. Provider  : BatchSpanProcessors on returned provider = {batch_count}")
    print(f"     If < 2: Dynatrace processor is on a discarded provider")
    print(f"     phoenix.otel.register() replaced the global after Dynatrace attached")
    print(f"     Fix: ensure _register_phoenix() runs BEFORE _add_dynatrace_exporter()")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())
