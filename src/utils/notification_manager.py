# src/utils/notification_manager.py
# Handles push notifications for new messages

class NotificationManager:
    def __init__(self):
        self.app_name = "SimpleSideband"
        print("Notification manager initialized")
    
    def show_notification(self, title, message, contact_name=None):
        """Show a push notification"""
        try:
            from plyer import notification
            if contact_name:
                title = contact_name + " - " + title
            notification.notify(
                title=title,
                message=message,
                app_name=self.app_name,
                timeout=5
            )
            print("Notification shown: " + title)
            return True
        except Exception as e:
            print("Notification error: " + str(e))
            return False
    
    def show_message_notification(self, contact_name, message_preview):
        """Show notification for new message"""
        preview = message_preview[:50] + "..." if len(message_preview) > 50 else message_preview
        return self.show_notification(
            title="New Message",
            message=preview,
            contact_name=contact_name
        )
    
    def show_image_notification(self, contact_name):
        """Show notification for new image"""
        return self.show_notification(
            title="New Image",
            message=contact_name + " sent you an image",
            contact_name=None
        )
    
    def vibrate(self, duration=0.5):
        """Vibrate device (Android)"""
        try:
            from plyer import vibrator
            vibrator.vibrate(duration)
            return True
        except Exception as e:
            print("Vibrate error: " + str(e))
            return False
