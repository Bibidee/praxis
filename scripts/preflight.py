import ast
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACTS = list((ROOT / "contracts").glob("*.py"))
if len(CONTRACTS) != 1:
    raise SystemExit(f"Expected exactly one deployable contract, found {len(CONTRACTS)}")
source = CONTRACTS[0].read_text(encoding="utf-8")
tree = ast.parse(source)
required = ["run_nondet_unsafe", "equivalent_analysis", "valid_analysis", "verdict_for", "plan_hash_match",
            "challenge_execution", "consume_execution", "is_executable", "MAX_EXECUTIONS_PER_MANDATE",
            "self._authority(mandate)", "Contract owner only", "Challenge window has closed", "not self.paused",
            "DECISION_CONFIDENCE = 75"]
missing = [item for item in required if item not in source]
if missing: raise SystemExit(f"Missing source invariants: {missing}")
classes = [node.name for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "Praxis"]
if classes != ["Praxis"]: raise SystemExit("Canonical Praxis class missing or duplicated")
checks = [
    [sys.executable, "-m", "pytest", "tests/direct", "-q"],
    [str(Path(sys.executable).with_name("genvm-lint.exe")), "check", str(CONTRACTS[0]), "--json"],
    [str(Path(sys.executable).with_name("genvm-lint.exe")), "schema", str(CONTRACTS[0]), "--output", str(ROOT / "artifacts" / "praxis.abi.json")],
]
for command in checks:
    result = subprocess.run(command, cwd=ROOT)
    if result.returncode != 0: raise SystemExit(result.returncode)
print(f"Praxis preflight passed: {len(required) + 2} source invariants, Direct Mode, lint, and schema")
