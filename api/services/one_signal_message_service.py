### OneSignal Service. This file handles OneSignal 'Message' APIs

import aiohttp
import json
from typing import Dict, Optional
from ..config import settings
from ..models.schemas import DeliveryRequest    


class OneSignalMessageService:
    """Service for sending messages via OneSignal"""
    
    ### OneSignal App Definitions
    def __init__(self):
        # Signal Post  (environment 1)
        self.app_id_1 = settings.signal_post_app_id
        self.api_key_1 = settings.signal_post_api_key
        # EMEA SE Demo (environment 2)
        self.app_id_2 = settings.emea_se_demo_app_id
        self.api_key_2 = settings.emea_se_demo_api_key
        ## add later

        self.base_url = "https://api.onesignal.com/notifications"

    ### SMS OTP from EMEA SE Demo App
    async def send_sms_otp(self, phone_number: str, otp_code: str, environment: int = 2) -> Dict:
        """
        Send an OTP SMS using OneSignal

        Args:
            phone_number: The phone number to send the OTP to
            otp_code: The message content (OTP code)
            environment: Which OneSignal environment to use (default: 2)
        Returns:
            Response from OneSignal API
        """
        ### Create Message Payload
        payload = {
            "app_id": getattr(self, f"app_id_{environment}"),
            "template_id": settings.emea_se_demo_sms_otp,
            "include_phone_numbers": [phone_number],
            "custom_data": {
                "signal_code": otp_code
            }
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Basic {getattr(self, f'api_key_{environment}')}"
        }
        ### API Request
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.base_url,
                json=payload,
                headers=headers
            ) as response:
                response_data = await response.json()
                print(f"Response from OneSignal: {response_data}")
                return response_data
                
    ### Delivery Service Sequence
    async def send_delivery_notification(self, request: DeliveryRequest, status: str, environment=1) -> Dict:
        """Send Delivery Notification Sequence"""

            # Debug: Log what we're about to send
        print(f"🔍 DEBUG - Attempting to send: {status}")
        print(f"🔍 DEBUG - Environment: {environment}")
        print(f"🔍 DEBUG - External ID: {request.external_id}")
        print(f"🔍 DEBUG - App ID: {getattr(self, f'app_id_{environment}', 'NOT FOUND')}")

        template_mapping = {
            "Delivery Pickup": settings.signal_post_delivery_pickup,
            "In transit": settings.signal_post_in_transit,
            "Delivered": settings.signal_post_delivered
        }
        
        template_id = template_mapping.get(status)
        print(f"🔍 DEBUG - Template ID: {template_id}")

        if not template_id:
            raise ValueError(f"Invalid status: {status}")
        
        payload = {
            "app_id": getattr(self, f"app_id_{environment}"),
            "include_aliases": {
                "external_id": [request.external_id]
            },
            "target_channel": "push",
            "template_id": template_id,
            "custom_data": {
                "tracking_id": request.tracking_id,
                "parcel_destination": request.parcel_destination
            }
        }
        
        print(f"🔍 DEBUG - Full payload: {json.dumps(payload, indent=2)}")
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Basic {getattr(self, f'api_key_{environment}')}"
        }
        
        ### API Request
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.base_url,
                json=payload,
                headers=headers
            ) as response:
                response_data = await response.json()
                print(f"Response from OneSignal: {response_data}")
                return response_data

            
# Create singleton instance        
onesignal_message_service = OneSignalMessageService()