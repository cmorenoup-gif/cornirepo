# Este archivo gestiona tus llaves secretas y la conexión a la SP-API.
import os
from sp_api.api import Orders
from sp_api.base import Marketplaces

class AmazonClient:
    def __init__(self):
        self.creds = {
            "refresh_token": os.getenv('SP_API_REFRESH_TOKEN', '').strip(),
            "lwa_app_id": os.getenv('SP_API_CLIENT_ID', '').strip(),
            "lwa_client_secret": os.getenv('SP_API_CLIENT_SECRET', '').strip(),
            "aws_access_key": os.getenv('SP_API_ACCESS_KEY', '').strip(),
            "aws_secret_key": os.getenv('SP_API_SECRET_KEY', '').strip(),
            "role_arn": os.getenv('SP_API_ROLE_ARN', '').strip()
        }

    def fetch_orders(self, created_after="2026-01-01T00:00:00Z"):
        client = Orders(credentials=self.creds, marketplace=Marketplaces.US)
        response = client.get_orders(CreatedAfter=created_after)
        return response.payload.get("Orders", [])
