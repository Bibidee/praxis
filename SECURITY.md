# Security model

## Invariants

- A proposal cannot bypass its immutable allowed target or maximum value.
- Only the contract owner can allocate mandates. Only a mandate authority can allocate its proposal slots. Consequently, an unauthorized outsider cannot increment either global lifetime counter.
- Semantic authorization requires exact evidence binding to target, value, and calldata hash.
- Malformed or unavailable nondeterministic results do not mutate a trusted verdict.
- Only the mandate authority can consume an authorized execution.
- Consumption is one-way and cannot occur during the challenge window.
- A proposal has at most one challenge and exactly one held bond.
- Contract and per-mandate storage are bounded.
- A challenge is accepted only before its exact deadline and at most once.
- A global pause blocks new proposals, ordinary reviews, challenges, consumption, and executable signalling, while allowing an already-held bond to be resolved.

## Trust assumptions

The GenLayer validator set and runtime provide consensus execution. Evidence hosts remain available and present substantially consistent content. Canonical evidence should be pinned to an immutable commit or content address. The plan author truthfully supplies a human-readable decoding of the committed calldata; the downstream executor must independently Keccak-256 hash the actual calldata before execution.

The owner is a trusted capacity allocator. `MAX_MANDATES`, `MAX_EXECUTIONS`, and each mandate's 32 execution slots are lifetime limits: cancellation and consumption preserve history and do not reclaim them. This centralization is intentional and narrowly protects finite shared storage; the owner cannot bypass semantic review, challenge timing, target/value constraints, or downstream execution gates.

## Known limitations

Natural-language interpretation can disagree or fail. Praxis treats that as non-authorization. Exact semantic agreement favors safety over liveness. Evidence can be unavailable or can change when a mutable URL is used; URL filtering reduces obvious local-network targets but is not a claim of complete SSRF elimination. Praxis does not execute downstream calls, cannot make consumption and that call atomic, and cannot prove that a prose decoding is correct without an external deterministic decoder.

Do not place secrets in mandates, plans, summaries, or URLs. They are public contract data.
