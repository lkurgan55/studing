from minio import Minio
import os
import shutil
from config import MINIO_ENDPOINT, MINIO_ACCESS_KEY, MINIO_SECRET_KEY

def download_from_minio(bucket: str, prefix_or_key: str, dest_dir: str, recursive: bool = False):
    """Download files from MinIO bucket and write it."""
    client = Minio(
        endpoint=MINIO_ENDPOINT,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=False
    )

    os.makedirs(dest_dir, exist_ok=True)

    if recursive:
        objects = client.list_objects(bucket, prefix=prefix_or_key, recursive=True)
        for obj in objects:
            local_path = os.path.join(dest_dir, os.path.basename(obj.object_name))
            with client.get_object(bucket, obj.object_name) as data, open(local_path, "wb") as f:
                shutil.copyfileobj(data, f)
    else:
        local_path = os.path.join(dest_dir, os.path.basename(prefix_or_key))
        with client.get_object(bucket, prefix_or_key) as data, open(local_path, "wb") as f:
            shutil.copyfileobj(data, f)

    print(f"Downloaded from bucket '{bucket}' to {dest_dir}")
