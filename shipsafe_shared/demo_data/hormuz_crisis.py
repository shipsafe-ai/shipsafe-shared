"""
Hormuz Crisis scenario — scripted, deterministic, high-fidelity mock data.

Timeline: 2026-06-01 14:55–15:02 UTC
Trigger: npx @shipsafe/<agent> demo

Every agent has its own view of this scenario.  This module provides
the shared seed data all six fixture loaders draw from.

Real events used as narrative source:
  - UKMTO advisory format from public bulletins
  - Strait of Hormuz coordinates (26.5°N, 56.5°E chokepoint)
  - Red Sea 2024 precedent for crisis avoidance routing

ISO 6346 container IDs: owner-code(3) + category(1) + serial(6) + check(1).
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

# ---------------------------------------------------------------------------
# Crisis metadata
# ---------------------------------------------------------------------------

CRISIS = {
    "id": "HORMUZ-2026-0601",
    "name": "Strait of Hormuz Transit Restriction",
    "locode_affected": "IRTHR",  # Bandar Abbas, Iran — closest port to chokepoint
    "chokepoint_lat": 26.5897,
    "chokepoint_lon": 56.3870,
    "ukmto_advisory": "UKMTO-2026-0601-004",
    "severity": "CRITICAL",
}

# ---------------------------------------------------------------------------
# Timeline events (deterministic, anchored to 2026-06-01)
# ---------------------------------------------------------------------------

T = {
    "t0": datetime(2026, 6, 1, 14, 55, 0, tzinfo=timezone.utc),   # UKMTO advisory
    "t1": datetime(2026, 6, 1, 14, 56, 0, tzinfo=timezone.utc),   # CargoDB conflicts
    "t2": datetime(2026, 6, 1, 14, 57, 0, tzinfo=timezone.utc),   # VoyageBlack window
    "t3": datetime(2026, 6, 1, 14, 58, 0, tzinfo=timezone.utc),   # RouteForge MR
    "t4": datetime(2026, 6, 1, 14, 59, 0, tzinfo=timezone.utc),   # TideSync Jebel Ali
    "t5": datetime(2026, 6, 1, 15,  0, 0, tzinfo=timezone.utc),   # NaviGuard block
    "t6": datetime(2026, 6, 1, 15,  1, 0, tzinfo=timezone.utc),   # AgentOps cascade
    "t7": datetime(2026, 6, 1, 15,  2, 0, tzinfo=timezone.utc),   # Human decision
}

# ---------------------------------------------------------------------------
# Vessel positions at crisis onset (Hormuz transit queue)
# ---------------------------------------------------------------------------

VESSEL_POSITIONS: list[dict[str, Any]] = [
    {
        "imo": "9811000",
        "name": "Ever Given",
        "lat": 26.5621,
        "lon": 56.3102,
        "speed_kn": 12.4,
        "heading_deg": 270,
        "status": "UNDERWAY",
        "conflict": True,
        "conflict_reason": "Entering restricted zone; nearest vessel 0.3 NM",
        "eta_jebel_ali": "2026-06-02T06:00:00Z",
    },
    {
        "imo": "9839430",
        "name": "MSC Gülsün",
        "lat": 26.5890,
        "lon": 56.4811,
        "speed_kn": 11.8,
        "heading_deg": 268,
        "status": "UNDERWAY",
        "conflict": True,
        "conflict_reason": "Overlapping waypoint with IMO 9863297 at T+18min",
        "eta_jebel_ali": "2026-06-02T08:30:00Z",
    },
    {
        "imo": "9863297",
        "name": "HMM Algeciras",
        "lat": 26.5744,
        "lon": 56.4423,
        "speed_kn": 13.1,
        "heading_deg": 271,
        "status": "UNDERWAY",
        "conflict": True,
        "conflict_reason": "Speed delta with ahead vessel creates collision corridor",
        "eta_jebel_ali": "2026-06-02T07:15:00Z",
    },
    {
        "imo": "9619907",
        "name": "Maersk Mc-Kinney Møller",
        "lat": 26.6102,
        "lon": 56.6234,
        "speed_kn": 10.2,
        "heading_deg": 265,
        "status": "SLOW_AHEAD",
        "conflict": False,
        "conflict_reason": None,
        "eta_jebel_ali": "2026-06-02T11:00:00Z",
    },
    {
        "imo": "9795726",
        "name": "COSCO Shipping Universe",
        "lat": 26.4988,
        "lon": 56.2891,
        "speed_kn": 0.0,
        "heading_deg": 0,
        "status": "ANCHORED",
        "conflict": True,
        "conflict_reason": "Anchored in transit lane; blocking inbound channel",
        "eta_jebel_ali": None,
    },
]

CONFLICT_COUNT = sum(1 for v in VESSEL_POSITIONS if v["conflict"])  # 4 primary + 19 others = 23

# ---------------------------------------------------------------------------
# Log entries for VoyageBlack (incident window 14:55–15:02)
# ---------------------------------------------------------------------------

LOG_ENTRIES: list[dict[str, Any]] = [
    {
        "timestamp": "2026-06-01T14:55:00Z",
        "service": "ukmto-feed",
        "level": "CRITICAL",
        "message": "UKMTO advisory UKMTO-2026-0601-004: Strait of Hormuz transit restriction in effect. "
                   "Mariners advised exercise extreme caution. Contact UKMTO on VHF Ch16.",
        "event_id": "EVT-001",
    },
    {
        "timestamp": "2026-06-01T14:55:42Z",
        "service": "ais-receiver",
        "level": "WARNING",
        "message": "AIS signal loss for 3 vessels in grid 26.5N/56.4E. Possible jamming.",
        "event_id": "EVT-002",
    },
    {
        "timestamp": "2026-06-01T14:56:11Z",
        "service": "routing-engine",
        "level": "ERROR",
        "message": "Route recalculation failed for IMO 9811000 (Ever Given): "
                   "primary waypoint WP-HORMUZ-07 marked restricted. Fallback route unavailable.",
        "event_id": "EVT-003",
    },
    {
        "timestamp": "2026-06-01T14:57:03Z",
        "service": "cargo-tracker",
        "level": "ERROR",
        "message": "Manifest conflict: container MSCU1847392 scheduled for Jebel Ali offload "
                   "but vessel transit now blocked. Destination port SLA breach imminent.",
        "event_id": "EVT-004",
    },
    {
        "timestamp": "2026-06-01T14:58:29Z",
        "service": "routing-engine",
        "level": "WARNING",
        "message": "Algorithm change MR !447 merged. New Hormuz crisis avoidance logic active. "
                   "Scenario tests bypassed in merge. Rollback candidate.",
        "event_id": "EVT-005",
    },
    {
        "timestamp": "2026-06-01T14:59:01Z",
        "service": "fivetran-sync",
        "level": "ERROR",
        "message": "Jebel Ali port arrival feed: last record timestamp 2026-06-01T04:33:00Z. "
                   "Expected freshness < 1h. Current lag: 4h 26m. SLA breached.",
        "event_id": "EVT-006",
    },
    {
        "timestamp": "2026-06-01T15:00:17Z",
        "service": "naviguard",
        "level": "CRITICAL",
        "message": "AI routing model regression detected. Crisis avoidance score: 31% "
                   "(baseline: 72%). Delta: -41%. Confidence: 94. BLOCK verdict issued.",
        "event_id": "EVT-007",
    },
    {
        "timestamp": "2026-06-01T15:01:08Z",
        "service": "agentops",
        "level": "WARNING",
        "message": "CargoDB latency spike: p99 8830ms (baseline 1002ms, 8.8x). "
                   "Cascade source: AIS feed timeout propagating to memory recall.",
        "event_id": "EVT-008",
    },
    {
        "timestamp": "2026-06-01T15:02:00Z",
        "service": "operator-console",
        "level": "INFO",
        "message": "Operator decision requested. 23 conflicts active, 1 AI regression, "
                   "3 stale reports. All agent verdicts pending human approval.",
        "event_id": "EVT-009",
    },
]

# ---------------------------------------------------------------------------
# Cargo manifests (ISO 6346 container IDs)
# ---------------------------------------------------------------------------

CARGO_MANIFESTS: list[dict[str, Any]] = [
    {
        "container_id": "MSCU1847392",
        "vessel_imo": "9811000",
        "origin_locode": "CNSHA",
        "destination_locode": "AEJEA",
        "hs_code": "8471.30",
        "description": "Laptop computers and notebooks",
        "weight_kg": 24000,
        "volume_cbm": 67.2,
        "priority": "HIGH",
        "sla_breach_at": "2026-06-02T06:00:00Z",
    },
    {
        "container_id": "EVGU4312861",
        "vessel_imo": "9811000",
        "origin_locode": "CNSHA",
        "destination_locode": "NLRTM",
        "hs_code": "6403.51",
        "description": "Leather footwear",
        "weight_kg": 18500,
        "volume_cbm": 58.0,
        "priority": "NORMAL",
        "sla_breach_at": "2026-06-03T12:00:00Z",
    },
    {
        "container_id": "HMMU7823940",
        "vessel_imo": "9863297",
        "origin_locode": "KRPUS",
        "destination_locode": "AEJEA",
        "hs_code": "2711.19",
        "description": "Liquefied petroleum gas in cylinders",
        "weight_kg": 21000,
        "volume_cbm": 45.0,
        "priority": "CRITICAL",
        "sla_breach_at": "2026-06-01T18:00:00Z",
    },
    {
        "container_id": "MAEU9034512",
        "vessel_imo": "9619907",
        "origin_locode": "DEHAM",
        "destination_locode": "SGSIN",
        "hs_code": "8481.80",
        "description": "Industrial valves and fittings",
        "weight_kg": 31000,
        "volume_cbm": 82.0,
        "priority": "NORMAL",
        "sla_breach_at": "2026-06-04T00:00:00Z",
    },
]

# ---------------------------------------------------------------------------
# Routing algorithm MR (RouteForge scenario)
# ---------------------------------------------------------------------------

ROUTING_MR = {
    "mr_id": "447",
    "title": "feat: add Hormuz crisis avoidance to waypoint scoring",
    "author": "dev-bot-42",
    "source_branch": "feat/hormuz-avoidance",
    "target_branch": "main",
    "state": "merged",
    "merged_at": "2026-06-01T14:58:29Z",
    "diff_summary": (
        "Modified waypoint_score() to apply -200 penalty to Hormuz transit "
        "zone during CRITICAL advisories. Penalty constant hardcoded; "
        "no unit tests added. Scenario test suite not run before merge."
    ),
    "scenario_test_results": {
        "normal_conditions_throughput_pct": 112,
        "hormuz_crisis_avoidance_pct": 31,
        "baseline_avoidance_pct": 72,
        "regression": True,
        "verdict": "BLOCK",
        "confidence": 94,
    },
}

# ---------------------------------------------------------------------------
# Port arrival feed (TideSync scenario)
# ---------------------------------------------------------------------------

PORT_ARRIVALS: list[dict[str, Any]] = [
    {
        "port_locode": "AEJEA",
        "vessel_imo": "9811000",
        "scheduled_arrival": "2026-06-02T06:00:00Z",
        "record_timestamp": "2026-06-01T04:33:00Z",
        "status": "STALE",
        "lag_minutes": 266,
        "sla_minutes": 60,
    },
    {
        "port_locode": "AEJEA",
        "vessel_imo": "9839430",
        "scheduled_arrival": "2026-06-02T08:30:00Z",
        "record_timestamp": "2026-06-01T04:31:00Z",
        "status": "STALE",
        "lag_minutes": 268,
        "sla_minutes": 60,
    },
    {
        "port_locode": "AEJEA",
        "vessel_imo": "9863297",
        "scheduled_arrival": "2026-06-02T07:15:00Z",
        "record_timestamp": "2026-06-01T04:29:00Z",
        "status": "STALE",
        "lag_minutes": 270,
        "sla_minutes": 60,
    },
]

# ---------------------------------------------------------------------------
# NaviGuard model performance
# ---------------------------------------------------------------------------

MODEL_METRICS = {
    "model_id": "routing-avoidance-v3.2",
    "evaluation_window": "2026-06-01T14:00:00Z/2026-06-01T15:00:00Z",
    "baseline_crisis_avoidance_pct": 72,
    "current_crisis_avoidance_pct": 31,
    "delta_pct": -41,
    "confidence_score": 94,
    "verdict": "BLOCK",
    "regression_category": "crisis_avoidance",
    "trace_ids_evidenced": [
        "trace-9f3a2b1c",
        "trace-7e4d6a0b",
        "trace-2c8f1e5d",
    ],
}

# ---------------------------------------------------------------------------
# AgentOps fleet snapshot at t6
# ---------------------------------------------------------------------------

FLEET_SNAPSHOT = {
    "timestamp": "2026-06-01T15:01:08Z",
    "agents": [
        {
            "name": "cargodb",
            "status": "DEGRADED",
            "p99_latency_ms": 8830,
            "baseline_p99_ms": 1002,
            "latency_multiplier": 8.8,
            "active_spans": 23,
            "tokens_used": 14200,
        },
        {
            "name": "routeforge",
            "status": "ACTIVE",
            "p99_latency_ms": 3210,
            "baseline_p99_ms": 2800,
            "latency_multiplier": 1.15,
            "active_spans": 5,
            "tokens_used": 8900,
        },
        {
            "name": "voyageblack",
            "status": "ACTIVE",
            "p99_latency_ms": 4100,
            "baseline_p99_ms": 3900,
            "latency_multiplier": 1.05,
            "active_spans": 9,
            "tokens_used": 12300,
        },
        {
            "name": "tidesync",
            "status": "ACTIVE",
            "p99_latency_ms": 1800,
            "baseline_p99_ms": 1600,
            "latency_multiplier": 1.13,
            "active_spans": 4,
            "tokens_used": 5100,
        },
        {
            "name": "naviguard",
            "status": "ACTIVE",
            "p99_latency_ms": 5500,
            "baseline_p99_ms": 4800,
            "latency_multiplier": 1.15,
            "active_spans": 7,
            "tokens_used": 9800,
        },
    ],
    "cascade_root": "cargodb",
    "cascade_reason": "AIS feed timeout → memory recall blocking → downstream agent queuing",
}
