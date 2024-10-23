const express = require('express');
const crypto = require('crypto');
const base64 = require('base64-js');

const app = express();
app.use(express.json());

// Mock function to derive a public key
function derivePublicKey(path, account) {
    // This is a mock implementation. In a real scenario, you'd use proper key derivation.
    const combinedInput = `${path}-${account}`;
    return crypto.createHash('sha256').update(combinedInput).digest('hex');
}

// Mock function to sign data
function signData(path, account, payload) {
    // This is a mock implementation. In a real scenario, you'd use proper signing algorithms.
    const combinedInput = `${path}-${account}-${payload}`;
    return crypto.createHash('sha256').update(combinedInput).digest('hex');
}

app.post('/derived_public_key', (req, res) => {
    const { path, account } = req.body;
    if (!path || !account) {
        return res.status(400).json({ error: 'Missing path or account' });
    }
    const derivedKey = derivePublicKey(path, account);
    res.json({ derived_public_key: derivedKey });
});

app.post('/sign', (req, res) => {
    const { path, account, payload } = req.body;
    if (!path || !account || !payload) {
        return res.status(400).json({ error: 'Missing path, account, or payload' });
    }
    try {
        const decodedPayload = base64.toByteArray(payload);
        if (decodedPayload.length !== 32) {
            return res.status(400).json({ error: 'Payload must decode to 32 bytes' });
        }
        const signature = signData(path, account, payload);
        res.json({ signature });
    } catch (error) {
        res.status(400).json({ error: 'Invalid base64 payload' });
    }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});
