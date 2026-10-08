import os
import hashlib
import logging
from typing import Tuple
from app.core.config import settings

logger = logging.getLogger("cloudmodx.s3")


class S3Service:
    def __init__(self):
        self.bucket_name = settings.ARTIFACT_BUCKET_NAME
        self.region = settings.AWS_REGION
        self._s3_client = None

    @property
    def s3_client(self):
        if self._s3_client is None:
            try:
                import boto3
                self._s3_client = boto3.client("s3", region_name=self.region)
            except Exception as e:
                logger.warning(f"Could not initialize S3 client: {e}")
                self._s3_client = None
        return self._s3_client

    def upload_artifact(
        self, file_content: bytes, filename: str, module_id: int, version: str
    ) -> Tuple[str, str, int, str]:
        """
        Uploads an artifact to S3 (or fallback local storage) and returns
        (storage_provider, storage_path, size_bytes, checksum).
        """
        size_bytes = len(file_content)
        checksum = hashlib.sha256(file_content).hexdigest()
        s3_key = f"modules/{module_id}/v{version}/{filename}"

        if self.s3_client and self.bucket_name:
            try:
                self.s3_client.put_object(
                    Bucket=self.bucket_name,
                    Key=s3_key,
                    Body=file_content,
                    ContentType="application/gzip" if filename.endswith((".tar.gz", ".tgz")) else "application/octet-stream",
                )
                storage_path = f"s3://{self.bucket_name}/{s3_key}"
                logger.info(f"Successfully uploaded artifact to S3: {storage_path}")
                return "s3", storage_path, size_bytes, checksum
            except Exception as e:
                logger.warning(f"S3 upload failed: {e}. Falling back to local storage.")

        # Fallback to local storage
        local_dir = os.path.join(settings.LOCAL_STORAGE_PATH, str(module_id), version)
        os.makedirs(local_dir, exist_ok=True)
        local_file_path = os.path.join(local_dir, filename)
        with open(local_file_path, "wb") as f:
            f.write(file_content)

        return "local", local_file_path, size_bytes, checksum


s3_service = S3Service()
