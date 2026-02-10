from pathlib import Path

from src.glimps.file_parsers.base_parser import BaseMolecularParser
from src.glimps.file_parsers.gro_parser import GROParser
from src.glimps.file_parsers.pdb_parser import PDBParser
from src.infrastructure.database.models.molecule import FileFormat


class ParserFactory:
    _parsers: dict[FileFormat, type[BaseMolecularParser]] = {
        FileFormat.PDB: PDBParser,
        FileFormat.GRO: GROParser,
    }

    @classmethod
    def get_parser(cls, file_path: Path) -> BaseMolecularParser:
        extension = file_path.suffix.lower().lstrip(".")
        try:
            file_format = FileFormat(extension)
        except ValueError:
            raise ValueError(f"Unsupported file format: {extension}")

        parser_class = cls._parsers.get(file_format)
        if parser_class is None:
            raise ValueError(f"No parser registered for format: {extension}")

        return parser_class()

    @classmethod
    def get_parser_for_format(cls, file_format: FileFormat) -> BaseMolecularParser:
        parser_class = cls._parsers.get(file_format)
        if parser_class is None:
            raise ValueError(f"No parser registered for format: {file_format}")

        return parser_class()

    @classmethod
    def register_parser(
        cls,
        file_format: FileFormat,
        parser_class: type[BaseMolecularParser],
    ) -> None:
        cls._parsers[file_format] = parser_class

    @classmethod
    def supported_formats(cls) -> list[FileFormat]:
        return list(cls._parsers.keys())
