"""REST client handling, including ZohoInventoryStream base class."""

from __future__ import annotations

import sys
import requests
import backoff
from datetime import timedelta
from time import sleep
from pathlib import Path
from pendulum import parse
from typing import Any, Callable, Iterable, cast

from singer_sdk.helpers.jsonpath import extract_jsonpath
from singer_sdk.pagination import BaseAPIPaginator  # noqa: TCH002
from singer_sdk.streams import RESTStream
from tap_zoho_inventory.auth import ZohoInventoryAuthenticator


if sys.version_info >= (3, 8):
    from functools import cached_property
else:
    from cached_property import cached_property

_Auth = Callable[[requests.PreparedRequest], requests.PreparedRequest]
SCHEMAS_DIR = Path(__file__).parent / Path("./schemas")


class ZohoInventoryStream(RESTStream):
    """ZohoInventory stream class."""

    @property
    def url_base(self) -> str:
        """Return the API URL root, configurable via tap settings."""
        account_server = self.config.get(
            "accounts-server", "https://accounts.zoho.com"
        )
        account_server = account_server.replace("accounts.", "inventory.")
        return f"{account_server}/api/v1"

    # Set this value or override `get_new_paginator`.
    next_page_token_jsonpath = "$.page_context.page"  # noqa: S105

    def get_next_page_token(self, response, previous_token: Any | None) -> Any | None:
        try:
            more_pages = response.json()['page_context']['has_more_page']
        except KeyError:
            return None

        if self.next_page_token_jsonpath and more_pages:
            all_matches = extract_jsonpath(
                self.next_page_token_jsonpath, response.json()
            )
            first_match = next(iter(all_matches), None)
            next_page_token = first_match
            return next_page_token + 1

        return None

    def backoff_wait_generator(self):
        return backoff.expo(base=3, factor=6)

    @cached_property
    def authenticator(self) -> _Auth:
        """Return a new authenticator object.

        Returns:
            An authenticator instance.
        """
        account_server = self.config.get(
            "accounts-server", "https://accounts.zoho.com"
        )
        auth_endpoint = f"{account_server}/oauth/v2/token"
        return ZohoInventoryAuthenticator.create_for_stream(self, auth_endpoint=auth_endpoint)

    @property
    def http_headers(self) -> dict:
        """Return the http headers needed.

        Returns:
            A dictionary of HTTP headers.
        """
        headers = {}
        if "user_agent" in self.config:
            headers["User-Agent"] = self.config.get("user_agent")

        return headers

    def get_starting_time(self, context):
        start_date = self.config.get("start_date")
        if start_date:
            start_date = parse(self.config.get("start_date"))
        rep_key = self.get_starting_timestamp(context)
        return rep_key or start_date

    def get_url_params(
        self,
        context: dict | None,  # noqa: ARG002
        next_page_token: Any | None,
    ) -> dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization.

        Args:
            context: The stream context.
            next_page_token: The next page index or value.

        Returns:
            A dictionary of URL query parameters.
        """
        params: dict = {}
        if self.config.get('organization_id'):
            params['organization_id'] = self.config.get('organization_id')
        if next_page_token:
            params["page"] = next_page_token
        if self.replication_key:
            params["sort"] = "asc"
            params["order_by"] = self.replication_key
            start_date = self.get_starting_time(context)
            start_date = start_date + timedelta(seconds=1)
            if start_date:
                params[self.replication_key] = start_date.strftime('%Y-%m-%dT%H:%M:%S%z')
        return params

    def prepare_request_payload(
        self,
        context: dict | None,  # noqa: ARG002
        next_page_token: Any | None,  # noqa: ARG002
    ) -> dict | None:
        """Prepare the data payload for the REST API request.

        By default, no payload will be sent (return None).

        Args:
            context: The stream context.
            next_page_token: The next page index or value.

        Returns:
            A dictionary with the JSON body for a POST requests.
        """
        # TODO: Delete this method if no payload is required. (Most REST APIs.)
        return None

    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        """Parse the response and return an iterator of result records.

        Args:
            response: The HTTP ``requests.Response`` object.

        Yields:
            Each record from the source.
        """
        decorated_request = self.request_decorator(self._request)
        res = response.json()
        lookup_name = res['page_context']['report_name'].lower().replace(' ', '')
        try:
            id_field = [x for x in res[lookup_name][0].keys() if x.endswith('_id')][0]
        except IndexError:
            self.logger.info(f'No id field found for {lookup_name}')
            self.logger.info(f"Got response: {res}")
            id_field = lookup_name if not lookup_name.endswith('s') else lookup_name[:-1]
            id_field = f'{id_field}_id'
            self.logger.info(f"Using {id_field} as id field")
        except KeyError:
            self.logger.info(f"Could not find {lookup_name} in response, falling back on url part")
            for key, value in response.json().items():
                if isinstance(value, list):
                    lookup_name = key
                    id_field = [x for x in value[0].keys() if x.endswith('_id')][0]
                    break

        if getattr(self, "has_lines", True):
            for record in response.json()[lookup_name]:
                sleep(1)
                try:
                    url = self.url_base + "/" + lookup_name + f"/{record[id_field]}"
                    response_obj = decorated_request(self.prepare_request_lines(url,{}), {})
                    detailed_record = list(extract_jsonpath(self.records_jsonpath, input=response_obj.json()))[0]
                    yield detailed_record
                except:
                    self.logger.info(f"Could not get lines for {self.name} with ID {record[id_field]}")
                    yield record
        else:
            yield from extract_jsonpath(self.records_jsonpath, input=response.json())


    def post_process(
        self,
        row: dict,
        context: dict | None = None,  # noqa: ARG002
    ) -> dict | None:
        """As needed, append or transform raw data to match expected structure.

        Args:
            row: An individual record from the stream.
            context: The stream context.

        Returns:
            The updated record dictionary, or ``None`` to skip the record.
        """
        self.replace_value(row,'',None)
        return row

    def replace_value(self, obj,val,replacement):
        for key in obj:
            if type(obj[key]) == dict:
                self.replace_value(obj[key],val,replacement)
            else:
                if obj[key] == val:
                    obj[key] = replacement

    def prepare_request_lines(self, url, params) -> requests.PreparedRequest:
        http_method = self.rest_method
        headers = self.http_headers
        authenticator = self.authenticator
        if authenticator:
            headers.update(authenticator.auth_headers or {})
        request = cast(
            requests.PreparedRequest,
            self.requests_session.prepare_request(
                requests.Request(
                    method=http_method,
                    url=url,
                    params=params,
                    headers=headers,
                ),
            ),
        )
        return request

    def validate_response(self, response):
        sleep(1.01)
        return super().validate_response(response)