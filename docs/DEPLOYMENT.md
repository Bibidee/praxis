# Deployment and live verification

The scripts use the official `genlayer-js` client and an encrypted local keystore. Never commit the password or keystore.

```text
set PRAXIS_KEYSTORE=C:\path\to\keystore.json
set PRAXIS_WALLET_PASSWORD=...
npm run deploy:studionet
set PRAXIS_CONTRACT=0x...
set PRAXIS_FIXTURE_COMMIT=<40-character immutable commit SHA>
npm run source:match
npm run verify:studionet
```

`deploy:studionet` deploys the exact bytes from `contracts/praxis.py`. `source:match` retrieves Explorer source and requires byte equality. `verify:studionet` refuses mutable fixture refs and requires a full commit SHA. It exercises authorization, challenge, expiry, pause consistency, consumption/replay, deterministic rejection, hostile semantic evidence, and cancellation while throttling RPC calls below Studionet's 30-request/minute limit.

Canonical deployment details and transaction evidence will be recorded here only after the exact published source has been deployed and verified.
