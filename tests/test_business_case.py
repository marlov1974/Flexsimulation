from flexsimulation.business_case import BusinessCaseResult


def test_net_value_per_customer() -> None:
    result = BusinessCaseResult(
        scenario_id="S3_portfolio_virtual_battery",
        households=10_000,
        net_value_sek=20_000_000,
    )

    assert result.net_value_per_customer_sek == 2000.0
