# Canonical deployment evidence

| Field | Verified value |
|---|---|
| Network | Studionet |
| Contract | `0x076aeCCc66673C93B54FafaB9C56Eb10fBc9D9Ed` |
| Deployment transaction | `0x543acd04b12f2f7763923445570a5307d4c5ff194146135b0cdb84904009ef78` |
| Owner | `0xF7FD246351268835Df39B1e8047fbCc4135E2B47` |
| Contract source commit | `130ff693f665dfc5e385c1b03ebab8796c7dfbba` |
| Immutable fixture commit | `ac5a12532444252fffe7896fb5e8955f542c9859` |
| Local source SHA-256 | `687dcde0a00f838c6b063794b4c8d71739c5795bcff085f1cc4b15279d4d1f39` |
| Explorer source SHA-256 | `687dcde0a00f838c6b063794b4c8d71739c5795bcff085f1cc4b15279d4d1f39` |
| Exact source match | PASS |
| Direct Mode | 28 passed, 0 failed |
| Preflight | PASS — 18 source invariants, GenVM lint, and schema |
| Studionet matrix | PASS — `exactSafety: true` |

This is the canonical v1.1 deployment. It adds `settle_expired_challenge`: after a full challenge window from `challenged_at`, anyone may refund the held bond to the challenger and cancel the execution. The previous v1.1 deployment at `0xC0208fE8d90D6E27B39abFEE0e358E4629EbDF94` is superseded because its owner could not run the owner-only lifecycle matrix.

## Key live transactions

- safe authorization: `0x8b299e9c767391b0d8bf11cc082d4a12204df6f5488fcbbb0269b36924a7b0ec`;
- challenge and re-review: `0x4136a43c5b77666c475de928ab7195d4e7cfb64f58ee57b5627a4d3b8d99e836`, `0x57811e955cb830ae52cc394b85d09d7304a16bdf04039cfd1fe1476c16a10d32`;
- pause/unpause: `0x6f36deb142d4a61c0df4243e59391cdc7ea190e7b42ad0ceb888f56598f908b0`, `0xe0a212aa411bb1d04e9782bcc8d04373735a6fd0ee7fa50dd8ac151c682046a0`;
- consumption and replay rejection: `0xce50c18f563e365e861e40b3bcc633ed42eaae36c2fb644658d7444aa5e4d167b`, `0xefccb816a7433cfa0e5565a0ac3823e8cd071f0ad5c22e916ad91919bd8c896a`;
- deterministic and hostile rejection: `0xef398f3727b878483c14954d74a74207f18d706db3d62e4cff77796996366d8e`, `0x3a807339be106eec4da565928e00c0901ab4c9d0451ad909c117778bfcfcdc8f`;
- expired challenge rejection: `0xed3333a394272d09ff83bbe7679d5c61f63ac34cc933dca73657ef509754771d`;
- held-bond timeout settlement: `0x7cc12a99b8323bd9d82c1cfc347413ff36a47914819173502972b10ab50157b3` — finalized, refunded, cancelled;
- cancellation: `0x0f92765acf9c05db35892fe1b500afacfbc2f1ee746d8d41ebfc7ba82567554b`.

## Reproduction

```text
set PRAXIS_CONTRACT=0x076aeCCc66673C93B54FafaB9C56Eb10fBc9D9Ed
set PRAXIS_FIXTURE_COMMIT=ac5a12532444252fffe7896fb5e8955f542c9859
npm run source:match
npm run verify:studionet
```

`verify:studionet` requires an encrypted owner keystore and throttles RPC starts to 24/minute.
