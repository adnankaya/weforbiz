
from wfb.payments.strategies.base import PaymentStrategy

class BankTransferPaymentStrategy(PaymentStrategy):
    def process_payment(self, amount):
        # Logic to process payment via bank transfer
        pass