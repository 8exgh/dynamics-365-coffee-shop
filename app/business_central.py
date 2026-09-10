import asyncio
import os
import time
from urllib.parse import urlparse
from uuid import UUID

import httpx


class ConnectionError(Exception):
    pass


class BusinessCentral:
    resources = {'customers', 'items', 'vendors', 'salesOrders', 'salesInvoices', 'purchaseOrders', 'purchaseInvoices', 'accounts', 'generalLedgerEntries', 'customerPayments', 'dimensions', 'locations'}

    def __init__(self):
        self.tenant = os.getenv('BC_TENANT_ID', '')
        self.company = os.getenv('BC_COMPANY_ID', '')
        self.client_id = os.getenv('BC_CLIENT_ID', '')
        self.secret = os.getenv('BC_CLIENT_SECRET', '')
        self.environment = os.getenv('BC_ENVIRONMENT', 'Sandbox')
        self.write_enabled = os.getenv('BC_ALLOW_WRITES', 'false').lower() == 'true'
        self.web_url = os.getenv('BC_WEB_URL', 'https://businesscentral.dynamics.com')
        self._token = None
        self._expires = 0
        self._lock = asyncio.Lock()
        if self.configured:
            for value in [self.tenant, self.company, self.client_id]:
                UUID(value)
            if not self.environment.replace('-', '').replace('_', '').isalnum():
                raise ValueError('BC_ENVIRONMENT must contain only letters, numbers, hyphens, or underscores.')
        url = urlparse(self.web_url)
        if url.scheme != 'https' or not url.netloc or url.username or url.password:
            raise ValueError('BC_WEB_URL must be an HTTPS URL without credentials.')

    @property
    def configured(self):
        return all([self.tenant, self.company, self.client_id, self.secret])

    @property
    def base(self):
        return f'https://api.businesscentral.dynamics.com/v2.0/{self.tenant}/{self.environment}/api/v2.0'

    def status(self):
        return {'configured': self.configured, 'write_enabled': self.write_enabled and self.configured, 'environment': self.environment, 'web_url': self.web_url, 'company_id': self.company if self.configured else None}

    async def token(self):
        if not self.configured:
            raise ConnectionError('Business Central is not configured. Add the BC settings in the server environment.')
        async with self._lock:
            if self._token and time.monotonic() < self._expires:
                return self._token
            async with httpx.AsyncClient(timeout=20) as client:
                response = await client.post(f'https://login.microsoftonline.com/{self.tenant}/oauth2/v2.0/token', data={'grant_type': 'client_credentials', 'client_id': self.client_id, 'client_secret': self.secret, 'scope': 'https://api.businesscentral.dynamics.com/.default'})
            if response.status_code != 200:
                raise ConnectionError(f'Microsoft authentication failed ({response.status_code}). Check application permissions and credentials.')
            data = response.json()
            self._token = data['access_token']
            self._expires = time.monotonic() + max(0, int(data.get('expires_in', 3600)) - 90)
            return self._token

    async def request(self, method, path, body=None, params=None):
        token = await self.token()
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.request(method, f'{self.base}/{path}', params=params, json=body, headers={'Authorization': f'Bearer {token}', 'Accept': 'application/json', 'OData-Version': '4.0'})
        if response.status_code == 401:
            self._expires = 0
        if not response.is_success:
            raise ConnectionError(f'Business Central returned HTTP {response.status_code}. Check the company, permissions, and document setup in Business Central.')
        return response.json() if response.content else {}

    async def list(self, resource):
        if resource not in self.resources:
            raise ConnectionError('Unsupported Business Central resource.')
        return await self.request('GET', f'companies({self.company})/{resource}', params={'$top': 100})

    async def draft_order(self, customer_id, item_id, quantity, reference):
        if not self.write_enabled:
            raise ConnectionError('Business Central writes are disabled. Set BC_ALLOW_WRITES=true to enable draft sales orders.')
        UUID(customer_id)
        UUID(item_id)
        if len(reference) != 32 or any(c not in '0123456789abcdef' for c in reference):
            raise ConnectionError('A valid request reference is required.')
        existing = await self.request('GET', f'companies({self.company})/salesOrders', params={'$filter': f"externalDocumentNumber eq '{reference}'", '$top': 1})
        if existing.get('value'):
            return existing['value'][0]
        return await self.request('POST', f'companies({self.company})/salesOrders', {'customerId': customer_id, 'externalDocumentNumber': reference, 'salesOrderLines': [{'lineType': 'Item', 'itemId': item_id, 'quantity': quantity}]})
