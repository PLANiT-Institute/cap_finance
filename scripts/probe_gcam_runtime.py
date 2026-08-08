#!/usr/bin/env python3
"""Record a reproducible, non-destructive GCAM runtime compatibility probe."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import subprocess
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run(command: list[str], cwd: Path | None = None, timeout: int = 30) -> dict[str, object]:
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        return {
            "command": command,
            "exit_code": result.returncode,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
        }
    except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
        return {"command": command, "exit_code": None, "stdout": "", "stderr": str(exc)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--package-dir", type=Path, default=Path("tmp/gcam-v9.1"))
    parser.add_argument("--output", type=Path, default=Path("outputs/gcam_runtime_probe.json"))
    parser.add_argument(
        "--java-home",
        type=Path,
        help="Optional project-local JDK home; recorded without changing the system Java installation.",
    )
    args = parser.parse_args()

    package = args.package_dir.resolve()
    executable = package / "exe" / "gcam"
    configuration = package / "exe" / "configuration_policy.xml"
    if not executable.is_file() or not configuration.is_file():
        raise SystemExit(f"GCAM executable/configuration not found under {package}")

    system_java_home = run(["/usr/libexec/java_home"])
    binary_type = run(["file", str(executable)])
    dependency_check = run(["otool", "-L", str(executable)])
    java_home_path = args.java_home.resolve() if args.java_home else None
    if java_home_path is None and system_java_home["exit_code"] == 0:
        java_home_path = Path(str(system_java_home["stdout"])).resolve()
    java_binary = java_home_path / "bin" / "java" if java_home_path else None
    libjvm = java_home_path / "lib" / "server" / "libjvm.dylib" if java_home_path else None
    java_version = (
        run([str(java_binary), "-version"])
        if java_binary is not None and java_binary.is_file()
        else {"command": [], "exit_code": None, "stdout": "", "stderr": "Java binary not resolved"}
    )
    version = run([str(executable), "--version"], cwd=executable.parent)
    version_id = run([str(executable), "--versionID"], cwd=executable.parent)
    missing_jvm = "libjvm.dylib" in (str(version["stderr"]) + str(version_id["stderr"]))
    version_ok = (
        version["exit_code"] == 0
        and version_id["exit_code"] == 0
        and "GCAM version 9.1" in str(version["stdout"])
        and str(version_id["stdout"]).strip() == "gcam-v9.1"
    )
    status = (
        "READY_FOR_CONFIGURED_RUN"
        if version_ok
        else "BLOCKED_MISSING_JAVA"
        if missing_jvm
        else "FAILED_VERSION_PROBE"
    )
    linked_lib = package / "libs" / "java" / "lib"
    linked_target = Path(os.path.realpath(linked_lib)) if linked_lib.exists() else None

    payload = {
        "probe_timestamp_kst": datetime.now(ZoneInfo("Asia/Seoul")).isoformat(),
        "status": status,
        "numeric_gcam_results_produced": False,
        "host": {"machine": platform.machine(), "platform": platform.platform()},
        "package_dir": str(package),
        "executable": str(executable),
        "executable_sha256": sha256(executable),
        "configuration": str(configuration),
        "configuration_sha256": sha256(configuration),
        "binary_type": binary_type,
        "dynamic_dependencies": dependency_check,
        "system_java_home_probe": system_java_home,
        "java_runtime": {
            "java_home": str(java_home_path) if java_home_path else "",
            "java_version": java_version,
            "libjvm": str(libjvm) if libjvm else "",
            "libjvm_exists": bool(libjvm and libjvm.is_file()),
            "gcam_java_link": str(linked_lib),
            "gcam_java_link_target": str(linked_target) if linked_target else "",
        },
        "version_probe": version,
        "version_id_probe": version_id,
        "interpretation": (
            "The official GCAM 9.1 binary and JNI runtime are loadable. This is a "
            "non-destructive compatibility check only; no model run or numeric result is claimed."
            if version_ok
            else "The official GCAM binary cannot load @rpath/libjvm.dylib. "
            "No GCAM climate pathway is activated and no numeric output is inferred."
            if missing_jvm
            else "The binary loaded but did not return the pinned GCAM 9.1 version identity."
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{status}: {args.output}")


if __name__ == "__main__":
    main()
