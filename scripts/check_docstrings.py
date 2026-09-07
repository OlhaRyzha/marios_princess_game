import ast
import re
from pathlib import Path

CYRILLIC_PATTERN = re.compile(r"[А-Яа-яІіЇїЄєҐґ]")


def find_non_english_docstrings(source_root: Path) -> list[str]:
    violations: list[str] = []
    for path in sorted(source_root.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if not isinstance(
                node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)
            ):
                continue
            docstring = ast.get_docstring(node, clean=False)
            if docstring and CYRILLIC_PATTERN.search(docstring):
                line = getattr(node, "lineno", 1)
                violations.append(f"{path}:{line}")
    return violations


if __name__ == "__main__":
    invalid_docstrings = find_non_english_docstrings(Path("game"))
    if invalid_docstrings:
        locations = "\n".join(invalid_docstrings)
        raise SystemExit(f"Docstrings must be written in English:\n{locations}")
