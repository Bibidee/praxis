import fs from "node:fs/promises";
import { setTimeout as delay } from "node:timers/promises";
import { Wallet } from "ethers";
import { createClient } from "genlayer-js";
import { studionet } from "genlayer-js/chains";
import { privateKeyToAccount } from "viem/accounts";

const address = process.env.PRAXIS_CONTRACT;
if (!address || !process.env.PRAXIS_KEYSTORE || !process.env.PRAXIS_WALLET_PASSWORD) throw new Error("PRAXIS_CONTRACT, PRAXIS_KEYSTORE and PRAXIS_WALLET_PASSWORD are required");
const wallet = await Wallet.fromEncryptedJson(await fs.readFile(process.env.PRAXIS_KEYSTORE, "utf8"), process.env.PRAXIS_WALLET_PASSWORD);
const client = createClient({ chain: studionet, endpoint: process.env.PRAXIS_RPC || "https://studio.genlayer.com/api", account: privateKeyToAccount(wallet.privateKey) });
const stamp = Date.now();
const target = "0x1111111111111111111111111111111111111111";
const otherTarget = "0x2222222222222222222222222222222222222222";
const safeHash = `0x${"ab".repeat(32)}`;
const hostileHash = `0x${"cd".repeat(32)}`;
const value = 100000000000000000n;
const bond = 10000000000000000n;
const transactions = [];
const states = [];
const json = input => JSON.stringify(input, (_, item) => typeof item === "bigint" ? item.toString() : item);
const fixtureCommit = process.env.PRAXIS_FIXTURE_COMMIT;
if (!/^[0-9a-f]{40}$/.test(fixtureCommit || "")) throw new Error("PRAXIS_FIXTURE_COMMIT must be an immutable 40-character commit SHA");
const rawBase = `https://raw.githubusercontent.com/Bibidee/praxis/${fixtureCommit}/fixtures`;
const RPC_MIN_INTERVAL_MS = 2500;
let lastRpcAt = 0;

async function throttled(operation) {
  const wait = RPC_MIN_INTERVAL_MS - (Date.now() - lastRpcAt);
  if (wait > 0) await delay(wait);
  lastRpcAt = Date.now();
  return operation();
}

async function rpc(operation, attempts = 8) {
  let last;
  for (let attempt = 0; attempt < attempts; attempt++) {
    try { return await throttled(operation); }
    catch (error) { last = error; await delay(Math.min(2000 * (attempt + 1), 10000)); }
  }
  throw last;
}

async function read(functionName, args = []) {
  return rpc(() => client.readContract({ address, functionName, args, transactionHashVariant: "latest-final" }));
}
async function terminal(hash) {
  for (let attempt = 0; attempt < 180; attempt++) {
    await delay(5000);
    let tx;
    try { tx = await rpc(() => client.getTransaction({ hash }), 4); }
    catch { continue; }
    if (["FINALIZED", "UNDETERMINED", "CANCELED"].includes(tx.statusName)) return tx;
  }
  throw new Error(`Transaction timeout: ${hash}`);
}
async function write(scenario, functionName, args, txValue = 0n) {
  const hash = await throttled(() => client.writeContract({ address, functionName, args, value: txValue, consensusMaxRotations: 5 }));
  const tx = await terminal(hash); const validators = tx.consensus_data?.validators || [];
  const validator = validators.find(item => Buffer.from(item.result || "", "base64").toString("utf8") !== "\u0002idle") || validators[0];
  const record = { scenario, functionName, hash, status: tx.statusName, result: tx.result_name,
    execution: validator?.execution_result, rotations: tx.rotation_count };
  transactions.push(record); console.log(json(record)); return record;
}
function accepted(record) {
  return record.status === "FINALIZED" && record.execution === "SUCCESS" && ["ACCEPTED", "MAJORITY_AGREE"].includes(record.result);
}
async function mustWrite(scenario, functionName, args, txValue = 0n) {
  const record = await write(scenario, functionName, args, txValue);
  if (!accepted(record)) throw new Error(`${functionName} failed: ${json(record)}`);
  return record;
}
async function mustReject(scenario, functionName, args, txValue = 0n) {
  const record = await write(scenario, functionName, args, txValue);
  if (accepted(record)) throw new Error(`${functionName} unexpectedly succeeded: ${json(record)}`);
  return record;
}
async function waitState(label, probe) {
  for (let attempt = 0; attempt < 90; attempt++) {
    try { const output = await probe(); if (output) return output; } catch {}
    await delay(4000);
  }
  throw new Error(`Canonical-state timeout: ${label}`);
}
async function createMandate(scenario, id, challengeWindow = 60n) {
  await mustWrite(scenario, "create_mandate", [id, `${scenario} mandate`,
    "Pay the approved security auditor for the completed audit. Do not create upgrade, treasury, emergency, or administrative authority.",
    `${rawBase}/governance_policy.md`, target, value, bond, challengeWindow]);
  return waitState(`${id} created`, async () => (await read("get_mandate", [id])).status === "active");
}
async function waitPastDeadline(state, challengeWindow) {
  const remainingMs = Math.max(0, (Number(state.reviewed_at) + Number(challengeWindow)) * 1000 - Date.now() + 5000);
  if (remainingMs > 0) await delay(remainingMs);
}
async function propose(scenario, executionId, mandateId, proposalTarget, hash, plan) {
  await mustWrite(scenario, "propose_execution", [executionId, mandateId, proposalTarget, value, hash, plan,
    "Pay the auditor only; create no permissions or additional calls."]);
  return waitState(`${executionId} proposed`, async () => (await read("get_execution", [executionId])).status === "proposed");
}
async function reviewUntilTerminal(scenario, executionId, attempts = 2) {
  for (let attempt = 0; attempt < attempts; attempt++) {
    const record = await write(scenario, "review_execution", [executionId]);
    const state = await read("get_execution", [executionId]);
    states.push({ scenario, stage: `review-${attempt + 1}`, transaction: record, state });
    if (accepted(record)) return state;
    if (state.status !== "proposed" || Number(state.reviewed_at) !== 0) throw new Error("Failed review mutated canonical state");
  }
  throw new Error(`${scenario} did not obtain an accepted review`);
}

await mustWrite("setup", "set_paused", [false]);

const safeMandate = `praxis-safe-m-${stamp}`;
const safeExecution = `praxis-safe-e-${stamp}`;
const safeWindow = 600n;
await createMandate("safe", safeMandate, safeWindow);
await propose("safe", safeExecution, safeMandate, target, safeHash, `${rawBase}/safe_execution_plan.md`);
let safeState = await reviewUntilTerminal("safe", safeExecution);
if (safeState.verdict !== "authorized") throw new Error(`Safe execution was not authorized: ${json(safeState)}`);
await mustWrite("safe-challenge", "challenge_execution", [safeExecution], bond);
await waitState("safe challenged", async () => (await read("get_execution", [safeExecution])).status === "proposed");
safeState = await reviewUntilTerminal("safe-challenge", safeExecution);
if (safeState.verdict !== "authorized" || BigInt(safeState.challenge_bond_held) !== 0n) throw new Error("Challenge re-review or bond settlement failed");
await waitPastDeadline(safeState, safeWindow);
const executable = await read("is_executable", [safeExecution]);
if (!executable.executable) throw new Error(`Authorized execution did not become consumable: ${json(executable)}`);
await mustWrite("pause-consistency", "set_paused", [true]);
const pausedExecutable = await read("is_executable", [safeExecution]);
if (pausedExecutable.executable) throw new Error("Paused contract reported execution as executable");
await mustWrite("pause-consistency", "set_paused", [false]);
if (!(await read("is_executable", [safeExecution])).executable) throw new Error("Unpaused execution did not become executable again");
await mustWrite("safe", "consume_execution", [safeExecution]);
safeState = await waitState("safe consumed", async () => {
  const row = await read("get_execution", [safeExecution]); return row.status === "consumed" ? row : null;
});
states.push({ scenario: "safe", stage: "consumed", state: safeState });
await mustReject("safe-replay", "consume_execution", [safeExecution]);

const deterministicMandate = `praxis-target-m-${stamp}`;
const deterministicExecution = `praxis-target-e-${stamp}`;
await createMandate("deterministic-negative", deterministicMandate);
await propose("deterministic-negative", deterministicExecution, deterministicMandate, otherTarget, safeHash, `${rawBase}/safe_execution_plan.md`);
const deterministicState = await reviewUntilTerminal("deterministic-negative", deterministicExecution, 1);
if (deterministicState.verdict !== "blocked" || deterministicState.confidence !== 100) throw new Error("Deterministic safety floor failed");
states.push({ scenario: "deterministic-negative", stage: "blocked", state: deterministicState });

const hostileMandate = `praxis-hostile-m-${stamp}`;
const hostileExecution = `praxis-hostile-e-${stamp}`;
await createMandate("semantic-negative", hostileMandate);
await propose("semantic-negative", hostileExecution, hostileMandate, target, hostileHash, `${rawBase}/hostile_execution_plan.md`);
const hostileState = await reviewUntilTerminal("semantic-negative", hostileExecution);
if (hostileState.verdict === "authorized") throw new Error(`Authority-expanding plan was authorized: ${json(hostileState)}`);
if (!['blocked', 'inconclusive'].includes(hostileState.verdict)) throw new Error("Hostile plan produced unknown verdict");
states.push({ scenario: "semantic-negative", stage: hostileState.verdict, state: hostileState });

const expiryMandate = `praxis-expiry-m-${stamp}`;
const expiryExecution = `praxis-expiry-e-${stamp}`;
await createMandate("challenge-expiry", expiryMandate);
await propose("challenge-expiry", expiryExecution, expiryMandate, target, safeHash, `${rawBase}/safe_execution_plan.md`);
const expiryState = await reviewUntilTerminal("challenge-expiry", expiryExecution);
if (expiryState.verdict !== "authorized") throw new Error("Challenge-expiry setup was not authorized");
await waitPastDeadline(expiryState, 60n);
await mustReject("challenge-expiry", "challenge_execution", [expiryExecution], bond);
if ((await read("get_execution", [expiryExecution])).status !== "reviewed") throw new Error("Expired challenge mutated execution state");

const cancelMandate = `praxis-cancel-m-${stamp}`;
const cancelExecution = `praxis-cancel-e-${stamp}`;
await createMandate("cancellation", cancelMandate);
await propose("cancellation", cancelExecution, cancelMandate, target, safeHash, `${rawBase}/safe_execution_plan.md`);
await mustWrite("cancellation", "cancel_execution", [cancelExecution]);
const cancelled = await waitState("cancelled", async () => {
  const row = await read("get_execution", [cancelExecution]); return row.status === "cancelled" ? row : null;
});
states.push({ scenario: "cancellation", stage: "cancelled", state: cancelled });

const exactSafety = safeState.status === "consumed" && deterministicState.verdict === "blocked" && !pausedExecutable.executable &&
  hostileState.verdict !== "authorized" && cancelled.status === "cancelled" && BigInt(safeState.challenge_bond_held) === 0n;
console.log(json({ contract: address, exactSafety, transactions, states }));
if (!exactSafety) process.exitCode = 1;
