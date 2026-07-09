# Clinical Gateway Architecture

```text
Patient
  |
  | 1. Sends message on WhatsApp / LINE / Zalo / Messenger
  v
Infobip Channel Layer
  |
  | 2. Inbound webhook call to your public URL
  v
POST /webhooks/infobip/inbound
  |
  | 3. Parse packet, normalize message, identify channel + clinic
  v
FastAPI Gateway
  |
  | 4. Idempotency check + log packet
  v
In-process Dummy Reply Composer
  |
  | 5. Build dummy reply and attach original metadata
  v
Outgoing Reply Packet
  |
  | 6. Send outbound message through Infobip API
  v
Infobip Message Send API
  |
  | 7. Delivers reply on the same patient channel/thread
  v
Patient

Supporting data flow:

   INFOBIP_BASE_URL + INFOBIP_API_KEY
            |
            v
      Backend outbound sender

   CLINIC_SENDER_MAP
            |
            v
   sender/channel -> clinic_id lookup
```

## Data Flow In Code

```text
Infobip webhook request
  -> [src/app/routers/infobip_webhook.py]
  -> normalize payload
  -> [src/app/services/normalizer.py]
  -> channel mapping
  -> [src/app/services/channel_registry.py]
  -> duplicate check
  -> [src/app/services/idempotency.py]
  -> in-process packet processor / dummy reply composer
  -> [src/app/services/clinical_backend_client.py]
  -> build outbound send payload
  -> [src/app/services/infobip_sender.py]
  -> Infobip Messages API
  -> patient receives reply
```

## Files Used

```text
[src/app/main.py]
  FastAPI app entrypoint
  - mounts the webhook router
  - exposes /healthz
  - keeps startup minimal

[src/app/routers/infobip_webhook.py]
  Inbound webhook handler
  - receives Infobip callback
  - normalizes the payload
  - checks idempotency
  - builds a dummy reply packet with original metadata
  - sends the reply back to Infobip

[src/app/services/normalizer.py]
  Payload normalization
  - reads Infobip payload structure
  - extracts channel, from, to, text, messageId
  - resolves clinic_id from CLINIC_SENDER_MAP

[src/app/services/channel_registry.py]
  Channel name mapping
  - converts Infobip channel strings to internal enum values

[src/app/services/idempotency.py]
  Duplicate protection
  - skips messages already processed by message_id

[src/app/services/clinical_backend_client.py]
  Dummy reply composer
  - logs the inbound packet
  - creates a random dummy message
  - returns reply text plus original message metadata

[src/app/services/infobip_sender.py]
  Outbound relay
  - builds Infobip Messages API request
  - uses INFOBIP_BASE_URL and INFOBIP_API_KEY

[src/app/models/messages.py]
  Data contracts
  - channel enum
  - inbound message model
  - outbound message model

[src/app/config.py]
  Runtime settings
  - INFOBIP_BASE_URL
  - INFOBIP_API_KEY
  - INFOBIP_WEBHOOK_SECRET
  - CLINIC_SENDER_MAP

[docs/architecture.md]
  This diagram and flow reference

[docs/startup.md]
  Local run and test commands

[tests/test_webhook_normalization.py]
  Normalization and inbound payload tests

[tests/test_outbound_relay.py]
  Outbound Infobip send tests
```

## Notes

- Infobip is only the transport layer.
- Your backend owns packet parsing, logging, metadata tagging, and reply composition.
- The webhook endpoint receives inbound messages only; the API key is used for outbound sends.
- For local testing, expose the FastAPI app with a tunnel and point Infobip webhook callbacks to that public URL.

## Verified Findings

```text
1) Inbound webhook path is correct and reachable:
  POST /webhooks/infobip/inbound

2) Outbound payload required Infobip Messages API shape updates:
  - channel must be provider enum (e.g., WHATSAPP)
  - sender field must be used
  - content.body.text + content.body.type=TEXT required

3) INFOBIP_BASE_URL can be host-only in env; code now auto-prefixes https://.

4) Duplicate message IDs are intentionally ignored by idempotency store.
  Reusing messageId returns status=duplicate.

5) Trial sender limitation confirmed:
  REJECTED_DESTINATION_NOT_REGISTERED (579)
  Destination must be allowlisted for trial/demo traffic.
```

## Current Status

```text
- Backend webhook flow: working
- Outbound Infobip call: working (accepted as PENDING_ACCEPTED)
- Real WhatsApp end-to-end on trial: depends on destination allowlist/trial policy
```