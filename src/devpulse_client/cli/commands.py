"""Command-line interface for DevPulse client.

This module provides CLI commands for enrollment and running the client.
"""

from __future__ import annotations

import typer
from loguru import logger

from ..app.app import DevPulseClient
from ..logger.logger_setup import setup_logging

app = typer.Typer(help="DevPulse Client CLI App")


@app.command()
def enroll(
    server: str = typer.Option("http://localhost:8000", help="DevPulse server URL"),
    username: str = typer.Option(..., help="Username for enrollment"),
    password: str = typer.Option(..., help="Password for enrollment"),
    user_email: str = typer.Option(..., help="User email for enrollment"),
):
    """Enroll this device using MAC address."""
    setup_logging()

    client = DevPulseClient(server)
    if client.signup(username=username, password=password, user_email=user_email):
        logger.info("✅ Enrollment completed successfully!")
        logger.info("You can now run the client with: devpulse-client run")
        typer.Exit(code=0)
    else:
        logger.error("❌ Enrollment failed!")
        typer.Exit(code=1)


@app.command()
def run(
    server: str = typer.Option("http://localhost:8000", help="DevPulse server URL"),
    username: str = typer.Option(..., help="Username for login"),
    password: str = typer.Option(..., help="Password for login"),
):
    """Run the DevPulse client."""
    setup_logging()

    client = DevPulseClient(server)
    client.start(username, password)