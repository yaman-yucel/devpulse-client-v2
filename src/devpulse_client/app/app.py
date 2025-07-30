from __future__ import annotations
from loguru import logger
from ..auth.client.auth_client import AuthClient
from ..ingest.client.event_client import ActivityTracker
from ..core.signal_handler.signal_handler import SignalHandler


class DevPulseClient:
    
    def __init__(
        self,
        server_url: str,
    ):
        self.server_url = server_url
        self.signal_received = False
        self.auth_client = AuthClient(server_url=server_url)
        self.access_token = None
        self.tracker: ActivityTracker | None = None
        self.signal_handler : SignalHandler | None = None
       
    def signup(
        self,
        username: str,
        password: str,
        user_email: str,
    ) -> bool:
        return self.auth_client.signup(username, password, user_email)

    def start(self, username: str, password: str) -> None:
        success, access_token = self.auth_client.login(username, password)
        if not success:
            logger.error(f"❌ Login failed for user {username}")
            return
        
        self.access_token = access_token
        self.tracker = ActivityTracker(self.server_url, access_token)
        self.signal_handler = SignalHandler([self.tracker.send_events])
        
        
        try:
            self.tracker.run()
        except KeyboardInterrupt:
            logger.info("Received interrupt, shutting down")
        except Exception as e: 
            logger.error(f"Failed to run tracker: {e}")
            return

