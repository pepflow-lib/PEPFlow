#!/usr/bin/env python3
"""Check an on-disk Lean entry using its project's actual language server.

Requires Lean's textDocument/waitForDiagnostics extension. Its response waits
for all diagnostics for the requested document version (Lean.Data.Lsp.Extra).
Empty or temporarily quiet diagnostics alone are never completion evidence.
This checks editor elaboration, not theorem scope or transitive axiom safety.
"""

import argparse
import hashlib
import json
import os
import queue
import signal
import subprocess
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path


class CheckFailure(Exception):
    pass


def process_options():
    if os.name == "nt":
        return {
            "creationflags": subprocess.CREATE_NEW_PROCESS_GROUP
            | subprocess.CREATE_NO_WINDOW
        }
    return {"start_new_session": True}


def stop_process_tree(process):
    """Only terminate the subprocess tree started by this invocation."""
    if os.name == "nt":
        if process.poll() is None:
            subprocess.run(
                ["taskkill", "/PID", str(process.pid), "/T", "/F"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NO_WINDOW,
                timeout=10,
                check=False,
            )
    else:
        try:
            os.killpg(process.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        if os.name != "nt":
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        else:
            process.kill()
        process.wait(timeout=5)


def probe(command, cwd, timeout):
    process = subprocess.Popen[bytes](
        command,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=False,
        **process_options(),
    )
    try:
        stdout, stderr = process.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        stop_process_tree(process)
        raise CheckFailure("Version probe timed out: " + repr(command))
    result = {
        "command": command,
        "exit_code": process.returncode,
        "stdout": stdout.decode("utf-8", errors="replace").strip(),
        "stderr": stderr.decode("utf-8", errors="replace").strip(),
    }
    if process.returncode:
        raise CheckFailure("Version probe failed: " + json.dumps(result))
    return result


def read_messages(stream, messages):
    try:
        while True:
            headers = {}
            while True:
                line = stream.readline(8193)
                if not line:
                    messages.put(("eof", None))
                    return
                if len(line) > 8192:
                    raise CheckFailure("Oversized language-server header")
                if line in (b"\r\n", b"\n"):
                    break
                name, separator, value = line.partition(b":")
                if not separator:
                    raise CheckFailure("Invalid language-server message header")
                headers[name.strip().lower()] = value.strip()
            length = int(headers.get(b"content-length", b"-1"))
            if not 0 <= length <= 32 * 1024 * 1024:
                raise CheckFailure("Invalid language-server Content-Length")
            payload = bytearray()
            while len(payload) < length:
                chunk = stream.read(length - len(payload))
                if not chunk:
                    raise CheckFailure("Language server ended inside a message")
                payload.extend(chunk)
            message = json.loads(payload)
            if not isinstance(message, dict) or message.get("jsonrpc") != "2.0":
                raise CheckFailure("Invalid JSON-RPC message")
            messages.put(("message", message))
    except Exception as error:
        messages.put(("error", str(error)))


class Session:
    def __init__(self, command, root, report, timeout):
        self.report = report
        self.root = root
        self.deadline = time.monotonic() + timeout
        self.messages = queue.Queue()
        self.check_complete = False
        self.stderr = bytearray()
        self.process = subprocess.Popen[bytes](
            command,
            cwd=root,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=False,
            **process_options(),
        )
        threading.Thread(
            target=read_messages,
            args=(self.process.stdout, self.messages),
            daemon=True,
        ).start()
        threading.Thread(target=self.read_stderr, daemon=True).start()

    def read_stderr(self):
        assert self.process.stderr is not None
        while True:
            chunk = self.process.stderr.read(4096)
            if not chunk:
                return
            self.stderr.extend(chunk)

    def send(self, message):
        assert self.process.stdin is not None
        payload = json.dumps({"jsonrpc": "2.0", **message}).encode("utf-8")
        self.process.stdin.write(
            f"Content-Length: {len(payload)}\r\n\r\n".encode("ascii") + payload
        )
        self.process.stdin.flush()

    def handle(self, message):
        method = message.get("method")
        params = message.get("params", {})
        if method and "id" in message:
            if method == "workspace/configuration":
                result = [None] * len(params.get("items", []))
            elif method == "workspace/workspaceFolders":
                result = [{"uri": self.root.as_uri(), "name": self.root.name}]
            elif method in (
                "client/registerCapability",
                "client/unregisterCapability",
                "window/workDoneProgress/create",
                "workspace/inlayHint/refresh",
                "workspace/semanticTokens/refresh",
                "workspace/codeLens/refresh",
                "workspace/diagnostic/refresh",
            ):
                result = None
            else:
                self.send(
                    {
                        "id": message["id"],
                        "error": {
                            "code": -32601,
                            "message": "Unsupported client request",
                        },
                    }
                )
                raise CheckFailure(
                    "Language server requested unsupported client method: " + method
                )
            self.send({"id": message["id"], "result": result})
        elif method == "textDocument/publishDiagnostics":
            if self.check_complete:
                self.report["cleanup_diagnostic_notifications"].append(params)
                return
            self.report["diagnostic_notifications"].append(params)
            if params.get("uri") == self.report["entry_uri"]:
                version = params.get("version")
                if version not in (None, self.report["document_version"]):
                    raise CheckFailure(
                        "Received diagnostics for an unexpected document version"
                    )
                self.report["diagnostics"] = params.get("diagnostics", [])
        elif method == "$/lean/fileProgress":
            self.report["progress_notifications"].append(params)
        elif method in ("window/logMessage", "window/showMessage"):
            self.report["server_messages"].append({"method": method, "params": params})

    def response(self, request_id, timeout=None):
        deadline = self.deadline if timeout is None else time.monotonic() + timeout
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise CheckFailure(
                    "Timed out waiting for language-server response " + str(request_id)
                )
            try:
                kind, value = self.messages.get(timeout=remaining)
            except queue.Empty:
                raise CheckFailure(
                    "Timed out waiting for language-server response " + str(request_id)
                )
            if kind == "eof":
                raise CheckFailure(
                    "Language server exited before completing response "
                    + str(request_id)
                )
            if kind == "error":
                raise CheckFailure("Language-server protocol error: " + value)
            self.handle(value)
            if value.get("id") == request_id and "method" not in value:
                if "error" in value:
                    raise CheckFailure(
                        "Language-server request failed: " + json.dumps(value["error"])
                    )
                if "result" not in value:
                    raise CheckFailure("Language-server response has no result")
                return value["result"]

    def close(self):
        try:
            if self.process.poll() is None:
                self.send({"id": 3, "method": "shutdown", "params": None})
                self.response(3, timeout=5)
                self.send({"method": "exit"})
                self.process.wait(timeout=5)
        except (OSError, CheckFailure, subprocess.TimeoutExpired) as error:
            self.report["cleanup_note"] = str(error)
        finally:
            stop_process_tree(self.process)
            self.report["server_exit_code"] = self.process.returncode
            self.report["server_stderr"] = self.stderr.decode("utf-8", errors="replace")


def validate_paths(root, entry):
    if not root.is_dir() or not entry.is_file() or entry.suffix != ".lean":
        raise CheckFailure(
            "Project root must be a directory and entry must be an existing .lean file"
        )
    if root != entry.parent and root not in entry.parents:
        raise CheckFailure("Entry must be inside the supplied Lake project root")
    configs = ("lakefile.toml", "lakefile.lean")
    if not any((root / name).is_file() for name in configs):
        raise CheckFailure("Project root has no lakefile.toml or lakefile.lean")
    current = entry.parent
    while current != root:
        if any((current / name).exists() for name in (*configs, "lean-toolchain")):
            raise CheckFailure(
                "A nested project or toolchain would change editor discovery: "
                + str(current)
            )
        current = current.parent
    for current in (root, *root.parents):
        pin = current / "lean-toolchain"
        if pin.is_file() and pin.read_text(encoding="utf-8").strip():
            return pin
    raise CheckFailure(
        "Project has no pinned lean-toolchain in its directory or an ancestor"
    )


def run(args, report):
    root = Path(args.project_root).resolve()
    entry = Path(args.entry).resolve()
    report.update(
        {"project_root": str(root), "entry": str(entry), "entry_uri": entry.as_uri()}
    )
    pin = validate_paths(root, entry)
    source_bytes = entry.read_bytes()
    source = source_bytes.decode("utf-8")
    report.update(
        {
            "entry_sha256": hashlib.sha256(source_bytes).hexdigest(),
            "toolchain_file": str(pin),
            "toolchain_pin": pin.read_text(encoding="utf-8").strip(),
            "cwd": str(root),
            "command": [args.lake, "serve", "--"],
            "lake_version": probe(
                [args.lake, "--version"], root, min(args.timeout, 30)
            ),
            "lean_version": probe(
                [args.lake, "env", "lean", "--version"], root, min(args.timeout, 30)
            ),
        }
    )
    session = Session(report["command"], root, report, args.timeout)
    try:
        session.send(
            {
                "id": 1,
                "method": "initialize",
                "params": {
                    "processId": os.getpid(),
                    "rootUri": root.as_uri(),
                    "workspaceFolders": [{"uri": root.as_uri(), "name": root.name}],
                    "capabilities": {
                        "textDocument": {"publishDiagnostics": {"versionSupport": True}}
                    },
                    "clientInfo": {"name": "lean-from-ipynb-verifier"},
                },
            }
        )
        report["initialize_result"] = session.response(1)
        session.send({"method": "initialized", "params": {}})
        session.send(
            {
                "method": "textDocument/didOpen",
                "params": {
                    "textDocument": {
                        "uri": entry.as_uri(),
                        "languageId": "lean4",
                        "version": 1,
                        "text": source,
                    }
                },
            }
        )
        wait_params = {"uri": entry.as_uri(), "version": 1}
        session.send(
            {
                "id": 2,
                "method": "textDocument/waitForDiagnostics",
                "params": wait_params,
            }
        )
        result = session.response(2)
        session.check_complete = True
        if not isinstance(result, dict):
            raise CheckFailure(
                "Unexpected waitForDiagnostics response (expected an object)"
            )
        report["completion"] = {
            "method": "textDocument/waitForDiagnostics",
            "params": wait_params,
            "response": result,
            "completed": True,
        }
        if entry.read_bytes() != source_bytes:
            raise CheckFailure(
                "Entry changed on disk while the language server was checking it"
            )
        # Preserve every notification; the final publish replaces earlier sets.
        # Fail conservatively if any error or sorry warning appeared during this
        # one immutable document version, even if a later publication cleared it.
        all_diagnostics = [
            diagnostic
            for notification in report["diagnostic_notifications"]
            for diagnostic in notification.get("diagnostics", [])
            if notification.get("uri") == entry.as_uri()
        ]
        all_diagnostics = list(
            {json.dumps(d, sort_keys=True): d for d in all_diagnostics}.values()
        )
        report["errors"] = [d for d in all_diagnostics if d.get("severity") == 1]
        report["warnings"] = [d for d in all_diagnostics if d.get("severity") == 2]
        report["sorry_diagnostics"] = [
            d
            for d in all_diagnostics
            if "sorry" in str(d.get("message", "")).lower()
            and d.get("severity") in (1, 2)
        ]
        if report["errors"] or report["sorry_diagnostics"]:
            raise CheckFailure("Language server reported an error or a sorry warning")
        if session.process.poll() is not None:
            raise CheckFailure(
                "Language server exited unexpectedly after checking the entry"
            )
        report["status"] = "passed"
    finally:
        session.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--project-root",
        required=True,
        help="Lake project directory used by editor and CLI",
    )
    parser.add_argument(
        "--entry",
        required=True,
        help="Exact generated entry path, relative to invocation directory",
    )
    parser.add_argument(
        "--lake", default="lake", help="Lake executable (default: lake on PATH)"
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=180,
        help="Server timeout in seconds (default: 180)",
    )
    parser.add_argument("--output", help="Write detailed JSON evidence to this path")
    args = parser.parse_args()
    if args.timeout <= 0:
        parser.error("--timeout must be positive")
    if args.output:
        output = Path(args.output).resolve()
        if (
            output == Path(args.entry).resolve()
            or output.suffix.lower() != ".json"
            or output.name.lower().endswith("manifest.json")
        ):
            parser.error(
                "--output must be an evidence .json file, not the entry or a dependency manifest"
            )
    report = {
        "status": "failed",
        "started_utc": datetime.now(timezone.utc).isoformat(),
        "document_version": 1,
        "completion": {"completed": False},
        "diagnostics": [],
        "diagnostic_notifications": [],
        "progress_notifications": [],
        "server_messages": [],
        "errors": [],
        "warnings": [],
        "sorry_diagnostics": [],
        "cleanup_diagnostic_notifications": [],
    }
    started = time.monotonic()
    try:
        run(args, report)
    except (
        CheckFailure,
        OSError,
        UnicodeError,
        ValueError,
        subprocess.SubprocessError,
    ) as error:
        report["status"] = "failed"
        report["failure"] = str(error)
    except KeyboardInterrupt:
        report["status"] = "failed"
        report["failure"] = "Interrupted before verification completed"
    report["elapsed_seconds"] = round(time.monotonic() - started, 3)
    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        Path(args.output).write_text(rendered, encoding="utf-8")
        print(
            json.dumps(
                {
                    "status": report["status"],
                    "output": str(Path(args.output).resolve()),
                    "failure": report.get("failure"),
                },
                ensure_ascii=True,
            )
        )
    else:
        print(json.dumps(report, ensure_ascii=True, indent=2))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    sys.exit(main())
