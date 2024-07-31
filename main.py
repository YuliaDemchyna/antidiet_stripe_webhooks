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

#about the company and product
article_number = os.getenv('ARTIKEL_NR')
item_name = os.getenv('VARE_NAVN')
item_quantity = os.getenv('VARE_ANTALL')
organization_number = os.getenv('ORGANISASJONSNUMMER')

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

        customer_details = event['data']['object']['customer_details']
        address = customer_details['address']
        email = customer_details['email']
        phone = customer_details['phone']

        # Formatting the address
        formatted_address = f"{address['line1']}, {address['city']}, {address['state']}, {address['postal_code']}, {address['country']}"

        # Print extracted information
        # print("Delivery Address:", formatted_address)
        # print("Email:", email)
        # print("Phone:", phone if phone else "No phone number provided")

        email_body = f"""
            Hei,

            Følgende info for å sende inn en innkjøpsordre:

            Artikkel-nr: {article_number}
            Vare Navn: {item_name}
            Antall: {item_quantity}

            Leveringsadresse:
            {address['line1']}
            {address['line2']}
            {address['postal_code']} {address['city']}
            {address['country']}

            Organisasjonsnummer det skal faktureres til:
            {organization_number}

            Kundeinformasjon:
            E-post: {email}
            Telefon: {phone}

            Med vennlig hilsen,
            ANTIDIET
            """

        print(email_body)
        #TODO do sendgrid email sending
    else:
        print(f'Unhandled event type {event["type"]}')

        #TODO good way to handle the failure?

    return JSONResponse(content={"success": True})
