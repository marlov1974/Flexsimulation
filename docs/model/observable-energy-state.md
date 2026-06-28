# Observable energy state

The first observation boundary is household-level 15-minute energy channels.

## Channels

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
+ consumption/load
- generation/export/discharge
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

The residual is observable as an aggregate, but its latent causes are not exposed.
