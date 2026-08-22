# Praxis — Steward Review Response

## Review request addressed

The steward identified a liveness failure: after a bonded challenge, an unavailable plan page or model could make re-review revert indefinitely. The bond remained held, ordinary cancellation was unavailable, and no expiry path could settle it.

## Resolution

Praxis v1.1.0 adds the public write method `settle_expired_challenge(execution_id)`.

`challenge_execution` now records `challenged_at`. Once `challenged_at + challenge_window` has elapsed, any account can call `settle_expired_challenge`. The contract atomically:

1. verifies the execution is still challenged and has a held bond;
2. clears the held-bond balance;
3. marks the execution `cancelled` with no verdict; and
4. returns the complete bond to the recorded challenger.

The route intentionally does not depend on the plan page, model availability, an owner transaction, or a successful re-review. It remains callable while the contract is globally paused and after the mandate has been closed. A challenger therefore has a deterministic on-chain exit even when external evidence infrastructure is unavailable.

## Safety properties

- **No early withdrawal:** settlement reverts before the exact expiry boundary.
- **No arbitrary withdrawal:** it requires a proposed execution, a recorded challenge timestamp, and a positive held bond.
- **No double settlement:** the first settlement clears the held bond and cancels the execution; a later call fails its state checks.
- **No forced re-review:** the timeout route resolves only the held bond and proposal lifecycle. It does not manufacture an authorization verdict.
- **Failure-safe behavior:** unavailable evidence or model responses cannot lock challenger funds indefinitely.

## Matching deployed source and live evidence

- **Repository:** https://github.com/Bibidee/praxis
- **Canonical Studionet contract:** [`0x076aeCCc66673C93B54FafaB9C56Eb10fBc9D9Ed`](https://explorer-studio.genlayer.com/address/0x076aeCCc66673C93B54FafaB9C56Eb10fBc9D9Ed)
- **Deployment transaction:** [`0x543acd04b12f2f7763923445570a5307d4c5ff194146135b0cdb84904009ef78`](https://explorer-studio.genlayer.com/tx/0x543acd04b12f2f7763923445570a5307d4c5ff194146135b0cdb84904009ef78)
- **Live timeout settlement:** [`0x7cc12a99b8323bd9d82c1cfc347413ff36a47914819173502972b10ab50157b3`](https://explorer-studio.genlayer.com/tx/0x7cc12a99b8323bd9d82c1cfc347413ff36a47914819173502972b10ab50157b3) — finalized successfully; the execution was cancelled and its held bond became zero.
- **Canonical source commit:** `130ff693f665dfc5e385c1b03ebab8796c7dfbba`
- **Source SHA-256:** `687dcde0a00f838c6b063794b4c8d71739c5795bcff085f1cc4b15279d4d1f39`
- **Source parity:** the deployed source and `contracts/praxis.py` match exactly.

## Verification

The updated source passed 28 Direct Mode tests, 18 preflight source invariants, GenVM lint, and schema validation. The Studionet verification matrix includes timeout settlement, early-settlement rejection, duplicate-settlement rejection, pause compatibility, mandate-closure compatibility, and post-settlement state checks.

Reproducible deployment and test evidence are in [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md). The contract design and consensus boundaries are documented in [`README.md`](README.md), [`docs/CONSENSUS.md`](docs/CONSENSUS.md), and [`SECURITY.md`](SECURITY.md).
