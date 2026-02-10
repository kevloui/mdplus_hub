from pathlib import Path

import mdtraj as md
import numpy as np

from src.glimps.file_parsers.base_parser import BaseMolecularParser, MolecularStructure


class PDBParser(BaseMolecularParser):
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
        atom_idx = 1

        for frame_idx in range(structure.n_frames):
            if structure.n_frames > 1:
                lines.append(f"MODEL     {frame_idx + 1}")

            for i in range(structure.n_atoms):
                x, y, z = structure.coordinates[frame_idx, i] * 10
                atom_name = structure.atom_names[i]
                res_name = structure.residue_names[i]
                res_id = structure.residue_ids[i] + 1

                line = (
                    f"ATOM  {atom_idx:5d} {atom_name:4s} {res_name:3s} A"
                    f"{res_id:4d}    {x:8.3f}{y:8.3f}{z:8.3f}"
                    f"  1.00  0.00          {atom_name[0]:>2s}"
                )
                lines.append(line)
                atom_idx += 1

            if structure.n_frames > 1:
                lines.append("ENDMDL")

        lines.append("END")
        return "\n".join(lines)
