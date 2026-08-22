# Praxis

Praxis is a contract-only semantic execution firewall: it lets an authority publish an immutable mandate, then permits a committed execution only when deterministic limits and independent GenLayer semantic review agree that the execution plan stays within that mandate.

There is no frontend or off-chain decision service. The canonical deployable source is [`contracts/praxis.py`](contracts/praxis.py).

Canonical Studionet deployment: [`0x076aeCCc66673C93B54FafaB9C56Eb10fBc9D9Ed`](https://explorer-studio.genlayer.com/address/0x076aeCCc66673C93B54FafaB9C56Eb10fBc9D9Ed) (v1.1.0, adds `settle_expired_challenge`). Exact source-parity and complete runtime evidence are recorded in [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md).

## Why this primitive exists

Transaction allowlists can constrain an address and value, but they cannot determine whether a natural-language execution plan preserves a mandate's purpose, recipient, constraints, and authority boundaries. Praxis combines both layers:

1. deterministic code enforces owner-only mandate allocation, authority-only proposal creation, target, value, lifecycle, replay protection, challenge timing, and bounded storage;
2. validators independently fetch the disclosed evidence and reason about semantic fidelity;
3. exact agreement is required on the load-bearing decision fields;
4. only an `authorized` result that survives its challenge window becomes executable.

Removing GenLayer consensus would replace independent observation with trust in one model or operator. That is the trust property Praxis is designed to avoid.

## Lifecycle

`create_mandate` → `propose_execution` → `review_execution` → challenge window → `consume_execution`

A proposal may instead become `blocked`, `inconclusive`, `cancelled`, or return to `proposed` after its single bonded challenge. Only the contract owner can create mandates, and only that mandate's authority can create proposals. This deliberately centralizes allocation of the lifetime global capacity so outsiders cannot exhaust it. A challenge is allowed only while `now < reviewed_at + challenge_window`. If re-review remains unavailable for a full `challenge_window` after `challenged_at`, anyone can call `settle_expired_challenge`; it refunds the challenger and cancels the execution, including during pause or mandate closure.

The plan evidence must explicitly reproduce the exact committed target, value, and calldata hash. This binds the semantic review to the execution commitment; it does not decode or execute calldata on behalf of an integrator.

### Challenge-bond liveness guarantee

`challenge_execution` records the on-chain `challenged_at` timestamp and holds the exact bond. After `challenged_at + challenge_window`, `settle_expired_challenge` is permissionless: it clears the held bond, refunds it to the recorded challenger, and permanently cancels the execution. It cannot run early, cannot settle an unchallenged execution, and cannot be run twice. The method deliberately bypasses the normal active-mandate gate, so a global pause or mandate closure cannot strand a challenger while external evidence or model infrastructure is unavailable.

This is a settlement route, not an authorization shortcut: it never creates a verdict or makes an execution consumable. The live timeout settlement [finalized successfully on Studionet](https://explorer-studio.genlayer.com/tx/0x7cc12a99b8323bd9d82c1cfc347413ff36a47914819173502972b10ab50157b3), leaving the execution cancelled with a zero held-bond balance.

## Public interface

Writes: `set_paused`, `create_mandate`, `set_mandate_status`, `propose_execution`, `review_execution`, `challenge_execution`, `settle_expired_challenge`, `consume_execution`, `cancel_execution`.

Views: `is_executable`, `get_mandate`, `get_execution`, `list_mandate_executions`, `get_info`.

## Local verification

Python 3.12 is required.

```text
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt
.venv/Scripts/python -m pytest tests/direct -q
.venv/Scripts/python scripts/preflight.py
```

The final local result is 28 Direct Mode tests passed, plus 18 preflight source invariants and successful GenVM lint/schema validation. `tests/conftest.py` is test infrastructure and the linter is explicitly scoped to `contracts/praxis.py`, avoiding accidental treatment of tests as deployable contracts.

Studionet commands are documented in [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md). Consensus boundaries and threat assumptions are in [`docs/CONSENSUS.md`](docs/CONSENSUS.md) and [`SECURITY.md`](SECURITY.md).

## Scope and limitations

Praxis is an authorization signal, not an executor, oracle of objective truth, or guarantee that prose accurately decodes arbitrary calldata. Integrators must verify `keccak256(actual_calldata) == calldata_hash` and coordinate consumption with downstream execution; Praxis cannot make that separate call atomic. Web availability and genuine validator disagreement fail closed without mutating an accepted review state.

## Repository policy

Exactly one contract is deployable. Fixtures, tests, and scripts are supporting evidence. The repository intentionally contains no frontend and no GitHub Actions workflow.

Licensed under MIT; see [`LICENSE`](LICENSE).
