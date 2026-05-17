import logging
from typing import List, Optional

import firebase_admin
from firebase_admin import messaging
from authentication.firebase import _initialize_firebase

logger = logging.getLogger(__name__)

def send_push_notification(
    token: str, 
    title: str, 
    body: str, 
    data: Optional[dict] = None
) -> Optional[str]:
    """
    Send a push notification to a single device.
    """
    try:
        _initialize_firebase()
        
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            data=data if data else {},
            token=token,
        )
        
        response = messaging.send(message)
        logger.info(f"Successfully sent message: {response}")
        return response
    except Exception as e:
        logger.error(f"Error sending push notification: {e}")
        return None

def send_multicast_push_notification(
    tokens: List[str], 
    title: str, 
    body: str, 
    data: Optional[dict] = None
):
    """
    Send a push notification to multiple devices.
    """
    try:
        _initialize_firebase()
        
        message = messaging.MulticastMessage(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            data=data if data else {},
            tokens=tokens,
        )
        
        response = messaging.send_multicast(message)
        logger.info(f"{response.success_count} messages were sent successfully")
        return response
    except Exception as e:
        logger.error(f"Error sending multicast notification: {e}")
        return None
