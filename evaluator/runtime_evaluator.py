import ast
import os
import subprocess
import json
import sys
import tempfile
import time
import shutil
from pathlib import Path


def run_command(cmd, cwd=None, timeout=60, shell=True):
    try:
        start = time.time()
        result = subprocess.run(
            cmd if isinstance(cmd, list) else cmd,
            cwd=cwd,
            shell=shell,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        duration = time.time() - start
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "duration": duration,
            "returncode": result.returncode,
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "stdout": "",
            "stderr": f"Command timed out after {timeout}s",
            "duration": timeout,
            "returncode": -1,
        }
    except Exception as e:
        return {
            "success": False,
            "stdout": "",
            "stderr": str(e),
            "duration": 999,
            "returncode": -1,
        }


def parse_syntax(project_dir):
    errors = []
    files_found = 0
    for py_file in Path(project_dir).rglob("*.py"):
        files_found += 1
        try:
            with open(py_file) as f:
                ast.parse(f.read())
        except SyntaxError as e:
            errors.append({"file": str(py_file), "error": str(e)})
    return {"files": files_found, "errors": errors, "valid": len(errors) == 0 and files_found > 0}


def count_ast_nodes(project_dir):
    total_nodes = 0
    for py_file in Path(project_dir).rglob("*.py"):
        try:
            with open(py_file) as f:
                tree = ast.parse(f.read())
                total_nodes += sum(1 for _ in ast.walk(tree))
        except SyntaxError:
            pass
    return total_nodes


def count_functions_and_classes(project_dir):
    functions = 0
    classes = 0
    for py_file in Path(project_dir).rglob("*.py"):
        try:
            with open(py_file) as f:
                tree = ast.parse(f.read())
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    functions += 1
                elif isinstance(node, ast.ClassDef):
                    classes += 1
        except SyntaxError:
            pass
    return {"functions": functions, "classes": classes}


def evaluate_project(project_dir, timeout=30):
    score = 0.0
    metrics = {}

    syntax_result = parse_syntax(project_dir)
    metrics["syntax"] = syntax_result
    if syntax_result["valid"]:
        score += 20.0
        metrics["syntax_score"] = 20.0
    else:
        metrics["syntax_score"] = 0.0

    node_count = count_ast_nodes(project_dir)
    metrics["ast_nodes"] = node_count

    structure = count_functions_and_classes(project_dir)
    metrics["structure"] = structure
    if structure["functions"] >= 1:
        score += 5.0
    if structure["classes"] >= 1:
        score += 5.0

    try:
        pytest_result = run_command(
            "python -m pytest -x --tb=short --no-header -q",
            cwd=project_dir,
            timeout=timeout,
        )
        metrics["pytest"] = pytest_result
        if pytest_result["success"]:
            score += 25.0
            metrics["pytest_score"] = 25.0
        elif "collected 0" in pytest_result["stdout"]:
            metrics["pytest_score"] = 0.0
        else:
            metrics["pytest_score"] = -5.0
            score -= 5.0
    except Exception:
        metrics["pytest"] = {"success": False, "stderr": "pytest failed to run"}

    try:
        lint_result = run_command(
            f"{sys.executable} -m flake8 --select=E,F,W --max-line-length=120 .",
            cwd=project_dir,
            timeout=30,
        )
        metrics["lint"] = lint_result
        if lint_result["success"]:
            score += 10.0
            metrics["lint_score"] = 10.0
        else:
            metrics["lint_score"] = 0.0
    except Exception:
        metrics["lint"] = {"success": False, "stderr": "flake8 failed"}

    try:
        import_result = run_command(
            f"{sys.executable} -c \"import ast, sys; path='{project_dir}'; sys.path.insert(0, path); exec(open(f'{project_dir}/main.py').read())\"",
            timeout=15,
        )
        metrics["runtime"] = import_result
        if import_result["success"]:
            score += 15.0
            metrics["runtime_score"] = 15.0
    except Exception:
        metrics["runtime"] = {"success": False, "stderr": "runtime execution failed"}

    has_test_files = len(list(Path(project_dir).rglob("test_*.py"))) > 0
    metrics["has_tests"] = has_test_files
    if has_test_files:
        score += 5.0

    has_readme = (Path(project_dir) / "README.md").exists()
    metrics["has_readme"] = has_readme
    if has_readme:
        score += 2.0

    has_requirements = (Path(project_dir) / "requirements.txt").exists() or (Path(project_dir) / "pyproject.toml").exists()
    metrics["has_requirements"] = has_requirements
    if has_requirements:
        score += 3.0

    py_files = list(Path(project_dir).rglob("*.py"))
    metrics["file_count"] = len(py_files)
    if len(py_files) >= 3:
        score += 5.0
    elif len(py_files) >= 2:
        score += 3.0
    elif len(py_files) >= 1:
        score += 1.0

    metrics["final_score"] = round(score, 1)

    return metrics
