from pathlib import Path

import mdtraj as md
import numpy as np

from src.glimps.file_parsers.base_parser import BaseMolecularParser, MolecularStructure


class GROParser(BaseMolecularParser):
    def parse(self, file_path: Path) -> MolecularStructure:
        trajectory = md.load(str(file_path))

        atom_names = [atom.name for atom in trajectory.topology.atoms]
        residue_names = [atom.residue.name for atom in trajectory.topology.atoms]
        residue_ids = [atom.residue.index for atom in trajectory.topology.atoms]

        return MolecularStructure(
            coordinates=trajectory.xyz.astype(np.float64),
            atom_names=atom_names,
            residue_names=residue_names,
            residue_ids=residue_ids,
            n_frames=trajectory.n_frames,
            n_atoms=trajectory.n_atoms,
        )

    def write(self, file_path: Path, structure: MolecularStructure) -> None:
        content = self.get_content(structure)
        file_path.write_text(content)

    def validate(self, file_path: Path) -> bool:
        try:
            md.load(str(file_path))
            return True
        except Exception:
            return False

    def get_content(self, structure: MolecularStructure) -> str:
        lines = []

        for frame_idx in range(structure.n_frames):
            lines.append(f"Frame {frame_idx + 1}")
            lines.append(f"{structure.n_atoms}")

            for i in range(structure.n_atoms):
                x, y, z = structure.coordinates[frame_idx, i]
                res_id = structure.residue_ids[i] + 1
                res_name = structure.residue_names[i]
                atom_name = structure.atom_names[i]

                line = f"{res_id:5d}{res_name:<5s}{atom_name:>5s}{i + 1:5d}{x:8.3f}{y:8.3f}{z:8.3f}"
                lines.append(line)

            lines.append("   0.00000   0.00000   0.00000")

        return "\n".join(lines)
