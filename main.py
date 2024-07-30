import json
import os
import stripe
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# The library needs to be configured with your account's secret key.
# Ensure the key is kept out of any version control system you might be using.
stripe.api_key = os.getenv("STRIPE_API_KEY")

# This is your Stripe CLI webhook secret for testing your endpoint locally.
endpoint_secret = os.getenv("STRIPE_ENDPOINT_SECRET")

app = FastAPI()

@app.post("/webhook_succesful_payment")
async def webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        raise HTTPException(status_code=400, detail=str(e))
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        raise HTTPException(status_code=400, detail=str(e))

    # Handle the event
    if event['type'] == 'checkout.session.async_payment_succeeded' or (event['type'] == 'checkout.session.completed' and event['data']['object']['payment_status'] == 'paid'):
        session = event['data']['object']
        print(session)
        #TODO get customer details here

        #TODO do sendgrid email sending
    else:
        print(f'Unhandled event type {event["type"]}')

        #TODO good way to handle the failure?

    return JSONResponse(content={"success": True})
