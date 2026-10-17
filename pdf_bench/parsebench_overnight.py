"""Run the declared local queue within the approved overnight resource budget."""

import argparse
import fcntl
import hashlib
import json
import math
import os
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from pdf_bench.persistence import write_json_atomic


def window_end(now: datetime) -> datetime | None:
    local = now.astimezone(ZoneInfo("America/New_York"))
    if 7 <= local.hour < 22:
        return None
    day = local + timedelta(days=1) if local.hour >= 22 else local
    return day.replace(hour=7, minute=0, second=0, microsecond=0)


def allocations(jobs: list[dict], slots: int) -> list[tuple[dict, int]]:
    """Reserve model capacity first, then share remaining calls among light parsers."""
    chosen = []
    for job in sorted(jobs, key=lambda j: (j["priority"], j["backend"])):
        count = min(job["workers"], slots)
        if count:
            chosen.append((job, count))
            slots -= count
    return chosen


def service_usage() -> dict:
    group = next(
        line.split(":", 2)[2]
        for line in Path("/proc/self/cgroup").read_text().splitlines()
        if line.startswith("0::")
    )
    root = Path("/sys/fs/cgroup") / group.lstrip("/")
    cpu = dict(line.split() for line in (root / "cpu.stat").read_text().splitlines())
    return {
        "cpu_seconds": int(cpu["usage_usec"]) / 1e6,
        "memory_bytes": int((root / "memory.current").read_text()),
    }


def pilot_estimates(config: dict, unit: Path) -> dict:
    estimates = []
    for job in config["jobs"]:
        target = unit / "full-comparison-evidence" / job["run"]
        pilot_path = target / "timing-pilot" / "journal.json"
        if not pilot_path.exists():
            continue
        pilot = json.loads(pilot_path.read_text())["attempts"]
        durations = [r["wall_time_seconds"] for r in pilot]
        completed = len(list((target / "attempts").glob("*/attempt.json")))
        plan = json.loads((target / "plan.json").read_text())
        hours = (len(plan["inputs"]) - completed) * sum(durations) / len(durations) / 3600
        estimates.append(
            {
                "backend": job["backend"],
                "completed": completed,
                "remaining": len(plan["inputs"]) - completed,
                "pilot_calls": len(pilot),
                "mean_wall_seconds": sum(durations) / len(durations),
                "serial_remaining_hours": hours,
                "nominal_parallel_remaining_hours": hours / job.get("pilot_speedup", 1),
                "workers": job["workers"],
            }
        )
    lower = max(
        [r["nominal_parallel_remaining_hours"] for r in estimates]
        + [sum(r["serial_remaining_hours"] for r in estimates) / config["max_calls"]]
    )
    return {
        "at": datetime.now(timezone.utc).isoformat(),
        "backends": estimates,
        "all_backends_sampled": bool(config["jobs"]) and len(estimates) == len(config["jobs"]),
        "nominal_critical_path_hours": lower,
        "planning_nights_range": [math.ceil(lower / 9), math.ceil(lower * 1.7 / 9)],
        "limitation": (
            "Small dimension-balanced sample; concurrency, document difficulty and failures "
            "can change throughput. Planning estimates, not parser latency rankings."
        ),
    }


def calibrated_jobs(config: dict, unit: Path) -> list[dict]:
    jobs = []
    for original in config["jobs"]:
        job = dict(original)
        target = unit / "full-comparison-evidence" / job["run"]
        paired = target / "timing-pilot-w2" / "journal.json"
        if job["workers"] == 2 and paired.exists():
            solo = json.loads((target / "timing-pilot" / "journal.json").read_text())["attempts"]
            parallel = json.loads(paired.read_text())["attempts"]
            solo_profile = target / "timing-pilot" / "resource-profile.json"
            parallel_profile = paired.parent / "resource-profile.json"
            job["pilot_speedup"] = 1.0
            if solo_profile.exists() and parallel_profile.exists():
                job["pilot_speedup"] = (
                    json.loads(solo_profile.read_text())["elapsed_seconds"]
                    / json.loads(parallel_profile.read_text())["elapsed_seconds"]
                )

            def failed(rows: list[dict]) -> int:
                return sum(r["outcome"] not in {"success_content", "success_empty"} for r in rows)

            if job["pilot_speedup"] < 1.2 or failed(parallel) > failed(solo):
                job["workers"] = 1
                job["pilot_speedup"] = 1.0
        jobs.append(job)
    return jobs


def run_queue(config_path: Path) -> None:
    config = json.loads(config_path.read_text())
    if config.get("execution_paused"):
        print("Benchmark execution is paused; nothing started.", flush=True)
        return
    unit = config_path.parent
    end = window_end(datetime.now(timezone.utc))
    if end is None:
        print("Outside approved 22:00-07:00 New York window; nothing started.", flush=True)
        return
    held = [j for j in config["jobs"] if j.get("hold_reason")]
    config["jobs"] = [j for j in config["jobs"] if not j.get("hold_reason")]
    config["held_jobs"] = held
    os.sched_setaffinity(0, set(config["cpus"]))
    os.nice(max(0, config["nice"] - os.getpriority(os.PRIO_PROCESS, 0)))
    for key in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
        os.environ[key] = "2"
    (unit / "overnight-logs").mkdir(exist_ok=True)
    with (unit / "overnight.lock").open("w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        sample = unit / config["sample"]
        start = datetime.now(timezone.utc)
        write_json_atomic(
            unit / "overnight-status.json",
            {
                "state": "running",
                "started_at": start.isoformat(),
                "stop_at": end.isoformat(),
                "policy": config,
            },
        )

        def launch(job: dict, workers: int, pilot: bool) -> tuple:
            target = unit / "full-comparison-evidence" / job["run"]
            if (
                hashlib.sha256((target / "plan.json").read_bytes()).hexdigest()
                != job["plan_sha256"]
            ):
                raise ValueError("Queue plan differs from approved frozen input/configuration")
            command = [
                job["python"],
                "-m",
                "pdf_bench.parsebench_full",
                "--resume",
                str(target),
                "--workers",
                str(workers),
                "--stop-at",
                end.isoformat(),
            ]
            if pilot:
                command.extend(["--sample", str(sample)])
            if job.get("grading"):
                command = [
                    config["native_python"],
                    "-m",
                    "pdf_bench.parsebench_full_native",
                    "--unit",
                    str(unit),
                    "--run",
                    str(target),
                    "--stop-at",
                    end.isoformat(),
                ]
            name = job["backend"] + (
                "-grade" if job.get("grading") else f"-pilot-w{workers}" if pilot else "-queue"
            )
            log = (
                unit / "overnight-logs" / (start.strftime("%Y%m%dT%H%M%S") + "-" + name + ".log")
            ).open("a")
            process = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT)
            return process, log, workers, job

        # An isolated common-input sample gives a baseline before resource sharing.
        for job in config["jobs"]:
            for workers in range(1, job["workers"] + 1):
                name = "timing-pilot" if workers == 1 else f"timing-pilot-w{workers}"
                pilot = unit / "full-comparison-evidence" / job["run"] / name
                if (pilot / "parse-complete.json").exists():
                    continue
                if (end - datetime.now(timezone.utc)).total_seconds() <= 240:
                    break
                before = service_usage()
                peak_memory = before["memory_bytes"]
                started = time.monotonic()
                process, log, _, _ = launch(job, workers, True)
                while process.poll() is None:
                    peak_memory = max(peak_memory, service_usage()["memory_bytes"])
                    time.sleep(1)
                code = process.returncode
                log.close()
                if code:
                    raise RuntimeError(
                        f"{job['backend']} timing pilot failed; inspect overnight log"
                    )
                after = service_usage()
                write_json_atomic(
                    pilot / "resource-profile.json",
                    {
                        "workers": workers,
                        "elapsed_seconds": time.monotonic() - started,
                        "cpu_seconds": after["cpu_seconds"] - before["cpu_seconds"],
                        "peak_sampled_service_memory_bytes": peak_memory,
                        "scope": "Pilot service and children; one-second memory samples",
                    },
                )
        config["jobs"] = calibrated_jobs(config, unit)
        write_json_atomic(unit / "overnight-estimates.json", pilot_estimates(config, unit))
        waiting = [
            j
            for j in config["jobs"]
            if not (unit / "full-comparison-evidence" / j["run"] / "parse-complete.json").exists()
        ]
        active: list[tuple] = []
        grading_scheduled: set[str] = set()
        failures = []
        last_status = 0.0
        while True:
            seconds_left = (end - datetime.now(timezone.utc)).total_seconds()
            for job in config["jobs"]:
                target = unit / "full-comparison-evidence" / job["run"]
                if (
                    seconds_left > 1800
                    and job["backend"] not in grading_scheduled
                    and (target / "parse-complete.json").exists()
                    and not (target / "native-latest.json").exists()
                ):
                    waiting.append({**job, "grading": True, "workers": 1, "priority": -1})
                    grading_scheduled.add(job["backend"])
            if not waiting and not active:
                break
            free = config["max_calls"] - sum(p[2] for p in active)
            if seconds_left > 240:
                for job, workers in allocations(waiting, free):
                    active.append(launch(job, workers, False))
                    waiting.remove(job)
            elif not active:
                break
            for item in list(active):
                process, log, _, job = item
                if process.poll() is not None:
                    log.close()
                    active.remove(item)
                    if process.returncode:
                        failures.append(
                            {
                                "backend": job["backend"],
                                "grading": job.get("grading", False),
                                "exit_code": process.returncode,
                            }
                        )
            if time.monotonic() - last_status >= 60:
                write_json_atomic(
                    unit / "overnight-status.json",
                    {
                        "state": "running",
                        "started_at": start.isoformat(),
                        "at": datetime.now(timezone.utc).isoformat(),
                        "stop_at": end.isoformat(),
                        "active": [
                            {
                                "backend": p[3]["backend"],
                                "workers": p[2],
                                "grading": p[3].get("grading", False),
                            }
                            for p in active
                        ],
                        "failures": failures,
                        "policy": config,
                        "service_usage": service_usage(),
                    },
                )
                last_status = time.monotonic()
            if active:
                time.sleep(2)
        write_json_atomic(unit / "overnight-estimates.json", pilot_estimates(config, unit))
        complete = all(
            (unit / "full-comparison-evidence" / j["run"] / "parse-complete.json").exists()
            for j in config["jobs"]
        )
        write_json_atomic(
            unit / "overnight-status.json",
            {
                "state": (
                    "held"
                    if held and not config["jobs"]
                    else "failed"
                    if failures
                    else "available_screen_complete"
                    if complete and held
                    else "parse_complete"
                    if complete
                    else "checkpointed"
                ),
                "started_at": start.isoformat(),
                "finished_at": datetime.now(timezone.utc).isoformat(),
                "stop_at": end.isoformat(),
                "policy": config,
                "failures": failures,
            },
        )


def launch_service(config_path: Path) -> None:
    config = json.loads(config_path.read_text())
    if config.get("execution_paused"):
        print("Benchmark execution is paused; no service started.")
        return
    end = window_end(datetime.now(timezone.utc))
    if end is None:
        print("Outside approved window; no service started.")
        return
    environment = {
        **os.environ,
        "XDG_RUNTIME_DIR": f"/run/user/{os.getuid()}",
        "DBUS_SESSION_BUS_ADDRESS": f"unix:path=/run/user/{os.getuid()}/bus",
    }
    seconds = max(1, int((end - datetime.now(timezone.utc)).total_seconds()) - 5)
    command = [
        "systemd-run",
        "--user",
        "--unit=pdfbench-overnight",
        "--collect",
        "--property=KillMode=control-group",
        "--property=TimeoutStopSec=5",
        f"--property=RuntimeMaxSec={seconds}s",
        f"--property=CPUQuota={len(config['cpus']) * 100}%",
        f"--property=MemoryMax={config['memory_gb']}G",
        "--property=MemorySwapMax=0",
        f"--property=Nice={config['nice']}",
        f"--working-directory={Path.cwd()}",
        sys.executable,
        "-m",
        "pdf_bench.parsebench_overnight",
        "--config",
        str(config_path),
    ]
    subprocess.run(command, env=environment, check=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--service", action="store_true")
    args = parser.parse_args()
    if args.service:
        launch_service(args.config.resolve())
    else:
        run_queue(args.config.resolve())


if __name__ == "__main__":
    main()
