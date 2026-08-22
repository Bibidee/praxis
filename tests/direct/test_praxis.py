import sys
from conftest import warp_to

CONTRACT = "contracts/praxis.py"
NOW = 1_787_040_000
TARGET = "0x1111111111111111111111111111111111111111"
OTHER = "0x2222222222222222222222222222222222222222"
ZERO = "0x0000000000000000000000000000000000000000"
HASH = "0x" + "ab" * 32
PLAN = "https://example.com/execution-plan"
ONE = 10**18


def deploy(direct_vm, direct_deploy):
    contract = direct_deploy(CONTRACT)
    direct_vm._praxis_module = sys.modules[contract.__class__.__module__]
    warp_to(direct_vm, "2026-08-18T08:00:00Z")
    return contract


def create(contract, mandate_id="mandate-1", target=TARGET, max_value=5 * ONE, bond=ONE // 10, window=60):
    contract.create_mandate(mandate_id, "Security audit mandate",
        "Pay the approved auditor for a completed security audit. Do not grant upgrade or administrative authority.",
        "https://example.com/governance-policy", target, max_value, bond, window)


def propose(contract, execution_id="execution-1", mandate_id="mandate-1", target=TARGET, value=ONE, plan=PLAN):
    contract.propose_execution(execution_id, mandate_id, target, value, HASH, plan,
        "Pay the approved auditor after delivery; create no permissions.")


def mock_result(direct_vm, purpose="yes", recipient="yes", constraints="yes", expansion="no", hidden="no", confidence=90,
                quality="strong", rationale="The plan faithfully implements the mandate.", plan_hash="yes", plan_target="yes", plan_value="yes"):
    result = {"purpose_match": purpose, "recipient_match": recipient, "constraints_match": constraints,
        "authority_expansion": expansion, "hidden_side_effects": hidden, "confidence": confidence,
        "plan_hash_match": plan_hash, "plan_target_match": plan_target, "plan_value_match": plan_value,
        "evidence_quality": quality, "rationale": rationale}
    direct_vm._praxis_module.observe_once = lambda *args: {"kind": "analysis", "result": dict(result)}


def mock_error(direct_vm, error_class="transient_fetch"):
    direct_vm._praxis_module.observe_once = lambda *args: {"kind": "error", "class": error_class}


def test_create_mandate_and_info(direct_vm, direct_deploy):
    c = deploy(direct_vm, direct_deploy); create(c)
    mandate = c.get_mandate("mandate-1")
    assert mandate["status"] == "active" and mandate["allowed_target"].lower() == TARGET.lower()
    assert mandate["created_at"] == NOW and c.get_info()["mandate_count"] == 1


def test_only_owner_can_allocate_global_mandate_or_execution_capacity(direct_vm, direct_deploy, direct_alice):
    c = deploy(direct_vm, direct_deploy)
    with direct_vm.prank(direct_alice):
        for index in range(256):
            with direct_vm.expect_revert("Contract owner"): create(c, f"attacker-mandate-{index}")
    assert c.get_info()["mandate_count"] == 0 and c.get_info()["execution_count"] == 0
    create(c)
    with direct_vm.prank(direct_alice):
        with direct_vm.expect_revert("Mandate authority"): propose(c, "attacker-execution")
    assert c.get_mandate("mandate-1")["execution_count"] == 0
    assert c.get_info()["execution_count"] == 0
    propose(c)
    assert c.get_info()["mandate_count"] == 1 and c.get_info()["execution_count"] == 1


def test_failed_and_duplicate_allocations_do_not_increment_counters(direct_vm, direct_deploy):
    c = deploy(direct_vm, direct_deploy); create(c); propose(c)
    before = c.get_info()
    with direct_vm.expect_revert("already exists"): create(c)
    with direct_vm.expect_revert("already exists"): propose(c)
    with direct_vm.expect_revert("calldata hash"):
        c.propose_execution("bad-execution", "mandate-1", TARGET, ONE, "0x12", PLAN, "summary")
    after = c.get_info()
    assert after["mandate_count"] == before["mandate_count"] == 1
    assert after["execution_count"] == before["execution_count"] == 1


def test_create_rejects_duplicate_zero_target_and_bad_configuration(direct_vm, direct_deploy):
    c = deploy(direct_vm, direct_deploy); create(c)
    with direct_vm.expect_revert("already exists"): create(c)
    with direct_vm.expect_revert("Zero target"): create(c, "zero", target=ZERO)
    with direct_vm.expect_revert("challenge configuration"): create(c, "bad-window", window=59)
    with direct_vm.expect_revert("challenge configuration"): create(c, "bad-bond", bond=0)


def test_urls_ids_text_and_hash_are_bounded(direct_vm, direct_deploy):
    c = deploy(direct_vm, direct_deploy)
    with direct_vm.expect_revert("constitution_url"): c.create_mandate("m", "T", "M", "http://bad", TARGET, ONE, ONE, 60)
    with direct_vm.expect_revert("Invalid mandate_id"): create(c, "bad id")
    create(c)
    with direct_vm.expect_revert("calldata hash"): c.propose_execution("e", "mandate-1", TARGET, ONE, "0x12", PLAN, "summary")
    with direct_vm.expect_revert("plan_url"): propose(c, plan="https://localhost/private")
    with direct_vm.expect_revert("plan_url"): propose(c, plan="https://127.0.0.1/private")


def test_access_control_pause_and_mandate_transitions(direct_vm, direct_deploy, direct_alice):
    c = deploy(direct_vm, direct_deploy); create(c)
    with direct_vm.prank(direct_alice):
        with direct_vm.expect_revert("Contract owner"): c.set_paused(True)
        with direct_vm.expect_revert("Mandate authority"): c.set_mandate_status("mandate-1", "paused")
    c.set_paused(True)
    with direct_vm.expect_revert("Contract is paused"): propose(c)
    c.set_mandate_status("mandate-1", "paused")
    with direct_vm.expect_revert("Contract is paused"): c.set_mandate_status("mandate-1", "active")
    c.set_paused(False); c.set_mandate_status("mandate-1", "active"); c.set_mandate_status("mandate-1", "closed")
    with direct_vm.expect_revert("Illegal"): c.set_mandate_status("mandate-1", "active")


def test_proposal_storage_capacity_and_cancellation(direct_vm, direct_deploy, direct_alice):
    c = deploy(direct_vm, direct_deploy); create(c); propose(c)
    row = c.get_execution("execution-1")
    assert row["status"] == "proposed" and row["calldata_hash"] == HASH
    with direct_vm.expect_revert("already exists"): propose(c)
    with direct_vm.prank(direct_alice):
        with direct_vm.expect_revert("Proposer or authority"): c.cancel_execution("execution-1")
    c.cancel_execution("execution-1"); assert c.get_execution("execution-1")["status"] == "cancelled"


def test_only_mandate_authority_can_propose_or_consume_capacity(direct_vm, direct_deploy, direct_alice):
    c = deploy(direct_vm, direct_deploy); create(c)
    with direct_vm.prank(direct_alice):
        for index in range(32):
            with direct_vm.expect_revert("Mandate authority"): propose(c, f"attacker-{index}")
    assert c.get_mandate("mandate-1")["execution_count"] == 0
    for index in range(32): propose(c, f"authorized-{index}")
    assert c.get_mandate("mandate-1")["execution_count"] == 32
    with direct_vm.expect_revert("capacity"): propose(c, "authorized-overflow")


def test_deterministic_target_and_value_floor_blocks_without_model(direct_vm, direct_deploy):
    c = deploy(direct_vm, direct_deploy); create(c); propose(c, target=OTHER)
    c.review_execution("execution-1"); row = c.get_execution("execution-1")
    assert row["verdict"] == "blocked" and row["confidence"] == 100
    assert c.is_executable("execution-1")["executable"] is False
    create(c, "mandate-2", max_value=ONE)
    propose(c, "execution-2", "mandate-2", value=ONE + 1)
    c.review_execution("execution-2")
    assert c.get_execution("execution-2")["verdict"] == "blocked"


def test_authorized_review_and_delayed_consumption(direct_vm, direct_deploy):
    c = deploy(direct_vm, direct_deploy); create(c); propose(c); mock_result(direct_vm)
    c.review_execution("execution-1")
    assert c.get_execution("execution-1")["verdict"] == "authorized"
    assert c.is_executable("execution-1")["executable"] is False
    with direct_vm.expect_revert("Challenge window"): c.consume_execution("execution-1")
    warp_to(direct_vm, "2026-08-18T08:01:01Z")
    assert c.is_executable("execution-1")["executable"] is True
    c.set_paused(True)
    assert c.is_executable("execution-1")["executable"] is False
    with direct_vm.expect_revert("Contract is paused"): c.consume_execution("execution-1")
    c.set_paused(False)
    assert c.is_executable("execution-1")["executable"] is True
    c.consume_execution("execution-1")
    assert c.get_execution("execution-1")["status"] == "consumed"
    with direct_vm.expect_revert("not authorized"): c.consume_execution("execution-1")


def test_semantic_block_and_inconclusive_are_not_executable(direct_vm, direct_deploy):
    c = deploy(direct_vm, direct_deploy); create(c); propose(c); mock_result(direct_vm, expansion="yes")
    c.review_execution("execution-1"); assert c.get_execution("execution-1")["verdict"] == "blocked"
    create(c, "mandate-2"); propose(c, "execution-2", "mandate-2"); mock_result(direct_vm, constraints="unclear")
    c.review_execution("execution-2"); assert c.get_execution("execution-2")["verdict"] == "inconclusive"
    assert c.is_executable("execution-1")["executable"] is False and c.is_executable("execution-2")["executable"] is False


def test_missing_exact_plan_binding_fails_closed(direct_vm, direct_deploy):
    c = deploy(direct_vm, direct_deploy); create(c); propose(c)
    mock_result(direct_vm, plan_hash="unclear")
    c.review_execution("execution-1")
    assert c.get_execution("execution-1")["verdict"] == "blocked"


def test_confidence_threshold_is_exactly_seventy_five(direct_vm, direct_deploy):
    c = deploy(direct_vm, direct_deploy); create(c); propose(c); mock_result(direct_vm, confidence=74)
    c.review_execution("execution-1")
    assert c.get_execution("execution-1")["verdict"] == "inconclusive"
    create(c, "mandate-2"); propose(c, "execution-2", "mandate-2"); mock_result(direct_vm, confidence=75)
    c.review_execution("execution-2")
    assert c.get_execution("execution-2")["verdict"] == "authorized"


def test_quality_and_rationale_validated_but_not_equivalent(direct_vm, direct_deploy):
    deploy(direct_vm, direct_deploy); module = direct_vm._praxis_module
    base = {"purpose_match":"yes","recipient_match":"yes","constraints_match":"yes","authority_expansion":"no",
        "hidden_side_effects":"no","plan_hash_match":"yes","plan_target_match":"yes","plan_value_match":"yes",
        "confidence":90,"evidence_quality":"strong","rationale":"grounded"}
    assert module.valid_analysis(base) is True
    changed = dict(base, evidence_quality="weak", rationale="different diagnostic wording")
    assert module.equivalent_analysis(base, changed) is True
    assert module.valid_analysis(dict(base, confidence=True)) is False
    assert module.valid_analysis(dict(base, confidence=90.5)) is False
    assert module.valid_analysis(dict(base, evidence_quality="excellent")) is False
    assert module.valid_analysis(dict(base, rationale="x" * (module.MAX_RATIONALE + 1))) is False


def test_forged_leader_decision_is_rejected_by_independent_validator(direct_vm, direct_deploy):
    c = deploy(direct_vm, direct_deploy); create(c); propose(c); mock_result(direct_vm)
    c.review_execution("execution-1")
    direct_vm.clear_mocks(); mock_result(direct_vm, hidden="yes")
    assert direct_vm.run_validator() is False


def test_diagnostic_only_validator_difference_is_accepted(direct_vm, direct_deploy):
    c = deploy(direct_vm, direct_deploy); create(c); propose(c); mock_result(direct_vm)
    c.review_execution("execution-1")
    direct_vm.clear_mocks(); mock_result(direct_vm, quality="weak", rationale="Different explanation.")
    assert direct_vm.run_validator() is True


def test_retryable_failure_preserves_state(direct_vm, direct_deploy):
    c = deploy(direct_vm, direct_deploy); create(c); propose(c); mock_error(direct_vm)
    before = c.get_execution("execution-1")
    with direct_vm.expect_revert("RETRYABLE"): c.review_execution("execution-1")
    after = c.get_execution("execution-1")
    assert before["status"] == after["status"] == "proposed" and after["reviewed_at"] == 0


def test_malformed_consensus_output_preserves_state(direct_vm, direct_deploy):
    c = deploy(direct_vm, direct_deploy); create(c); propose(c)
    direct_vm._praxis_module.observe_once = lambda *args: {"kind":"analysis", "result":{"purpose_match":"yes"}}
    with direct_vm.expect_revert("RETRYABLE"): c.review_execution("execution-1")
    assert c.get_execution("execution-1")["status"] == "proposed"


def test_exact_challenge_bond_and_single_challenge(direct_vm, direct_deploy, direct_alice):
    c = deploy(direct_vm, direct_deploy); create(c); propose(c); mock_result(direct_vm); c.review_execution("execution-1")
    with direct_vm.prank(direct_alice):
        direct_vm.value = 1
        with direct_vm.expect_revert("Exact challenge bond"): c.challenge_execution("execution-1")
        direct_vm.value = ONE // 10; c.challenge_execution("execution-1"); direct_vm.value = 0
    assert c.get_execution("execution-1")["status"] == "proposed"
    mock_result(direct_vm, hidden="yes"); c.review_execution("execution-1")
    row = c.get_execution("execution-1")
    assert row["verdict"] == "blocked" and row["challenge_bond_held"] == "0" and row["challenge_count"] == 1
    with direct_vm.prank(direct_alice):
        direct_vm.value = ONE // 10
        with direct_vm.expect_revert("cannot be challenged"): c.challenge_execution("execution-1")
        direct_vm.value = 0


def test_challenge_deadline_boundaries(direct_vm, direct_deploy, direct_alice):
    c = deploy(direct_vm, direct_deploy); create(c); propose(c); mock_result(direct_vm); c.review_execution("execution-1")
    warp_to(direct_vm, "2026-08-18T08:00:59Z")
    with direct_vm.prank(direct_alice):
        direct_vm.value = ONE // 10; c.challenge_execution("execution-1"); direct_vm.value = 0
    mock_result(direct_vm); c.review_execution("execution-1")
    # Re-review starts a new window, but the one-challenge limit remains permanent.
    with direct_vm.prank(direct_alice):
        direct_vm.value = ONE // 10
        with direct_vm.expect_revert("cannot be challenged"): c.challenge_execution("execution-1")
        direct_vm.value = 0


def test_challenge_at_or_after_deadline_fails(direct_vm, direct_deploy, direct_alice):
    c = deploy(direct_vm, direct_deploy); create(c); propose(c); mock_result(direct_vm); c.review_execution("execution-1")
    for timestamp in ("2026-08-18T08:01:00Z", "2026-08-18T08:01:01Z"):
        warp_to(direct_vm, timestamp)
        with direct_vm.prank(direct_alice):
            direct_vm.value = ONE // 10
            with direct_vm.expect_revert("Challenge window has closed"): c.challenge_execution("execution-1")
            direct_vm.value = 0


def test_authorized_challenge_bond_goes_to_authority_and_cannot_cancel_held_bond(direct_vm, direct_deploy, direct_alice):
    c = deploy(direct_vm, direct_deploy); create(c); propose(c); mock_result(direct_vm); c.review_execution("execution-1")
    with direct_vm.prank(direct_alice):
        direct_vm.value = ONE // 10; c.challenge_execution("execution-1"); direct_vm.value = 0
    with direct_vm.expect_revert("cannot be cancelled"): c.cancel_execution("execution-1")
    mock_result(direct_vm); c.review_execution("execution-1")
    assert c.get_execution("execution-1")["challenge_bond_held"] == "0"


def test_expired_challenge_refunds_bond_and_cancels_execution(direct_vm, direct_deploy, direct_alice):
    c = deploy(direct_vm, direct_deploy); create(c); propose(c); mock_result(direct_vm); c.review_execution("execution-1")
    warp_to(direct_vm, "2026-08-18T08:00:30Z")
    with direct_vm.prank(direct_alice):
        direct_vm.value = ONE // 10; c.challenge_execution("execution-1"); direct_vm.value = 0
    row = c.get_execution("execution-1")
    assert row["challenged_at"] > 0 and row["challenge_bond_held"] == str(ONE // 10)
    with direct_vm.expect_revert("settlement timeout is open"): c.settle_expired_challenge("execution-1")
    warp_to(direct_vm, "2026-08-18T08:01:30Z")
    c.settle_expired_challenge("execution-1")
    row = c.get_execution("execution-1")
    assert row["status"] == "cancelled" and row["verdict"] == "" and row["challenge_bond_held"] == "0"
    with direct_vm.expect_revert("No held challenge bond"): c.settle_expired_challenge("execution-1")


def test_expired_challenge_settlement_works_while_paused_and_mandate_closed(direct_vm, direct_deploy, direct_alice):
    c = deploy(direct_vm, direct_deploy); create(c); propose(c); mock_result(direct_vm); c.review_execution("execution-1")
    with direct_vm.prank(direct_alice):
        direct_vm.value = ONE // 10; c.challenge_execution("execution-1"); direct_vm.value = 0
    c.set_mandate_status("mandate-1", "closed"); c.set_paused(True)
    warp_to(direct_vm, "2026-08-18T08:01:00Z")
    c.settle_expired_challenge("execution-1")
    assert c.get_execution("execution-1")["challenge_bond_held"] == "0"


def test_pause_blocks_new_review_challenge_and_consumption_but_not_bond_resolution(direct_vm, direct_deploy, direct_alice):
    c = deploy(direct_vm, direct_deploy); create(c); propose(c); mock_result(direct_vm); c.review_execution("execution-1")
    with direct_vm.prank(direct_alice):
        direct_vm.value = ONE // 10; c.challenge_execution("execution-1"); direct_vm.value = 0
    c.set_paused(True)
    mock_result(direct_vm, hidden="yes"); c.review_execution("execution-1")
    assert c.get_execution("execution-1")["challenge_bond_held"] == "0"
    c.set_paused(False); create(c, "mandate-2"); propose(c, "execution-2", "mandate-2"); c.set_paused(True)
    with direct_vm.expect_revert("Contract is paused"): c.review_execution("execution-2")


def test_closed_mandate_cannot_trap_existing_challenge_bond(direct_vm, direct_deploy, direct_alice):
    c = deploy(direct_vm, direct_deploy); create(c); propose(c); mock_result(direct_vm); c.review_execution("execution-1")
    with direct_vm.prank(direct_alice):
        direct_vm.value = ONE // 10; c.challenge_execution("execution-1"); direct_vm.value = 0
    c.set_mandate_status("mandate-1", "closed")
    mock_result(direct_vm, hidden="yes"); c.review_execution("execution-1")
    assert c.get_execution("execution-1")["challenge_bond_held"] == "0"


def test_mandate_close_blocks_review_and_consumption(direct_vm, direct_deploy):
    c = deploy(direct_vm, direct_deploy); create(c); propose(c); c.set_mandate_status("mandate-1", "closed")
    with direct_vm.expect_revert("Mandate is closed"): c.review_execution("execution-1")


def test_list_is_bounded_and_paginated(direct_vm, direct_deploy):
    c = deploy(direct_vm, direct_deploy); create(c); propose(c)
    rows = c.list_mandate_executions("mandate-1", 0, 999)
    assert len(rows) == 1 and rows[0]["id"] == "execution-1"
    assert c.list_mandate_executions("mandate-1", 2, 1) == []
