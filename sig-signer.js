import { connect, keyStores, utils } from 'near-api-js';
const express = require('express');

export class SigSigner {
  constructor(accountId, networkId = 'testnet') {
    this.accountId = accountId;
    this.networkId = networkId;
  }

  async init() {
    const keyStore = new keyStores.BrowserLocalStorageKeyStore();
    const config = {
      networkId: this.networkId,
      keyStore,
      nodeUrl: `https://rpc.${this.networkId}.near.org`,
      walletUrl: `https://wallet.${this.networkId}.near.org`,
      helperUrl: `https://helper.${this.networkId}.near.org`,
      explorerUrl: `https://explorer.${this.networkId}.near.org`,
    };

    this.near = await connect(config);
    this.account = await this.near.account(this.accountId);
  }

  async derivedPublicKey(seed) {
    const result = await this.account.functionCall({
      contractId: 'sig.near',
      methodName: 'derived_public_key',
      args: { seed: utils.serialize.base_encode(seed) },
    });
    return utils.serialize.base_decode(result);
  }

  async sign(message, seed) {
    const result = await this.account.functionCall({
      contractId: 'sig.near',
      methodName: 'sign',
      args: {
        message: utils.serialize.base_encode(message),
        seed: utils.serialize.base_encode(seed),
      },
    });
    return utils.serialize.base_decode(result);
  }
}



const app = express();
app.use(express.json());

const signer = new SigSigner('your-account-id.testnet');

app.post('/derived_public_key', async (req, res) => {
  const { path, account } = req.body;
  if (!path || !account) {
    return res.status(400).json({ error: 'Missing path or account' });
  }
  
  try {
    await signer.init();
    const seed = Buffer.from(`${path}-${account}`);
    const derivedKey = await signer.derivedPublicKey(seed);
    res.json({ derived_public_key: utils.serialize.base_encode(derivedKey) });
  } catch (error) {
    res.status(500).json({ error: 'Failed to derive public key' });
  }
});

app.post('/sign', async (req, res) => {
  const { path, account, payload } = req.body;
  if (!path || !account || !payload) {
    return res.status(400).json({ error: 'Missing path, account, or payload' });
  }

  try {
    await signer.init();
    const decodedPayload = utils.serialize.base_decode(payload);
    if (decodedPayload.length !== 32) {
      return res.status(400).json({ error: 'Payload must decode to 32 bytes' });
    }
    const seed = Buffer.from(`${path}-${account}`);
    const signature = await signer.sign(decodedPayload, seed);
    res.json({ signature: utils.serialize.base_encode(signature) });
  } catch (error) {
    res.status(500).json({ error: 'Failed to sign data' });
  }
});

const PORT = process.env.PORT || 3001;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});