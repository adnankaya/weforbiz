from wfb.payments.strategies.base import PaymentStrategy


class PayPalPaymentStrategy(PaymentStrategy):
    def process_payment(self, amount):
        # Logic to process payment via PayPal
        pass
