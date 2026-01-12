from sp_api.api import Sellers
from sp_api.base import Marketplaces
import os

creds = {
    "refresh_token": os.getenv('SP_API_REFRESH_TOKEN', '').strip(),
    "lwa_app_id": os.getenv('SP_API_CLIENT_ID', '').strip(),
    "lwa_client_secret": os.getenv('SP_API_CLIENT_SECRET', '').strip(),
    "aws_access_key": os.getenv('SP_API_ACCESS_KEY', '').strip(),
    "aws_secret_key": os.getenv('SP_API_SECRET_KEY', '').strip(),
    "role_arn": os.getenv('SP_API_ROLE_ARN', '').strip()
}

# Cliente en Sandbox
sellers_client = Sellers(
    **creds,
    marketplace=Marketplaces.US,
    sandbox=True  # <-- Esto activa el Sandbox
)

response = sellers_client.get_marketplace_participation()
print(response.payload)
