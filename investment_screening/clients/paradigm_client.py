"""
ParadigmClient - API client for LightOn/Paradigm services
"""

import asyncio
import aiohttp
import logging
from typing import List, Dict, Any
from config.settings import MAX_WAIT_TIME, POLL_INTERVAL

logger = logging.getLogger(__name__)

class ParadigmClient:
    """Client for interacting with LightOn/Paradigm API"""
    
    def __init__(self, api_key: str, base_url: str):
        self.base_url = base_url
        self.api_key = api_key
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
    
    async def upload_file(self, file_path: str, filename: str) -> Dict[str, Any]:
        """Upload a file to LightOn/Paradigm"""
        try:
            # Try different possible endpoints
            possible_endpoints = [
                f"{self.base_url}/api/v2/files/upload",
                f"{self.base_url}/files/upload", 
                f"{self.base_url}/api/files/upload"
            ]
            
            for endpoint in possible_endpoints:
                try:
                    logger.info(f"Trying upload endpoint: {endpoint}")
                    
                    # Prepare file upload
                    form_data = aiohttp.FormData()
                    form_data.add_field('file', 
                                      open(file_path, 'rb'), 
                                      filename=filename,
                                      content_type='application/octet-stream')
                    form_data.add_field('collection_type', 'private')
                    
                    # Upload without Content-Type header for multipart
                    headers = {"Authorization": f"Bearer {self.api_key}"}
                    
                    async with aiohttp.ClientSession() as session:
                        async with session.post(endpoint, headers=headers, data=form_data) as response:
                            if response.status == 200:
                                result = await response.json()
                                logger.info(f"Upload successful via {endpoint}")
                                return result
                            else:
                                error_text = await response.text()
                                logger.warning(f"Upload failed via {endpoint}: {response.status} - {error_text}")
                                
                except Exception as e:
                    logger.warning(f"Upload attempt failed for {endpoint}: {str(e)}")
                    continue
            
            # If all endpoints failed
            raise Exception("All upload endpoints failed")
            
        except Exception as e:
            logger.error(f"File upload error: {str(e)}")
            raise e
    
    async def delete_file(self, file_id: int) -> bool:
        """Delete a file from LightOn/Paradigm"""
        try:
            possible_endpoints = [
                f"{self.base_url}/api/v2/files/{file_id}",
                f"{self.base_url}/files/{file_id}",
                f"{self.base_url}/api/files/{file_id}"
            ]
            
            for endpoint in possible_endpoints:
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.delete(endpoint, headers=self.headers) as response:
                            if response.status in [200, 204, 404]:  # 404 means already deleted
                                logger.info(f"Delete successful via {endpoint}")
                                return True
                            else:
                                error_text = await response.text()
                                logger.warning(f"Delete failed via {endpoint}: {response.status} - {error_text}")
                                
                except Exception as e:
                    logger.warning(f"Delete attempt failed for {endpoint}: {str(e)}")
                    continue
            
            raise Exception("All delete endpoints failed")
            
        except Exception as e:
            logger.error(f"File delete error: {str(e)}")
            raise e

    async def document_search(self, query: str, **kwargs) -> Dict[str, Any]:
        """Search for documents using the provided query"""
        endpoint = f"{self.base_url}/api/v2/chat/document-search"
        payload = {"query": query, **kwargs}
        
        async with aiohttp.ClientSession() as session:
            async with session.post(endpoint, json=payload, headers=self.headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise Exception(f"API error {response.status}: {await response.text()}")
    
    async def analyze_documents_with_polling(self, query: str, document_ids: List[int], **kwargs) -> str:
        """Analyze documents with polling for completion"""
        # Start analysis
        endpoint = f"{self.base_url}/api/v2/chat/document-analysis"
        payload = {"query": query, "document_ids": document_ids, **kwargs}
        
        async with aiohttp.ClientSession() as session:
            async with session.post(endpoint, json=payload, headers=self.headers) as response:
                if response.status == 200:
                    result = await response.json()
                    chat_response_id = result.get("chat_response_id")
                else:
                    raise Exception(f"Analysis API error {response.status}: {await response.text()}")
        
        # Poll for results
        elapsed = 0
        
        while elapsed < MAX_WAIT_TIME:
            endpoint = f"{self.base_url}/api/v2/chat/document-analysis/{chat_response_id}"
            async with aiohttp.ClientSession() as session:
                async with session.get(endpoint, headers=self.headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        status = result.get("status", "")
                        if status.lower() in ["completed", "complete", "finished", "success"]:
                            analysis_result = result.get("result") or result.get("detailed_analysis") or "Analysis completed"
                            return analysis_result
                        elif status.lower() in ["failed", "error"]:
                            raise Exception(f"Analysis failed: {status}")
                    elif response.status == 404:
                        # Analysis not ready yet, continue polling
                        pass
                    else:
                        raise Exception(f"Polling API error {response.status}: {await response.text()}")
                    
                    await asyncio.sleep(POLL_INTERVAL)
                    elapsed += POLL_INTERVAL
        
        raise Exception("Analysis timed out")
    
    async def chat_completion(self, prompt: str, model: str = "alfred-4.2") -> str:
        """Generate chat completion using the specified model"""
        endpoint = f"{self.base_url}/api/v2/chat/completions"
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(endpoint, json=payload, headers=self.headers) as response:
                if response.status == 200:
                    result = await response.json()
                    return result["choices"][0]["message"]["content"]
                else:
                    raise Exception(f"Paradigm chat completion API error {response.status}: {await response.text()}")