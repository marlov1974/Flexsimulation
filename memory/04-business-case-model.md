# Business case model

The simulator compares business-case scenarios rather than only asset performance.

## Initial scenario ladder

```text
S0_fragmented_no_coordination
S1_local_smart_optimisation
S2_dual_home_integrated_optimisation
S3_portfolio_virtual_battery
S4_full_market_optimizer
```

## Local vs system business case

The simulator must distinguish between:

```text
local gross business case
```

and:

```text
integrated net portfolio business case
```

A local gross business case may include flexibility revenue and direct partner cost, while excluding system effects. An integrated net portfolio business case must include customer value, rebound, wholesale position, imbalance, intraday recovery, delivery risk, cross-asset effects, customer constraints and operating cost.

## Hidden system costs and missed value

The simulator should make these visible:

- rebound energy and rebound recovery cost,
- imbalance exposure,
- missing wholesale or portfolio position integration,
- customer promise violations,
- duplicated integrations,
- lost cross-asset effects,
- weak baseline quality,
- local optimisation conflicts,
- reduced future optionality,
- energy sharing treated as an administrative problem instead of value source.

## Value categories

- customer savings
- customer flexibility bonus
- customer progression or next-best-upgrade value
- energy-sharing value
- spot optimisation value
- intraday optimisation value
- mFRR or flexibility market revenue
- wholesale position value
- imbalance cost avoided
- rebound cost or rebound value
- delivery error and penalties
- platform and operational cost
- retention or stickiness effect
- strategic control effect
- value attribution by capability

## Scaling principle

The simulator does not need to simulate the entire addressable market. It should simulate enough households for stable portfolio statistics, report values per customer and per 1,000 customers, and scale to market assumptions by segment.
