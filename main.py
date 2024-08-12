import json
import os
import stripe
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail



# Load environment variables from .env file
load_dotenv()

# The library needs to be configured with your account's secret key.
# Ensure the key is kept out of any version control system you might be using.
stripe.api_key = os.getenv("STRIPE_API_KEY")

# This is your Stripe CLI webhook secret for testing your endpoint locally.
endpoint_secret = os.getenv("STRIPE_ENDPOINT_SECRET")

#about the product
article_number = '44-5361-2'
item_name = 'Withings Body Smart badrumsvåg med kroppsanalys, WiFi'
item_quantity = 1

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

        email_body = f"""
        Hei, 
        
        Vi har en ny innkjøpsordre basert på vår nyligste kundeaktivitet. 
        
        Her er detaljene for bestillingen: 
        * Artikkel-nr: {article_number}
        * Artikelnavn: {item_name}
        * Antall: {item_quantity}
        
        Leveringsaddresse: 
        * {customer_details['name']}
        * E-post: {customer_details['email']}
        * Telefon: {customer_details['phone'] if customer_details['phone'] else 'Ikke oppgitt'}
        * {address['line1']}
        * {address['postal_code']} {address['city']}
        * {address['country']}
        
        Faktureres til: 
        * Org.nr. 930688614 
        * invoice@anti.diet 
        * Selskapsnavn ANTI DIET AS 
        
        Ta gjerne kontakt hvis dere har spørsmål og oppgi vårt interne referansenummer: 
        Kontaktperson: 
        * Carl H.B. Haukås 
        * Daglig leder | ANTIDIET 
        * +47 40634490 
        * carl@anti.diet 
        
        Takk for at dere er en super samarbeidspartner.
        Med vennlig hilsen, 
        Gjengen i ANTIDIET.
        """

        send_plain_text_email( os.environ.get('SENDGRID_API_KEY'),'yulia@anti.diet' , 'yuliademchyna@gmail.com', 'test email', email_body)
    else:
        print(f'Unhandled event type {event["type"]}')

    return JSONResponse(content={"success": True})


#make all fields that are neccesary to order obligatory!! phone number?

def send_plain_text_email(api_key, from_email, to_emails, subject, content):
    message = Mail(
        from_email=from_email,
        to_emails=to_emails,
        subject=subject,
        plain_text_content=content
    )

    try:
        sg = SendGridAPIClient(api_key)
        response = sg.send(message)
        print(f"Email sent successfully. Status Code: {response.status_code}")
        print(f"Response Body: {response.body}")
        print(f"Response Headers: {response.headers}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

