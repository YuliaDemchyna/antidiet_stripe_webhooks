# Stripe Webhook Handler for Successful Payments

This FastAPI application handles Stripe webhook events for successful payments and sends order details via email using SendGrid.

## Event Selection

[The Session object Stripe docs](https://docs.stripe.com/api/checkout/sessions/object)

The webhook listens for two types of events:

```python
event['type'] == 'checkout.session.async_payment_succeeded' or 
(event['type'] == 'checkout.session.completed' and event['data']['object']['payment_status'] == 'paid')
```

This condition ensures that we capture successful payments for both immediate and asynchronous payment methods. The `checkout.session.completed` event with `payment_status == 'paid'` covers immediate payments, while `checkout.session.async_payment_succeeded` handles asynchronous payments that complete after the checkout.

### Subscription Handling

For subscription plans, this event will fire on each successful payment. To prevent multiple executions:

1. Store a flag in your database indicating whether the initial order has been processed.
2. Use Stripe metadata to mark the subscription as processed:

```python
stripe.Subscription.modify(
    subscription_id,
    metadata={'initial_order_processed': 'true'}
)
```

Then, check this metadata before processing:

```python
if not event['data']['object'].get('metadata', {}).get('initial_order_processed'):
    # Process the order
    # Set the metadata flag
```

## Code Flow

1. The webhook receives a POST request from Stripe.
2. It verifies the Stripe signature to ensure the request is legitimate.
3. For successful payments, it extracts customer details from the event.
4. An email is composed with order details and customer information.
5. The email is sent using SendGrid.

To ensure we only order scales for customers who want them:

1. Check for a specific product ID in the line items of the checkout session.
2. Use Stripe Checkout's custom fields to let customers opt-in for the scale.

Example:

```python
if any(item['price']['product'] == 'prod_scale_id' for item in session['line_items']):
    # Process scale order
```

## Improvement Suggestions

1. Update a database with the customer's order status.
2. Implement error handling.

## Setup and Running

1. Install requirements:
   ```
   pip install fastapi uvicorn stripe python-dotenv sendgrid
   ```

2. Set up environment variables in a `.env` file:
   ```
   STRIPE_API_KEY=your_stripe_api_key
   STRIPE_ENDPOINT_SECRET=your_stripe_webhook_secret
   SENDGRID_API_KEY=your_sendgrid_api_key
   ```

3. Run the FastAPI server:
   ```
   uvicorn main:app --reload
   ```

4. Use Stripe CLI to forward events to your local server:
   ```
   stripe listen --forward-to localhost:8000/webhook_succesful_payment
   ```

## Deployment to AWS

1. Set up an EC2 instance with Python installed.
2. Clone your repository to the instance.
3. Install required packages and set up environment variables.
4. Use a process manager like PM2 to run the FastAPI app.
5. Set up Nginx as a reverse proxy to forward requests to your app.
6. Configure SSL with Let's Encrypt for HTTPS.
7. Update your Stripe webhook settings to point to your new endpoint.

Remember to secure your EC2 instance and follow AWS best practices for production deployments.
