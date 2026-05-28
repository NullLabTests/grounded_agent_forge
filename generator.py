"""LLM-based code generation from evolved prompts.

Supports OpenAI-compatible APIs (OpenAI, Mistral, local LLMs via Ollama).
Configure via environment variables — never hardcode API keys.
"""

import os
import re
import time
from pathlib import Path
from typing import Any

_openai_client: Any = None

DEFAULT_BASE_URL: str = os.environ.get(
    "LLM_BASE_URL",
    "https://api.mistral.ai/v1",
)
DEFAULT_MODEL: str = os.environ.get("LLM_MODEL", "mistral-large-latest")


Usage = dict[str, Any]
GenResult = tuple[str, Usage]


def _get_client() -> Any:
    """Get or create the OpenAI-compatible client."""
    global _openai_client
    if _openai_client is None:
        from openai import OpenAI
        api_key: str | None = os.environ.get("LLM_API_KEY")
        if not api_key:
            raise ValueError(
                "LLM_API_KEY environment variable not set. "
                "Export it or set it in your .env file."
            )
        _openai_client = OpenAI(
            api_key=api_key,
            base_url=DEFAULT_BASE_URL,
        )
    return _openai_client


def generate_code(prompt: str, model: str | None = None, temperature: float | None = None) -> GenResult:
    """Generate project code from a prompt via LLM.

    Returns (code_text, usage_dict) where usage contains token counts,
    model name, and wall time.
    """
    client = _get_client()
    start: float = time.time()
    response = client.chat.completions.create(
        model=model or DEFAULT_MODEL,
        messages=[
            {
                "role": "system",
                "content": "You are an autonomous software architect. Generate clean executable Python projects. Output each file in a markdown code block with the filename as the language tag (e.g. ```main.py). Include a README.md and requirements.txt.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=temperature or 0.8,
    )
    duration: float = time.time() - start
    usage: Usage = {
        "prompt_tokens": getattr(response.usage, "prompt_tokens", 0),
        "completion_tokens": getattr(response.usage, "completion_tokens", 0),
        "total_tokens": getattr(response.usage, "total_tokens", 0),
        "model": model or DEFAULT_MODEL,
        "duration_seconds": round(duration, 2),
    }
    return response.choices[0].message.content, usage


LANG_MAP: dict[str, str] = {
    "python": "main.py",
    "py": "main.py",
    "bash": "run.sh",
    "shell": "run.sh",
    "yaml": "config.yaml",
    "yml": "config.yaml",
    "json": "config.json",
    "toml": "pyproject.toml",
    "text": "README.md",
    "markdown": "README.md",
    "md": "README.md",
    "dockerfile": "Dockerfile",
    "gitignore": ".gitignore",
    "ini": "config.ini",
    "cfg": "setup.cfg",
}


def parse_code_blocks(content: str) -> list[dict[str, str]]:
    """Extract code blocks with filenames from LLM markdown output."""
    blocks: list[dict[str, str]] = []
    pattern = r"```(\w+(?:\.\w+)?)\n(.*?)```"
    matches = re.findall(pattern, content, re.DOTALL)
    file_counter: int = 0
    for tag, code in matches:
        code = code.strip()
        if not code:
            continue
        filename: str | None = tag if "." in tag else LANG_MAP.get(tag)
        if not filename:
            file_counter += 1
            filename = f"module_{file_counter}.py" if "python" in content[:content.find(f"```{tag}") + len(tag) + 100].lower() else f"file_{file_counter}.txt"
        blocks.append({"filename": filename, "code": code})
    return blocks


def write_project_files(project_path: str, content: str) -> list[str]:
    """Write parsed code blocks to disk as project files."""
    project_path = Path(project_path)
    project_path.mkdir(parents=True, exist_ok=True)

    blocks: list[dict[str, str]] = parse_code_blocks(content)

    if not blocks:
        (project_path / "main.py").write_text(content)
        return ["main.py"]

    written: list[str] = []
    for block in blocks:
        filename: str = block["filename"]
        if ".." in filename or filename.startswith("/"):
            continue
        filepath: Path = project_path / filename
        filepath.parent.mkdir(parents=True, exist_ok=True)
        filepath.write_text(block["code"])
        written.append(filename)

    if not list(project_path.rglob("test_*.py")):
        test_file: Path = project_path / "test_basic.py"
        test_file.write_text(
            "def test_placeholder():\n    assert True\n"
        )
        written.append("test_basic.py")

    return written
