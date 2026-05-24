# Payment Processing Flow

Build tests for a payment checkout flow used by an e-commerce application.

The flow starts when a customer submits a cart and payment method on the checkout page. The backend validates the cart totals, applies discounts and tax, and creates a payment intent with a third-party payment provider. If the payment method requires additional verification, the system must return a pending status and expose a client secret for the frontend to complete authentication.

Once payment is confirmed, the order service reserves inventory, creates the order record, and emits an order-confirmed event. If inventory is unavailable after payment authorization, the system must fail gracefully, reverse the payment authorization when possible, and return an error explaining that stock was not available. If payment confirmation fails, the checkout should remain in an unpaid state and the user should be able to retry with the same cart.

Important behaviors to test:
- Successful payment with a valid card
- Declined card or invalid payment method
- 3D Secure / additional verification required
- Duplicate payment submission should not charge twice
- Cart total mismatch should fail validation
- Partial payment or expired authorization should be handled safely
- Large amounts, zero amounts, and currency edge cases
- Timeout from the payment provider
- Event emission after successful order creation
- Idempotency key handling across repeated requests
