# Canonical deployment evidence

| Field | Verified value |
|---|---|
| Network | Studionet |
| Contract | `0x2a60858a993E10A403FfBE63B50B5B121F00C337` |
| Deployment transaction | `0x946e93610a7aaa07d2682d1268cea5d12c5bc7a29480b809b7ab2b17ff17c184` |
| Contract source commit | `9fb8ed927b3da61e78a6385e1dab2d531eb2e3f3` |
| Runtime evidence record commit | `b07501b30ea1fe8c8785500f4eabe5ca1071462e` |
| Immutable fixture commit | `ac5a12532444252fffe7896fb5e8955f542c9859` |
| Local source SHA-256 | `50702b1e7d8f257344bfeac68b822f752fe2a8ea77cfbfce1e4505af2d809a86` |
| Explorer source SHA-256 | `50702b1e7d8f257344bfeac68b822f752fe2a8ea77cfbfce1e4505af2d809a86` |
| Exact source match | PASS |
| Direct Mode | 26 passed, 0 failed |
| Preflight | PASS — 16 source invariants |
| GenVM lint | PASS — 3 checks |
| GenVM schema | PASS — Praxis, 13 methods (8 write, 5 view) |
| Studionet matrix | PASS — `exactSafety: true` |

Deployment finalized with `MAJORITY_AGREE`, validator execution `SUCCESS`, and zero rotations. The deployed bytes exactly match `contracts/praxis.py` at the source commit. Live evidence used the immutable fixture commit above, including its governance policy. SHA-256 here is source integrity; execution plans use Keccak-256 calldata commitments.

## Key live transactions

- safe authorization: `0x23df1744a85775db3493eb5bbaa050fb3be8f136cf304695841486f1d471aa77` — authorized, confidence 95;
- challenge within window: `0xe6d27fcad3283397f529bb172c21a4d99bb9d0b6dfb4864c8355122742dc3528` — accepted;
- challenged re-review and bond settlement: `0xd3c63e7088fdaba0010c2c817e92da04fb73c1b5a7fa3fe56fc26ba3e5e6ced7` — authorized, held bond zero;
- pause on/off: `0xf40d72c997146b1844dd868e42b614fe73fa1e87734a70151d9813f2744e99e9`, `0x226b4623329720abdddca277c8896b13a249a03cdabdf81ae4c96edb8f815c6b` — executable false then true;
- consumption: `0xb8275ba45414dd8dbe6d4e413a9c8d2951cd20b09107a889edc25d1a6562e5f3` — consumed;
- replay: `0xeb292909f07078307fe107bd7b922bcd483bb6a999028445864556f4564ea0be` — expected rollback;
- deterministic wrong-target review: `0x4cccba16bb8d65f5f03d918503c7d4867f44e3f4a072c12292dbc10535406b5f` — blocked at confidence 100;
- hostile semantic review: `0xba4a6653d23e2a1e585507cdb94b46be6cc918426a21e834e82140505ae9d2c7` — blocked, authority expansion identified;
- expired challenge: `0x72e8a2fad958057f94b56180dd35d59220dbd3c0dff0ccd1196375c2fbf9c069` — expected rollback, reviewed state preserved;
- cancellation: `0xa1dc398ee673f8960cc2a1d75c0dd9cc0180fcd1a70137219978a92efa79717d` — cancelled.

The owner-only mandate allocation and authority-only proposal allocation are proven locally by adversarial Direct Mode tests. The live matrix confirms the authorized owner lifecycle; it does not claim a second live signer test.

## Reproduction

The scripts use an encrypted local keystore, throttle RPC starts to 24/minute, and never require credentials in the repository.

```text
set PRAXIS_KEYSTORE=C:\path\to\encrypted-keystore.json
set PRAXIS_WALLET_PASSWORD=...
set PRAXIS_CONTRACT=0x2a60858a993E10A403FfBE63B50B5B121F00C337
set PRAXIS_FIXTURE_COMMIT=ac5a12532444252fffe7896fb5e8955f542c9859
npm run source:match
npm run verify:studionet
```
