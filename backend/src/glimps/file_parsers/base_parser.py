from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from numpy.typing import NDArray


@dataclass
class MolecularStructure:
    coordinates: NDArray[np.float64]
    atom_names: list[str]
    residue_names: list[str]
    residue_ids: list[int]
    n_frames: int
    n_atoms: int

    @property
    def shape(self) -> tuple[int, int, int]:
        return (self.n_frames, self.n_atoms, 3)


class BaseMolecularParser(ABC):
    @abstractmethod
    def parse(self, file_path: Path) -> MolecularStructure:
        pass

    @abstractmethod
    def write(self, file_path: Path, structure: MolecularStructure) -> None:
        pass

    @abstractmethod
    def validate(self, file_path: Path) -> bool:
        pass

    @abstractmethod
    def get_content(self, structure: MolecularStructure) -> str:
        pass
