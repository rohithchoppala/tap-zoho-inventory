"""zoho-inventory tap class."""

from __future__ import annotations

from singer_sdk import Tap
from singer_sdk import typing as th  # JSON schema typing helpers

# TODO: Import your custom stream types here:
from tap_zoho_inventory import streams
import inspect


class TapZohoInventory(Tap):
    """ZohoInventory tap class."""

    name = "tap-ZohoInventory"

    # TODO: Update this section with the actual config values you expect:
    config_jsonschema = th.PropertiesList(
        th.Property(
            "client_id",
            th.StringType,
            required=True,
            secret=True,  # Flag config as protected.
            description="The token to authenticate against the API service",
        ),
        th.Property(
            "client_secret",
            th.StringType,
            required=True,
            description="Project IDs to replicate",
        ),
        th.Property(
            "access_token",
            th.StringType,
            description="The earliest record date to sync",
        ),
        th.Property(
            "refresh_token",
            th.StringType,
            description="The url for the API service",
            required=True
        ),
    ).to_dict()

    def discover_streams(self) -> list[streams.ZohoInventoryStream]:
        """Return a list of discovered streams.

        Returns:
            A list of discovered streams.
        """
        return [
           cls(self) for name, cls in inspect.getmembers(streams, inspect.isclass) if cls.__module__ == 'tap_zoho_inventory.streams'
        ]



if __name__ == "__main__":
    TapZohoInventory.cli()
