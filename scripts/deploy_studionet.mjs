import fs from "node:fs/promises";
import { setTimeout as delay } from "node:timers/promises";
import { Wallet } from "ethers";
import { createClient } from "genlayer-js";
import { studionet } from "genlayer-js/chains";
import { privateKeyToAccount } from "viem/accounts";

if (!process.env.PRAXIS_WALLET_PASSWORD || !process.env.PRAXIS_KEYSTORE) throw new Error("PRAXIS_WALLET_PASSWORD and PRAXIS_KEYSTORE are required");
const wallet = await Wallet.fromEncryptedJson(await fs.readFile(process.env.PRAXIS_KEYSTORE, "utf8"), process.env.PRAXIS_WALLET_PASSWORD);
const client = createClient({ chain: studionet, endpoint: process.env.PRAXIS_RPC || "https://studio.genlayer.com/api", account: privateKeyToAccount(wallet.privateKey) });
const code = await fs.readFile("contracts/praxis.py", "utf8");
const hash = await client.deployContract({ code, args: [wallet.address], consensusMaxRotations: 5 });
console.log(JSON.stringify({ deploymentTransaction: hash, owner: wallet.address }, null, 2));
for (let attempt = 0; attempt < 180; attempt++) {
  await delay(5000); const tx = await client.getTransaction({ hash });
  if (!["FINALIZED", "UNDETERMINED", "CANCELED"].includes(tx.statusName)) continue;
  const validators = tx.consensus_data?.validators || [];
  const validator = validators.find(item => Buffer.from(item.result || "", "base64").toString("utf8") !== "\u0002idle") || validators[0];
  const contractAddress = tx.data?.calldata?.contractAddress || tx.recipient || tx.to;
  const result = { deploymentTransaction: hash, status: tx.statusName, result: tx.result_name,
    execution: validator?.execution_result, rotations: tx.rotation_count, contractAddress };
  console.log(JSON.stringify(result, null, 2));
  if (result.status !== "FINALIZED" || result.execution !== "SUCCESS" || !contractAddress) process.exitCode = 1;
  process.exit();
}
throw new Error(`Deployment timeout: ${hash}`);
