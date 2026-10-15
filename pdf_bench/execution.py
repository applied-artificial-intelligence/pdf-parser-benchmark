"""Isolate one parser call, retain returned bytes and enforce its wall-clock limit."""

import hashlib
import math
import multiprocessing as mp
import os
import signal
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pdf_bench.systems.base_parser import BaseParser


class EnforcedParseTimeoutError(TimeoutError):
    """Raised only by the parent process that enforces the attempt deadline."""


@dataclass
class ParseAttempt:
    outcome: str
    parse_time_seconds: float | None
    wall_time_seconds: float
    output_path: Path | None = None
    output_sha256: str | None = None
    error: str | None = None
    error_type: str | None = None
    returned_path: str | None = None
    worker_pid: int | None = None


def _parser_child(connection, parser_class, options, input_path, directory) -> None:
    if os.name == "posix":
        os.setsid()
    started = None
    try:
        parser = parser_class(**options)
        if hasattr(parser, "_get_backend"):
            parser._get_backend()
        parser_output = directory / "parser-output"
        parser_output.mkdir()
        started = time.perf_counter()
        connection.send({"event": "parse_started", "at": started})
        returned = Path(parser.parse(input_path, parser_output))
        data = returned.read_bytes()
        content = data.decode("utf-8")
        frozen = directory / "retained-output.md"
        with frozen.open("xb") as stream:
            stream.write(data)
        connection.send(
            {
                "event": "terminal",
                "outcome": "success_content" if content.strip() else "success_empty",
                "parse_time_seconds": time.perf_counter() - started,
                "output_sha256": hashlib.sha256(data).hexdigest(),
                "returned_path": str(returned),
            }
        )
    except Exception as error:
        connection.send(
            {
                "event": "terminal",
                "outcome": "parser_failure" if started is not None else "initialization_failure",
                "parse_time_seconds": time.perf_counter() - started if started else None,
                "error": str(error),
                "error_type": type(error).__name__,
            }
        )
    finally:
        connection.close()


def _stop_worker(process) -> None:
    if process.pid is None:
        return
    if process.is_alive():
        try:
            if os.name == "posix" and os.getpgid(process.pid) == process.pid:
                os.killpg(process.pid, signal.SIGTERM)
            else:
                process.terminate()
        except ProcessLookupError:
            pass
        process.join(0.5)
        if process.is_alive():
            try:
                if os.name == "posix" and os.getpgid(process.pid) == process.pid:
                    os.killpg(process.pid, signal.SIGKILL)
                else:
                    process.kill()
            except ProcessLookupError:
                pass
            process.join(1)
        if process.is_alive():
            raise RuntimeError("Timed-out work could not be stopped; attempt remains incomplete")
    process.join()


def execute_parser(
    parser_class: type[BaseParser],
    options: dict[str, Any],
    input_path: Path,
    attempt_dir: Path,
    timeout_seconds: float = 300,
) -> ParseAttempt:
    """Measure call/read/retention after initialization; wall time also includes startup."""
    if not math.isfinite(timeout_seconds) or timeout_seconds <= 0:
        raise ValueError("Timeout must be positive")
    attempt_dir = attempt_dir.resolve()
    attempt_dir.mkdir(parents=True, exist_ok=False)
    context = mp.get_context("spawn")
    receiver, sender = context.Pipe(duplex=False)
    process = context.Process(
        target=_parser_child,
        args=(sender, parser_class, options, input_path.resolve(), attempt_dir),
    )
    started, parse_started = time.perf_counter(), None
    terminal = None
    worker_pid = None
    try:
        process.start()
        worker_pid = process.pid
        sender.close()
        deadline = started + timeout_seconds
        while terminal is None:
            remaining = deadline - time.perf_counter()
            if remaining <= 0:
                raise EnforcedParseTimeoutError(f"Attempt exceeded {timeout_seconds:g} seconds")
            if receiver.poll(min(remaining, 0.1)):
                try:
                    message = receiver.recv()
                except EOFError:
                    break
                if message["event"] == "parse_started":
                    parse_started = message["at"]
                elif message["event"] == "terminal":
                    terminal = message
            elif not process.is_alive():
                break
        if terminal is None:
            terminal = {
                "outcome": "parser_failure"
                if parse_started is not None
                else "initialization_failure",
                "parse_time_seconds": (
                    time.perf_counter() - parse_started if parse_started is not None else None
                ),
                "error": f"Worker exited without a terminal outcome (exit {process.exitcode})",
                "error_type": "WorkerExit",
            }
    except EnforcedParseTimeoutError as error:
        _stop_worker(process)
        terminal = {
            "outcome": "enforced_timeout",
            "parse_time_seconds": (
                time.perf_counter() - parse_started if parse_started is not None else None
            ),
            "error": str(error),
            "error_type": type(error).__name__,
        }
    except Exception as error:
        terminal = {
            "outcome": "parser_failure" if parse_started is not None else "initialization_failure",
            "parse_time_seconds": (
                time.perf_counter() - parse_started if parse_started is not None else None
            ),
            "error": str(error),
            "error_type": type(error).__name__,
        }
    finally:
        _stop_worker(process)
        receiver.close()
        sender.close()
        process.close()
    output = attempt_dir / "retained-output.md"
    output_hash = terminal.get("output_sha256")
    if output_hash is not None and hashlib.sha256(output.read_bytes()).hexdigest() != output_hash:
        raise ValueError("Returned output bytes changed before retention was verified")
    return ParseAttempt(
        outcome=terminal["outcome"],
        parse_time_seconds=terminal["parse_time_seconds"],
        wall_time_seconds=time.perf_counter() - started,
        output_path=output if output_hash is not None else None,
        output_sha256=output_hash,
        error=terminal.get("error"),
        error_type=terminal.get("error_type"),
        returned_path=terminal.get("returned_path"),
        worker_pid=worker_pid,
    )
