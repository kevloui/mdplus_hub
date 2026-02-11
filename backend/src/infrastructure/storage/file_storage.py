from abc import ABC, abstractmethod
from pathlib import Path

import numpy as np
from numpy.typing import NDArray

from src.config import settings


class FileStorage(ABC):
    @abstractmethod
    async def save_bytes(self, path: str, data: bytes) -> None:
        pass

    @abstractmethod
    async def load_bytes(self, path: str) -> bytes:
        pass

    @abstractmethod
    async def save_numpy(self, path: str, data: NDArray) -> None:
        pass

    @abstractmethod
    async def load_numpy(self, path: str) -> NDArray:
        pass

    @abstractmethod
    async def delete(self, path: str) -> None:
        pass

    @abstractmethod
    async def exists(self, path: str) -> bool:
        pass


class LocalFileStorage(FileStorage):
    def __init__(self, base_path: str):
        self._base_path = Path(base_path)
        self._base_path.mkdir(parents=True, exist_ok=True)

    def _resolve_path(self, path: str) -> Path:
        full_path = self._base_path / path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        return full_path

    async def save_bytes(self, path: str, data: bytes) -> None:
        file_path = self._resolve_path(path)
        file_path.write_bytes(data)

    async def load_bytes(self, path: str) -> bytes:
        file_path = self._resolve_path(path)
        return file_path.read_bytes()

    async def save_numpy(self, path: str, data: NDArray) -> None:
        file_path = self._resolve_path(path)
        np.save(file_path, data)

    async def load_numpy(self, path: str) -> NDArray:
        file_path = self._resolve_path(path)
        if not file_path.suffix:
            file_path = file_path.with_suffix(".npy")
        return np.load(file_path)

    async def delete(self, path: str) -> None:
        file_path = self._resolve_path(path)
        if file_path.exists():
            file_path.unlink()

    async def exists(self, path: str) -> bool:
        file_path = self._resolve_path(path)
        return file_path.exists()


class S3FileStorage(FileStorage):
    def __init__(self, bucket: str, region: str | None = None):
        import boto3

        self._bucket = bucket
        self._client = boto3.client("s3", region_name=region)

    async def save_bytes(self, path: str, data: bytes) -> None:
        self._client.put_object(Bucket=self._bucket, Key=path, Body=data)

    async def load_bytes(self, path: str) -> bytes:
        response = self._client.get_object(Bucket=self._bucket, Key=path)
        return response["Body"].read()

    async def save_numpy(self, path: str, data: NDArray) -> None:
        import io

        buffer = io.BytesIO()
        np.save(buffer, data)
        buffer.seek(0)
        self._client.put_object(Bucket=self._bucket, Key=path, Body=buffer.getvalue())

    async def load_numpy(self, path: str) -> NDArray:
        import io

        response = self._client.get_object(Bucket=self._bucket, Key=path)
        buffer = io.BytesIO(response["Body"].read())
        return np.load(buffer)

    async def delete(self, path: str) -> None:
        self._client.delete_object(Bucket=self._bucket, Key=path)

    async def exists(self, path: str) -> bool:
        try:
            self._client.head_object(Bucket=self._bucket, Key=path)
            return True
        except Exception:
            return False


_storage_instance: FileStorage | None = None


def get_file_storage() -> FileStorage:
    global _storage_instance

    if _storage_instance is None:
        if settings.storage_backend == "s3":
            _storage_instance = S3FileStorage(
                bucket=settings.s3_bucket or "",
                region=settings.s3_region,
            )
        else:
            _storage_instance = LocalFileStorage(settings.storage_path)

    return _storage_instance
