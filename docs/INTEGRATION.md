# Integration guide

The contract owner creates a mandate, becoming its authority and the only account permitted to create proposals against its bounded capacity. Global and per-mandate counters are lifetime allocations and are not reclaimed. A proposal commits `target`, `declared_value`, and a 32-byte `calldata_hash`, plus an immutable HTTPS plan URL that explicitly states those exact values and explains the call's effects.

After `review_execution` reaches `reviewed`, consumers call `is_executable`. Execute only when `executable` is true, and verify locally that:

1. destination equals `target`;
2. transferred value equals `declared_value`;
3. `keccak256(actual_calldata)` equals `calldata_hash`.

Only after all three checks should the mandate authority coordinate `consume_execution` with the downstream action. Praxis provides replay-resistant authorization state, but it does not make a separate downstream call atomic; integrations must handle that race and failure boundary explicitly.

Read `get_execution` for audit fields. Treat `rationale` as diagnostic only; use `verdict`, `status`, and `is_executable` for machine decisions.
