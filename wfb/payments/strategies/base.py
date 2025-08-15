from abc import ABC, abstractmethod


class PaymentStrategy(ABC):
    @abstractmethod
    def process_payment(self, amount):
        pass

    @abstractmethod
    def checkout_init(self, *args, **kwargs):
        pass

    @abstractmethod
    def checkout_retrieve(self, *args, **kwargs):
        pass
