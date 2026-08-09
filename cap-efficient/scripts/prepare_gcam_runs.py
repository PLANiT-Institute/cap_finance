#!/usr/bin/env python3
"""Prepare isolated, auditable GCAM 9.1 target-finder configurations."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import platform
import subprocess
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


SCENARIOS = {
    "GCAM_15C": "gcam/policy_target_temperature_1p5.xml",
    "GCAM_2C": "gcam/policy_target_temperature_2p0.xml",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def set_named(root: ET.Element, section: str, name: str, value: str) -> None:
    matches = root.findall(f"./{section}/Value[@name='{name}']")
    if len(matches) != 1:
        raise ValueError(f"Expected exactly one {section}/Value[@name={name!r}], got {len(matches)}")
    matches[0].text = value


def run(command: list[str], cwd: Path | None = None) -> dict[str, object]:
    result = subprocess.run(command, cwd=cwd, capture_output=True, text=True, check=False)
    return {
        "command": command,
        "exit_code": result.returncode,
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
    }


def write_config(
    source: Path,
    destination: Path,
    scenario_id: str,
    policy_file: Path,
    exe_dir: Path,
    output_dir: Path,
    smoke: bool = False,
) -> None:
    tree = ET.parse(source)
    root = tree.getroot()
    scenario_slug = "GCAM_SMOKE" if smoke else scenario_id
    set_named(root, "Files", "policy-target-file", os.path.relpath(policy_file, exe_dir))
    set_named(root, "Files", "xmldb-location", f"../output/cap_efficient/{scenario_slug}/database_basexdb")
    set_named(root, "Files", "restart", f"generated/{scenario_slug}/restart/restart")
    set_named(root, "Files", "xmlDebugFileName", f"generated/{scenario_slug}/debug.xml")
    set_named(root, "Files", "hector-output", f"../output/cap_efficient/{scenario_slug}/gcam-hector-outputstream.csv")
    set_named(root, "Files", "costCurvesOutputFileName", f"generated/{scenario_slug}/cost_curves.xml")
    set_named(root, "Strings", "scenarioName", f"cap_efficient_{scenario_slug}")
    if smoke:
        set_named(root, "Bools", "find-path", "0")
        set_named(root, "Ints", "stop-year", "2020")
    destination.parent.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    (destination.parent / scenario_slug / "restart").mkdir(parents=True, exist_ok=True)
    ET.indent(tree, space="  ")
    tree.write(destination, encoding="utf-8", xml_declaration=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--package-dir", type=Path, default=Path("tmp/gcam-v9.1"))
    parser.add_argument("--data-dir", type=Path, default=Path("data"))
    parser.add_argument("--java-home", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("outputs/gcam_run_preparation.json"))
    args = parser.parse_args()

    package = args.package_dir.resolve()
    data_dir = args.data_dir.resolve()
    java_home = args.java_home.resolve()
    exe_dir = package / "exe"
    source_policy = exe_dir / "configuration_policy.xml"
    source_reference = exe_dir / "configuration_ref.xml"
    executable = exe_dir / "gcam"
    libjvm_dir = java_home / "lib" / "server"
    libjvm = libjvm_dir / "libjvm.dylib"
    for path in (source_policy, source_reference, executable, libjvm):
        if not path.is_file():
            raise FileNotFoundError(path)

    run_manifest = {row["scenario_id"]: row for row in rows(data_dir / "gcam_run_manifest.csv")}
    if set(run_manifest) != set(SCENARIOS):
        raise ValueError("GCAM run manifest scenario set does not match preparation set")
    origin_hash = sha256(source_policy)
    generated_dir = exe_dir / "generated"
    prepared: dict[str, object] = {}
    for scenario_id, relative_policy in SCENARIOS.items():
        manifest = run_manifest[scenario_id]
        if origin_hash != manifest["configuration_origin_sha256"]:
            raise ValueError(f"{scenario_id} official configuration origin SHA256 mismatch")
        policy = data_dir / relative_policy
        if sha256(policy) != manifest["policy_target_sha256"]:
            raise ValueError(f"{scenario_id} target file SHA256 mismatch")
        destination = generated_dir / f"configuration_{scenario_id}.xml"
        output_dir = package / "output" / "cap_efficient" / scenario_id
        write_config(source_policy, destination, scenario_id, policy, exe_dir, output_dir)
        prepared[scenario_id] = {
            "configuration": str(destination),
            "configuration_sha256": sha256(destination),
            "policy_target_file": str(policy),
            "policy_target_sha256": sha256(policy),
            "database_dir": str(output_dir / "database_basexdb"),
            "run_command": [str(executable), "-C", os.path.relpath(destination, exe_dir)],
        }

    smoke_policy = data_dir / SCENARIOS["GCAM_2C"]
    smoke_config = generated_dir / "configuration_GCAM_SMOKE.xml"
    smoke_output = package / "output" / "cap_efficient" / "GCAM_SMOKE"
    write_config(source_reference, smoke_config, "GCAM_SMOKE", smoke_policy, exe_dir, smoke_output, smoke=True)

    java_link = package / "libs" / "java" / "lib"
    java_link.parent.mkdir(parents=True, exist_ok=True)
    if java_link.is_symlink():
        if java_link.resolve() != libjvm_dir:
            raise ValueError(f"Existing GCAM Java link points to {java_link.resolve()}, not {libjvm_dir}")
    elif java_link.exists():
        raise ValueError(f"GCAM Java link path exists but is not a symlink: {java_link}")
    else:
        java_link.symlink_to(libjvm_dir)

    version_probe = run([str(executable), "--version"], cwd=exe_dir)
    version_id_probe = run([str(executable), "--versionID"], cwd=exe_dir)
    if version_probe["exit_code"] != 0 or version_id_probe["stdout"] != "gcam-v9.1":
        raise RuntimeError("Pinned GCAM 9.1 binary did not pass the version probe")

    payload = {
        "prepared_at_kst": datetime.now(ZoneInfo("Asia/Seoul")).isoformat(),
        "status": "READY_FOR_SMOKE_RUN",
        "numeric_gcam_results_produced": False,
        "host": {"machine": platform.machine(), "platform": platform.platform()},
        "gcam": {
            "package_dir": str(package),
            "executable": str(executable),
            "executable_sha256": sha256(executable),
            "version_probe": version_probe,
            "version_id_probe": version_id_probe,
            "configuration_origin": str(source_policy),
            "configuration_origin_sha256": origin_hash,
        },
        "java": {
            "java_home": str(java_home),
            "java_version": run([str(java_home / "bin" / "java"), "-version"]),
            "libjvm": str(libjvm),
            "libjvm_sha256": sha256(libjvm),
            "gcam_java_link": str(java_link),
            "gcam_java_link_target": str(java_link.resolve()),
        },
        "smoke": {
            "configuration": str(smoke_config),
            "configuration_sha256": sha256(smoke_config),
            "database_dir": str(smoke_output / "database_basexdb"),
            "run_command": [str(executable), "-C", os.path.relpath(smoke_config, exe_dir)],
            "scope": "reference configuration stopped at 2020; runtime/integration test only",
        },
        "scenarios": prepared,
        "activation_warning": "Prepared configurations are project-authored inputs, not official JGCRI results. Do not activate scenarios until full runs and all query/hash gates pass.",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"READY_FOR_SMOKE_RUN: {args.output}")


if __name__ == "__main__":
    main()
