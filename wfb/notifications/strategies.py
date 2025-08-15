from abc import ABC, abstractmethod


class NotificationStrategy(ABC):
    @abstractmethod
    def send_notification(self, user, message):
        pass


class EmailNotificationStrategy(NotificationStrategy):
    def send_notification(self, user, message):
        # Code for sending email notification to the user
        pass


class SMSNotificationStrategy(NotificationStrategy):
    def send_notification(self, user, message):
        # Code for sending SMS notification to the user
        pass


class PushNotificationStrategy(NotificationStrategy):
    def send_notification(self, user, message):
        # Code for sending push notification to the user
        pass
