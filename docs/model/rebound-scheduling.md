# Rebound scheduling

Any activation that defers or advances energy creates a rebound position.

## Rebound position

A rebound position should track:

- household id,
- site id,
- asset type,
- energy kWh,
- direction,
- created timestep,
- earliest recovery timestep,
- latest recovery timestep,
- maximum recovery kW,
- source activation id,
- market area,
- status.

## Business meaning

Rebound is not only an operational side effect. It is a portfolio position that can be scheduled and potentially monetised or cost-minimised through intraday trading and future flexibility planning.
