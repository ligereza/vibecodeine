from __future__ import annotations

import json

from cultura.mak_plataforma import azure_services


class _Response:
    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self, _limit):
        return json.dumps(self.payload).encode("utf-8")


def test_emit_event_drops_content_fields_and_requires_acceptance(monkeypatch):
    monkeypatch.setattr(
        azure_services, "_connection_string",
        lambda: "InstrumentationKey=00000000-0000-0000-0000-000000000000;"
                "IngestionEndpoint=https://example.invalid/",
    )
    captured = {}

    def fake_urlopen(request, timeout):
        captured["payload"] = json.loads(request.data)
        return _Response({"itemsReceived": 1, "itemsAccepted": 1, "errors": []})

    monkeypatch.setattr(azure_services.urllib.request, "urlopen", fake_urlopen)
    result = azure_services.emit_event(
        "mak.test", properties={"status": "ok", "prompt": "do not send"},
        measurements={"latency_ms": 12, "raw_bytes": 9000})
    props = captured["payload"]["data"]["baseData"]["properties"]
    measures = captured["payload"]["data"]["baseData"]["measurements"]
    assert props == {"status": "ok"}
    assert measures == {"latency_ms": 12.0}
    assert result["sent"] is True
    assert result["items_accepted"] == 1
    assert result["dropped_properties"] == 1
    assert result["dropped_measurements"] == 1


def test_emit_event_reports_rejected_envelope_without_provider_body(monkeypatch):
    monkeypatch.setattr(
        azure_services, "_connection_string",
        lambda: "InstrumentationKey=00000000-0000-0000-0000-000000000000;"
                "IngestionEndpoint=https://example.invalid/",
    )
    monkeypatch.setattr(
        azure_services.urllib.request, "urlopen",
        lambda *_args, **_kwargs: _Response({
            "itemsReceived": 1, "itemsAccepted": 0,
            "errors": [{"message": "provider detail must stay hidden"}],
        }),
    )
    result = azure_services.emit_event("mak.test", properties={"status": "bad"})
    assert result == {
        "available": False, "sent": False, "error": "appinsights_event_rejected",
    }


def test_inventory_keeps_app_insights_partial_until_workload_forwarding_exists():
    resources = [{"type": "Microsoft.Insights/components", "name": "insights",
                  "resourceGroup": "makmak", "location": "brazilsouth",
                  "state": "Succeeded"}]
    row = next(item for item in azure_services._service_rows(resources)
               if item["id"] == "application_insights")
    assert row["resource_state"] == "live"
    assert row["integration_state"] == "partial"


def test_disabled_subscription_blocks_costed_integrations_but_keeps_inventory():
    resources = [
        {"type": "Microsoft.Search/searchServices", "name": "search",
         "resourceGroup": "makmak", "location": "brazilsouth", "state": "Succeeded"},
        {"type": "Microsoft.Insights/components", "name": "insights",
         "resourceGroup": "makmak", "location": "brazilsouth", "state": "Succeeded"},
    ]
    rows = {row["id"]: row for row in azure_services._service_rows(resources, "Disabled")}
    assert rows["search"]["resource_state"] == "live"
    assert rows["search"]["integration_state"] == "blocked_subscription"
    assert rows["application_insights"]["integration_state"] == "partial"
