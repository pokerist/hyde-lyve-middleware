import time
import hmac
import hashlib
import base64
import uuid
import json
import requests
from urllib.parse import urlparse
from typing import Dict, Optional
import logging
from config import Config

logger = logging.getLogger(__name__)

class HikCentralClient:
    def __init__(self):
        self.app_key = Config.HIKCENTRAL_APP_KEY
        self.app_secret = Config.HIKCENTRAL_APP_SECRET
        self.base_url = self._clean_base_url(Config.HIKCENTRAL_BASE_URL)
        self.verify_ssl = Config.HIKCENTRAL_VERIFY_SSL
        
    def _clean_base_url(self, url: str) -> str:
        """Ensures base URL is just scheme://host:port"""
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}"
    
    def _get_content_md5(self, body: str) -> str:
        """Calculate Content-MD5 header value"""
        md5_hash = hashlib.md5(body.encode('utf-8')).digest()
        return base64.b64encode(md5_hash).decode('utf-8')
    
    def _generate_signature(self, method: str, uri: str, headers: Dict) -> str:
        """Generate HMAC-SHA256 signature required by HikCentral"""
        # 1. Construct the string to sign
        parts = [
            method,
            headers.get('Accept', '*/*'),
            headers.get('Content-MD5', ''),
            headers.get('Content-Type', ''),
            headers.get('Date', ''),
        ]
        
        # 2. Add custom x-ca-* headers (sorted alphabetically)
        x_ca_headers = [
            f"x-ca-key:{headers.get('X-Ca-Key')}",
            f"x-ca-nonce:{headers.get('X-Ca-Nonce')}",
            f"x-ca-timestamp:{headers.get('X-Ca-Timestamp')}",
        ]
        parts.extend(x_ca_headers)
        
        # 3. Add the URI (resource path)
        parts.append(uri)
        
        string_to_sign = '\n'.join(parts)
        
        # 4. Compute HMAC-SHA256
        signature = hmac.new(
            self.app_secret.encode('utf-8'),
            string_to_sign.encode('utf-8'),
            hashlib.sha256
        ).digest()
        
        return base64.b64encode(signature).decode('utf-8')
    
    def _build_headers(self, body_str: str = "") -> Dict:
        """Builds the complete set of headers for the request"""
        timestamp = str(int(time.time() * 1000))
        nonce = str(uuid.uuid4())
        
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json;charset=UTF-8',
            'X-Ca-Key': self.app_key,
            'X-Ca-Nonce': nonce,
            'X-Ca-Timestamp': timestamp,
            'X-Ca-Signature-Headers': 'x-ca-key,x-ca-nonce,x-ca-timestamp',
            'userId': Config.HIKCENTRAL_USER_ID
        }
        
        if body_str:
            headers['Content-MD5'] = self._get_content_md5(body_str)
            
        return headers
    
    def make_request(self, endpoint: str, body: Dict = None, method: str = 'POST') -> Optional[Dict]:
        """
        Execute the API request
        endpoint: e.g., '/artemis/api/resource/v1/person/single/add'
        """
        full_url = f"{self.base_url}{endpoint}"
        body_str = json.dumps(body) if body else ""
        
        # 1. Prepare Headers
        headers = self._build_headers(body_str)
        
        # 2. Sign the Request
        signature = self._generate_signature(method, endpoint, headers)
        headers['X-Ca-Signature'] = signature
        
        logger.info(f"Making {method} request to: {full_url}")
        
        try:
            # 3. Send Request
            if method.upper() == 'POST':
                response = requests.post(
                    full_url,
                    data=body_str,
                    headers=headers,
                    verify=self.verify_ssl,
                    timeout=Config.API_TIMEOUT
                )
            elif method.upper() == 'PUT':
                response = requests.put(
                    full_url,
                    data=body_str,
                    headers=headers,
                    verify=self.verify_ssl,
                    timeout=Config.API_TIMEOUT
                )
            elif method.upper() == 'DELETE':
                response = requests.delete(
                    full_url,
                    headers=headers,
                    verify=self.verify_ssl,
                    timeout=Config.API_TIMEOUT
                )
            elif method.upper() == 'GET':
                response = requests.get(
                    full_url,
                    headers=headers,
                    verify=self.verify_ssl,
                    timeout=Config.API_TIMEOUT
                )
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            # 4. Handle Response
            if response.status_code in [200, 201]:
                result = response.json()
                if result.get('code') == '0':
                    logger.info(f"Request successful: {result}")
                    return result
                else:
                    logger.error(f"HikCentral Error: {result.get('msg')} (Code: {result.get('code')})")
                    return None
            else:
                logger.error(f"HTTP Error: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.Timeout:
            logger.error(f"Request timeout after {Config.API_TIMEOUT} seconds")
            return None
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection Failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return None
    
    def add_person(self, person_data: Dict) -> Optional[Dict]:
        """Add a new person to HikCentral"""
        endpoint = '/artemis/api/resource/v1/person/single/add'
        return self.make_request(endpoint, person_data, 'POST')
    
    def update_person(self, person_code: str, person_data: Dict) -> Optional[Dict]:
        """Update an existing person in HikCentral"""
        endpoint = f'/artemis/api/resource/v1/person/single/update'
        person_data['personCode'] = person_code
        return self.make_request(endpoint, person_data, 'PUT')
    
    def delete_person(self, person_code: str) -> Optional[Dict]:
        """Delete a person from HikCentral"""
        endpoint = f'/artemis/api/resource/v1/person/single/delete'
        body = {'personCode': person_code}
        return self.make_request(endpoint, body, 'POST')
    
    def get_person(self, person_code: str) -> Optional[Dict]:
        """Get person details from HikCentral"""
        endpoint = f'/artemis/api/resource/v1/person/condition'
        body = {'personCode': person_code}
        return self.make_request(endpoint, body, 'POST')