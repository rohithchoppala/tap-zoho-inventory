"""Stream type classes for tap-ZohoInventory."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable

import requests

from tap_zoho_inventory.client import ZohoInventoryStream

from singer_sdk import typing as th  # JSON Schema typing helpers
from singer_sdk.helpers.jsonpath import extract_jsonpath


# TODO: Delete this is if not using json files for schema definition
SCHEMAS_DIR = Path(__file__).parent / Path("./schemas")
# TODO: - Override `UsersStream` and `GroupsStream` with your own stream definition.
#       - Copy-paste as many times as needed to create multiple stream types.


class ProductsStream(ZohoInventoryStream):
    """Define custom stream."""

    name = "items"
    path = "/items"
    records_jsonpath = "$.item[*]"

    schema_filepath = SCHEMAS_DIR / "items_indv_schema.json"

    def get_child_context(self, record, context):
        """Return a child context object for a given record."""
        return {
            "item_id": record["item_id"],
        }


class PurchaseOrders(ZohoInventoryStream):
    """Define custom stream."""

    name = "purchaseorders"
    path = "/purchaseorders"
    records_jsonpath = "$.purchaseorder[*]"

    schema_filepath = SCHEMAS_DIR / "purchaseorders_indv_schema.json"

    def get_child_context(self, record, context):
        """Return a child context object for a given record."""
        return {
            "purchaseorder_id": record["purchaseorder_id"],
        }


class SalesOrdersStream(ZohoInventoryStream):
    """Define custom stream."""

    name = "salesorders"
    path = "/salesorders"
    records_jsonpath = "$.salesorder"

    schema_filepath = SCHEMAS_DIR / "salesorders_indv_schema.json"
    # Optionally, you may also use `schema_filepath` in place of `schema`:
    # schema_filepath = SCHEMAS_DIR / "users.json"  # noqa: ERA001

    def get_child_context(self, record, context):
        """Return a child context object for a given record."""
        return {
            "salesorder_id": record["salesorder_id"],
        }


class SuppliersStream(ZohoInventoryStream):
    """Define custom stream."""
    name = "contacts"
    path = "/vendors"
    records_jsonpath = "$.contact[*]"
    schema_filepath = SCHEMAS_DIR / "contacts_indv_schema.json"


class SalesOrderDetailsStream(ZohoInventoryStream):
    name = "salesorder"
    path = "/salesorders/{salesorder_id}"
    parent_stream_type = SalesOrdersStream
    records_jsonpath = "$.salesorder[*]"
    schema_filepath = SCHEMAS_DIR / "salesorders_details_indv_schema.json"

    def parse_response(self, response):
        yield from extract_jsonpath(self.records_jsonpath, input=response.json())


class PurchaseOrderDetailStream(ZohoInventoryStream):
    name = "purchaseorder"
    path = "/purchaseorders/{purchaseorder_id}"
    parent_stream_type = PurchaseOrders
    records_jsonpath = "$.purchaseorder[*]"
    schema_filepath = SCHEMAS_DIR / "purchaseorders_details_indv_schema.json"

    def parse_response(self, response):
        yield from extract_jsonpath(self.records_jsonpath, input=response.json())


class ProductDetailsStream(ZohoInventoryStream):
    name = "product"
    path = "/items/{item_id}"
    parent_stream_type = ProductsStream
    records_jsonpath = "$.item[*]"
    schema_filepath = SCHEMAS_DIR / "product_details_indv_schema.json"

    def parse_response(self, response):
        yield from extract_jsonpath(self.records_jsonpath, input=response.json())

