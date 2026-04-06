"""
tests/test_whatsapp_bot.py - Tests for WhatsApp bot functionality.
"""

import pytest
import os
import sys
import json
import shutil

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from whatsapp_bot import OpenGuyWhatsAppBot


class MockWhatsAppBot(OpenGuyWhatsAppBot):
    """Mock WhatsApp bot for testing without Twilio API calls."""
    
    def __init__(self):
        """Initialize mock bot without credentials."""
        self.account_sid = "test_account"
        self.auth_token = "test_token"
        self.twilio_phone = "whatsapp:+1234567890"
        self.executor = None
        self.user_sessions = {}
        
        # Import managers and exceptions
        from notes_manager import NoteManager
        self.notes = NoteManager(notes_dir="test_robot_notes")
        
        # Rate limiting settings
        self.rate_limit = (10, 60)
        
        # Safety settings
        self.max_distance_cm = 200
        self.max_angle_deg = 360
        self.require_confirmation = False
        
        # Create executor
        from hybrid_sim import HybridExecutor
        self.executor = HybridExecutor(try_hardware=False)
        
        self.sent_messages = []
        self.sent_media = []
    
    def send_message(self, phone_number: str, text: str) -> bool:
        """Mock send_message that records calls."""
        self.sent_messages.append({
            "phone_number": phone_number,
            "text": text
        })
        return True
    
    def send_media(self, phone_number: str, media_url: str, caption: str = "") -> bool:
        """Mock send_media that records calls."""
        self.sent_media.append({
            "phone_number": phone_number,
            "media_url": media_url,
            "caption": caption
        })
        return True


class TestWhatsAppBot:
    """Test suite for WhatsApp bot."""
    
    @pytest.fixture
    def bot(self):
        """Create mock bot for testing."""
        bot = MockWhatsAppBot()
        yield bot
        # Cleanup test notes directory
        if os.path.exists("test_robot_notes"):
            shutil.rmtree("test_robot_notes")
    
    def test_bot_initialization(self, bot):
        """Bot should initialize correctly."""
        assert bot is not None
        assert bot.executor is not None
        assert bot.account_sid == "test_account"
    
    def test_handle_start_command(self, bot):
        """Should handle /start command."""
        message = {
            "From": "whatsapp:+9876543210",
            "Body": "/start",
            "MessageSid": "test123"
        }
        response = bot.handle_message(message)
        assert "Welcome to OpenGuy" in response
        assert "natural language" in response
    
    def test_handle_help_command(self, bot):
        """Should handle /help command."""
        message = {
            "From": "whatsapp:+9876543210",
            "Body": "/help",
            "MessageSid": "test123"
        }
        response = bot.handle_message(message)
        assert "Commands" in response
        assert "move" in response.lower()
    
    def test_handle_status_command(self, bot):
        """Should handle /status command."""
        message = {
            "From": "whatsapp:+9876543210",
            "Body": "/status",
            "MessageSid": "test123"
        }
        response = bot.handle_message(message)
        assert "Status" in response
        assert "Position" in response
    
    def test_handle_mode_command(self, bot):
        """Should handle /mode command."""
        message = {
            "From": "whatsapp:+9876543210",
            "Body": "/mode",
            "MessageSid": "test123"
        }
        response = bot.handle_message(message)
        assert "MODE" in response
        assert "SIMULATOR" in response or "HARDWARE" in response
    
    def test_handle_stop_command(self, bot):
        """Should handle /stop command."""
        message = {
            "From": "whatsapp:+9876543210",
            "Body": "/stop",
            "MessageSid": "test123"
        }
        response = bot.handle_message(message)
        assert "stopped" in response.lower() or "no active" in response.lower()
    
    def test_handle_unknown_command(self, bot):
        """Should handle unknown commands."""
        message = {
            "From": "whatsapp:+9876543210",
            "Body": "/unknown",
            "MessageSid": "test123"
        }
        response = bot.handle_message(message)
        assert "Unknown command" in response
    
    def test_handle_start_variations(self, bot):
        """Should handle start command variations."""
        for start_text in ["/start", "start", "hello", "hi"]:
            message = {
                "From": "whatsapp:+9876543210",
                "Body": start_text,
                "MessageSid": "test123"
            }
            response = bot.handle_message(message)
            assert "Welcome" in response or "welcome" in response.lower()
    
    def test_handle_move_command(self, bot):
        """Should handle move commands."""
        message = {
            "From": "whatsapp:+9876543210",
            "Body": "move forward 10 cm",
            "MessageSid": "test123"
        }
        response = bot.handle_message(message)
        assert response is not None
        assert "move" in response.lower() or "action" in response.lower()
    
    def test_handle_rotate_command(self, bot):
        """Should handle rotate commands."""
        message = {
            "From": "whatsapp:+9876543210",
            "Body": "rotate right 45 degrees",
            "MessageSid": "test123"
        }
        response = bot.handle_message(message)
        assert response is not None
        assert "rotate" in response.lower() or "action" in response.lower()
    
    def test_handle_grab_command(self, bot):
        """Should handle grab commands."""
        message = {
            "From": "whatsapp:+9876543210",
            "Body": "grab the object",
            "MessageSid": "test123"
        }
        response = bot.handle_message(message)
        assert response is not None
        assert "grab" in response.lower() or "gripper" in response.lower()
    
    def test_confidence_scoring(self, bot):
        """Response should include confidence scoring."""
        message = {
            "From": "whatsapp:+9876543210",
            "Body": "move forward 10 cm",
            "MessageSid": "test123"
        }
        response = bot.handle_message(message)
        assert "Confidence" in response
    
    def test_user_session_tracking(self, bot):
        """Bot should track user sessions."""
        phone = "whatsapp:+9876543210"
        message = {
            "From": phone,
            "Body": "move forward",
            "MessageSid": "test123"
        }
        
        bot.handle_message(message)
        
        # Check session was created
        assert phone.replace("whatsapp:", "") in bot.user_sessions
        session = bot.user_sessions[phone.replace("whatsapp:", "")]
        assert session['commands_executed'] == 1
    
    def test_send_message_recorded(self, bot):
        """Mock bot should record sent messages."""
        bot.send_message("+9876543210", "test message")
        assert len(bot.sent_messages) == 1
        assert bot.sent_messages[0]["text"] == "test message"
    
    def test_send_media_recorded(self, bot):
        """Mock bot should record sent media."""
        bot.send_media("+9876543210", "https://example.com/image.jpg", "Image caption")
        assert len(bot.sent_media) == 1
        assert bot.sent_media[0]["media_url"] == "https://example.com/image.jpg"
    
    def test_multi_command_sequence(self, bot):
        """Should handle multiple commands from same user."""
        phone = "whatsapp:+9876543210"
        
        # First command
        msg1 = {"From": phone, "Body": "move forward", "MessageSid": "test1"}
        response1 = bot.handle_message(msg1)
        
        # Second command
        msg2 = {"From": phone, "Body": "rotate right", "MessageSid": "test2"}
        response2 = bot.handle_message(msg2)
        
        # Check session tracks both
        session = bot.user_sessions[phone.replace("whatsapp:", "")]
        assert session['commands_executed'] == 2
    
    def test_invalid_command(self, bot):
        """Should handle invalid/unclear commands."""
        message = {
            "From": "whatsapp:+9876543210",
            "Body": "xyzabc nonsense gibberish",
            "MessageSid": "test123"
        }
        response = bot.handle_message(message)
        assert "couldn't understand" in response.lower() or "try" in response.lower()
    
    def test_phone_format_handling(self, bot):
        """Should handle various phone formats."""
        # With "whatsapp:" prefix
        msg1 = {
            "From": "whatsapp:+1234567890",
            "Body": "move forward",
            "MessageSid": "test1"
        }
        response1 = bot.handle_message(msg1)
        assert response1 is not None
        
        # Session should be stored without "whatsapp:" prefix
        assert "1234567890" in bot.user_sessions or "+1234567890" in [s for s in bot.user_sessions]
