# Consensus design

`review_execution` first applies a deterministic safety floor. A target outside the mandate or a value above its cap is blocked without model inference.

Resource allocation is deterministic and precedes semantic consensus. Only the contract owner can create mandates, and only a mandate authority can create its proposals. Global and per-mandate bounds are lifetime limits; terminal records remain available for audit and do not reclaim capacity.

For candidates that pass that floor, each validator independently fetches the constitution and execution-plan evidence and runs the same bounded assessment. Untrusted source text is JSON-encoded as data and explicitly excluded from the instruction hierarchy. Model output is strictly parsed, type-checked, range-checked, and reduced to bounded fields before any storage mutation.

The validator does not trust the leader payload. It rejects a malformed envelope and independently recomputes the observation. Exact equality is required for the eight semantic/binding choices and their derived verdict. Diagnostic prose and evidence-quality wording are not consensus dimensions. Exactness is deliberately conservative: disagreement produces no accepted mutation rather than averaging away a security boundary.

Verdict derivation is deterministic:

- `authorized`: purpose, recipient, constraints, plan hash, plan target, and plan value are all `yes`; authority expansion and hidden side effects are `no`; confidence is at least 75.
- `blocked`: a material mismatch or forbidden authority/side effect is positively identified.
- `inconclusive`: every other well-formed observation.

Fetch failures, empty evidence, malformed output, and unavailable inference are explicit retryable errors. They do not become authorization.

Challenge settlement is also deterministic. One exact bond can reopen an authorized or inconclusive review. On re-review, a non-authorized result returns the bond to the challenger; an authorized result transfers it to the mandate authority. A held bond remains resolvable during a global pause or after mandate closure so administrative action cannot trap it.

The challenge deadline is exact: a challenge is valid only when `now < reviewed_at + challenge_window`; equality or a later timestamp is expired. Blocked outcomes are not challengeable and a proposal can be challenged only once. Global pause blocks new challenges, but never blocks re-review of a proposal with a held bond.
