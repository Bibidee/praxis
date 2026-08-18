# Canonical deployment evidence

| Field | Verified value |
|---|---|
| Network | Studionet |
| Contract | `0x7f2F0aE07B7bcFec1709794F12A44813DB8BD071` |
| Deployment transaction | `0xc8ce8a247a1564b2e74bfbf8cb008ac91f3180cfab550d9b6fa7ff0984d0eff3` |
| Contract source commit | `db88898b3fd455d575b2efcc9c8f002e72ac2819` |
| Immutable fixture commit | `db88898b3fd455d575b2efcc9c8f002e72ac2819` |
| Local source SHA-256 | `80d5fe0bdfda523ca9ce22ba878efbb4669013a89ec5024c108e7fc2538f954d` |
| Explorer source SHA-256 | `80d5fe0bdfda523ca9ce22ba878efbb4669013a89ec5024c108e7fc2538f954d` |
| Exact source match | PASS |
| Direct Mode | 24 passed, 0 failed |
| Preflight | PASS — 15 source invariants |
| GenVM lint | PASS — 3 checks |
| GenVM schema | PASS — Praxis, 13 methods (8 write, 5 view) |
| Studionet matrix | PASS — `exactSafety: true` |

The deployment finalized with `MAJORITY_AGREE`, validator execution `SUCCESS`, and zero rotations. The deployed contract bytes exactly match `contracts/praxis.py` at the source commit above. SHA-256 in this document is solely source-file integrity; execution plans use Keccak-256 calldata commitments.

## Key live transactions

- safe semantic authorization: `0x9253b41c0d4cd46834857622a3db02baa2b8d97042e11fb8063a1cbdd9991a68` — authorized;
- challenge accepted within window: `0x2ee51f851b38773d4c640d7ed3b1fbdfad8c4cfcf251044219e4d25eceee065a`;
- challenged re-review and bond settlement: `0xf7df2d7497c31d0ce43fb7385c07f35bab4eed29d76fad39f6489be6d3a712e6` — authorized, held bond `0`;
- pause on/off: `0x709c40886f2a39ee1b9ec9a72ffa0d6bfe27ee7d496e55f29ee71be916db93a2`, `0x0628bf732a4fc75e09505b232c0969d384f342f4d64e6b6ab9ab50b023db3c85` — executable false while paused and true after unpause;
- consumption: `0x1d1fe76265d5d53037a9d712038760dea68c99f96958b7bc2bc264052f920ff1` — consumed;
- consumption replay: `0x312f36298e550c9eae5441cb305f9b841894c3f0e95ddd960006233572710c8a` — expected rollback;
- deterministic wrong-target review: `0x814327f77f4aeb31047a04f2c4cb52dfa62babfe11176dfad8ca56b489b494fd` — blocked at confidence 100;
- hostile authority-expansion review: `0x1f1e1f36d1d215dd392300497933172507ad2bf2999810dba051267fbac7c69f` — blocked;
- expired challenge: `0xb836a078e457429079c7bfda3a55d3af1c1c3ac4834b46f792fed44cfaaaa287` — expected rollback, reviewed state preserved;
- cancellation: `0x01b1cc95055260cdae5d37597ad2669dcfa65c06a1220c6591fc71384265409f` — cancelled.

## Reproduction

The verifier throttles all RPC starts to 24/minute and requires a full immutable fixture commit.

```text
set PRAXIS_KEYSTORE=C:\path\to\encrypted-keystore.json
set PRAXIS_WALLET_PASSWORD=...
set PRAXIS_CONTRACT=0x7f2F0aE07B7bcFec1709794F12A44813DB8BD071
set PRAXIS_FIXTURE_COMMIT=db88898b3fd455d575b2efcc9c8f002e72ac2819
npm run source:match
npm run verify:studionet
```

No credential is stored in the repository.
