"""Tests for demo_data loaders — smoke + contract checks."""

import pytest


class TestLoadVessels:
    def test_returns_five_vessels(self):
        from shipsafe_shared.demo_data import load_vessels
        v = load_vessels()
        assert len(v) == 5

    def test_each_vessel_has_required_fields(self):
        from shipsafe_shared.demo_data import load_vessels
        required = {"imo", "mmsi", "name", "operator", "flag", "type", "teu_capacity"}
        for vessel in load_vessels():
            assert required <= vessel.keys()

    def test_imo_numbers_are_strings(self):
        from shipsafe_shared.demo_data import load_vessels
        for v in load_vessels():
            assert isinstance(v["imo"], str)
            assert v["imo"].isdigit()

    def test_ever_given_present(self):
        from shipsafe_shared.demo_data import load_vessels
        names = [v["name"] for v in load_vessels()]
        assert "Ever Given" in names


class TestLoadPorts:
    def test_returns_six_ports(self):
        from shipsafe_shared.demo_data import load_ports
        p = load_ports()
        assert len(p) == 6

    def test_each_port_has_locode_and_coords(self):
        from shipsafe_shared.demo_data import load_ports
        required = {"locode", "name", "country", "lat", "lon", "timezone"}
        for port in load_ports():
            assert required <= port.keys()

    def test_jebel_ali_present(self):
        from shipsafe_shared.demo_data import load_ports
        codes = [p["locode"] for p in load_ports()]
        assert "AEJEA" in codes

    def test_locode_format(self):
        from shipsafe_shared.demo_data import load_ports
        for port in load_ports():
            assert len(port["locode"]) == 5
            assert port["locode"].isupper()


class TestFixturesForCargodb:
    def test_has_required_keys(self):
        from shipsafe_shared.demo_data import fixtures_for_cargodb
        f = fixtures_for_cargodb()
        assert {"crisis", "timeline", "vessel_positions", "conflict_count",
                "cargo_manifests", "vessels", "ports"} <= f.keys()

    def test_conflict_count_positive(self):
        from shipsafe_shared.demo_data import fixtures_for_cargodb
        assert fixtures_for_cargodb()["conflict_count"] > 0

    def test_cargo_manifests_have_iso_6346_ids(self):
        from shipsafe_shared.demo_data import fixtures_for_cargodb
        for m in fixtures_for_cargodb()["cargo_manifests"]:
            cid = m["container_id"]
            assert len(cid) == 11
            assert cid[:4].isupper()


class TestFixturesForRouteforge:
    def test_has_routing_mr(self):
        from shipsafe_shared.demo_data import fixtures_for_routeforge
        f = fixtures_for_routeforge()
        assert "routing_mr" in f
        assert f["routing_mr"]["mr_id"] == "447"

    def test_scenario_shows_regression(self):
        from shipsafe_shared.demo_data import fixtures_for_routeforge
        mr = fixtures_for_routeforge()["routing_mr"]
        assert mr["scenario_test_results"]["regression"] is True
        assert mr["scenario_test_results"]["verdict"] == "BLOCK"


class TestFixturesForVoyageblack:
    def test_log_entries_ordered_by_timestamp(self):
        from shipsafe_shared.demo_data import fixtures_for_voyageblack
        entries = fixtures_for_voyageblack()["log_entries"]
        timestamps = [e["timestamp"] for e in entries]
        assert timestamps == sorted(timestamps)

    def test_log_entries_have_event_ids(self):
        from shipsafe_shared.demo_data import fixtures_for_voyageblack
        for e in fixtures_for_voyageblack()["log_entries"]:
            assert e["event_id"].startswith("EVT-")


class TestFixturesForTidesync:
    def test_stale_arrivals_present(self):
        from shipsafe_shared.demo_data import fixtures_for_tidesync
        f = fixtures_for_tidesync()
        assert f["stale_count"] > 0
        assert f["affected_port"] == "AEJEA"

    def test_all_arrivals_breach_sla(self):
        from shipsafe_shared.demo_data import fixtures_for_tidesync
        for a in fixtures_for_tidesync()["port_arrivals"]:
            assert a["lag_minutes"] > a["sla_minutes"]


class TestFixturesForNaviguard:
    def test_model_metrics_show_regression(self):
        from shipsafe_shared.demo_data import fixtures_for_naviguard
        m = fixtures_for_naviguard()["model_metrics"]
        assert m["delta_pct"] < 0
        assert m["verdict"] == "BLOCK"
        assert m["confidence_score"] >= 90

    def test_trace_ids_evidenced(self):
        from shipsafe_shared.demo_data import fixtures_for_naviguard
        m = fixtures_for_naviguard()["model_metrics"]
        assert len(m["trace_ids_evidenced"]) >= 1


class TestFixturesForAgentops:
    def test_fleet_snapshot_has_all_five_agents(self):
        from shipsafe_shared.demo_data import fixtures_for_agentops
        agents = fixtures_for_agentops()["fleet_snapshot"]["agents"]
        names = {a["name"] for a in agents}
        assert names == {"cargodb", "routeforge", "voyageblack", "tidesync", "naviguard"}

    def test_cargodb_shows_latency_spike(self):
        from shipsafe_shared.demo_data import fixtures_for_agentops
        agents = fixtures_for_agentops()["fleet_snapshot"]["agents"]
        cargodb = next(a for a in agents if a["name"] == "cargodb")
        assert cargodb["latency_multiplier"] > 5

    def test_cascade_root_identified(self):
        from shipsafe_shared.demo_data import fixtures_for_agentops
        snap = fixtures_for_agentops()["fleet_snapshot"]
        assert snap["cascade_root"] == "cargodb"
