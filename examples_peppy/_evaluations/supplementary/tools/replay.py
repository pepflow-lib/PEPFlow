"""Replay the actual 30 archived notebooks using saved certificates, without AI.

Example: python examples_peppy/_evaluations/supplementary/tools/replay.py --trial bppm/r01
Every run uses new disposable copies, captures cell progress, blocks new CVXPY
optimization by default, and returns nonzero for any incomplete/failed replay.
"""

from __future__ import annotations

import argparse
import contextlib
import json
import os
import platform
import importlib.metadata
import subprocess
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

from audit_archive import load_publication_manifest
from shared_storage import load_shared_files
from replay_support import CAMPAIGN_ID, CONDITIONS, PROOF_PLANS, HistoricalPaths, guard_writes, parse_trial, prepare_trial, sha256

HERE = Path(__file__).resolve().parent
REPOSITORY = HERE.parents[3]
CAMPAIGN = HERE.parents[1]


def write_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=True, default=str) + "\n", encoding="utf-8")


def worker(config_file: Path) -> int:
    """Run one copy in its own Python process; exceptions remain visible."""
    if sys.flags.optimize:
        raise RuntimeError("Replay requires active Python assertions; do not use -O or PYTHONOPTIMIZE")
    config = json.loads(config_file.read_text(encoding="utf-8"))
    work = Path(config["work"]).resolve()
    result_path = Path(config["result"]).resolve()
    result = {"trial": config["trial"], "mode": "all notebook code cells, sequentially",
              "optimization_allowed": config["allow_solve"], "executed_cells": [],
              "path_mappings": [], "solver_calls": [], "executed_scripts": [], "status": "running"}
    result["environment"] = {"python": sys.version, "platform": platform.platform(), "packages": {}}
    for package in ("numpy", "sympy", "scipy", "cvxpy", "clarabel", "scs", "matplotlib"):
        try:
            result["environment"]["packages"][package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            result["environment"]["packages"][package] = "not installed"
    result["runner_sha256"] = sha256(Path(__file__).read_bytes())
    mapper = HistoricalPaths(work, config["trial"])
    cache = work / ".runtime"
    cache.mkdir(exist_ok=True)
    for key in ("TEMP", "TMP", "TMPDIR", "IPYTHONDIR", "MPLCONFIGDIR", "JUPYTER_RUNTIME_DIR",
                "JUPYTER_CONFIG_DIR", "XDG_CACHE_HOME"):
        target = cache / key.lower()
        target.mkdir(exist_ok=True)
        os.environ[key] = str(target)
    for key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
        os.environ[key] = "1"
    os.environ["MPLBACKEND"] = "Agg"
    os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
    sys.dont_write_bytecode = True
    os.chdir(work)
    sys.path[:0] = [str(work / "supplementary/approved"), str(work),
                    str(work / "supplementary/helpers"), str(work / "supplementary/h"),
                    str(work / "supplementary")]
    try:
        import cvxpy as cp
        import matplotlib.pyplot as plt
        import pathlib
        import pepflow
        if not Path(pepflow.__file__).resolve().is_relative_to(work / "supplementary/approved"):
            raise RuntimeError("Imported framework is outside the replay copy")
        result["framework_import"] = str(pepflow.__file__)

        # Public derivative bytes and historical inventory pins stay unchanged.
        # Only constructing a Path redirects an archived absolute trial location.
        original_path = pathlib.Path

        original_new = original_path.__new__

        def redirected_path(cls, *args, **kwargs):
            mapped = tuple(mapper.map(arg) if isinstance(arg, str) else arg for arg in args)
            return original_new(cls, *mapped, **kwargs)

        original_path.__new__ = redirected_path
        original_solve = cp.Problem.solve

        def guarded_solve(problem, *args, **kwargs):
            result["solver_calls"].append({"cell": result.get("current_cell"),
                                           "solver": str(kwargs.get("solver", "default"))})
            if not config["allow_solve"]:
                raise RuntimeError("New CVXPY optimization blocked in saved-data replay; use --allow-solve explicitly")
            return original_solve(problem, *args, **kwargs)

        cp.Problem.solve = guarded_solve
        plt.show = lambda *args, **kwargs: plt.close("all")
        guard_writes(work, result_path.parent)
        notebook_path = work / config["notebook"]
        notebook = json.loads(notebook_path.read_text(encoding="utf-8-sig"))
        result["notebook_sha256"] = sha256(notebook_path.read_bytes())
        namespace = {"__name__": "__main__"}
        units = [{"index": index, "id": cell.get("id"), "source": "".join(cell["source"])}
                 for index, cell in enumerate(notebook["cells"]) if cell["cell_type"] == "code"]
        if config.get("proof_only"):
            plan = PROOF_PLANS[config["trial"]]
            result["mode"] = "reviewed original symbolic proof units only"
            result["proof_scope"] = plan["scope"]
            result["excluded_scope"] = "Full notebook execution, discovery, original numerical certificate provenance and numerical-to-symbolic linkage are not established by this mode."
            result["excluded_code_cell_ids"] = [unit["id"] for unit in units if unit["id"] not in plan.get("cells", [])]
            if "cells" in plan:
                available = {unit["id"]: unit for unit in units}
                units = [dict(available[identity]) for identity in plan["cells"]]
                for unit in units:
                    segment = plan.get("segments", {}).get(unit["id"])
                    if segment:
                        if sha256(unit["source"].encode("utf-8")) != segment["sha256"]:
                            raise ValueError(f"Reviewed segment source changed: {unit['id']}")
                        lines = unit["source"].splitlines(keepends=True)
                        selected_lines = {line for first, last in segment["execute_lines"] for line in range(first, last + 1)}
                        # Blank excluded lines rather than renumbering tracebacks.
                        unit["source"] = "".join(line if index in selected_lines else "\n"
                                                  for index, line in enumerate(lines, 1))
                        unit["segment"] = segment
            else:
                units = [{"script": relative, "source": (work / relative).read_text(encoding="utf-8-sig")}
                         for relative in plan["scripts"]]
            import numpy as np
            import sympy as sp
            namespace.update(pf=pepflow, np=np, sp=sp, json=json, Path=Path,
                             notebook_dir=work, root=work)

        # Cache cell text so inspect.getsource works for archived authoring cells.
        import linecache
        for unit in units:
            identity = {key: value for key, value in unit.items() if key != "source"}
            result["current_cell"] = identity
            print(f"EXECUTE {identity}", flush=True)
            result["path_mappings"] = mapper.events
            write_json(result_path, result)
            source = unit["source"]
            filename = str(work / unit["script"]) if "script" in unit else f"<archived-notebook-cell-{unit['index']}>"
            linecache.cache[filename] = (len(source), None, source.splitlines(keepends=True), filename)
            if "script" in unit:
                namespace["__file__"] = filename
                sys.argv = [filename]
            exec(compile(source, filename, "exec"), namespace)
            identity["source_sha256"] = sha256(source.encode("utf-8"))
            result["executed_scripts" if "script" in unit else "executed_cells"].append(identity)
        if not result["executed_cells"] and not result["executed_scripts"]:
            raise RuntimeError("No executable units were selected")
        result.pop("current_cell", None)
        if result["solver_calls"] and not config["allow_solve"]:
            raise RuntimeError("Notebook caught a blocked optimization attempt; replay is incomplete")
        result["status"] = "completed"
        result["completion_scope"] = ("Symbolic identity replay completed; see proof_scope and excluded_scope" if config.get("proof_only") else "Every notebook code cell executed; this is not an independent proof audit")
        for name in ("proof_checks", "symbolic_results", "exact_identity_evidence", "step_verified",
                     "base_verified", "boundary_verified", "certificate_checked", "grouping_checked"):
            if name in namespace:
                result.setdefault("notebook_check_values", {})[name] = namespace[name]
    except BaseException as exc:
        result["status"] = "failed"
        result["error_type"] = type(exc).__name__
        result["error"] = str(exc)
        result["traceback"] = traceback.format_exc()
        if "namespace" in locals():
            failures = []
            for variable, value in namespace.items():
                if not isinstance(value, dict):
                    continue
                provenance = value.get("certificate_provenance", {})
                if not isinstance(provenance, dict):
                    continue
                for relative, expected in provenance.get("source_hashes", {}).items():
                    candidate = Path(mapper.map(relative))
                    if not candidate.is_absolute():
                        candidate = work / candidate
                    try:
                        actual = sha256(candidate.read_bytes())
                    except OSError:
                        actual = None
                    if actual != expected:
                        item = {"path": relative, "expected": expected, "actual": actual}
                        if item not in failures:
                            failures.append(item)
            if failures:
                result["provenance_hash_failures"] = failures
        traceback.print_exc()
    finally:
        result["path_mappings"] = mapper.events
        write_json(result_path, result)
    return 0 if result["status"] == "completed" else 1


def main(argv: list[str] | None = None) -> int:
    if sys.flags.optimize:
        raise RuntimeError("Replay requires active Python assertions; do not use -O or PYTHONOPTIMIZE")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trial", action="append", help="e.g. bppm/r01; repeat for multiple trials")
    parser.add_argument("--all", action="store_true", help="all six conditions and five repetitions")
    parser.add_argument("--r01", action="store_true", help="first trial of each condition")
    parser.add_argument("--timeout", type=float, default=180, help="wall-clock seconds per notebook (default: 180)")
    parser.add_argument("--proof-only", action="store_true", help="execute an explicitly inspected symbolic plan; only supported r01 trials, with excluded scope recorded")
    parser.add_argument("--use-imported-sources", action="store_true", help="permit only previously audited historical hash differences; notebook assertions still run unchanged")
    parser.add_argument("--allow-solve", action="store_true", help="explicitly permit new optimization")
    parser.add_argument("--python", default=sys.executable, help="interpreter with experiment dependencies installed")
    parser.add_argument("--worker", type=Path, help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    if args.worker:
        return worker(args.worker)
    if args.timeout <= 0:
        parser.error("--timeout must be positive")
    if sum(bool(value) for value in (args.trial, args.all, args.r01)) != 1:
        parser.error("choose --trial, --r01, or --all")
    trials = (args.trial if args.trial else [f"{condition}/r{repeat:02d}" for condition in CONDITIONS
              for repeat in (range(1, 6) if args.all else (1,))])
    for trial in trials:
        parse_trial(trial)
        if args.proof_only and trial not in PROOF_PLANS:
            parser.error(f"No reviewed proof-only plan for {trial}; use full notebook mode")
    imported_baseline = None
    if args.use_imported_sources:
        audit = json.loads((HERE / "archive-audit.json").read_text(encoding="utf-8-sig"))
        imported_baseline = {item["canonical"]: item for item in audit["mapped_validation_files"]}
    shared = load_shared_files(CAMPAIGN)
    manifest_path = HERE / "publication-manifest.json"
    publication = load_publication_manifest(CAMPAIGN, manifest_path, shared) if manifest_path.exists() else {}
    publication_identity = ({"manifest_sha256": sha256(manifest_path.read_bytes()),
                             "verified_file_count": len(publication)} if publication else None)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S_%fZ")
    output = REPOSITORY / ".runtime" / "peppy-replay" / stamp
    output.mkdir(parents=True)
    summary = {"started_utc": stamp, "python": args.python, "timeout_seconds": args.timeout,
               "optimization_allowed": args.allow_solve, "use_imported_sources": args.use_imported_sources, "proof_only": args.proof_only, "campaign": CAMPAIGN_ID, "trials": [],
               "publication_normalization": publication_identity}
    print(f"Replay results: {output}", flush=True)
    for trial in trials:
        condition, repeat = parse_trial(trial)
        label = f"{condition}_{repeat}"
        directory = output / label
        directory.mkdir()
        result = {"trial": trial, "status": "preparation_failed"}
        started = time.monotonic()
        publication_result = None
        try:
            work = directory / "trial"
            preparation = prepare_trial(CAMPAIGN, HERE / "framework", trial, work, imported_baseline, publication, shared)
            if publication_identity:
                publication_result = {**publication_identity,
                    "verified_trial_files": len(preparation["verified_publication_files"]),
                    "accepted_inventory_records": len(preparation["accepted_publication_sources"])}
            write_json(directory / "preparation.json", preparation)
            if preparation["unresolved_inventory"]:
                raise ValueError("Unresolved historical submission hashes; see preparation.json")
            notebooks = list(work.glob("*.ipynb"))
            if len(notebooks) != 1:
                raise ValueError(f"Expected one primary notebook; found {len(notebooks)}")
            result_path = directory / "result.json"
            configuration = {"trial": trial, "work": str(work), "notebook": notebooks[0].name,
                             "result": str(result_path), "allow_solve": args.allow_solve, "proof_only": args.proof_only}
            config_path = directory / "config.json"
            write_json(config_path, configuration)
            with (directory / "execution.log").open("w", encoding="utf-8") as log:
                environment = dict(os.environ, PYTHONUTF8="1", PYTHONDONTWRITEBYTECODE="1")
                environment.pop("PYTHONOPTIMIZE", None)
                process = subprocess.Popen([args.python, "-B", str(Path(__file__).resolve()),
                                            "--worker", str(config_path)], stdout=log,
                                           stderr=subprocess.STDOUT, env=environment)
                try:
                    returncode = process.wait(timeout=args.timeout)
                    result = json.loads(result_path.read_text(encoding="utf-8")) if result_path.exists() else {
                        "trial": trial, "status": "worker_failed", "error": "Worker exited without a report"}
                    result["exit_code"] = returncode
                    if returncode != 0 and result["status"] == "completed":
                        result["status"] = "worker_failed"
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()
                    result = json.loads(result_path.read_text(encoding="utf-8")) if result_path.exists() else {"trial": trial}
                    result["status"] = "timeout"
                    result["error"] = f"Exceeded {args.timeout} seconds; no completion claimed"
        except Exception as exc:
            result["error_type"] = type(exc).__name__
            result["error"] = str(exc)
        result["publication_normalization"] = publication_result
        result["elapsed_seconds"] = round(time.monotonic() - started, 3)
        write_json(directory / "result.json", result)
        summary["trials"].append({**result, "directory": str(directory)})
        write_json(output / "summary.json", summary)
        print(f"{trial}: {result['status']} ({result['elapsed_seconds']}s)", flush=True)
    return 0 if all(item["status"] == "completed" for item in summary["trials"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
