"""Stream type classes for tap-ZohoInventory."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, Dict, Any, Optional

from pendulum import parse
from tap_zoho_inventory.client import ZohoInventoryStream

from singer_sdk.helpers.jsonpath import extract_jsonpath


SCHEMAS_DIR = Path(__file__).parent / Path("./schemas")

class ProductsStream(ZohoInventoryStream):

    name = "products"
    path = "/items"
    records_jsonpath = "$.items[*]"
    replication_key = "last_modified_time"
    schema_filepath = SCHEMAS_DIR / "items_indv_schema.json"
    custom_fields_key = "item"
    has_lines = False

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

class CompositeItemsStream(ZohoInventoryStream):
    name = "composite_items"
    path = "/compositeitems"
    records_jsonpath = "$.composite_items[*]"
    replication_key = "last_modified_time"
    schema_filepath = SCHEMAS_DIR / "composite_items_schema.json"
    custom_fields_key = "composite_item"
    has_lines = False

    def get_child_context(self, record, context):
        """Return a child context object for a given record."""
        return {
            "composite_item_id": record["composite_item_id"],
        }
class CompositeItemsDetailsStream(ZohoInventoryStream):
     name = "composite_items_details"
     path = "/compositeitems/{composite_item_id}"
     parent_stream_type = CompositeItemsStream
     records_jsonpath = "$.composite_item[*]"
     schema_filepath = SCHEMAS_DIR / "composite_items_indv_schema.json"
     custom_fields_key = "composite_item"

     def parse_response(self, response):
         for record in extract_jsonpath(self.records_jsonpath, input=response.json()):
             record = self.move_custom_fields_to_root(record)
             yield record    


class AssemblyOrdersStream(ZohoInventoryStream):
    name = "assembly_orders"
    path = "/bundles"
    records_jsonpath = "$.bundles[*]"
    replication_key = "last_modified_time"
    schema_filepath = SCHEMAS_DIR / "assembly_orders_schema.json"
    custom_fields_key = "bundle"
    has_lines = False
    
    def get_records(self, context: Optional[dict]) -> Iterable[Dict[str, Any]]:
        """Get records from the API."""
        sync_assembly_orders = self.config.get("sync_assembly_orders",True)
        if not sync_assembly_orders:
            self.logger.info("Assembly orders sync is disabled in config. Skipping sync.")
            return []

        return super().get_records(context)
    
    def get_child_context(self, record, context):
        """Return a child context object for a given record."""
        return {
            "bundle_id": record["bundle_id"],
        }


class AssemblyOrdersDetailsStream(ZohoInventoryStream):
    name = "assembly_orders_details"
    path = "/bundles/{bundle_id}"
    parent_stream_type = AssemblyOrdersStream
    records_jsonpath = "$.bundle[*]"
    schema_filepath = SCHEMAS_DIR / "assembly_orders_details_schema.json"
    custom_fields_key = "bundle"
    def parse_response(self, response):
        for record in extract_jsonpath(self.records_jsonpath, input=response.json()):
            record = self.move_custom_fields_to_root(record)
            yield record    
