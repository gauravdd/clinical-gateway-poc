# Clinical Gateway Proto

FastAPI service that treats Infobip as channel plumbing only.

## Broad Flow (ASCII)

```text
  Patient (WhatsApp)
      |
      |  inquiry: "hi"
      v
  +------------------+
  |     Infobip      |
  +------------------+
      |
      |  inbound webhook POST
      v
  +-------------------------------------------+
  | Clinical Gateway Backend (this project)   |
  | - parse + normalize                        |
  | - idempotency check                        |
  | - build dummy reply + metadata             |
  +-------------------------------------------+
      |
      |  outbound send via Messages API
      v
  +------------------+
  |     Infobip      |
  +------------------+
      |
      |  delivery to same patient thread
      v
  Patient (WhatsApp)
```

## Simple Sequence + Key Files (Only)

1. Inbound request arrives at webhook route:
  [src/app/routers/infobip_webhook.py](src/app/routers/infobip_webhook.py)
2. Payload is normalized:
  [src/app/services/normalizer.py](src/app/services/normalizer.py)
3. Channel value is normalized:
  [src/app/services/channel_registry.py](src/app/services/channel_registry.py)
4. Duplicate message protection is applied:
  [src/app/services/idempotency.py](src/app/services/idempotency.py)
5. Dummy reply + source metadata are composed:
  [src/app/services/clinical_backend_client.py](src/app/services/clinical_backend_client.py)
6. Outbound request is sent to Infobip:
  [src/app/services/infobip_sender.py](src/app/services/infobip_sender.py)
7. App wiring and logging setup:
  [src/app/main.py](src/app/main.py)

## Identity model (current)
- clinic_id_type: PHONE_NUMBER
- patient_id_type: PHONE_NUMBER
- patient identity is channel-scoped (no cross-channel unification)

## Requirements
- Python 3.11+

## Quick start

1. Create and activate virtualenv.
2. Install package:
   - `pip install -e .[dev]`
3. Copy env file:
   - `cp .env.example .env`
4. Edit `.env` with your Infobip base URL and API key.
5. Start backend:
   - `uvicorn app.main:app --reload --app-dir src`
6. Start ngrok tunnel in another terminal:
   - `ngrok http 8000`
7. Configure Infobip webhook URL using ngrok domain:
   - `https://YOUR-NGROK-DOMAIN.ngrok-free.app/webhooks/infobip/inbound`

## Endpoints
- `GET /`
- `GET /healthz`
- `POST /webhooks/infobip/inbound`

## Infobip Setup (Simple)

1. Open `Developer Tools -> Subscriptions Management`.
2. In `Notification profiles`, create profile:
  - Name: `clinical-gateway-proto`
  - Webhook URL: `https://YOUR-NGROK-DOMAIN.ngrok-free.app/webhooks/infobip/inbound`
3. In `Subscriptions`, create subscription:
  - Channel: `WHATSAPP`
  - Event: `INBOUND_MESSAGE`
  - Notification profile: `clinical-gateway-proto`
4. Save and keep subscription active.
5. Send a test message to your Infobip WhatsApp sender.
6. Confirm request in ngrok inspector (`http://127.0.0.1:4040`) and app logs.

### Trial Account Notes

- Trial/test sender may allow only approved destination numbers.
- If outbound is rejected with code `579` and reason `REJECTED_DESTINATION_NOT_REGISTERED`, destination is not allowlisted for trial.
- In that case, use an allowlisted number or request allowlisting from Infobip support.

## Curl Test (Inbound Simulation)

```bash
curl -X POST https://sprang-cover-grinch.ngrok-free.dev/webhooks/infobip/inbound \
  -H "Content-Type: application/json" \
  -d '{"results":[{"channel":"whatsapp","from":"+91SenderNumber-FILL_THIS","to":"+447860088970","text":"hello","messageId":"manual-581","conversationId":"c-1"}]}'
```

## Example Response

```json
{
  "status": "sent",
  "message_id": "manual-581",
  "correlation_id": "7d92c914-bf11-4528-9758-2c291bf1c263",
  "processed": {
    "dummy_message": {
      "message_id": "201667540aed43c0a35d495c98b5bc03",
      "text": "We have captured the request and attached the original message metadata."
    },
    "source_message": {
      "message_id": "manual-581",
      "thread_id": "c-1",
      "clinic_id": "+447860088970",
      "clinic_identifier": "+447860088970",
      "patient_id": "whatsapp:+91SenderNumber-FILL_THIS",
      "patient_identifier": "+91SenderNumber-FILL_THIS",
      "channel": "whatsapp",
      "text": "hello"
    },
    "reply_text": "We have captured the request and attached the original message metadata. Ref: manual-581"
  },
  "provider_result": {
    "bulkId": "17835230609249445148272",
    "messages": [
      {
        "messageId": "17835230609249445148271",
        "status": {
          "groupId": 1,
          "groupName": "PENDING",
          "id": 26,
          "name": "PENDING_ACCEPTED",
          "description": "Message sent to next instance"
        },
        "destination": "+91SenderNumber-FILL_THIS"
      }
    ]
  }
}
```

## Deeper Docs

- Architecture details: [docs/architecture.md](docs/architecture.md)
- Startup and troubleshooting commands: [docs/startup.md](docs/startup.md)

## Notes
- This prototype does not perform medical triage or medical decisioning.
- Real doctor verification UI/flow is out of scope in v1.
