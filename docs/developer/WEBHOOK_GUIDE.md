# Webhook Integration & Signature Verification Guide

Outbound webhooks allow your external services to subscribe to asynchronous events emitted by AI Job Copilot.

---

## 1. Subscribed Event Types

| Event Name | Trigger |
|---|---|
| `resume.parsed` | Emitted when a candidate uploads a resume and text/skills parsing succeeds |
| `job.matched` | Emitted when an ingested job listing evaluates against a candidate with a score >= 75% |
| `report.generated` | Emitted when a PDF or JSON analytics report generation completes |
| `application.created` | Emitted when a job application record is added (manually or via API) |
| `application.updated` | Emitted when an application status or interview stage updates |

---

## 2. Webhook Payload Structure

Webhook deliveries send a `POST` request with a JSON payload:

```json
{
  "id": "evt_550e8400_e29b_41d4_a716_446655440000",
  "event": "application.created",
  "timestamp": 1727521200,
  "data": {
    "application_id": "e4444444-4444-4444-4444-444444444444",
    "job_id": "d3333333-3333-3333-3333-333333333333",
    "job_title": "Principal Platform Engineer",
    "company": "Stripe",
    "status": "Applied"
  }
}
```

---

## 3. Cryptographic Signature Verification (HMAC-SHA256)

Every webhook request contains the `X-Webhook-Signature` header:
```http
X-Webhook-Signature: t=1727521200,v1=9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08
X-Webhook-Event: application.created
```

### Signature Construction
1. Extract the timestamp `t` and the signature `v1` from the `X-Webhook-Signature` header.
2. Concatenate: `${t}.${raw_request_body}`.
3. Compute the HMAC-SHA256 hash using your webhook secret (`whsec_...`) as the secret key.
4. Perform a timing-safe equality comparison against `v1`.

### Verification Code Examples

#### Node.js / TypeScript
```typescript
import crypto from 'crypto';

export function verifyWebhookSignature(
  rawBody: string,
  signatureHeader: string,
  secret: string,
  toleranceSeconds: number = 300
): boolean {
  const parts = signatureHeader.split(',');
  const tPart = parts.find((p) => p.startsWith('t='));
  const v1Part = parts.find((p) => p.startsWith('v1='));

  if (!tPart || !v1Part) return false;

  const timestamp = parseInt(tPart.slice(2), 10);
  const signature = v1Part.slice(3);

  // Prevent replay attacks (check 5 min tolerance)
  const now = Math.floor(Date.now() / 1000);
  if (Math.abs(now - timestamp) > toleranceSeconds) {
    return false;
  }

  const signedPayload = `${timestamp}.${rawBody}`;
  const expectedSignature = crypto
    .createHmac('sha256', secret)
    .update(signedPayload, 'utf8')
    .digest('hex');

  return crypto.timingSafeEqual(
    Buffer.from(signature, 'hex'),
    Buffer.from(expectedSignature, 'hex')
  );
}
```

#### Python (FastAPI / Flask)
```python
import hmac
import hashlib
import time

def verify_webhook_signature(
    raw_body: bytes,
    signature_header: str,
    secret: str,
    tolerance_seconds: int = 300,
) -> bool:
    try:
        parts = dict(item.split("=", 1) for item in signature_header.split(","))
        timestamp = int(parts.get("t", "0"))
        signature = parts.get("v1", "")

        # Verify timestamp to prevent replay attacks
        now = int(time.time())
        if abs(now - timestamp) > tolerance_seconds:
            return False

        signed_payload = f"{timestamp}.".encode("utf-8") + raw_body
        expected = hmac.new(
            secret.encode("utf-8"),
            signed_payload,
            hashlib.sha256,
        ).hexdigest()

        return hmac.compare_digest(expected, signature)
    except Exception:
        return False
```

---

## 4. Retries & Delivery Logs

- AI Job Copilot automatically retries delivery up to **3 times** with exponential backoff on HTTP `5xx` responses or network timeouts.
- All delivery attempts, HTTP status codes, durations, and payload errors are logged and viewable in the Developer Portal under **Webhooks > Delivery Logs**.
