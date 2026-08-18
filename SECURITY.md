# Security model

## Invariants

- A proposal cannot bypass its immutable allowed target or maximum value.
- Semantic authorization requires exact evidence binding to target, value, and calldata hash.
- Malformed or unavailable nondeterministic results do not mutate a trusted verdict.
- Only the mandate authority can consume an authorized execution.
- Consumption is one-way and cannot occur during the challenge window.
- A proposal has at most one challenge and exactly one held bond.
- Contract and per-mandate storage are bounded.
- A global pause blocks new proposals, ordinary reviews, challenges, and consumption, while allowing an already-held bond to be resolved.

## Trust assumptions

The GenLayer validator set and runtime provide consensus execution. Evidence hosts remain available and present substantially consistent content. The plan author truthfully supplies a human-readable decoding of the committed calldata; the downstream executor must independently hash the actual calldata before execution.

## Known limitations

Natural-language interpretation can disagree or fail. Praxis treats that as non-authorization. Exact semantic agreement favors safety over liveness. A page may change between proposal and review, so integrators should use immutable content-addressed evidence. Praxis does not execute downstream calls and cannot prove that a prose decoding is correct without an external deterministic decoder.

Do not place secrets in mandates, plans, summaries, or URLs. They are public contract data.
