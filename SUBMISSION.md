# Submission notes

Praxis is a reusable semantic execution firewall rather than a product application. Its load-bearing GenLayer operation is independent semantic assessment of whether disclosed execution effects remain inside an immutable mandate. Deterministic code retains control of hard limits, state transitions, verdict derivation, challenge economics, and downstream authorization.

Reviewer evidence:

- one canonical contract: `contracts/praxis.py`;
- 28 passing Direct Mode tests, including forged-leader, malformed-output, strict-type, global and per-mandate capacity protection, deadline boundaries, lifecycle, challenge timeout/refund, pause, and downstream-gate cases;
- 16 zero-dependency source invariants;
- current GenVM lint and schema validation pass;
- committed Studionet deployment/parity/runtime scripts;
- no frontend and no CI workflow.

Canonical Studionet deployment: `0x2a60858a993E10A403FfBE63B50B5B121F00C337`, transaction `0x946e93610a7aaa07d2682d1268cea5d12c5bc7a29480b809b7ab2b17ff17c184`. Explorer and local source SHA-256 are both `50702b1e7d8f257344bfeac68b822f752fe2a8ea77cfbfce1e4505af2d809a86`. Exact source parity and the full `exactSafety: true` matrix passed; see `docs/DEPLOYMENT.md`.

The owner-only mandate allocator prevents outsiders from consuming the lifetime global mandate or execution pools; mandate authorities alone allocate their proposal slots. This is a narrow, documented centralization tradeoff for bounded permanent storage. Challenges require the exact bond, occur at most once, and are valid only before the deadline. If re-review remains unavailable for one challenge window, anyone can refund the challenger and cancel through `settle_expired_challenge`, including during pause or mandate closure. Validators independently fetch and reproduce the eight load-bearing semantic/binding decisions; rationale remains diagnostic.

Praxis intentionally does not prove that prose correctly decodes arbitrary calldata or make downstream execution atomic. Consumers must independently verify target, value, and `keccak256(actual_calldata)` before coordinating consumption and execution.
