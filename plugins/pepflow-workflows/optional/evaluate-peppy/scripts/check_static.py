#!/usr/bin/env python3
"""Check approved sources in a disposable project, without ancestor tool settings.

This is an instruction-based resolution adapter, not an OS access sandbox. Use a
reviewed Python environment: installed packages and interpreter startup hooks are
trusted inputs. Evidence records resolution probes, not an exhaustive read audit.
Exit codes: 0 passed, 1 real source diagnostics, 2 operational/preflight failure.
"""

import argparse
import hashlib
import json
import os
import re
import shutil
import signal
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, TypedDict


class ProcessOptions(TypedDict, total=False):
    creationflags: int
    start_new_session: bool


class OperationalError(Exception):
    """The approved checking route could not be established."""


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def within(path, root):
    return path == root or root in path.parents


def checked_path(value, root=None, directory=False):
    path = Path(value).absolute()
    resolved = path.resolve(strict=True)
    if path != resolved or any(p.is_symlink() for p in [path, *path.parents]):
        raise OperationalError(f"Linked paths are not supported: {path}")
    if root is not None and not within(resolved, root):
        raise OperationalError(f"Path is outside attempt root: {resolved}")
    if directory != resolved.is_dir():
        raise OperationalError(f"Unexpected file/directory type: {resolved}")
    return resolved


def copy_source(source, target, manifest):
    source = checked_path(source)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)
    manifest.append(
        {"source": str(source), "staged": str(target), "sha256": digest(source)}
    )


def copy_python_tree(source, target, manifest):
    # No workflow trees, data, caches, results, or browser profiles are copied.
    count = 0
    for current, directories, files in os.walk(source, followlinks=False):
        directories[:] = [
            name
            for name in directories
            if not name.startswith(".") and name != "__pycache__"
        ]
        for name in directories:
            checked_path(Path(current) / name, directory=True)
        for name in files:
            item = Path(current) / name
            if item.suffix not in {".py", ".pyi"} and name != "py.typed":
                continue
            count += 1
            if count > 2000:
                raise OperationalError(
                    "Source scope exceeds 2000 files; select a narrower approved root"
                )
            copy_source(item, target / item.relative_to(source), manifest)


def run_command(command, cwd, env, evidence, label, timeout):
    row: dict[str, Any] = {
        "label": label,
        "command": [str(x) for x in command],
        "cwd": str(cwd),
    }
    evidence["commands"].append(row)
    options: ProcessOptions = (
        {"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP}
        if os.name == "nt"
        else {"start_new_session": True}
    )
    # Avoid Popen's context manager: its final wait is unbounded if termination
    # itself is denied or broken. Keep the owned PID in evidence in that case.
    process = subprocess.Popen(
        row["command"],
        cwd=cwd,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        **options,
    )
    assert process.stdout is not None and process.stderr is not None
    try:
        stdout, stderr = process.communicate(timeout=timeout)
    except subprocess.TimeoutExpired as error:
        row.update(timed_out=True, owned_pid=process.pid, cleanup_errors=[])
        try:
            # A fresh Jupyter kernel is a descendant: killing just the launcher
            # would leave it alive and could keep its private files locked.
            if os.name == "nt":
                termination = [
                    str(Path(os.environ["SystemRoot"]) / "System32" / "taskkill.exe"),
                    "/PID",
                    str(process.pid),
                    "/T",
                    "/F",
                ]
                killed = subprocess.run(termination, capture_output=True, timeout=10)
                row["termination"] = {
                    "command": termination,
                    "returncode": killed.returncode,
                }
                row["descendant_cleanup_confirmed"] = killed.returncode == 0
            else:
                os.killpg(process.pid, signal.SIGKILL)
                row["termination"] = {"process_group": process.pid, "signal": "SIGKILL"}
                row["descendant_cleanup_confirmed"] = True
        except (OSError, subprocess.SubprocessError) as cleanup_error:
            row["cleanup_errors"].append(str(cleanup_error))
            row["descendant_cleanup_confirmed"] = False
        try:
            if process.poll() is None:
                process.kill()
            stdout, stderr = process.communicate(timeout=10)
            process.stdout.close()
            process.stderr.close()
        except (OSError, subprocess.SubprocessError) as cleanup_error:
            row["cleanup_errors"].append(str(cleanup_error))
            row["descendant_cleanup_confirmed"] = False
            stdout, stderr = error.stdout or "", error.stderr or ""
        row.update(
            returncode=process.poll(),
            stdout=stdout.decode("utf-8", "replace")
            if isinstance(stdout, bytes)
            else stdout,
            stderr=stderr.decode("utf-8", "replace")
            if isinstance(stderr, bytes)
            else stderr,
        )
        raise OperationalError(
            f"{label} exceeded its operation timeout; see owned-PID cleanup evidence"
        ) from error
    process.stdout.close()
    process.stderr.close()
    result = subprocess.CompletedProcess(
        row["command"], process.returncode, stdout, stderr
    )
    row.update(returncode=result.returncode, stdout=result.stdout, stderr=result.stderr)
    return result


def notebook(cells):
    return {
        "nbformat": 4,
        "nbformat_minor": 5,
        "metadata": {
            "kernelspec": {
                "name": "peppy-probe",
                "display_name": "Peppy probe",
                "language": "python",
            }
        },
        "cells": [
            {
                "cell_type": "code",
                "id": f"probe-{i}",
                "metadata": {},
                "execution_count": None,
                "outputs": [],
                "source": source,
            }
            for i, source in enumerate(cells)
        ],
    }


def verify_search_paths(output, roots, site_paths):
    # Full ty 0.0.82 diagnostics enumerate every effective resolution path on a
    # missing import. Fail closed if the version changes that evidence format.
    rows = re.findall(r"^info:\s+\d+\. (.+?) \((.+?)\)\s*$", output, re.MULTILINE)
    if not rows:
        raise OperationalError(
            "ty did not expose its resolution paths in the missing-module probe"
        )
    observed_first_party = set()
    for value, kind in rows:
        if (
            value == "vendored://stdlib"
            and kind == "stdlib typeshed stubs vendored by ty"
        ):
            continue
        path = Path(value).resolve()
        if kind == "first-party code" and path in roots:
            observed_first_party.add(path)
        elif kind == "site-packages" and path in site_paths:
            continue
        else:
            raise OperationalError(f"Unexpected ty resolution route: {value} ({kind})")
    if observed_first_party != set(roots):
        raise OperationalError(
            "ty's effective first-party roots differ from the declared roots"
        )
    return [{"path": value, "kind": kind} for value, kind in rows]


def perform(args, evidence):
    attempt = checked_path(args.attempt_root, directory=True)
    executables = {}
    for name in ("python", "ruff", "ty"):
        value = getattr(args, name)
        if not Path(value).is_absolute():
            raise OperationalError(
                f"--{name} must be a pinned absolute executable path"
            )
        executables[name] = checked_path(value)
    helpers = [checked_path(p, attempt, directory=True) for p in args.helper_root]
    if attempt in helpers:
        raise OperationalError(
            "Select narrow helper directories, not the whole attempt"
        )
    packages = [checked_path(p, directory=True) for p in args.approved_package]
    names = [p.name for p in packages]
    if (
        len(names) != len(set(names))
        or args.framework_module.split(".")[0] not in names
    ):
        raise OperationalError(
            "Provide distinct approved package directories including the framework"
        )
    for package in packages:
        if not (package / "__init__.py").is_file():
            raise OperationalError(
                f"Expected a package directory, not its repository parent: {package}"
            )
    targets = [checked_path(p, attempt) for p in args.targets]
    if any(p.suffix not in {".py", ".pyi", ".ipynb"} for p in targets):
        raise OperationalError("Targets must be Python sources or Jupyter notebooks")
    if args.mode == "check" and not targets:
        raise OperationalError("check requires explicit notebook/setup targets")

    runtime_root = attempt / "supplementary" / ".runtime"
    for directory in (runtime_root.parent, runtime_root):
        directory.mkdir(exist_ok=True)
        checked_path(directory, attempt, directory=True)
    with tempfile.TemporaryDirectory(
        prefix="static-check-", dir=runtime_root
    ) as temporary:
        stage = Path(temporary).resolve()
        evidence["temporary_root"] = str(stage)
        source_root, generic_root = stage / "source", stage / "approved"
        source_root.mkdir()
        generic_root.mkdir()
        manifest = evidence["sources"] = []
        for package in packages:
            copy_python_tree(package, generic_root / package.name, manifest)
        staged_helpers = []
        if args.mode == "check":
            for helper in helpers:
                destination = source_root / helper.relative_to(attempt)
                copy_python_tree(helper, destination, manifest)
                destination.mkdir(parents=True, exist_ok=True)
                staged_helpers.append(destination)
            for target in targets:
                copy_source(target, source_root / target.relative_to(attempt), manifest)

        # The generic notebook uses FEG's `from runtime import ...` shape, with
        # the helper in a separate directory, without executing actual setup code.
        probe_root = stage / "probe"
        probe_root.mkdir()
        probe_helpers = [probe_root / p.relative_to(attempt) for p in helpers]
        for directory in probe_helpers:
            directory.mkdir(parents=True, exist_ok=True)
        probe_file = probe_root / args.probe_helper_path
        if not within(probe_file.resolve(), probe_root):
            raise OperationalError(
                "The generic helper layout escaped its private probe directory"
            )
        probe_file.parent.mkdir(parents=True, exist_ok=True)
        probe_file.write_text("VALUE: int = 7\n", encoding="utf-8")
        probe_roots = list(dict.fromkeys([probe_root, *probe_helpers, generic_root]))
        real_roots = list(dict.fromkeys([source_root, *staged_helpers, generic_root]))
        roots = real_roots if args.mode == "check" else probe_roots
        evidence["declared_roots"] = [str(p) for p in roots]
        evidence["helper_roots"] = [str(p) for p in helpers]
        evidence["approved_packages"] = [str(p) for p in packages]
        (stage / "pyproject.toml").write_text(
            '[project]\nname = "peppy-static-scope"\nversion = "0.0.0"\n',
            encoding="utf-8",
        )
        cache = stage / "cache"
        cache.mkdir()
        env = {
            key: value
            for key, value in os.environ.items()
            if not key.upper().startswith(
                ("PYTHON", "TY_", "RUFF_", "JUPYTER", "IPYTHON")
            )
            and key not in {"VIRTUAL_ENV", "CONDA_PREFIX"}
        }
        for key in (
            "TMP",
            "TEMP",
            "TMPDIR",
            "XDG_CACHE_HOME",
            "IPYTHONDIR",
            "MPLCONFIGDIR",
            "JUPYTER_RUNTIME_DIR",
            "JUPYTER_CONFIG_DIR",
            "PYTHONPYCACHEPREFIX",
        ):
            location = cache / key.lower()
            location.mkdir()
            env[key] = str(location)
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        env["PYTHONIOENCODING"] = "utf-8"
        env["JUPYTER_PATH"] = str(cache / "jupyter")
        env["JUPYTER_NO_CONFIG"] = "1"
        evidence["private_environment"] = {
            key: value
            for key, value in env.items()
            if str(value).startswith(str(cache))
        }

        def execute(command, label):
            return run_command(command, stage, env, evidence, label, args.timeout)

        evidence["tools"] = {}
        for name, path in executables.items():
            result = execute([path, "--version"], f"{name}_version")
            if result.returncode:
                raise OperationalError(f"Cannot determine {name} version")
            evidence["tools"][name] = {
                "path": str(path),
                "sha256": digest(path),
                "version": (result.stdout + result.stderr).strip(),
            }
        if args.expect_ty_version and not evidence["tools"]["ty"]["version"].startswith(
            "ty " + args.expect_ty_version + " "
        ):
            raise OperationalError(
                "ty version differs from the frozen expected version"
            )
        python_info = execute(
            [
                executables["python"],
                "-I",
                "-B",
                "-c",
                "import json,sys,sysconfig,importlib.metadata; print(json.dumps({'executable':sys.executable,"
                "'paths':sys.path,'site_paths':list(set([sysconfig.get_path('purelib'),"
                "sysconfig.get_path('platlib')])), 'distribution_versions':"
                "{d.metadata['Name']:d.version for d in importlib.metadata.distributions()}}))",
            ],
            "python_environment",
        )
        if python_info.returncode:
            raise OperationalError("Cannot inspect the pinned Python environment")
        evidence["python_environment"] = json.loads(python_info.stdout)
        site_paths = {
            Path(p).resolve() for p in evidence["python_environment"]["site_paths"]
        }

        # Inspect real analysis precedence without importing any generated code.
        # Python import discovery ignores .pyi files, so check those separately.
        framework_name, dependency_name = (
            args.framework_module.split(".")[0],
            args.dependency.split(".")[0],
        )
        for name in [*names, dependency_name]:
            for root in roots:
                if root == generic_root and name in names and name != dependency_name:
                    continue
                for candidate in (
                    root / (name + ".py"),
                    root / (name + ".pyi"),
                    root / name,
                ):
                    if candidate.exists():
                        raise OperationalError(
                            f"Generated/source path shadows an approved module: {candidate}"
                        )
        lookup = (
            "import importlib.machinery,json,sys\n"
            f"roots={repr([str(p) for p in roots])}\n"
            f"names={repr([framework_name, dependency_name])}\n"
            "found={name:importlib.machinery.PathFinder.find_spec(name,roots+sys.path) for name in names}\n"
            "print(json.dumps({name:(spec.origin if spec else None) for name,spec in found.items()}))\n"
        )
        lookup_result = execute(
            [executables["python"], "-I", "-B", "-c", lookup],
            "source_origin_probe_no_execution",
        )
        if lookup_result.returncode:
            raise OperationalError("Cannot establish actual source/module precedence")
        source_origins = json.loads(lookup_result.stdout)
        expected_origins = {
            framework_name: [generic_root / framework_name],
            dependency_name: list(site_paths),
        }
        for name, permitted in expected_origins.items():
            origin = source_origins.get(name)
            if not origin or not any(
                within(Path(origin).resolve(), root) for root in permitted
            ):
                raise OperationalError(
                    f"Unexpected non-executing module origin for {name}: {origin}"
                )
        evidence["source_module_origins_without_execution"] = source_origins

        def ty_command(check_roots, paths, label):
            config = (
                "[environment]\nroot = "
                + json.dumps([str(p) for p in check_roots])
                + "\n"
            )
            config_path = stage / (label + ".toml")
            config_path.write_text(config, encoding="utf-8")
            evidence.setdefault("configurations", {})[str(config_path)] = config
            return [
                executables["ty"],
                "check",
                "--project",
                stage,
                "--config-file",
                config_path,
                "--python",
                executables["python"],
                "--color",
                "never",
                "--no-progress",
                "--no-respect-ignore-files",
                *paths,
            ]

        missing = stage / "missing_probe.py"
        missing_name = "peppy_intentionally_missing_resolution_probe_21e74a"
        missing.write_text(f"import {missing_name}\n", encoding="utf-8")
        resolution = execute(
            ty_command(roots, [missing], "resolution"), "missing_module_probe"
        )
        output = resolution.stdout + resolution.stderr
        if (
            resolution.returncode != 1
            or f"Cannot resolve imported module `{missing_name}`" not in output
        ):
            raise OperationalError(
                "Expected missing-module diagnostic was not produced"
            )
        evidence["effective_resolution_paths"] = verify_search_paths(
            output, roots, site_paths
        )

        framework, dependency = args.framework_module, args.dependency
        bootstrap = (
            "import sys\nsys.path[:0] = " + repr([str(p) for p in probe_roots]) + "\n"
        )
        imported = (
            f"import json\nfrom pathlib import Path\nimport {probe_file.stem} as runtime\n"
            f"import {framework} as framework\nimport {dependency} as dependency\n"
            "assert runtime.VALUE == 7\n"
            "locations = {'helper': str(Path(runtime.__file__).resolve()), "
            "'framework': str(Path(framework.__file__).resolve()), "
            "'dependency': str(Path(dependency.__file__).resolve())}\n"
            "print(json.dumps(locations))\n"
        )
        probe_notebook = probe_root / "preflight.ipynb"
        probe_notebook.write_text(
            json.dumps(notebook([bootstrap, imported])), encoding="utf-8"
        )
        ruff_base = [
            executables["ruff"],
            "check",
            "--isolated",
            "--no-cache",
            "--output-format",
            "full",
        ]
        for command, label in [
            (ruff_base + [probe_notebook, probe_file], "preflight_ruff"),
            (
                ty_command(probe_roots, [probe_notebook, probe_file], "preflight"),
                "preflight_ty",
            ),
        ]:
            if execute(command, label).returncode:
                raise OperationalError(f"Generic import preflight failed: {label}")
        kernel_dir = cache / "jupyter" / "kernels" / "peppy-probe"
        kernel_dir.mkdir(parents=True)
        (kernel_dir / "kernel.json").write_text(
            json.dumps(
                {
                    "argv": [
                        str(executables["python"]),
                        "-I",
                        "-B",
                        "-m",
                        "ipykernel_launcher",
                        "-f",
                        "{connection_file}",
                    ],
                    "display_name": "Peppy isolated probe",
                    "language": "python",
                }
            ),
            encoding="utf-8",
        )
        runner = (
            "import json,nbformat\nfrom nbclient import NotebookClient\n"
            f"nb=nbformat.read({str(probe_notebook)!r},as_version=4)\n"
            f"NotebookClient(nb,timeout={max(1, args.timeout - 15)},kernel_name='peppy-probe',"
            f"resources={{'metadata':{{'path':{str(probe_root)!r}}}}}).execute()\n"
            "print(json.dumps([o.get('text','') for c in nb.cells for o in c.get('outputs',[]) "
            "if o.get('output_type')=='stream']))\n"
        )
        runtime = execute(
            [executables["python"], "-I", "-B", "-c", runner],
            "clean_kernel_import_probe",
        )
        if runtime.returncode:
            raise OperationalError("Clean-kernel import probe failed")
        streams = json.loads(runtime.stdout)
        origins = json.loads("".join(streams))
        if Path(origins["helper"]) != probe_file:
            raise OperationalError("The runtime helper was shadowed")
        if not within(
            Path(origins["framework"]), generic_root / framework.split(".")[0]
        ):
            raise OperationalError(
                "The framework was resolved outside the approved staged package"
            )
        if not any(within(Path(origins["dependency"]), p) for p in site_paths):
            raise OperationalError(
                "The installed dependency was shadowed or resolved outside the pinned environment"
            )
        evidence["runtime_import_origins"] = origins
        evidence["preflight_passed"] = True
        if args.mode == "check":
            staged_targets = [source_root / p.relative_to(attempt) for p in targets]
            checks = [
                execute(ruff_base + staged_targets, "source_ruff"),
                execute(ty_command(real_roots, staged_targets, "source"), "source_ty"),
            ]
            if any(result.returncode not in (0, 1) for result in checks):
                raise OperationalError(
                    "A required source check had a tool execution error"
                )
            evidence["status"] = (
                "checks_failed" if any(r.returncode for r in checks) else "passed"
            )
        else:
            evidence["status"] = "passed"
    evidence["temporary_scope_removed"] = not stage.exists()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("preflight", "check"))
    for name in ("python", "ruff", "ty", "attempt-root", "evidence"):
        parser.add_argument("--" + name, required=True)
    parser.add_argument(
        "--approved-package",
        action="append",
        required=True,
        help="Reviewed generic Python package directory (e.g. /approved/pepflow)",
    )
    parser.add_argument(
        "--helper-root",
        action="append",
        default=[],
        help="Attempt-owned helper source directory; repeat for multiple roots",
    )
    parser.add_argument("--framework-module", default="pepflow")
    parser.add_argument("--dependency", default="numpy")
    parser.add_argument(
        "--probe-helper-path",
        default="supplementary/runtime.py",
        help="Frozen relative helper-file layout, independent of declared search roots",
    )
    parser.add_argument("--expect-ty-version", default="0.0.82")
    parser.add_argument(
        "--timeout",
        type=int,
        default=120,
        help="Per-command bound, within the existing attempt deadline",
    )
    parser.add_argument("targets", nargs="*")
    args = parser.parse_args(argv)
    evidence = {
        "schema_version": "peppy-static-isolation-v1",
        "mode": args.mode,
        "started_utc": datetime.now(timezone.utc).isoformat(),
        "commands": [],
        "status": "operational_error",
        "access_mode": "instruction_only",
        "audit_limit": "Resolution probes are not an exhaustive filesystem read audit; "
        "the pinned interpreter and its installed startup hooks/dependencies must be reviewed.",
    }
    evidence_path = Path(args.evidence).absolute()
    evidence_writable = False
    try:
        attempt = checked_path(args.attempt_root, directory=True)
        if (
            not within(evidence_path.resolve(), attempt)
            or evidence_path != evidence_path.resolve()
            or evidence_path.exists()
        ):
            raise OperationalError(
                "Use a new evidence file within the attempt; previous evidence is immutable"
            )
        evidence_writable = True
        if args.timeout <= 0:
            raise OperationalError("--timeout must be positive")
        for value in (args.framework_module, args.dependency):
            if not re.fullmatch(r"[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*", value):
                raise OperationalError("Module names must be dotted Python identifiers")
        helper_layout = Path(args.probe_helper_path)
        if (
            helper_layout.anchor
            or ".." in helper_layout.parts
            or helper_layout.suffix != ".py"
            or not helper_layout.stem.isidentifier()
        ):
            raise OperationalError(
                "--probe-helper-path must be a relative .py path with an importable module name"
            )
        perform(args, evidence)
    except (OperationalError, OSError, ValueError, subprocess.SubprocessError) as error:
        evidence["status"] = "operational_error"
        evidence["error"] = str(error)
    finally:
        evidence["finished_utc"] = datetime.now(timezone.utc).isoformat()
        if "temporary_root" in evidence:
            evidence["temporary_scope_removed"] = not Path(
                evidence["temporary_root"]
            ).exists()
    # Do not overwrite prior evidence, even when validation failed.
    if evidence_writable and not evidence_path.exists():
        evidence_path.parent.mkdir(parents=True, exist_ok=True)
        with evidence_path.open("x", encoding="utf-8") as handle:
            json.dump(evidence, handle, indent=2)
            handle.write("\n")
    print(
        json.dumps(
            {
                "status": evidence["status"],
                "evidence": str(evidence_path),
                "error": evidence.get("error"),
            }
        )
    )
    return {"passed": 0, "checks_failed": 1, "operational_error": 2}[evidence["status"]]


if __name__ == "__main__":
    raise SystemExit(main())
