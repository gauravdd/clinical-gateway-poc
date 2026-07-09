# Startup Guide

## Run Locally

```bash
source .venv/bin/activate
uvicorn app.main:app --reload --app-dir src
```

## Ngrok Steps

1. Make sure ngrok is authenticated on this Mac:

```bash
ngrok config add-authtoken YOUR_AUTHTOKEN
```

2. Start the tunnel on port 8000:

```bash
ngrok http 8000
```

3. Copy the HTTPS forwarding URL ngrok prints.

4. Your public webhook URL will be:

```text
https://YOUR-NGROK-DOMAIN.ngrok-free.app/webhooks/infobip/inbound
```

## Infobip Steps

1. Open your Infobip dashboard and go to the WhatsApp channel setup.

2. Find the inbound webhook or callback URL field.

3. Paste your public ngrok webhook URL:

```text
https://YOUR-NGROK-DOMAIN.ngrok-free.app/webhooks/infobip/inbound
```

4. Save the channel configuration.

5. Send a test WhatsApp message to the Infobip number/sender.

6. Confirm your FastAPI app receives the POST request and sends the reply back.

## Test

```bash
source .venv/bin/activate
pytest
```

## Logs

- Logs print to the terminal where `uvicorn` is running.
- They are not saved to a file by default.
- If you want a file, start the app like this:

```bash
source .venv/bin/activate
uvicorn app.main:app --reload --app-dir src > app.log 2>&1
```

- Webhook logs include `message_id`, `thread_id`, `clinic_id`, `patient_id`, `channel`, and `correlation_id`.

## Sample Webhook Request

```bash
curl -X POST http://127.0.0.1:8000/webhooks/infobip/inbound \
  -H "Content-Type: application/json" \
  -d '{"results":[{"channel":"whatsapp","from":"+919972181700","to":"+447860088970","text":"hello","messageId":"manual-581","conversationId":"c-1"}]}'
```

## Public Webhook Test Through Ngrok

```bash
curl -X POST https://YOUR-NGROK-DOMAIN.ngrok-free.app/webhooks/infobip/inbound \
  -H "Content-Type: application/json" \
  -d '{"results":[{"channel":"whatsapp","from":"+919972181700","to":"+447860088970","text":"hello","messageId":"manual-582","conversationId":"c-1"}]}'
```

## Generate Unique Message IDs (Avoid Duplicate Response)

```bash
MSG_ID="manual-$(date +%s)"
curl -X POST https://YOUR-NGROK-DOMAIN.ngrok-free.app/webhooks/infobip/inbound \
  -H "Content-Type: application/json" \
  -d "{\"results\":[{\"channel\":\"whatsapp\",\"from\":\"+919972181700\",\"to\":\"+447860088970\",\"text\":\"hello\",\"messageId\":\"$MSG_ID\",\"conversationId\":\"c-1\"}]}"
```

## WhatsApp Trial Notes

- Trial sender traffic may reject non-allowlisted destination numbers.
- Known error: `REJECTED_DESTINATION_NOT_REGISTERED (579)`.
- For successful trial delivery, use a destination number allowed by Infobip trial policy.
- Manual webhook simulation can fully validate backend behavior even when trial channel delivery is restricted.

## Quick Troubleshooting

1. If no request appears in ngrok inspector (`http://127.0.0.1:4040`): Infobip did not call webhook.
2. If request appears in ngrok but no app logs: app route/process mismatch.
3. If app logs inbound but response has outbound error: check Infobip error detail in response body.
4. If response is `duplicate`: use a new `messageId`.

## Notes

- Use `docs/architecture.md` for the high-level data flow.
- Use `README.md` for the project overview.
- `INFOBIP_WEBHOOK_SECRET` is optional for this POC unless you add signature verification.