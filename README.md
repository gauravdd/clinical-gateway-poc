# Clinical Gateway Proto

FastAPI service that treats Infobip as channel plumbing only:
- Receives inbound channel messages from Infobip webhook
- Normalizes channel payload into one internal contract
- Calls backend dummy clinical decision endpoint (auto-approved mock)
- Sends approved response back through Infobip on same channel/thread

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
4. Edit `.env` with your Infobip base URL + API key.
5. Run app:
   - `uvicorn app.main:app --reload --app-dir src`

## Endpoints
- `GET /`
- `GET /healthz`
- `POST /webhooks/infobip/inbound`

## Sample webhook payload
```json
{
  "results": [
    {
      "channel": "whatsapp",
      "from": "+15550001111",
      "to": "+14155550100",
      "text": "I have a fever",
      "messageId": "m-1",
      "conversationId": "c-1"
    }
  ]
}
```

## Notes
- This prototype does not perform medical triage or medical decisioning.
- Real doctor verification UI/flow is out of scope in v1.
