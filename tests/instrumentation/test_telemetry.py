"""
Tests for shipsafe_shared.instrumentation.telemetry.

TDD — these tests define the contract; run them RED before
writing the implementation.

Coverage targets:
- init_telemetry() with no env vars → console exporter only, no crash
- init_telemetry() with PHOENIX_API_KEY → Phoenix exporter registered
- init_telemetry() with DT_ENVIRONMENT → Dynatrace OTLP exporter added
- init_telemetry() with both → both exporters registered
- Dynatrace env-var correctness: all four required vars set exactly
- Returns a TracerProvider
- Idempotent second call doesn't double-register
- project_name propagates to Phoenix registration
"""

import importlib
import os
import sys
from unittest.mock import MagicMock, call, patch

import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _reload_telemetry():
    """Force fresh module import so module-level state is reset between tests."""
    mod_name = "shipsafe_shared.instrumentation.telemetry"
    if mod_name in sys.modules:
        del sys.modules[mod_name]
    return importlib.import_module(mod_name)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
    """Strip all telemetry-related env vars before each test."""
    for var in (
        "PHOENIX_API_KEY",
        "PHOENIX_COLLECTOR_ENDPOINT",
        "DT_ENVIRONMENT",
        "DT_OTLP_TOKEN",
        "OTEL_EXPORTER_OTLP_PROTOCOL",
        "OTEL_EXPORTER_OTLP_ENDPOINT",
        "OTEL_EXPORTER_OTLP_HEADERS",
        "OTEL_EXPORTER_OTLP_METRICS_TEMPORALITY_PREFERENCE",
    ):
        monkeypatch.delenv(var, raising=False)
    yield


@pytest.fixture(autouse=True)
def reset_module():
    """Ensure the module is reimported cleanly for each test."""
    yield
    mod_name = "shipsafe_shared.instrumentation.telemetry"
    if mod_name in sys.modules:
        del sys.modules[mod_name]


# ---------------------------------------------------------------------------
# 1. No env vars → console exporter only, no crash
# ---------------------------------------------------------------------------

class TestNoEnvVars:
    def test_returns_tracer_provider(self):
        with patch("shipsafe_shared.instrumentation.telemetry.TracerProvider") as MockTP:
            mock_provider = MagicMock()
            MockTP.return_value = mock_provider

            from shipsafe_shared.instrumentation.telemetry import init_telemetry
            result = init_telemetry("test-agent")

        assert result is mock_provider

    def test_phoenix_register_not_called(self):
        with (
            patch("shipsafe_shared.instrumentation.telemetry.TracerProvider"),
            patch("shipsafe_shared.instrumentation.telemetry._register_phoenix") as mock_phoenix,
        ):
            from shipsafe_shared.instrumentation.telemetry import init_telemetry
            init_telemetry("test-agent")

        mock_phoenix.assert_not_called()

    def test_dynatrace_exporter_not_added(self):
        with (
            patch("shipsafe_shared.instrumentation.telemetry.TracerProvider"),
            patch("shipsafe_shared.instrumentation.telemetry._add_dynatrace_exporter") as mock_dt,
        ):
            from shipsafe_shared.instrumentation.telemetry import init_telemetry
            init_telemetry("test-agent")

        mock_dt.assert_not_called()


# ---------------------------------------------------------------------------
# 2. PHOENIX_API_KEY set → Phoenix exporter registered
# ---------------------------------------------------------------------------

class TestPhoenixOnly:
    def test_phoenix_register_called_with_project_name(self, monkeypatch):
        monkeypatch.setenv("PHOENIX_API_KEY", "pk-test-key")

        with (
            patch("shipsafe_shared.instrumentation.telemetry.TracerProvider"),
            patch("shipsafe_shared.instrumentation.telemetry._register_phoenix") as mock_phoenix,
            patch("shipsafe_shared.instrumentation.telemetry._add_dynatrace_exporter"),
        ):
            from shipsafe_shared.instrumentation.telemetry import init_telemetry
            init_telemetry("naviguard")

        mock_phoenix.assert_called_once_with("naviguard")

    def test_dynatrace_not_added_when_no_dt_env(self, monkeypatch):
        monkeypatch.setenv("PHOENIX_API_KEY", "pk-test-key")

        with (
            patch("shipsafe_shared.instrumentation.telemetry.TracerProvider"),
            patch("shipsafe_shared.instrumentation.telemetry._register_phoenix"),
            patch("shipsafe_shared.instrumentation.telemetry._add_dynatrace_exporter") as mock_dt,
        ):
            from shipsafe_shared.instrumentation.telemetry import init_telemetry
            init_telemetry("naviguard")

        mock_dt.assert_not_called()


# ---------------------------------------------------------------------------
# 3. DT_ENVIRONMENT set → Dynatrace exporter added
# ---------------------------------------------------------------------------

class TestDynatraceOnly:
    def test_dt_exporter_added(self, monkeypatch):
        monkeypatch.setenv("DT_ENVIRONMENT", "https://abc123.live.dynatrace.com")
        monkeypatch.setenv("DT_OTLP_TOKEN", "dt-token-xyz")

        with (
            patch("shipsafe_shared.instrumentation.telemetry.TracerProvider") as MockTP,
            patch("shipsafe_shared.instrumentation.telemetry._register_phoenix"),
            patch("shipsafe_shared.instrumentation.telemetry._add_dynatrace_exporter") as mock_dt,
        ):
            MockTP.return_value = MagicMock()
            from shipsafe_shared.instrumentation.telemetry import init_telemetry
            provider = init_telemetry("routeforge")

        mock_dt.assert_called_once_with(provider)

    def test_phoenix_not_called_when_no_phoenix_key(self, monkeypatch):
        monkeypatch.setenv("DT_ENVIRONMENT", "https://abc123.live.dynatrace.com")
        monkeypatch.setenv("DT_OTLP_TOKEN", "dt-token-xyz")

        with (
            patch("shipsafe_shared.instrumentation.telemetry.TracerProvider"),
            patch("shipsafe_shared.instrumentation.telemetry._register_phoenix") as mock_phoenix,
            patch("shipsafe_shared.instrumentation.telemetry._add_dynatrace_exporter"),
        ):
            from shipsafe_shared.instrumentation.telemetry import init_telemetry
            init_telemetry("routeforge")

        mock_phoenix.assert_not_called()


# ---------------------------------------------------------------------------
# 4. Both env vars → both exporters
# ---------------------------------------------------------------------------

class TestBothExporters:
    def test_both_register_and_dt_called(self, monkeypatch):
        monkeypatch.setenv("PHOENIX_API_KEY", "pk-key")
        monkeypatch.setenv("DT_ENVIRONMENT", "https://abc123.live.dynatrace.com")
        monkeypatch.setenv("DT_OTLP_TOKEN", "dt-token")

        with (
            patch("shipsafe_shared.instrumentation.telemetry.TracerProvider") as MockTP,
            patch("shipsafe_shared.instrumentation.telemetry._register_phoenix") as mock_phoenix,
            patch("shipsafe_shared.instrumentation.telemetry._add_dynatrace_exporter") as mock_dt,
        ):
            MockTP.return_value = MagicMock()
            from shipsafe_shared.instrumentation.telemetry import init_telemetry
            provider = init_telemetry("agentops")

        mock_phoenix.assert_called_once_with("agentops")
        mock_dt.assert_called_once_with(provider)


# ---------------------------------------------------------------------------
# 5. Dynatrace env-var correctness (the four silent-fail traps)
# ---------------------------------------------------------------------------

class TestDynatraceEnvVars:
    """
    _add_dynatrace_exporter() must set all four required env vars exactly.
    Documented in PARTNER-INTEGRATION.md §6 and PHASES.md Day 2 checklist.
    """

    def test_protocol_set_to_http_protobuf(self, monkeypatch):
        monkeypatch.setenv("DT_ENVIRONMENT", "https://abc123.live.dynatrace.com")
        monkeypatch.setenv("DT_OTLP_TOKEN", "dt-token")

        with patch(
            "shipsafe_shared.instrumentation.telemetry.OTLPSpanExporter"
        ) as MockExporter:
            MockExporter.return_value = MagicMock()
            mod = _reload_telemetry()
            provider = MagicMock()
            provider.add_span_processor = MagicMock()
            mod._add_dynatrace_exporter(provider)

        assert os.environ.get("OTEL_EXPORTER_OTLP_PROTOCOL") == "http/protobuf"

    def test_endpoint_has_no_signal_suffix(self, monkeypatch):
        """Endpoint must be base /api/v2/otlp — SDK appends /v1/traces itself."""
        monkeypatch.setenv("DT_ENVIRONMENT", "https://abc123.live.dynatrace.com")
        monkeypatch.setenv("DT_OTLP_TOKEN", "dt-token")

        with patch(
            "shipsafe_shared.instrumentation.telemetry.OTLPSpanExporter"
        ) as MockExporter:
            MockExporter.return_value = MagicMock()
            mod = _reload_telemetry()
            provider = MagicMock()
            provider.add_span_processor = MagicMock()
            mod._add_dynatrace_exporter(provider)

        endpoint = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT", "")
        assert endpoint == "https://abc123.live.dynatrace.com/api/v2/otlp"
        assert not endpoint.endswith("/v1/traces")
        assert not endpoint.endswith("/v1/metrics")
        assert not endpoint.endswith("/v1/logs")

    def test_auth_header_uses_api_token_format(self, monkeypatch):
        """Header must be 'Authorization=Api-Token <token>' (not 'Bearer')."""
        monkeypatch.setenv("DT_ENVIRONMENT", "https://abc123.live.dynatrace.com")
        monkeypatch.setenv("DT_OTLP_TOKEN", "dt-secret-token")

        with patch(
            "shipsafe_shared.instrumentation.telemetry.OTLPSpanExporter"
        ) as MockExporter:
            MockExporter.return_value = MagicMock()
            mod = _reload_telemetry()
            provider = MagicMock()
            provider.add_span_processor = MagicMock()
            mod._add_dynatrace_exporter(provider)

        header = os.environ.get("OTEL_EXPORTER_OTLP_HEADERS", "")
        assert "Authorization=Api-Token dt-secret-token" in header

    def test_metrics_temporality_set_to_delta(self, monkeypatch):
        """Dynatrace requires delta temporality; OTel default is cumulative."""
        monkeypatch.setenv("DT_ENVIRONMENT", "https://abc123.live.dynatrace.com")
        monkeypatch.setenv("DT_OTLP_TOKEN", "dt-token")

        with patch(
            "shipsafe_shared.instrumentation.telemetry.OTLPSpanExporter"
        ) as MockExporter:
            MockExporter.return_value = MagicMock()
            mod = _reload_telemetry()
            provider = MagicMock()
            provider.add_span_processor = MagicMock()
            mod._add_dynatrace_exporter(provider)

        assert (
            os.environ.get("OTEL_EXPORTER_OTLP_METRICS_TEMPORALITY_PREFERENCE") == "delta"
        )

    def test_otlp_exporter_constructed_with_trace_endpoint(self, monkeypatch):
        """OTLPSpanExporter receives the /v1/traces endpoint explicitly.

        The base env var (OTEL_EXPORTER_OTLP_ENDPOINT) stays at /api/v2/otlp
        for SDK-level metric/log signal discovery.  The span exporter gets the
        full /v1/traces URL directly in its constructor so it does not rely on
        the SDK appending the signal suffix (which behaves differently across
        SDK versions and transport implementations).
        """
        monkeypatch.setenv("DT_ENVIRONMENT", "https://abc123.live.dynatrace.com")
        monkeypatch.setenv("DT_OTLP_TOKEN", "dt-token")

        # Import before patching so the module is in sys.modules; then patch
        # the name on that module object (not a reload which creates a new one).
        import shipsafe_shared.instrumentation.telemetry as telemetry_mod

        with patch.object(telemetry_mod, "OTLPSpanExporter") as MockExporter:
            MockExporter.return_value = MagicMock()
            provider = MagicMock()
            provider.add_span_processor = MagicMock()
            telemetry_mod._add_dynatrace_exporter(provider)

        MockExporter.assert_called_once()
        _, kwargs = MockExporter.call_args
        assert kwargs.get("endpoint") == "https://abc123.live.dynatrace.com/api/v2/otlp/v1/traces"

    def test_span_processor_added_to_provider(self, monkeypatch):
        monkeypatch.setenv("DT_ENVIRONMENT", "https://abc123.live.dynatrace.com")
        monkeypatch.setenv("DT_OTLP_TOKEN", "dt-token")

        with patch(
            "shipsafe_shared.instrumentation.telemetry.OTLPSpanExporter"
        ) as MockExporter:
            MockExporter.return_value = MagicMock()
            mod = _reload_telemetry()
            provider = MagicMock()
            provider.add_span_processor = MagicMock()
            mod._add_dynatrace_exporter(provider)

        provider.add_span_processor.assert_called_once()


# ---------------------------------------------------------------------------
# 6. Silent-fail: missing DT_OTLP_TOKEN → skip DT, no crash
# ---------------------------------------------------------------------------

class TestDynatraceMissingToken:
    def test_no_crash_when_dt_token_missing(self, monkeypatch):
        monkeypatch.setenv("DT_ENVIRONMENT", "https://abc123.live.dynatrace.com")
        # DT_OTLP_TOKEN deliberately not set

        with (
            patch("shipsafe_shared.instrumentation.telemetry.TracerProvider"),
            patch("shipsafe_shared.instrumentation.telemetry._add_dynatrace_exporter") as mock_dt,
        ):
            from shipsafe_shared.instrumentation.telemetry import init_telemetry
            init_telemetry("tidesync")

        mock_dt.assert_not_called()


# ---------------------------------------------------------------------------
# 6b. _register_phoenix internals — covers lines 86-95
# ---------------------------------------------------------------------------

class TestRegisterPhoenixInternals:
    def test_calls_phoenix_register_with_correct_args(self):
        import shipsafe_shared.instrumentation.telemetry as telemetry_mod

        with patch("phoenix.otel.register") as mock_register:
            telemetry_mod._register_phoenix("naviguard")

        mock_register.assert_called_once_with(
            project_name="naviguard",
            auto_instrument=True,
        )

    def test_swallows_exception_on_phoenix_failure(self):
        """Phoenix import failure must not crash the agent."""
        import shipsafe_shared.instrumentation.telemetry as telemetry_mod

        with patch("phoenix.otel.register", side_effect=RuntimeError("phoenix down")):
            # should not raise
            telemetry_mod._register_phoenix("naviguard")


# ---------------------------------------------------------------------------
# 7. project_name propagates
# ---------------------------------------------------------------------------

class TestProjectName:
    @pytest.mark.parametrize("agent_name", [
        "cargodb", "routeforge", "voyageblack",
        "tidesync", "naviguard", "agentops",
    ])
    def test_project_name_passed_to_phoenix(self, monkeypatch, agent_name):
        monkeypatch.setenv("PHOENIX_API_KEY", "pk-key")

        with (
            patch("shipsafe_shared.instrumentation.telemetry.TracerProvider"),
            patch("shipsafe_shared.instrumentation.telemetry._register_phoenix") as mock_phoenix,
            patch("shipsafe_shared.instrumentation.telemetry._add_dynatrace_exporter"),
        ):
            from shipsafe_shared.instrumentation.telemetry import init_telemetry
            init_telemetry(agent_name)

        mock_phoenix.assert_called_once_with(agent_name)
