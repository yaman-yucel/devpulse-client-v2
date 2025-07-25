"""Clean DevPulse application with simplified credential management.

This is the DevPulse client that integrates:
- Simple MAC address-based device enrollment and validation
- Dynamic configuration from server
- Clean tracking components
- Event pipeline architecture
"""

from __future__ import annotations

import signal
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

from loguru import logger

from ..auth.client.auth_client import AuthClient

from devpulse_client.config.tracker_config import tracker_settings
from devpulse_client.core import ActivityStateTask, HeartbeatTask, ScreenshotCapturer, WindowTrackerTask
from devpulse_client.queue.event_store import EventStore
from devpulse_client.tables.activity_table import ActivityEventType
# from .events import ActivityEventType
# from .trackers import ActivityTracker, HeartbeatTracker, ScreenshotTracker, WindowTracker

class ActivityTracker:
    """Tracks idle/lock state and captures screenshots, persisting everything to Postgres."""

    SUPPORTED_SYSTEMS: set[str] = {"windows", "darwin", "linux"}

    def __init__(self) -> None:
        self.screenshot_dir = tracker_settings.screenshot_dir
        self.event_store = EventStore()
        self.capturer = ScreenshotCapturer(self.screenshot_dir)
        self.tasks: list = [
            HeartbeatTask(interval=tracker_settings.HEARTBEAT_EVERY),
            WindowTrackerTask(interval=tracker_settings.WINDOW_EVENT_INTERVAL),
            ActivityStateTask(),
        ]

    def run(self) -> None:
        """Main synchronous loop orchestrating all tracking operations."""
        logger.info("Starting activity tracker")

        # Abort early if the platform isn't supported
        if tracker_settings.system not in self.SUPPORTED_SYSTEMS:
            logger.error(f"Unsupported system: {tracker_settings.system}")
            return

        # Log the start of the activity tracker
        start_time = time.time()
        status = ActivityEventType.STARTED.value
        logger.info(f"Logging activity: {status}")
        self.event_store.log_activity(status, timestamp=datetime.fromtimestamp(start_time))
        
        
        
        try:
            while True:
                now = time.time()
                for t in self.tasks:
                    t.tick(now)
                time.sleep(0.1)  # Prevent high CPU usage
                
            
        finally:
            # Log the stop of the activity tracker
            stop_time = time.time()
            status = ActivityEventType.STOPPED.value
            logger.info(f"Logging activity: {status}")
            self.event_store.log_activity(status, timestamp=datetime.fromtimestamp(stop_time))




class DevPulseClient:
    """Clean DevPulse client with simplified credential management."""

    def __init__(
        self,
        server_url: str,
        # config_dir: Optional[Path] = None,
    ):
        """Initialize DevPulse client.

        Args:
            server_url: URL of the DevPulse server
            config_dir: Directory for configuration files
        """
        self.server_url = server_url
        self.signal_received = False
        self.auth_client = AuthClient(server_url=server_url)
        self.access_token = None
        # self.config_manager = get_config_manager()

        # Initialize components (will be set up after enrollment/config)
        # self.config: Optional[DevPulseConfig] = None

        # self.trackers: list = []

        # Set up signal handling
        # self._setup_signal_handling()

        logger.info(f"Initialized DevPulse client for server: {server_url}")

    def signup(
        self,
        username: str,
        password: str,
        user_email: str,
    ) -> bool:
        logger.info(f"Starting enrollment for user: {username}")

        success = self.auth_client.signup(username, password, user_email)

        if success:
            logger.info("✅ Enrollment successful")
            return True
        else:
            logger.error("❌ Enrollment failed")
            return False

    def start(self, username: str, password: str) -> bool:
        """Start the DevPulse client.

        Returns:
            True if started successfully, False otherwise
        """

        # Validate credentials with server
        logger.info("Validating credentials with server...")
        success, access_token = self.auth_client.login(username, password)
        if not success:
            logger.error(f"❌ {access_token}")
            return False
        self.access_token = access_token

        logger.info("✅ Access token recieved.")

        # Start pipeline
        # if not self.pipeline.start():
        #     logger.error("Failed to start event pipeline")
        #     return False

        #     # Initialize tracking components
        #     self._initialize_trackers()

        #     logger.info("DevPulse client started successfully")
        #     return True
        return True
        # except Exception as e:
        #     logger.error(f"Failed to start client: {e}")
        #     return False

    #     def run(self) -> bool:
    #         """Run the main tracking loop.

    #         Returns:
    #             True if completed successfully, False if errors occurred
    #         """
    #         if not self.config or not self.pipeline:
    #             logger.error("Client not properly initialized. Call start() first.")
    #             return False

    #         logger.info("Starting main tracking loop...")

    #         try:
    #             # Initialize trackers
    #             for tracker in self.trackers:
    #                 if hasattr(tracker, "initialize"):
    #                     tracker.initialize()

    #             # Main loop
    #             while True:
    #                 # Run all trackers
    #                 for tracker in self.trackers:
    #                     try:
    #                         tracker.tick()
    #                     except Exception as e:
    #                         logger.error(f"Error in tracker {type(tracker).__name__}: {e}")

    #                 # Sleep for the configured delay
    #                 if self.config.tracker.system_run_delay > 0:
    #                     time.sleep(self.config.tracker.system_run_delay)

    # except KeyboardInterrupt:
    #     logger.info("Received keyboard interrupt")
    #     return True
    # except Exception as e:
    #     logger.error(f"Error in main loop: {e}")
    #     return False
    # finally:
    #     self._shutdown()
    #     return True

    #     def stop(self) -> None:
    #         """Stop the DevPulse client gracefully."""
    #         logger.info("Stopping DevPulse client...")
    #         self._shutdown()

    #     def get_status(self) -> dict:
    #         """Get client status information.

    #         Returns:
    #             Dictionary with status information
    #         """
    #         status = {
    #             "enrolled": self.credential_manager.is_enrolled(),
    #             "running": self.pipeline is not None and self.pipeline._running if self.pipeline else False,
    #             "server_url": self.server_url,
    #         }

    #         # Add device information if enrolled
    #         if status["enrolled"]:
    #             device_id, user_id = self.credential_manager.get_device_info()
    #             status.update(
    #                 {
    #                     "device_id": device_id,
    #                     "user_id": user_id,
    #                 }
    #             )

    #         # Add pipeline stats if running
    #         if self.pipeline:
    #             status["pipeline_stats"] = self.pipeline.get_pipeline_stats()

    #         return status

    #     def force_sync(self) -> bool:
    #         """Force synchronization of pending events.

    #         Returns:
    #             True if successful, False otherwise
    #         """
    #         if self.pipeline:
    #             return self.pipeline.force_batch_send()
    #         return False

    #     def _create_pipeline_config(self) -> PipelineConfig:
    #         """Create pipeline configuration from current config."""
    #         if not self.config:
    #             raise RuntimeError("No configuration loaded")

    #         return PipelineConfig(
    #             client_id=self.config.client_id,
    #             username=self.config.username,
    #             api_base_url=self.config.server_url,
    #             api_key=self.config.api_key,
    #             queue_config=self.config.get_queue_config(),
    #             wal_config=self.config.get_wal_config(),
    #             batcher_config=self.config.get_batcher_config(),
    #             sender_config=self.config.get_sender_config(),
    #             stats_report_interval=self.config.pipeline.stats_report_interval,
    #         )

    # def _initialize_trackers(self) -> None:
    #     """Initialize tracking components."""
    #     # if not self.config or not self.pipeline:
    #     #     raise RuntimeError("Configuration or pipeline not available")

    #     # Get event producer for trackers
    #     event_producer = self.pipeline.get_producer("trackers")

    #     # Create tracking components
    #     self.trackers = [
    #         HeartbeatTracker(event_producer=event_producer),
    #         ActivityTracker(event_producer=event_producer),
    #         WindowTracker(event_producer=event_producer),
    #         ScreenshotTracker(event_producer=event_producer),
    #     ]

    #     logger.info(f"Initialized {len(self.trackers)} tracking components")

    def _setup_signal_handling(self) -> None:
        """Set up signal handlers for graceful shutdown."""

        def signal_handler(signum, frame):
            if self.signal_received:
                logger.warning("Signal already received, ignoring additional signal")
                return
            self.signal_received = True
            signal_name = signal.Signals(signum).name
            logger.info(f"Received {signal_name} signal, shutting down...")
            self._shutdown()
            sys.exit(0)

        # Register signal handlers
        if hasattr(signal, "SIGINT"):
            signal.signal(signal.SIGINT, signal_handler)
        if hasattr(signal, "SIGTERM"):
            signal.signal(signal.SIGTERM, signal_handler)
        # Windows-specific
        if hasattr(signal, "SIGBREAK"):
            signal.signal(signal.SIGBREAK, signal_handler)

    def _shutdown(self) -> None:
        """Perform graceful shutdown."""
        logger.info("Performing graceful shutdown...")

        try:
            # Shutdown trackers
            for tracker in self.trackers:
                if hasattr(tracker, "shutdown"):
                    try:
                        tracker.shutdown()
                    except Exception as e:
                        logger.error(f"Error shutting down tracker: {e}")

            # Shutdown pipeline
            if self.pipeline:
                self.pipeline.stop()

            logger.info("Shutdown complete")

        except Exception as e:
            logger.error(f"Error during shutdown: {e}")


# def create_devpulse_client(server_url: str, **kwargs) -> DevPulseClient:
#     """Create a DevPulse client with default configuration.

#     Args:
#         server_url: URL of the DevPulse server
#         **kwargs: Additional arguments for DevPulseClient

#     Returns:
#         Configured DevPulse client
#     """
#     return DevPulseClient(server_url=server_url, **kwargs)
