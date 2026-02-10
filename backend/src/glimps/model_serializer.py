import pickle
from pathlib import Path

from src.glimps.adapter import GlimpsAdapter


class ModelSerializer:
    @staticmethod
    def serialize(adapter: GlimpsAdapter) -> bytes:
        return pickle.dumps(adapter)

    @staticmethod
    def deserialize(data: bytes) -> GlimpsAdapter:
        return pickle.loads(data)

    @staticmethod
    def save(adapter: GlimpsAdapter, file_path: Path) -> None:
        data = ModelSerializer.serialize(adapter)
        file_path.write_bytes(data)

    @staticmethod
    def load(file_path: Path) -> GlimpsAdapter:
        data = file_path.read_bytes()
        return ModelSerializer.deserialize(data)
