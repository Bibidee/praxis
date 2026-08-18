# Deployment and live verification

The scripts use the official `genlayer-js` client and an encrypted local keystore. Never commit the password or keystore.

```text
set PRAXIS_KEYSTORE=C:\path\to\keystore.json
set PRAXIS_WALLET_PASSWORD=...
npm run deploy:studionet
set PRAXIS_CONTRACT=0x...
npm run source:match
npm run verify:studionet
```

`deploy:studionet` deploys the exact bytes from `contracts/praxis.py`. `source:match` retrieves Explorer source and requires byte equality. `verify:studionet` exercises a safe authorization/challenge/consumption lifecycle, deterministic target rejection, hostile semantic evidence that must fail closed, and cancellation. It reads stored state after every terminal transaction.

Canonical deployment details and transaction evidence will be recorded here only after the exact published source has been deployed and verified.
