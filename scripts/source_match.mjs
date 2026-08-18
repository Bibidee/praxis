import fs from "node:fs/promises";
import { createHash } from "node:crypto";
import { createClient } from "genlayer-js";
import { studionet } from "genlayer-js/chains";

if (!process.env.PRAXIS_CONTRACT) throw new Error("PRAXIS_CONTRACT is required");
const client = createClient({ chain: studionet, endpoint: process.env.PRAXIS_RPC || "https://studio.genlayer.com/api" });
const local = await fs.readFile("contracts/praxis.py", "utf8");
const deployedValue = await client.getContractCode(process.env.PRAXIS_CONTRACT);
const deployed = typeof deployedValue === "string" ? deployedValue : new TextDecoder().decode(deployedValue);
const digest = value => createHash("sha256").update(value, "utf8").digest("hex");
const result = { address: process.env.PRAXIS_CONTRACT, localSha256: digest(local), deployedSha256: digest(deployed), exactMatch: local === deployed };
console.log(JSON.stringify(result, null, 2)); if (!result.exactMatch) process.exitCode = 1;
