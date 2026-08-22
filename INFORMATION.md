# Praxis — Submission Information

## Submission

- **Category:** GenLayer Intelligent Contract
- **Type:** Standalone, contract-only reusable primitive
- **Repository:** https://github.com/Bibidee/praxis
- **Canonical contract:** [`0x076aeCCc66673C93B54FafaB9C56Eb10fBc9D9Ed`](https://explorer-studio.genlayer.com/address/0x076aeCCc66673C93B54FafaB9C56Eb10fBc9D9Ed)
- **Deployment transaction:** [`0x543acd04b12f2f7763923445570a5307d4c5ff194146135b0cdb84904009ef78`](https://explorer-studio.genlayer.com/tx/0x543acd04b12f2f7763923445570a5307d4c5ff194146135b0cdb84904009ef78)
- **Canonical source commit:** `130ff693f665dfc5e385c1b03ebab8796c7dfbba`
- **Source SHA-256:** `687dcde0a00f838c6b063794b4c8d71739c5795bcff085f1cc4b15279d4d1f39`
- **Deployed-source parity:** exact byte match verified

## What Praxis does

Praxis is a semantic execution firewall for mandate-driven actions. An owner creates an immutable mandate with a permitted target, maximum value, challenge configuration, and semantic constraints. The mandate authority then commits a proposed execution and its Keccak-256 calldata commitment.

Deterministic contract code enforces authority-only allocation, bounded storage, exact target/value limits, state transitions, replay protection, challenge deadlines, and downstream consumption gates. GenLayer validators independently fetch the disclosed evidence and assess purpose, recipient, constraints, authority expansion, hidden side effects, and exact target/value/calldata-hash binding.

Authorization fails closed. A result becomes consumable only after the challenge window and only when `is_executable` returns true. Integrators must independently verify the actual target, value, and `keccak256(calldata)` before coordinating execution.

## Why GenLayer consensus is load-bearing

The leader result is not trusted. Validators independently fetch and analyze evidence, then compare the eight load-bearing semantic and binding decisions. Exact agreement is required on those decisions; rationale and evidence-quality prose are diagnostic only. Without GenLayer consensus, a single model or operator could authorize an execution that misrepresents an immutable mandate.

## Challenge fail-safe

A single exact-bond challenge can reopen an authorized or inconclusive review. If re-review remains unavailable, `settle_expired_challenge` provides a permissionless liveness escape hatch after `challenged_at + challenge_window`: it refunds the full held bond to the challenger and cancels the execution. It remains usable during a global pause or after mandate closure, so infrastructure failure cannot trap funds.

Live timeout settlement evidence: [`0x7cc12a99b8323bd9d82c1cfc347413ff36a47914819173502972b10ab50157b3`](https://explorer-studio.genlayer.com/tx/0x7cc12a99b8323bd9d82c1cfc347413ff36a47914819173502972b10ab50157b3).

## Verification evidence

- 28 Direct Mode tests passed.
- 18 source invariants passed in preflight.
- GenVM lint and schema generation passed.
- Studionet verification matrix returned `exactSafety: true`.
- The live matrix covers safe authorization, challenge/re-review, bond settlement, pause consistency, consumption/replay protection, deterministic rejection, hostile semantic evidence, expiry rejection, cancellation, and timeout refund/cancellation.

See [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md), [`docs/CONSENSUS.md`](docs/CONSENSUS.md), [`SECURITY.md`](SECURITY.md), and [`docs/INTEGRATION.md`](docs/INTEGRATION.md) for reproducible evidence, design details, and limitations.
