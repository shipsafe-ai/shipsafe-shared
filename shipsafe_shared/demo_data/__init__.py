"""
Demo data loaders — each agent imports the slice it needs.

Usage:
    from shipsafe_shared.demo_data import (
        load_vessels, load_ports,
        fixtures_for_cargodb,
        fixtures_for_routeforge,
        fixtures_for_voyageblack,
        fixtures_for_tidesync,
        fixtures_for_naviguard,
        fixtures_for_agentops,
    )
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

_HERE = Path(__file__).parent


def load_vessels() -> list[dict[str, Any]]:
    return json.loads((_HERE / "vessels.json").read_text())


def load_ports() -> list[dict[str, Any]]:
    return json.loads((_HERE / "ports.json").read_text())


def fixtures_for_cargodb() -> dict[str, Any]:
    from shipsafe_shared.demo_data.hormuz_crisis import (
        CARGO_MANIFESTS,
        CONFLICT_COUNT,
        CRISIS,
        T,
        VESSEL_POSITIONS,
    )
    return {
        "crisis": CRISIS,
        "timeline": T,
        "vessel_positions": VESSEL_POSITIONS,
        "conflict_count": CONFLICT_COUNT,
        "cargo_manifests": CARGO_MANIFESTS,
        "vessels": load_vessels(),
        "ports": load_ports(),
    }


def fixtures_for_routeforge() -> dict[str, Any]:
    from shipsafe_shared.demo_data.hormuz_crisis import CRISIS, ROUTING_MR, T
    return {
        "crisis": CRISIS,
        "timeline": T,
        "routing_mr": ROUTING_MR,
    }


def fixtures_for_voyageblack() -> dict[str, Any]:
    from shipsafe_shared.demo_data.hormuz_crisis import (
        CARGO_MANIFESTS,
        CRISIS,
        LOG_ENTRIES,
        ROUTING_MR,
        T,
        VESSEL_POSITIONS,
    )
    return {
        "crisis": CRISIS,
        "timeline": T,
        "log_entries": LOG_ENTRIES,
        "vessel_positions": VESSEL_POSITIONS,
        "cargo_manifests": CARGO_MANIFESTS,
        "routing_mr": ROUTING_MR,
    }


def fixtures_for_tidesync() -> dict[str, Any]:
    from shipsafe_shared.demo_data.hormuz_crisis import CRISIS, PORT_ARRIVALS, T
    return {
        "crisis": CRISIS,
        "timeline": T,
        "port_arrivals": PORT_ARRIVALS,
        "stale_count": len(PORT_ARRIVALS),
        "affected_port": "AEJEA",
    }


def fixtures_for_naviguard() -> dict[str, Any]:
    from shipsafe_shared.demo_data.hormuz_crisis import CRISIS, MODEL_METRICS, ROUTING_MR, T
    return {
        "crisis": CRISIS,
        "timeline": T,
        "model_metrics": MODEL_METRICS,
        "routing_mr": ROUTING_MR,
    }


def fixtures_for_agentops() -> dict[str, Any]:
    from shipsafe_shared.demo_data.hormuz_crisis import CRISIS, FLEET_SNAPSHOT, LOG_ENTRIES, T
    return {
        "crisis": CRISIS,
        "timeline": T,
        "fleet_snapshot": FLEET_SNAPSHOT,
        "log_entries": LOG_ENTRIES,
    }


__all__ = [
    "load_vessels",
    "load_ports",
    "fixtures_for_cargodb",
    "fixtures_for_routeforge",
    "fixtures_for_voyageblack",
    "fixtures_for_tidesync",
    "fixtures_for_naviguard",
    "fixtures_for_agentops",
]
