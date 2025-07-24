"""Main entry point for DevPulse client CLI app."""

from devpulse_client.cli.commands import app


def main() -> None:
    """Run the DevPulse CLI app."""
    app()


if __name__ == "__main__":
    main()
