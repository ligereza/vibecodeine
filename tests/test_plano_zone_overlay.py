from flujo.plano import render_rider, render_svg, validate_evento, validate_zone_overlay


def _evento_con_overlay():
    return {
        "nombre": "Festival Overlay 2026",
        "duracion_horas": 6,
        "voluntarios": 7,
        "asistentes_estimados": 2500,
        "incluye_testeo": True,
        "masivo": True,
        "zone_overlay": {
            "enabled": True,
            "schema_version": "0.1",
            "zones": [
                {"zone_id": "FOH_VJ", "label": "FOH visual", "plane": "physical",
                 "purpose": "control visual", "x_m": 12.0, "y_m": 0.0, "w_m": 3.0, "h_m": 2.0},
                {"zone_id": "NETWORK_CORE", "label": "Núcleo de red", "plane": "logical"},
            ],
            "nodes": [
                {"node_id": "xio-foh-01", "label": "XIO FOH", "zone_id": "FOH_VJ",
                 "role": "observe", "mode": "observe", "x_m": 12.6, "y_m": 0.8},
                {"node_id": "vj-host-01", "label": "VJ host", "zone_id": "FOH_VJ",
                 "role": "visual_writer", "mode": "proposal_only", "active_writer": True,
                 "writer_groups": ["visual_cues"], "x_m": 13.6, "y_m": 0.8},
                {"node_id": "network-core-01", "label": "Network core", "zone_id": "NETWORK_CORE",
                 "role": "router", "mode": "observe"},
            ],
            "links": [
                {"from": "xio-foh-01", "to": "vj-host-01", "transport": "OSC",
                 "channel": "/timecode", "direction": "observe"},
            ],
        },
    }


def test_overlay_legacy_is_opt_in():
    event = {"nombre": "Legacy", "duracion_horas": 3, "voluntarios": 3}
    report = validate_evento(event)
    assert report["ok"] is True
    assert report["summary"]["zone_overlay"]["enabled"] is False
    assert "GRAFO OPERATIVO" not in render_svg(event)
    assert "Grafo operativo" not in render_rider(event)


def test_overlay_validates_and_renders_physical_and_logical_layers():
    event = _evento_con_overlay()
    report = validate_zone_overlay(event)
    assert report["ok"] is True
    assert report["summary"] == {"enabled": True, "zones": 2, "nodes": 3, "links": 1}

    svg = render_svg(event)
    assert "FOH_VJ" in svg
    assert "xio-foh-01" in svg
    assert "OSC" in svg
    assert "SOLO OBSERVACIÓN" in svg

    rider = render_rider(event)
    assert "Grafo operativo XIO/FOH/VJ" in rider
    assert "network-core-01" in rider
    assert "xio-foh-01 → vj-host-01" in rider

    event_report = validate_evento(event)
    assert event_report["ok"] is True
    assert event_report["summary"]["zone_overlay"]["links"] == 1


def test_overlay_rejects_multiple_active_writers_and_bad_references():
    event = {
        "zone_overlay": {
            "enabled": True,
            "zones": [{"zone_id": "FOH_VJ", "plane": "physical"}],
            "nodes": [
                {"node_id": "vj-a", "zone_id": "FOH_VJ", "active_writer": True,
                 "writer_groups": ["visual_cues"]},
                {"node_id": "vj-b", "zone_id": "FOH_VJ", "active_writer": True,
                 "writer_groups": ["visual_cues"]},
            ],
            "links": [{"from": "vj-a", "to": "missing", "transport": "OSC"}],
        }
    }
    report = validate_zone_overlay(event)
    assert report["ok"] is False
    text = " ".join(report["errors"])
    assert "varios escritores activos" in text
    assert "referencia nodo inexistente" in text

