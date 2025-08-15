
from wfb.payments.strategies.base import PaymentStrategy

class CreditCardPaymentStrategy(PaymentStrategy):
    def process_payment(self, amount):
        # Logic to process payment via credit card
        pass