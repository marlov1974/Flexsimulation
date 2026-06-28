from flexsimulation.activation import calculate_response_kw


def test_ev_pause_response() -> None:
    assert calculate_response_kw(11.0, 0.0) == 11.0


def test_battery_discharge_response() -> None:
    assert calculate_response_kw(0.0, -5.0) == 5.0


def test_pv_curtailment_difference() -> None:
    # Planned PV -6 kW and actual PV -3 kW means production was reduced by 3 kW.
    assert calculate_response_kw(-6.0, -3.0) == -3.0
