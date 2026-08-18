# Integration guide

An authority creates a mandate and communicates its ID. A proposer commits the proposed call using `target`, `declared_value`, and a 32-byte `calldata_hash`, plus an immutable HTTPS plan URL that explicitly states those exact values and explains the call's effects.

After `review_execution` reaches `reviewed`, consumers call `is_executable`. Execute only when `executable` is true, and verify locally that:

1. destination equals `target`;
2. transferred value equals `declared_value`;
3. `keccak256(calldata)` equals `calldata_hash`.

Then the mandate authority calls `consume_execution` before performing or atomically coordinating the downstream action. Praxis provides replay-resistant authorization state, not atomic execution across another contract.

Read `get_execution` for audit fields. Treat `rationale` as diagnostic only; use `verdict`, `status`, and `is_executable` for machine decisions.
