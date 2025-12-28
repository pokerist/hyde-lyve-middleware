import aiohttp
import hashlib
import hmac
import base64
import time
import json
import logging
from typing import Optional, Dict, Any
from urllib.parse import urlparse
from app.config import settings

logger = logging.getLogger(__name__)

class HikCentralClient:
    def __init__(self):
        self.base_url = self._clean_base_url(settings.hikcentral_base_url)
        self.app_key = settings.hikcentral_app_key
        self.app_secret = settings.hikcentral_app_secret
        self.user_id = settings.hikcentral_user_id
        self.org_index_code = settings.hikcentral_org_index_code
        self.verify_ssl = settings.hikcentral_verify_ssl
    
    def _clean_base_url(self, url: str) -> str:
        """Ensures base URL is just scheme://host:port"""
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}"
    
    def _get_content_md5(self, body: str) -> str:
        """Calculate Content-MD5 header value"""
        md5_hash = hashlib.md5(body.encode('utf-8')).digest()
        return base64.b64encode(md5_hash).decode('utf-8')
    
    def _generate_signature(self, method: str, uri: str, headers: Dict[str, str]) -> str:
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
        # Note: HikCentral Python demos often put x-ca- headers directly in the string
        # Standard format: header_name:header_value
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
    
    def _build_headers(self, method: str, uri: str, body_str: str = "") -> Dict[str, str]:
        """Builds the complete set of headers for the request"""
        timestamp = str(int(time.time() * 1000))
        nonce = str(int(time.time()))
        
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json;charset=UTF-8',
            'X-Ca-Key': self.app_key,
            'X-Ca-Nonce': nonce,
            'X-Ca-Timestamp': timestamp,
            'X-Ca-Signature-Headers': 'x-ca-key,x-ca-nonce,x-ca-timestamp',
            'userId': self.user_id
        }
        
        if body_str:
            headers['Content-MD5'] = self._get_content_md5(body_str)
        
        # Generate signature
        signature = self._generate_signature(method, uri, headers)
        headers['X-Ca-Signature'] = signature
        
        return headers
    
    async def add_person(self, person_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Add person to HikCentral"""
        uri = "/artemis/api/resource/v1/person/single/add"
        url = f"{self.base_url}{uri}"
        
        # Prepare person data for HikCentral
        hikcentral_data = {
            "personCode": person_data.get("personCode", ""),
            "personFamilyName": person_data.get("personFamilyName", ""),
            "personGivenName": person_data.get("personGivenName", ""),
            "gender": person_data.get("gender", 1),
            "orgIndexCode": person_data.get("orgIndexCode", self.org_index_code),
            "phoneNo": person_data.get("phoneNo", ""),
            "email": person_data.get("email", ""),
            "certificateType": person_data.get("certificateType", 111),
            "certificateNum": person_data.get("certificateNum", ""),
            "personType": person_data.get("personType", 1),
            "beginTime": person_data.get("beginTime", ""),
            "endTime": person_data.get("endTime", ""),
            "faces": person_data.get("faces", [])
        }
        
        body_str = json.dumps(hikcentral_data, separators=(',', ':'))
        headers = self._build_headers("POST", uri, body_str)
        
        logger.info(f"Requesting: {url}")
        logger.info(f"Headers: {headers}")
        logger.info(f"Body: {body_str}")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    data=body_str,
                    headers=headers,
                    ssl=self.verify_ssl,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    response_text = await response.text()
                    logger.info(f"HikCentral add_person response: {response.status} - {response_text}")
                    
                    if response.status == 200:
                        response_data = await response.json()
                        if response_data.get("code") == "0":
                            return {
                                "success": True,
                                "data": response_data.get("data", {}),
                                "message": "Person added successfully"
                            }
                        else:
                            return {
                                "success": False,
                                "message": response_data.get("msg", "Unknown error"),
                                "code": response_data.get("code")
                            }
                    else:
                        return {
                            "success": False,
                            "message": f"HTTP {response.status}: {response_text}",
                            "code": str(response.status)
                        }
                        
        except Exception as e:
            logger.error(f"Error adding person to HikCentral: {e}")
            return {
                "success": False,
                "message": f"Network error: {str(e)}",
                "code": "NETWORK_ERROR"
            }
    
    async def update_person(self, person_id: str, person_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update person in HikCentral"""
        uri = "/artemis/api/resource/v1/person/single/update"
        url = f"{self.base_url}{uri}"
        
        # Prepare update data
        update_data = {
            "personId": person_id,
            "personFamilyName": person_data.get("personFamilyName", ""),
            "personGivenName": person_data.get("personGivenName", ""),
            "gender": person_data.get("gender", 1),
            "phoneNo": person_data.get("phoneNo", ""),
            "email": person_data.get("email", ""),
            "certificateType": person_data.get("certificateType", 111),
            "certificateNum": person_data.get("certificateNum", ""),
            "personType": person_data.get("personType", 1),
            "beginTime": person_data.get("beginTime", ""),
            "endTime": person_data.get("endTime", "")
        }
        
        body_str = json.dumps(update_data, separators=(',', ':'))
        headers = self._build_headers("PUT", uri, body_str)
        
        logger.info(f"Requesting: {url}")
        logger.info(f"Headers: {headers}")
        logger.info(f"Body: {body_str}")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.put(
                    url,
                    data=body_str,
                    headers=headers,
                    ssl=self.verify_ssl,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    response_text = await response.text()
                    logger.info(f"HikCentral update_person response: {response.status} - {response_text}")
                    
                    if response.status == 200:
                        response_data = await response.json()
                        if response_data.get("code") == "0":
                            return {
                                "success": True,
                                "data": response_data.get("data", {}),
                                "message": "Person updated successfully"
                            }
                        else:
                            return {
                                "success": False,
                                "message": response_data.get("msg", "Unknown error"),
                                "code": response_data.get("code")
                            }
                    else:
                        return {
                            "success": False,
                            "message": f"HTTP {response.status}: {response_text}",
                            "code": str(response.status)
                        }
                        
        except Exception as e:
            logger.error(f"Error updating person in HikCentral: {e}")
            return {
                "success": False,
                "message": f"Network error: {str(e)}",
                "code": "NETWORK_ERROR"
            }
    
    async def delete_person(self, person_id: str) -> Optional[Dict[str, Any]]:
        """Delete person from HikCentral"""
        uri = "/artemis/api/resource/v1/person/single/delete"
        url = f"{self.base_url}{uri}"
        
        delete_data = {
            "personId": person_id
        }
        
        body_str = json.dumps(delete_data, separators=(',', ':'))
        headers = self._build_headers("DELETE", uri, body_str)
        
        logger.info(f"Requesting: {url}")
        logger.info(f"Headers: {headers}")
        logger.info(f"Body: {body_str}")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.delete(
                    url,
                    data=body_str,
                    headers=headers,
                    ssl=self.verify_ssl,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    response_text = await response.text()
                    logger.info(f"HikCentral delete_person response: {response.status} - {response_text}")
                    
                    if response.status == 200:
                        response_data = await response.json()
                        if response_data.get("code") == "0":
                            return {
                                "success": True,
                                "data": response_data.get("data", {}),
                                "message": "Person deleted successfully"
                            }
                        else:
                            return {
                                "success": False,
                                "message": response_data.get("msg", "Unknown error"),
                                "code": response_data.get("code")
                            }
                    else:
                        return {
                            "success": False,
                            "message": f"HTTP {response.status}: {response_text}",
                            "code": str(response.status)
                        }
                        
        except Exception as e:
            logger.error(f"Error deleting person from HikCentral: {e}")
            return {
                "success": False,
                "message": f"Network error: {str(e)}",
                "code": "NETWORK_ERROR"
            }
    
    async def get_person(self, person_id: str) -> Optional[Dict[str, Any]]:
        """Get person from HikCentral"""
        uri = "/artemis/api/resource/v1/person/single/info"
        url = f"{self.base_url}{uri}"
        
        params = {
            "personId": person_id
        }
        
        headers = self._build_headers("GET", uri)
        
        logger.info(f"Requesting: {url}")
        logger.info(f"Headers: {headers}")
        logger.info(f"Params: {params}")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url,
                    params=params,
                    headers=headers,
                    ssl=self.verify_ssl,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    response_text = await response.text()
                    logger.info(f"HikCentral get_person response: {response.status} - {response_text}")
                    
                    if response.status == 200:
                        response_data = await response.json()
                        if response_data.get("code") == "0":
                            return {
                                "success": True,
                                "data": response_data.get("data", {}),
                                "message": "Person retrieved successfully"
                            }
                        else:
                            return {
                                "success": False,
                                "message": response_data.get("msg", "Unknown error"),
                                "code": response_data.get("code")
                            }
                    else:
                        return {
                            "success": False,
                            "message": f"HTTP {response.status}: {response_text}",
                            "code": str(response.status)
                        }
                        
        except Exception as e:
            logger.error(f"Error getting person from HikCentral: {e}")
            return {
                "success": False,
                "message": f"Network error: {str(e)}",
                "code": "NETWORK_ERROR"
            }
    
    async def generate_qr_code(self, person_id: str, unit_id: str, validity_minutes: int = 60) -> Optional[Dict[str, Any]]:
        """Generate QR code for person in HikCentral"""
        uri = "/artemis/api/visitor/access/qrCode/generate"
        url = f"{self.base_url}{uri}"
        
        qr_data = {
            "personId": person_id,
            "unitId": unit_id,
            "validityMinutes": validity_minutes
        }
        
        body_str = json.dumps(qr_data, separators=(',', ':'))
        headers = self._build_headers("POST", uri, body_str)
        
        logger.info(f"Requesting: {url}")
        logger.info(f"Headers: {headers}")
        logger.info(f"Body: {body_str}")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    data=body_str,
                    headers=headers,
                    ssl=self.verify_ssl,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    response_text = await response.text()
                    logger.info(f"HikCentral generate_qr_code response: {response.status} - {response_text}")
                    
                    if response.status == 200:
                        response_data = await response.json()
                        if response_data.get("code") == "0":
                            return {
                                "success": True,
                                "data": response_data.get("data", {}),
                                "message": "QR code generated successfully"
                            }
                        else:
                            return {
                                "success": False,
                                "message": response_data.get("msg", "Unknown error"),
                                "code": response_data.get("code")
                            }
                    else:
                        return {
                            "success": False,
                            "message": f"HTTP {response.status}: {response_text}",
                            "code": str(response.status)
                        }
                        
        except Exception as e:
            logger.error(f"Error generating QR code in HikCentral: {e}")
            return {
                "success": False,
                "message": f"Network error: {str(e)}",
                "code": "NETWORK_ERROR"
            }