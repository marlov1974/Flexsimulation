# Baseline and activation

Flexibility is measured as deviation from a plan.

## Baseline world

The baseline world is what the controller planned to do without activation.

## Activation world

The activation world is what actually happened after an activation signal changed the plan.

## Response

```text
response_kw = baseline_power_kw - actual_power_kw
```

Positive response can represent upward regulation when load is reduced or discharge/export increases.

Examples:

- planned EV +11 kW, actual 0 kW gives +11 kW up response.
- planned battery 0 kW, actual -5 kW gives +5 kW up response.
- planned PV -6 kW, actual -3 kW represents curtailment and down regulation.
