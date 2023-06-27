"""Tests standard tap features using the built-in SDK tests library."""

import datetime

from singer_sdk.testing import get_tap_test_class

from tap_zoho_inventory.tap import Tapzoho-inventory

SAMPLE_CONFIG = {
    "start_date": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d"),
    # TODO: Initialize minimal tap config
}


# Run standard built-in tap tests from the SDK:
TestTapzoho-inventory = get_tap_test_class(
    tap_class=Tapzoho-inventory,
    config=SAMPLE_CONFIG,
)


# TODO: Create additional tests as appropriate for your tap.
