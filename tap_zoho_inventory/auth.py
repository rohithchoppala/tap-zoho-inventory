"""zoho-inventory Authentication."""

from __future__ import annotations

from singer_sdk.authenticators import OAuthAuthenticator, SingletonMeta


# The SingletonMeta metaclass makes your streams reuse the same authenticator instance.
# If this behaviour interferes with your use-case, you can remove the metaclass.
class ZohoInventoryAuthenticator(OAuthAuthenticator, metaclass=SingletonMeta):
    """Authenticator class for zoho-inventory."""

    @property
    def oauth_request_body(self) -> dict:
        """Define the OAuth request body for the AutomaticTestTap API.

        Returns:
            A dict with the request body
        """
        # TODO: Define the request body needed for the API.
        return {
            "resource": self._auth_endpoint,
            "scope": self.oauth_scopes,
            "redirect_uri": self.config["redirect_uri"],
            "client_id": self.config["client_id"],
            "client_secret": self.config["client_secret"],
            "refresh_token": self.config["refresh_token"],
            "grant_type": "refresh_token",
        }

    @property
    def auth_headers(self) -> dict:
        if not self.is_token_valid():
            self.update_access_token()

        result = super().auth_headers
        result["Authorization"] = f"Zoho-oauthtoken {self.access_token}"

        return result


    @classmethod
    def create_for_stream(cls, stream, auth_endpoint) -> ZohoInventoryAuthenticator:  # noqa: ANN001
        """Instantiate an authenticator for a specific Singer stream.

        Args:
            stream: The Singer stream instance.

        Returns:
            A new authenticator.
        """
        return cls(
            stream=stream,
            auth_endpoint=auth_endpoint,
            oauth_scopes="ZohoInventory.salesorders.READ,ZohoInventory.contacts.READ,ZohoInventory.items.READ,ZohoInventory.purchaseorders.READ",
        )
