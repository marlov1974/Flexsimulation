# Observation boundary

The simulator is a synthetic reality proxy. It may use latent states to generate reality, but ML and bidding models must only see configured observations.

## Forbidden for ML/bidding models

- person objects
- shower objects
- travel intent
- true future behaviour
- internal load events
- true future weather
- hidden device failure state

## First observable household-level channels

```text
total_power_kw
pv_power_kw
ev_power_kw
heatpump_power_kw
battery_power_kw
planned_total_power_kw
planned_pv_power_kw
planned_ev_power_kw
planned_heatpump_power_kw
planned_battery_power_kw
```

## Sign convention

```text
+ means electricity consumption/load
- means generation/export/discharge
```

## Residual

```text
residual_uncontrolled_kw =
  total_power_kw
  - pv_power_kw
  - ev_power_kw
  - heatpump_power_kw
  - battery_power_kw
```

## Response

For upward regulation from load reduction or discharge:

```text
up_response_kw = baseline_power_kw - actual_power_kw
```

Examples:

- EV planned +11 kW and actual 0 kW gives +11 kW up response.
- Battery planned 0 kW and actual -5 kW gives +5 kW up response.
- PV planned -6 kW and actual -3 kW is down regulation from curtailment.
