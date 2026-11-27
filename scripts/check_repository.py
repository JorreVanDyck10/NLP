"""Controleer de repository zonder dependencies of modeldownloads."""

import json
import re
import subprocess
import sys
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
ROOT_FILES = {"README.md", "AGENTS.md", "CONTRIBUTING.md", ".gitignore", ".env.example"}
ROOT_DIRECTORIES = {"docs", "data", "reports", "scripts", ".github"}
REQUIRED_FILES = {
    "README.md", "AGENTS.md", "CONTRIBUTING.md", ".gitignore", "docs/README.md",
    ".github/pull_request_template.md", ".github/workflows/repository-check.yml",
}
# Bestandslinks in de eenvoudige inline-notatie die deze repository gebruikt.
MARKDOWN_LINK = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")


def check_repository():
    result = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        cwd=ROOT, check=True, stdout=subprocess.PIPE,
    )
    names = sorted(set(result.stdout.decode("utf-8").split("\0")) - {""})
    # --no-index detecteert ook lokale bestanden die toch geforceerd gevolgd worden.
    ignored_result = subprocess.run(
        ["git", "check-ignore", "--no-index", "--stdin", "-z"],
        cwd=ROOT, input=("\0".join(names) + "\0").encode("utf-8"),
        stdout=subprocess.PIPE,
    )
    if ignored_result.returncode not in (0, 1):
        raise RuntimeError("De .gitignore-controle kon niet worden uitgevoerd")
    ignored = set(ignored_result.stdout.decode("utf-8").split("\0"))
    errors = [f"{name}: verplicht bestand ontbreekt" for name in sorted(REQUIRED_FILES)
              if not (ROOT / name).is_file()]
    checked = 0
    for name in names:
        path = ROOT / name
        # Een nog niet gestagede verhuizing laat het oude pad in de index staan.
        if not path.exists():
            continue
        checked += 1
        parts = PurePosixPath(name).parts
        filename = parts[-1]
        root_file_allowed = (
            filename in ROOT_FILES or filename.endswith(".py")
            or re.fullmatch(r"requirements(?:-[a-z0-9-]+)?\.txt", filename)
        )
        if (len(parts) == 1 and not root_file_allowed) or (
            len(parts) > 1 and parts[0] not in ROOT_DIRECTORIES
        ):
            errors.append(f"{name}: past niet in de afgesproken rootindeling")
        if name in ignored:
            errors.append(f"{name}: uitgesloten door .gitignore; hoort niet in Git")
        try:
            if path.suffix == ".py":
                # compile schrijft geen __pycache__ en importeert geen dependencies.
                compile(path.read_bytes(), name, "exec")
            elif path.suffix == ".json":
                json.loads(path.read_text(encoding="utf-8"))
            elif path.suffix == ".md":
                text = path.read_text(encoding="utf-8")
                # Voorbeelden in codeblokken zijn geen navigatielinks.
                text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
                for match in MARKDOWN_LINK.finditer(text):
                    target = match.group(1).strip().split(' "', 1)[0].strip("<>")
                    link = urlsplit(target)
                    if link.scheme or link.netloc or not link.path:
                        continue
                    destination = (path.parent / unquote(link.path)).resolve()
                    if not destination.is_relative_to(ROOT) or not destination.exists():
                        errors.append(f"{name}: ongeldige lokale link: {target}")
        except (OSError, UnicodeError, ValueError, SyntaxError) as exc:
            errors.append(f"{name}: {exc}")
    if errors:
        print("Repositorycontrole mislukt:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"Repositorycontrole geslaagd ({checked} bestanden): structuur, links, Python en JSON.")
    return 0


if __name__ == "__main__":
    sys.exit(check_repository())
