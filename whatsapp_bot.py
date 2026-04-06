"""
whatsapp_bot.py - WhatsApp bot interface for OpenGuy.
Control robots via WhatsApp chat with natural language commands.

Uses Twilio's WhatsApp Business API for message handling.
"""

import os
import logging
from typing import Optional, Dict, Any
import requests
import json

from parser import parse
from hybrid_sim import HybridExecutor


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OpenGuyWhatsAppBot:
    """WhatsApp bot interface for OpenGuy robot control via Twilio."""
    
    def __init__(self, account_sid: str, auth_token: str, twilio_phone: str, executor: Optional[HybridExecutor] = None):
        """
        Initialize WhatsApp bot using Twilio.
        
        Args:
            account_sid: Twilio Account SID
            auth_token: Twilio Auth Token
            twilio_phone: Twilio WhatsApp number (e.g., "whatsapp:+1234567890")
            executor: Optional HybridExecutor instance (creates own if not provided)
        """
        self.account_sid = account_sid
        self.auth_token = auth_token
        self.twilio_phone = twilio_phone
        self.executor = executor or HybridExecutor(try_hardware=True)
        self.user_sessions: Dict[str, Dict[str, Any]] = {}  # Store per-user state
        
        # Twilio messaging endpoint
        self.api_url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json"
    
    def send_message(self, phone_number: str, text: str) -> bool:
        """
        Send WhatsApp message via Twilio.
        
        Args:
            phone_number: Recipient phone in E.164 format (e.g., "+1234567890")
            text: Message text to send
            
        Returns:
            True if successful
        """
        try:
            # Ensure phone has whatsapp: prefix
            recipient = f"whatsapp:{phone_number}" if not phone_number.startswith("whatsapp:") else phone_number
            
            payload = {
                "From": self.twilio_phone,
                "To": recipient,
                "Body": text
            }
            
            response = requests.post(
                self.api_url,
                data=payload,
                auth=(self.account_sid, self.auth_token)
            )
            
            if response.status_code in [200, 201]:
                logger.info(f"Message sent to {phone_number}")
                return True
            else:
                logger.error(f"Failed to send message: {response.text}")
                return False
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return False
    
    def send_media(self, phone_number: str, media_url: str, caption: str = "") -> bool:
        """
        Send media (image/video) via WhatsApp.
        
        Args:
            phone_number: Recipient phone number
            media_url: URL to media file
            caption: Optional caption
            
        Returns:
            True if successful
        """
        try:
            recipient = f"whatsapp:{phone_number}" if not phone_number.startswith("whatsapp:") else phone_number
            
            payload = {
                "From": self.twilio_phone,
                "To": recipient,
                "MediaUrl": media_url
            }
            if caption:
                payload["Body"] = caption
            
            response = requests.post(
                self.api_url,
                data=payload,
                auth=(self.account_sid, self.auth_token)
            )
            
            return response.status_code in [200, 201]
        except Exception as e:
            logger.error(f"Error sending media: {e}")
            return False
    
    def handle_message(self, incoming_message: Dict[str, Any]) -> str:
        """
        Handle incoming WhatsApp message from Twilio webhook.
        
        Args:
            incoming_message: Message data from Twilio webhook
            
        Returns:
            Response text to send back
        """
        phone_number = incoming_message.get("From", "").replace("whatsapp:", "")
        text = incoming_message.get("Body", "").strip()
        message_sid = incoming_message.get("MessageSid", "unknown")
        
        logger.info(f"Message from {phone_number}: {text}")
        
        # Initialize user session if needed
        if phone_number not in self.user_sessions:
            self.user_sessions[phone_number] = {
                "last_action": None,
                "pending_chain": None,
                "commands_executed": 0
            }
        
        # Handle special commands
        if text == "/start" or text.lower() in ["start", "hello", "hi"]:
            return self._handle_start(phone_number)
        elif text == "/help" or text.lower() == "help":
            return self._handle_help(phone_number)
        elif text == "/status" or text.lower() == "status":
            return self._handle_status(phone_number)
        elif text == "/mode" or text.lower() == "mode":
            return self._handle_mode(phone_number)
        elif text == "/stop" or text.lower() == "stop":
            return self._handle_stop(phone_number)
        elif text.startswith("/"):
            return f"❓ Unknown command: {text}\nType /help for available commands."
        
        # Handle robot commands
        return self._handle_robot_command(phone_number, text)
    
    def _handle_start(self, phone_number: str) -> str:
        """Handle start command."""
        response = (
            "🤖 *Welcome to OpenGuy!*\n\n"
            "I can control robot arms using natural language.\n\n"
            "Try commands like:\n"
            "• move forward 10 cm\n"
            "• rotate right 45 degrees\n"
            "• grab the object\n"
            "• move forward, rotate right, and grab\n\n"
            "Type /help for more info."
        )
        return response
    
    def _handle_help(self, phone_number: str) -> str:
        """Handle help command."""
        response = (
            "*📖 Available Commands*\n\n"
            "*Special Commands:*\n"
            "/start - Welcome message\n"
            "/help - Show this help\n"
            "/status - Robot status\n"
            "/mode - Check simulator/hardware mode\n"
            "/stop - Stop command chain\n\n"
            "*Robot Commands:*\n"
            "Say anything to control the robot:\n"
            "• move forward/backward/left/right\n"
            "• rotate left/right by angle\n"
            "• grab / release\n"
            "• multi-step: move forward, rotate right, grab\n\n"
            "*Examples:*\n"
            "go 10cm right\n"
            "spin 90 degrees\n"
            "pick up the block\n"
            "move forward 20cm and release"
        )
        return response
    
    def _handle_status(self, phone_number: str) -> str:
        """Handle status command."""
        status = self.executor.get_status()
        
        mode = "🟢 HARDWARE" if status['mode'] == 'hardware' else "🟡 SIMULATOR"
        hw_available = "✅ Yes" if status.get('hardware_available') else "❌ No"
        
        response = (
            "*🤖 Robot Status*\n\n"
            f"Mode: {mode}\n"
            f"Hardware Available: {hw_available}\n"
            f"Position: ({status.get('x', 0):.1f}, {status.get('y', 0):.1f})\n"
            f"Facing: {status.get('facing', 0):.0f}°\n"
            f"Gripper: {'Open' if status.get('gripper_open', True) else 'Closed'}\n"
            f"Commands Executed: {status.get('commands_executed', 0)}"
        )
        return response
    
    def _handle_mode(self, phone_number: str) -> str:
        """Handle mode command."""
        status = self.executor.get_status()
        
        if status['mode'] == 'hardware':
            return "🟢 *HARDWARE MODE*\nControlling real robot arm via USB/Serial"
        else:
            return "🟡 *SIMULATOR MODE*\nNo hardware detected. Using virtual simulator."
    
    def _handle_stop(self, phone_number: str) -> str:
        """Handle stop command."""
        if phone_number in self.user_sessions:
            self.user_sessions[phone_number]['pending_chain'] = None
            return "⏹️ Command chain stopped."
        return "No active command chain."
    
    def _handle_robot_command(self, phone_number: str, text: str) -> str:
        """Handle robot commands."""
        try:
            # Parse the command
            parsed = parse(text, use_ai=True)
            
            if not parsed['action'] or parsed['action'] == 'unknown':
                return "❓ Sorry, I couldn't understand that. Try:\n• move forward\n• rotate right\n• grab"
            
            # Execute the command
            result = self.executor.execute(
                action=parsed['action'],
                direction=parsed['direction'],
                distance_cm=parsed['distance_cm'],
                angle_deg=parsed['angle_deg']
            )
            
            # Update session
            self.user_sessions[phone_number]['last_action'] = parsed['action']
            self.user_sessions[phone_number]['commands_executed'] += 1
            
            # Format response
            lines = result.get('output', [])
            if not lines and 'status' in result:
                lines = [result['status']]
            
            confidence = parsed.get('confidence', 0)
            conf_emoji = "🟢" if confidence >= 0.8 else "🟡" if confidence >= 0.5 else "🔴"
            
            response = (
                f"{conf_emoji} *Confidence: {confidence:.0%}*\n\n"
                f"*Action:* {parsed['action'].title()}\n"
            )
            
            if parsed['direction']:
                response += f"*Direction:* {parsed['direction']}\n"
            if parsed['distance_cm']:
                response += f"*Distance:* {parsed['distance_cm']}cm\n"
            if parsed['angle_deg']:
                response += f"*Angle:* {parsed['angle_deg']}°\n"
            
            response += f"\n*Result:*\n" + "\n".join(lines)
            
            return response
            
        except Exception as e:
            logger.error(f"Command execution error: {e}")
            return f"⚠️ Error: {str(e)}"
    
    def handle_webhook(self, message_data: Dict[str, Any]) -> str:
        """
        Handle incoming webhook from Twilio.
        
        Args:
            message_data: Message data from webhook
            
        Returns:
            Response to send
        """
        return self.handle_message(message_data)
    
    def close(self):
        """Close bot and cleanup."""
        self.executor.close()


def create_whatsapp_bot(
    account_sid: Optional[str] = None,
    auth_token: Optional[str] = None,
    twilio_phone: Optional[str] = None,
    executor: Optional[HybridExecutor] = None
) -> OpenGuyWhatsAppBot:
    """
    Create and configure WhatsApp bot using Twilio.
    
    Args:
        account_sid: Twilio Account SID (defaults to TWILIO_ACCOUNT_SID env var)
        auth_token: Twilio Auth Token (defaults to TWILIO_AUTH_TOKEN env var)
        twilio_phone: Twilio WhatsApp number (defaults to TWILIO_WHATSAPP_NUMBER env var)
        executor: Optional HybridExecutor instance
        
    Returns:
        Configured WhatsApp bot instance
        
    Raises:
        ValueError: If required credentials are missing
    """
    account_sid = account_sid or os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = auth_token or os.getenv("TWILIO_AUTH_TOKEN")
    twilio_phone = twilio_phone or os.getenv("TWILIO_WHATSAPP_NUMBER")
    
    if not all([account_sid, auth_token, twilio_phone]):
        raise ValueError(
            "Missing Twilio credentials. Set environment variables:\n"
            "TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_WHATSAPP_NUMBER"
        )
    
    return OpenGuyWhatsAppBot(account_sid, auth_token, twilio_phone, executor=executor)
