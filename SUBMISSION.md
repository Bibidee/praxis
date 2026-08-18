# Submission notes

Praxis is a reusable semantic execution firewall rather than a product application. Its load-bearing GenLayer operation is independent semantic assessment of whether disclosed execution effects remain inside an immutable mandate. Deterministic code retains control of hard limits, state transitions, verdict derivation, challenge economics, and downstream authorization.

Reviewer evidence:

- one canonical contract: `contracts/praxis.py`;
- 26 passing Direct Mode tests, including forged-leader, malformed-output, strict-type, global and per-mandate capacity protection, deadline boundaries, lifecycle, challenge, pause, and downstream-gate cases;
- 16 zero-dependency source invariants;
- current GenVM lint and schema validation pass;
- committed Studionet deployment/parity/runtime scripts;
- no frontend and no CI workflow.

Canonical Studionet deployment: `0x7f2F0aE07B7bcFec1709794F12A44813DB8BD071`, transaction `0xc8ce8a247a1564b2e74bfbf8cb008ac91f3180cfab550d9b6fa7ff0984d0eff3`. Explorer and local source SHA-256 are both `80d5fe0bdfda523ca9ce22ba878efbb4669013a89ec5024c108e7fc2538f954d`. The full live matrix returned `exactSafety: true`; see `docs/DEPLOYMENT.md`.

The owner-only mandate allocator prevents outsiders from consuming the lifetime global mandate or execution pools; mandate authorities alone allocate their proposal slots. This is a narrow, documented centralization tradeoff for bounded permanent storage. Challenges require the exact bond, occur at most once, and are valid only before the deadline. Validators independently fetch and reproduce the eight load-bearing semantic/binding decisions; rationale remains diagnostic.

Praxis intentionally does not prove that prose correctly decodes arbitrary calldata or make downstream execution atomic. Consumers must independently verify target, value, and `keccak256(actual_calldata)` before coordinating consumption and execution.
