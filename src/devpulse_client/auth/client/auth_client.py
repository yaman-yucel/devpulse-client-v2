"""Enrollment client for DevPulse server communication."""

from __future__ import annotations

import platform
import socket

import httpx
from loguru import logger

from ..collectors import DeviceFingerprintCollector
from ..models.enrollment_models import LoginRequest, SignupRequest


class AuthClient:
    """Client for enrolling and authenticating devices with the DevPulse server."""

    def __init__(
        self,
        server_url: str,
        timeout_seconds: int = 30,
    ):
        self.server_url = server_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self.signup_endpoint = "/api/credentials/signup"
        self.token_endpoint = "/api/credentials/token"
        self._fingerprint_collector = DeviceFingerprintCollector()
        self.headers = {
            "Content-Type": "application/json",
            "User-Agent": "DevPulse-Client/2.0.0",
        }

    def signup(self, username: str, password: str, user_email: str, hostname: str | None = None, platform_name: str | None = None) -> bool:
        # Auto-detect system information if not provided
        if hostname is None:
            hostname = socket.gethostname()

        if platform_name is None:
            platform_name = self._detect_platform()
        logger.info("OKEY")
        device_fingerprint = self._fingerprint_collector.collect_fingerprint()
        if device_fingerprint is None:
            logger.error("Failed to collect device fingerprint")
            return False

        request = SignupRequest(
            username=username,
            user_email=user_email,
            password=password,
            hostname=hostname,
            platform=platform_name,
            device_fingerprint=device_fingerprint,  # holds mac, and other optional fields, mac is used for server side verification
        )

        logger.info(f"Enrolling device: {hostname} ({platform_name}) for user: {username}")

        response = self._send_signup_request(request)

        return response

    def _send_signup_request(self, request: SignupRequest) -> bool:
        try:
            full_url = f"{self.server_url}{self.signup_endpoint}"
            payload = request.model_dump()
            with httpx.Client(timeout=10.0) as client:
                response = client.post(full_url, json=payload, headers=self.headers)
                if response.status_code == 200:
                    response_data = response.json()
                    return response_data["status"]
                else:
                    return False
        except httpx.HTTPStatusError:
            return False
        except httpx.RequestError:
            return False
        except Exception:
            return False

    def _detect_platform(self) -> str:
        """Detect the current platform."""
        system = platform.system().lower()

        # Map Python platform names to DevPulse platform names
        platform_mapping = {
            "linux": "linux",
            "darwin": "macos",
            "windows": "windows",
        }

        return platform_mapping.get(system, system)

    def test_connectivity(self) -> tuple[bool, str]:
        """Test connectivity to the enrollment server.

        Returns:
            Tuple of (success, message)
        """
        try:
            # Try to connect to the base URL
            url = f"{self.server_url}/health"  # Assume there's a health endpoint
            with httpx.Client(timeout=10.0) as client:
                response = client.get(url, headers=self.headers)
                if response.status_code == 200:
                    return True, "Server connectivity OK"
                else:
                    return False, f"Server returned HTTP {response.status_code}"

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                # Health endpoint might not exist, but server is reachable
                return True, "Server reachable (health endpoint not found)"
            else:
                return False, f"HTTP error: {e.response.status_code} {e.response.reason_phrase}"

        except httpx.RequestError as e:
            return False, f"Network error: {e}"

        except Exception as e:
            return False, f"Connectivity test failed: {e}"

    def login(self, username: str, password: str) -> tuple[bool, str | None]:
        """Validate credentials for a device."""
        try:
            device_fingerprint = self._fingerprint_collector.collect_fingerprint(mac_only=True)
            login_request = LoginRequest(username=username, password=password, mac_address=device_fingerprint.mac_address, never_expires=True)
            success, access_token = self._send_login_request(login_request)
            return success, access_token
        except Exception as e:
            logger.error(f"Credential validation error: {e}")
            return False, None

    def _send_login_request(self, login_request: LoginRequest) -> tuple[bool, str | None]:
        """Send credentials to the server for validation and return (is_valid, message)."""
        try:
            full_url = f"{self.server_url}{self.token_endpoint}"
            payload = login_request.model_dump()
            with httpx.Client(timeout=10.0) as client:
                response = client.post(full_url, json=payload, headers=self.headers)
                if response.status_code == 200:
                    logger.info(f"Credential validation successful: {response.json()}")
                    return True, response.json()["access_token"]
                else:
                    logger.error(f"Credential validation failed: {response.json()}")
                    return False, None
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e.response.status_code} {e.response.reason_phrase}")
            raise e
        except httpx.RequestError as e:
            logger.error(f"Network error: {e}")
            raise e
        except Exception as e:
            logger.error(f"Credential validation error: {e}")
            raise e
