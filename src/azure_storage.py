"""
Azure Blob Storage utility for persistent PDF/document storage.
Supports both Azure Blob Storage and local file system fallback.
"""

import os
import logging
import io
import tempfile
from pathlib import Path
from typing import Optional, BinaryIO

logger = logging.getLogger(__name__)


class AzureStorageManager:
    """
    Manages document storage using Azure Blob Storage.
    Falls back to local file system if Azure credentials are not configured.
    """
    
    def __init__(self):
        self.connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        self.container_name = os.getenv("AZURE_STORAGE_CONTAINER", "documents")
        self.use_azure = self.connection_string is not None
        
        if self.use_azure:
            try:
                from azure.storage.blob import BlobServiceClient
                self.blob_service_client = BlobServiceClient.from_connection_string(
                    self.connection_string
                )
                self.container_client = self.blob_service_client.get_container_client(
                    self.container_name
                )
                logger.info(f"Azure Blob Storage initialized (container: {self.container_name})")
            except ImportError:
                logger.warning("azure-storage-blob not installed. Falling back to local storage.")
                self.use_azure = False
            except Exception as e:
                logger.error(f"Failed to initialize Azure Blob Storage: {e}. Using local storage.")
                self.use_azure = False
        else:
            logger.info("AZURE_STORAGE_CONNECTION_STRING not set. Using local temp storage.")
    
    def upload_document(self, file_name: str, file_content: bytes) -> str:
        """
        Upload a document to storage.
        
        Args:
            file_name: Name of the file
            file_content: Binary content of the file
            
        Returns:
            str: Storage path/identifier
        """
        if self.use_azure:
            try:
                blob_client = self.container_client.upload_blob(
                    name=file_name,
                    data=file_content,
                    overwrite=True
                )
                logger.info(f"Uploaded document to Azure: {file_name}")
                return f"azure://{self.container_name}/{file_name}"
            except Exception as e:
                logger.error(f"Failed to upload to Azure: {e}. Falling back to local storage.")
                return self._save_local(file_name, file_content)
        else:
            return self._save_local(file_name, file_content)
    
    def download_document(self, storage_path: str) -> Optional[bytes]:
        """
        Download a document from storage.
        
        Args:
            storage_path: Path/identifier returned by upload_document
            
        Returns:
            bytes: File content, or None if not found
        """
        if storage_path.startswith("azure://"):
            if not self.use_azure:
                logger.error("Cannot download from Azure: storage not configured")
                return None
            
            try:
                # Parse azure://container/path
                file_name = storage_path.split("azure://", 1)[1].split("/", 1)[1]
                blob_client = self.container_client.get_blob_client(file_name)
                content = blob_client.download_blob().readall()
                logger.info(f"Downloaded document from Azure: {file_name}")
                return content
            except Exception as e:
                logger.error(f"Failed to download from Azure: {e}")
                return None
        else:
            return self._read_local(storage_path)
    
    def delete_document(self, storage_path: str) -> bool:
        """
        Delete a document from storage.
        
        Args:
            storage_path: Path/identifier returned by upload_document
            
        Returns:
            bool: True if successful, False otherwise
        """
        if storage_path.startswith("azure://"):
            if not self.use_azure:
                logger.warning("Cannot delete from Azure: storage not configured")
                return False
            
            try:
                file_name = storage_path.split("azure://", 1)[1].split("/", 1)[1]
                blob_client = self.container_client.get_blob_client(file_name)
                blob_client.delete_blob()
                logger.info(f"Deleted document from Azure: {file_name}")
                return True
            except Exception as e:
                logger.error(f"Failed to delete from Azure: {e}")
                return False
        else:
            return self._delete_local(storage_path)
    
    def list_documents(self) -> list:
        """
        List all documents in storage.
        
        Returns:
            list: List of storage paths
        """
        if self.use_azure:
            try:
                blobs = self.container_client.list_blobs()
                paths = [f"azure://{self.container_name}/{blob.name}" for blob in blobs]
                logger.info(f"Listed {len(paths)} documents from Azure")
                return paths
            except Exception as e:
                logger.error(f"Failed to list documents from Azure: {e}")
                return []
        else:
            return self._list_local()
    
    # Local file system fallback methods
    
    def _save_local(self, file_name: str, file_content: bytes) -> str:
        """Save to local temp directory."""
        temp_dir = tempfile.gettempdir()
        file_path = os.path.join(temp_dir, f"juriscope_{file_name}")
        
        try:
            with open(file_path, "wb") as f:
                f.write(file_content)
            logger.info(f"Saved document locally: {file_path}")
            return file_path
        except Exception as e:
            logger.error(f"Failed to save document locally: {e}")
            return None
    
    def _read_local(self, file_path: str) -> Optional[bytes]:
        """Read from local file."""
        try:
            with open(file_path, "rb") as f:
                content = f.read()
            logger.info(f"Read document locally: {file_path}")
            return content
        except Exception as e:
            logger.error(f"Failed to read document locally: {e}")
            return None
    
    def _delete_local(self, file_path: str) -> bool:
        """Delete local file."""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Deleted document locally: {file_path}")
                return True
            else:
                logger.warning(f"File not found: {file_path}")
                return False
        except Exception as e:
            logger.error(f"Failed to delete document locally: {e}")
            return False
    
    def _list_local(self) -> list:
        """List local files in temp directory."""
        temp_dir = tempfile.gettempdir()
        try:
            files = [os.path.join(temp_dir, f) for f in os.listdir(temp_dir) 
                    if f.startswith("juriscope_")]
            logger.info(f"Listed {len(files)} documents from local storage")
            return files
        except Exception as e:
            logger.error(f"Failed to list local documents: {e}")
            return []


# Global instance
_storage_manager: Optional[AzureStorageManager] = None


def get_storage_manager() -> AzureStorageManager:
    """Get or create the global storage manager instance."""
    global _storage_manager
    if _storage_manager is None:
        _storage_manager = AzureStorageManager()
    return _storage_manager
