"""Stream type classes for tap-ZohoInventory."""

from __future__ import annotations

from pathlib import Path

from singer_sdk import typing as th  # JSON Schema typing helpers

from tap_zoho_inventory.client import ZohoInventoryStream

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


class PurchaseOrders(ZohoInventoryStream):
    """Define custom stream."""

    name = "purchaseorders"
    path = "/purchaseorders"
    records_jsonpath = "$.purchaseorder[*]"

    schema_filepath = SCHEMAS_DIR / "purchaseorders_indv_schema.json"



class SalesOrdersStream(ZohoInventoryStream):
    """Define custom stream."""

    name = "salesorders"
    path = "/salesorders"
    records_jsonpath = "$.salesorder"

    schema_filepath = SCHEMAS_DIR / "salesorders_indv_schema.json"
    # Optionally, you may also use `schema_filepath` in place of `schema`:
    # schema_filepath = SCHEMAS_DIR / "users.json"  # noqa: ERA001


class SuppliersStream(ZohoInventoryStream):
    """Define custom stream."""

    name = "contacts"
    
    path = "/vendors"
    records_jsonpath = "$.contact"
    
    schema_filepath = SCHEMAS_DIR / "contacts_indv_schema.json"