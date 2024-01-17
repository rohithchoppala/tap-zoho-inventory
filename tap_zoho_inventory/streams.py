"""Stream type classes for tap-ZohoInventory."""

from __future__ import annotations

from pathlib import Path

from pendulum import parse
from tap_zoho_inventory.client import ZohoInventoryStream

from singer_sdk.helpers.jsonpath import extract_jsonpath


SCHEMAS_DIR = Path(__file__).parent / Path("./schemas")

class ProductsStream(ZohoInventoryStream):

    name = "products"
    path = "/items"
    records_jsonpath = "$.item[*]"
    replication_key = "last_modified_time"
    schema_filepath = SCHEMAS_DIR / "items_indv_schema.json"
    custom_fields_key = "item"

    def get_child_context(self, record, context):
        """Return a child context object for a given record."""
        return {
            "item_id": record["item_id"],
        }


class PurchaseOrders(ZohoInventoryStream):

    name = "purchase_orders"
    path = "/purchaseorders"
    replication_key = "last_modified_time"
    records_jsonpath = "$.purchaseorder[*]"
    custom_fields_key = "purchaseorder"

    schema_filepath = SCHEMAS_DIR / "purchaseorders_indv_schema.json"

    def get_child_context(self, record, context):
        """Return a child context object for a given record."""
        return {
            "purchaseorder_id": record["purchaseorder_id"],
        }


class SalesOrdersStream(ZohoInventoryStream):

    name = "sales_orders"
    path = "/salesorders"
    records_jsonpath = "$.salesorder"
    replication_key = "last_modified_time"
    custom_fields_key = "salesorder"

    schema_filepath = SCHEMAS_DIR / "salesorders_indv_schema.json"
    # Optionally, you may also use `schema_filepath` in place of `schema`:
    # schema_filepath = SCHEMAS_DIR / "users.json"  # noqa: ERA001

    def get_child_context(self, record, context):
        """Return a child context object for a given record."""
        return {
            "salesorder_id": record["salesorder_id"],
        }


class SuppliersStream(ZohoInventoryStream):
    name = "contacts"
    path = "/vendors"
    records_jsonpath = "$.contact[*]"
    schema_filepath = SCHEMAS_DIR / "contacts_indv_schema.json"
    replication_key = "last_modified_time"


class SalesOrderDetailsStream(ZohoInventoryStream):
    name = "sales_orders_details"
    path = "/salesorders/{salesorder_id}"
    parent_stream_type = SalesOrdersStream
    records_jsonpath = "$.salesorder[*]"
    schema_filepath = SCHEMAS_DIR / "salesorders_details_indv_schema.json"
    custom_fields_key = "salesorder"

    def parse_response(self, response):
        for record in extract_jsonpath(self.records_jsonpath, input=response.json()):
            record = self.move_custom_fields_to_root(record)
            yield record


class PurchaseOrderDetailStream(ZohoInventoryStream):
    name = "purchase_orders_details"
    path = "/purchaseorders/{purchaseorder_id}"
    parent_stream_type = PurchaseOrders
    records_jsonpath = "$.purchaseorder[*]"
    schema_filepath = SCHEMAS_DIR / "purchaseorders_details_indv_schema.json"
    custom_fields_key = "purchaseorder"

    def parse_response(self, response):
        for record in extract_jsonpath(self.records_jsonpath, input=response.json()):
            record = self.move_custom_fields_to_root(record)
            yield record


class ProductDetailsStream(ZohoInventoryStream):
    name = "product_details"
    path = "/items/{item_id}"
    parent_stream_type = ProductsStream
    records_jsonpath = "$.item[*]"
    schema_filepath = SCHEMAS_DIR / "product_details_indv_schema.json"
    custom_fields_key = "item"

    def parse_response(self, response):
        for record in extract_jsonpath(self.records_jsonpath, input=response.json()):
            record = self.move_custom_fields_to_root(record)
            yield record


class PurchaseReceivesStream(ZohoInventoryStream):
    name = "purchase_receives"
    path = "/purchasereceives"
    records_jsonpath = "$.purchasereceives[*]"
    schema_filepath = SCHEMAS_DIR / "purchase_receives_schema.json"
    replication_key = "last_modified_time"
    has_lines = False
    custom_fields_key = "purchase_receive"

    def post_process(self, row, context):
        row_last_mod_time = parse(row["last_modified_time"])
        if row_last_mod_time > self.get_starting_time(context):
            return super().post_process(row, context)

        return None

    def get_child_context(self, record, context):
        """Return a child context object for a given record."""
        return {
            "purchasereceive_id": record["purchasereceive_id"],
        }


class PurchaseReceivesDetailStream(ZohoInventoryStream):
    name = "purchasereceives_details"
    path = "/purchasereceives/{purchasereceive_id}"
    parent_stream_type = PurchaseReceivesStream
    records_jsonpath = "$.purchasereceive[*]"
    schema_filepath = SCHEMAS_DIR / "purchasereceives_details_indv_schema.json"
    custom_fields_key = "purchase_receive"

    def parse_response(self, response):
        for record in extract_jsonpath(self.records_jsonpath, input=response.json()):
            record = self.move_custom_fields_to_root(record)
            yield record
