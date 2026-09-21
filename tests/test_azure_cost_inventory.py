from tools.azure_cost_inventory import build_snapshot


def test_missing_cost_is_unknown_not_zero_and_no_mutations():
    resources = [{
        "id": "/subscriptions/s/resourceGroups/g/providers/Microsoft.ApiManagement/service/api",
        "name": "api", "type": "Microsoft.ApiManagement/service",
        "sku": {"name": "BasicV2"},
    }]
    usage = [{"instanceName": resources[0]["id"], "pretaxCost": "None"}]
    result = build_snapshot(resources, [], usage, start="2026-09-01", end="2026-09-20")
    assert result["monetary_cost"]["status"] == "unavailable"
    assert result["monetary_cost"]["total"] is None
    assert result["budget_count"] == 0
    assert result["mutations"] == []
    assert result["decisions"][0]["decision"] == "review_no_backend"


def test_numeric_costs_are_summed_only_when_every_row_is_numeric():
    result = build_snapshot([], [{}], [
        {"instanceName": "historic-a", "pretaxCost": 1.25},
        {"instanceName": "historic-b", "pretaxCost": "2.50"},
    ], start="2026-09-01", end="2026-09-20")
    assert result["monetary_cost"] == {
        "status": "measured", "numeric_rows": 2, "total": 3.75,
        "rule": "null or absent cost is unknown, never zero",
    }
