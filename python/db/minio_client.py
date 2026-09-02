import logging
import io
import json
from pathlib import Path
import pandas as pd
from typing import Union, Dict, Any
from python.config import (
    MINIO_ENDPOINT, MINIO_ACCESS_KEY, MINIO_SECRET_KEY, MINIO_SECURE, MINIO_BUCKET_NAME, BASE_DIR
)

logger = logging.getLogger("MinioClient")

class MinioClient:
    """
    MinIO S3-compatible Data Lake Client with local file storage fallback.
    """
    def __init__(self):
        self.use_local = False
        self.local_dir = BASE_DIR / "data" / "lake"
        self.client = None
        self._init_client()

    def _init_client(self):
        try:
            from minio import Minio
            self.client = Minio(
                MINIO_ENDPOINT,
                access_key=MINIO_ACCESS_KEY,
                secret_key=MINIO_SECRET_KEY,
                secure=MINIO_SECURE
            )
            # Test bucket existence
            if not self.client.bucket_exists(MINIO_BUCKET_NAME):
                self.client.make_bucket(MINIO_BUCKET_NAME)
            logger.info(f"Connected to MinIO bucket: {MINIO_BUCKET_NAME}")
        except Exception as e:
            logger.warning(f"MinIO storage unavailable ({e}). Using local filesystem Lakehouse fallback.")
            self.use_local = True
            self.local_dir.mkdir(parents=True, exist_ok=True)

    def upload_json(self, object_path: str, data: Union[Dict[str, Any], list]):
        content = json.dumps(data, indent=2, default=str).encode("utf-8")
        if self.use_local:
            target_path = self.local_dir / object_path
            target_path.parent.mkdir(parents=True, exist_ok=True)
            with open(target_path, "wb") as f:
                f.write(content)
            logger.info(f"[Local Lake] Saved JSON: {target_path}")
        else:
            self.client.put_object(
                MINIO_BUCKET_NAME,
                object_path,
                io.BytesIO(content),
                length=len(content),
                content_type="application/json"
            )
            logger.info(f"[MinIO Lake] Uploaded JSON: {object_path}")

    def upload_parquet(self, object_path: str, df: pd.DataFrame):
        buffer = io.BytesIO()
        try:
            df.to_parquet(buffer, index=False)
            content_type = "application/octet-stream"
            content = buffer.getvalue()
        except (ImportError, Exception) as e:
            # Fallback to CSV if pyarrow/fastparquet engine is not installed
            csv_buffer = io.BytesIO()
            df.to_csv(csv_buffer, index=False)
            content = csv_buffer.getvalue()
            content_type = "text/csv"
            object_path = object_path.replace(".parquet", ".csv")

        if self.use_local:
            target_path = self.local_dir / object_path
            target_path.parent.mkdir(parents=True, exist_ok=True)
            with open(target_path, "wb") as f:
                f.write(content)
            logger.info(f"[Local Lake] Saved file: {target_path}")
        else:
            self.client.put_object(
                MINIO_BUCKET_NAME,
                object_path,
                io.BytesIO(content),
                length=len(content),
                content_type=content_type
            )
            logger.info(f"[MinIO Lake] Uploaded file: {object_path}")

