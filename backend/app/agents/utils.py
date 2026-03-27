from __future__ import annotations

import json
import re
import tomllib
from pathlib import PurePosixPath


CODE_EXTENSIONS = {
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".java",
    ".go",
    ".rs",
    ".rb",
    ".php",
    ".cs",
    ".cpp",
    ".c",
    ".h",
    ".hpp",
    ".swift",
    ".kt",
    ".scala",
}
DOC_EXTENSIONS = {".md", ".rst", ".txt"}
CONFIG_EXTENSIONS = {".json", ".yaml", ".yml", ".toml", ".ini", ".cfg"}
CONFIG_FILENAMES = {
    "dockerfile",
    "docker-compose.yml",
    ".gitignore",
    ".env.example",
}
TEST_DIRECTORY_MARKERS = ("test/", "tests/", "__tests__/")
CI_MARKERS = (".github/workflows/", ".gitlab-ci.yml", "azure-pipelines", ".circleci/")


def clamp_score(score: float) -> float:
    return max(0.0, min(100.0, round(score, 2)))


def is_test_file(path: str) -> bool:
    lower = path.lower()
    name = PurePosixPath(path).name.lower()
    return (
        lower.startswith(TEST_DIRECTORY_MARKERS)
        or "/tests/" in lower
        or "/test/" in lower
        or "/__tests__/" in lower
        or name.startswith("test_")
        or name.endswith(("_test.py", ".test.js", ".test.ts", ".spec.js", ".spec.ts", ".spec.tsx"))
    )


def is_code_file(path: str) -> bool:
    suffix = PurePosixPath(path).suffix.lower()
    return suffix in CODE_EXTENSIONS and not is_test_file(path)


def is_doc_file(path: str) -> bool:
    suffix = PurePosixPath(path).suffix.lower()
    return suffix in DOC_EXTENSIONS or PurePosixPath(path).name.lower().startswith("readme")


def is_config_file(path: str) -> bool:
    name = PurePosixPath(path).name.lower()
    suffix = PurePosixPath(path).suffix.lower()
    return suffix in CONFIG_EXTENSIONS or name in CONFIG_FILENAMES


def is_ci_file(path: str) -> bool:
    lower = path.lower()
    return lower.endswith(".gitlab-ci.yml") or any(marker in lower for marker in CI_MARKERS)


def prioritize_paths(paths: list[str]) -> list[str]:
    def score(path: str) -> tuple[int, str]:
        lower = path.lower()
        name = PurePosixPath(path).name.lower()
        priority = 0
        if name.startswith("readme"):
            priority += 5
        if lower.startswith(("src/", "app/", "lib/")):
            priority += 4
        if is_test_file(path):
            priority += 3
        if is_config_file(path):
            priority += 2
        if is_ci_file(path):
            priority += 1
        return (-priority, lower)

    return sorted(paths, key=score)


def snippet_for_prompt(path: str, content: str, max_chars: int = 3500) -> str:
    trimmed = content[:max_chars]
    return f"FILE: {path}\n```text\n{trimmed}\n```"


def build_prompt_context(file_contents: dict[str, str], paths: list[str], max_files: int = 10) -> str:
    selected = prioritize_paths(paths)[:max_files]
    return "\n\n".join(
        snippet_for_prompt(path, file_contents[path])
        for path in selected
        if path in file_contents
    )


def extract_dependencies(file_contents: dict[str, str]) -> list[str]:
    dependencies: set[str] = set()

    for path, content in file_contents.items():
        name = PurePosixPath(path).name.lower()

        if name == "requirements.txt":
            for line in content.splitlines():
                cleaned = line.strip()
                if not cleaned or cleaned.startswith("#"):
                    continue
                dependencies.add(re.split(r"[<>=!~\[]", cleaned, maxsplit=1)[0].strip())

        elif name == "package.json":
            try:
                payload = json.loads(content)
            except json.JSONDecodeError:
                continue
            for section in ("dependencies", "devDependencies", "peerDependencies"):
                dependencies.update((payload.get(section) or {}).keys())

        elif name == "pyproject.toml":
            try:
                payload = tomllib.loads(content)
            except tomllib.TOMLDecodeError:
                continue
            project = payload.get("project", {})
            for item in project.get("dependencies", []):
                dependencies.add(re.split(r"[<>=!~\[]", item, maxsplit=1)[0].strip())
            poetry = payload.get("tool", {}).get("poetry", {})
            for dep_name in (poetry.get("dependencies") or {}).keys():
                if dep_name != "python":
                    dependencies.add(dep_name)

        elif name == "go.mod":
            for line in content.splitlines():
                stripped = line.strip()
                if stripped.startswith("require "):
                    candidate = stripped.replace("require ", "", 1).strip()
                    dependencies.add(candidate.split()[0])

    return sorted(dep for dep in dependencies if dep)


def build_result(score: float, strengths: list[str], improvements: list[str], details: str) -> dict[str, object]:
    return {
        "score": clamp_score(score),
        "strengths": strengths,
        "improvements": improvements,
        "details": details,
    }


def fallback_code_analysis(file_contents: dict[str, str], code_paths: list[str]) -> dict[str, object]:
    score = 45.0
    strengths: list[str] = []
    improvements: list[str] = []
    total_lines = 0
    has_error_handling = False
    has_types = False

    for path in code_paths:
        content = file_contents.get(path, "")
        total_lines += len(content.splitlines())
        if "try:" in content or "except " in content or "catch (" in content:
            has_error_handling = True
        if re.search(r"def .+\) -> ", content) or re.search(r": [A-Z_a-z][A-Za-z0-9_.\\[\\]| ]+", content):
            has_types = True

    if code_paths:
        score += min(20.0, len(code_paths) * 2.5)
        strengths.append(f"{len(code_paths)} arquivos de codigo relevantes foram identificados.")
    else:
        improvements.append("Nenhum arquivo de codigo representativo foi encontrado para analise.")

    if has_error_handling:
        score += 10
        strengths.append("Ha sinais de tratamento explicito de erros em pontos do codigo.")
    else:
        improvements.append("Reforce o tratamento de erros com caminhos de falha mais claros.")

    if has_types:
        score += 8
        strengths.append("O codigo aparenta usar type hints ou assinaturas mais explicitas.")
    else:
        improvements.append("Adicione contratos mais claros, como tipos, validacoes e interfaces.")

    if total_lines > 2000:
        score -= 5
        improvements.append("O volume de codigo sugere revisar modulos longos e responsabilidades amplas.")

    details = (
        "Fallback heuristico usado para qualidade de codigo. "
        f"Foram considerados {len(code_paths)} arquivos e aproximadamente {total_lines} linhas."
    )
    return build_result(score, strengths, improvements, details)


def fallback_docs_analysis(file_contents: dict[str, str], doc_paths: list[str], code_paths: list[str]) -> dict[str, object]:
    score = 20.0
    strengths: list[str] = []
    improvements: list[str] = []

    readme_path = next((path for path in doc_paths if PurePosixPath(path).name.lower().startswith("readme")), None)
    if readme_path:
        score += 35
        readme_content = file_contents.get(readme_path, "").lower()
        strengths.append("O repositorio possui README principal.")
        if "install" in readme_content or "instal" in readme_content:
            score += 10
            strengths.append("O README inclui instrucoes de instalacao.")
        else:
            improvements.append("Inclua instrucoes de instalacao e setup no README.")
        if "usage" in readme_content or "exemplo" in readme_content or "example" in readme_content:
            score += 10
            strengths.append("O README parece trazer orientacao de uso ou exemplos.")
        else:
            improvements.append("Adicione exemplos de uso ou fluxos de execucao no README.")
    else:
        improvements.append("Adicione um README.md com contexto, instalacao e uso.")

    for optional_file in ("changelog.md", "contributing.md", "license"):
        if optional_file in {PurePosixPath(path).name.lower() for path in doc_paths}:
            score += 5

    docstring_hits = 0
    for path in code_paths[:10]:
        content = file_contents.get(path, "")
        docstring_hits += content.count('"""') + content.count("/**")
    if docstring_hits:
        score += min(20.0, docstring_hits * 2.0)
        strengths.append("Ha sinais de docstrings ou comentarios estruturados no codigo.")
    else:
        improvements.append("Adicione docstrings ou comentarios para fluxos nao triviais.")

    details = (
        "Fallback heuristico usado para documentacao. "
        f"Foram avaliados {len(doc_paths)} arquivos de docs e {len(code_paths)} arquivos de codigo."
    )
    return build_result(score, strengths, improvements, details)


def fallback_tests_analysis(file_contents: dict[str, str], test_paths: list[str], code_paths: list[str]) -> dict[str, object]:
    score = 10.0
    strengths: list[str] = []
    improvements: list[str] = []

    if test_paths:
        ratio = len(test_paths) / max(len(code_paths), 1)
        score += 40
        score += min(20.0, ratio * 25)
        strengths.append(f"{len(test_paths)} arquivos de teste foram encontrados.")
        assertion_hits = sum(
            file_contents.get(path, "").lower().count("assert") + file_contents.get(path, "").lower().count("expect(")
            for path in test_paths[:10]
        )
        if assertion_hits:
            score += 10
            strengths.append("Os testes aparentam conter assercoes explicitas.")
        else:
            improvements.append("Revise a profundidade das assercoes e cubra casos limite.")
    else:
        improvements.append("Adicione testes automatizados para reduzir regressao.")

    if any(is_ci_file(path) for path in file_contents):
        score += 10
        strengths.append("Ha arquivos de CI/CD que podem orquestrar execucao de testes.")
    else:
        improvements.append("Configure CI/CD para executar testes continuamente.")

    details = (
        "Fallback heuristico usado para testes. "
        f"Foram comparados {len(test_paths)} arquivos de teste e {len(code_paths)} arquivos de codigo."
    )
    return build_result(score, strengths, improvements, details)


def fallback_security_analysis(file_contents: dict[str, str], all_paths: list[str]) -> dict[str, object]:
    score = 35.0
    strengths: list[str] = []
    improvements: list[str] = []

    combined_text = "\n".join(file_contents.values()).lower()
    secret_pattern = re.compile(r"(api[_-]?key|secret|token|password)\s*[:=]\s*[\"'][^\"']+[\"']")
    if secret_pattern.search(combined_text):
        score -= 35
        improvements.append("Foram encontrados sinais de credenciais hardcoded; revise secrets imediatamente.")
    else:
        score += 15
        strengths.append("Nao foram encontrados indicios obvios de credenciais hardcoded nas amostras.")

    lower_paths = {path.lower() for path in all_paths}
    if ".gitignore" in lower_paths:
        score += 10
        strengths.append("O repositorio inclui .gitignore.")
    else:
        improvements.append("Adicione .gitignore para evitar vazamento de arquivos sensiveis.")

    if ".env.example" in lower_paths or any(path.lower().endswith("settings.py") for path in all_paths):
        score += 10
        strengths.append("Ha sinais de configuracao baseada em ambiente.")
    else:
        improvements.append("Documente variaveis de ambiente em .env.example.")

    details = (
        "Fallback heuristico usado para seguranca. "
        "A analise cobriu secrets aparentes, higiene de configuracao e sinais de protecao operacional."
    )
    return build_result(score, strengths, improvements, details)


def structure_analysis(file_tree: list[str], file_contents: dict[str, str]) -> dict[str, object]:
    score = 40.0
    strengths: list[str] = []
    improvements: list[str] = []
    root_entries = {path.split("/", 1)[0] for path in file_tree}

    if any(entry in root_entries for entry in ("src", "app", "lib")):
        score += 20
        strengths.append("O codigo principal parece estar organizado em um diretorio dedicado.")
    else:
        improvements.append("Considere centralizar o codigo em src/, app/ ou lib/ para reduzir dispersao.")

    if "tests" in root_entries or "test" in root_entries:
        score += 12
        strengths.append("Ha separacao explicita para testes.")
    else:
        improvements.append("Separe os testes em um diretorio proprio.")

    if any(path.lower().startswith(".github/workflows/") for path in file_tree):
        score += 8
        strengths.append("O repositorio inclui automacao de workflow.")

    if len(root_entries) > 12:
        score -= 6
        improvements.append("Ha muitos itens no nivel raiz; simplifique a estrutura inicial.")

    if any(PurePosixPath(path).name.lower().startswith("readme") for path in file_tree):
        score += 8

    details = (
        "Estrutura calculada heuristically a partir da arvore do repositorio e artefatos encontrados. "
        f"Foram observados {len(root_entries)} agrupamentos principais na raiz."
    )
    return build_result(score, strengths, improvements, details)
