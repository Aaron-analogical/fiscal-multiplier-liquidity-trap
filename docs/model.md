# The model in plain English

This note explains the moving parts without the algebra. The full derivation is in the [English thesis](../paper/thesis_en.pdf).

## The question

The fiscal multiplier is how many dollars of GDP one extra dollar of government spending produces. It depends on the state of the economy and on how the spending is paid for.

## The economy

- **Households** consume, work, and save in government bonds. They also value bonds for their safety. A shock to that preference for safety makes them save more, which pushes rates down.
- **Firms** have some pricing power and pay a cost to change prices, so prices are sticky. This is why spending can raise output at all.
- **The government** spends on consumption or on investment. Investment builds public capital after a delay and makes firms more productive.
- **The central bank** sets the nominal rate with a Taylor rule, but it cannot go below zero. When it hits zero, the economy is in a liquidity trap.

## Why financing matters

A lump-sum tax does not change anyone's incentives. A labor tax does: it discourages work, which raises firms' costs and inflation.

- In normal times, higher inflation makes the central bank raise rates, which weakens the stimulus.
- In a trap, rates cannot move, so higher inflation lowers the real interest rate, which strengthens the stimulus.

That is the simple model's result. The full model adds a catch: if the tax stays high after the trap ends, people expect lower future income and the central bank is back in action, so the gain disappears. This is why tax timing matters most.

## Scenarios

| Setting | Values |
|---|---|
| Financing | Lump-sum tax, labor tax, debt repaid by a labor tax |
| Spending | All consumption (α = 0) or all investment (α = 1) |
| Time to build | 1 or 16 quarters |
| State | Normal times, or a 12-quarter liquidity trap |
| Tax response to debt, γn | 0.05 to 0.25 (debt only) |

All scenarios share one steady state with zero tax and zero debt, so only the response to the shock differs.

## Measuring the multiplier

- **Impact multiplier:** change in GDP divided by change in spending in the first quarter.
- **Present-value multiplier:** the same ratio using discounted sums over 500 quarters.

In a trap, the changes compare a run with both shocks against a run with only the liquidity shock. This separates the effect of spending from the recession itself.

## Calibration

| Parameter | Value |
|---|---|
| Discount factor, β | 0.99 |
| Elasticity of substitution between goods, θ | 6 |
| Preference parameters, σ and γ | 1 and 0.29 |
| Output elasticity to labor and to public capital, a and b | 1 and 0.08 |
| Slope of inflation on marginal cost, κ | 0.03 |
| Taylor rule response to inflation and to output, φπ and φy | 1.5 and 0.05 |
| Interest rate smoothing, ρr | 0 |
| Persistence of spending, ρ | 0.8 |
| Spending to GDP, ḡ | 0.2 |
| Public investment share of spending, ᾱ | 0.23 |
| Depreciation, δ | 0.025 |
| Persistence of the liquidity shock and of the tax, ρζ and ρn | 0.95 and 0.5 |
| Size of each shock | 0.01 |

The simple model sets φy = 0, δ = 1, and adds trap persistence p = 0.8.

## Notes on this rebuild

- The thesis listings are merged into one file, [`fiscal.mod`](../model/fiscal.mod), with switches for financing and build time.
- It uses Dynare's current perfect-foresight commands, not the older `simul` command in the thesis listings.
- Time to build follows equation (19), so one quarter means `gi(-1)`.
- Spending shortens the trap by one or two quarters in some runs. The 12-quarter check applies to the runs with the liquidity shock alone.
- Real-rate panels show the nominal rate minus current inflation, as in the thesis figures.
