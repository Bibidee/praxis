import fs from "node:fs/promises";
import { createHash } from "node:crypto";
import { setTimeout as delay } from "node:timers/promises";
import { createClient } from "genlayer-js";
import { studionet } from "genlayer-js/chains";

if (!process.env.PRAXIS_CONTRACT) throw new Error("PRAXIS_CONTRACT is required");
const client = createClient({ chain: studionet, endpoint: process.env.PRAXIS_RPC || "https://studio.genlayer.com/api" });
const local = await fs.readFile("contracts/praxis.py", "utf8");
let deployedValue;
let lastError;
for (let attempt = 0; attempt < 8; attempt++) {
  try { deployedValue = await client.getContractCode(process.env.PRAXIS_CONTRACT); break; }
  catch (error) { lastError = error; await delay(2500 * (attempt + 1)); }
}
if (deployedValue === undefined) throw lastError;
const deployed = typeof deployedValue === "string" ? deployedValue : new TextDecoder().decode(deployedValue);
const digest = value => createHash("sha256").update(value, "utf8").digest("hex");
const result = { address: process.env.PRAXIS_CONTRACT, localSha256: digest(local), deployedSha256: digest(deployed), exactMatch: local === deployed };
console.log(JSON.stringify(result, null, 2)); if (!result.exactMatch) process.exitCode = 1;
