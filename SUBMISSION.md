# Submission notes

Praxis is a reusable semantic execution firewall rather than a product application. Its load-bearing GenLayer operation is independent semantic assessment of whether disclosed execution effects remain inside an immutable mandate. Deterministic code retains control of hard limits, state transitions, verdict derivation, challenge economics, and downstream authorization.

Reviewer evidence:

- one canonical contract: `contracts/praxis.py` (v1.1.0);
- 28 passing Direct Mode tests, including forged-leader, malformed-output, strict-type, global and per-mandate capacity protection, deadline boundaries, lifecycle, challenge timeout/refund, pause, and downstream-gate cases;
- 18 zero-dependency source invariants;
- current GenVM lint and schema validation pass;
- committed Studionet deployment/parity/runtime scripts;
- no frontend and no CI workflow.

Canonical Studionet deployment: `0xC0208fE8d90D6E27B39abFEE0e358E4629EbDF94`, transaction `0x6c61950d800516aff8cab1fd3268ccd7160184f7357a1f0ef9061545b2839cfd`. Explorer and local source SHA-256 are both `687dcde0a00f838c6b063794b4c8d71739c5795bcff085f1cc4b15279d4d1f39`. Exact source parity confirmed live (`SOURCE MATCH: PASS`); preflight passed (28 Direct Mode tests, 18 source invariants, GenVM lint/schema). This redeploy adds `settle_expired_challenge`, a fail-safe timeout that refunds a held challenge bond and cancels the execution if re-review stays unavailable for a full challenge window. The full live behavioral matrix (`exactSafety` transactions) from the previous `0x2a60858a993E10A403FfBE63B50B5B121F00C337` deployment has not yet been re-run against this address -- see `docs/DEPLOYMENT.md` for the full record and what remains to reproduce it.

The owner-only mandate allocator prevents outsiders from consuming the lifetime global mandate or execution pools; mandate authorities alone allocate their proposal slots. This is a narrow, documented centralization tradeoff for bounded permanent storage. Challenges require the exact bond, occur at most once, and are valid only before the deadline. If re-review remains unavailable for one challenge window, anyone can refund the challenger and cancel through `settle_expired_challenge`, including during pause or mandate closure. Validators independently fetch and reproduce the eight load-bearing semantic/binding decisions; rationale remains diagnostic.

Praxis intentionally does not prove that prose correctly decodes arbitrary calldata or make downstream execution atomic. Consumers must independently verify target, value, and `keccak256(actual_calldata)` before coordinating consumption and execution.
