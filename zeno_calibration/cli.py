import argparse
import os
import sys
import json

try:
    import yaml
except ImportError:
    yaml = None

from .calibrator import ZenoCalibrator


def load_config(path: str) -> dict:
    if not os.path.exists(path):
        print(f"[ZENO] Config file not found: {path}")
        sys.exit(1)

    if path.endswith(".json"):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    if path.endswith(".yaml") or path.endswith(".yml"):
        if yaml is None:
            print("[ZENO] PyYAML is required for YAML configs. Install with: pip install pyyaml")
            sys.exit(1)
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    print(f"[ZENO] Unsupported config format (use .json or .yaml): {path}")
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Zeno Calibration CLI")
    parser.add_argument(
        "--config",
        "-c",
        default="config.yaml",
        help="Path to config file (YAML or JSON). Default: config.yaml"
    )
    args = parser.parse_args()

    config = load_config(args.config)

    model_config = config.get("model")
    scenario_paths = config.get("calibration", {}).get("tests", [])

    if not model_config:
        print("[ZENO] Config is missing 'model' section.")
        sys.exit(1)

    if not scenario_paths:
        print("[ZENO] Config is missing 'calibration.tests' list.")
        sys.exit(1)

    # Normalize scenario paths (relative to repo root)
    scenario_paths = [os.path.normpath(p) for p in scenario_paths]

    print("[ZENO] Starting calibration…")
    calibrator = ZenoCalibrator(model_config=model_config, scenario_paths=scenario_paths)
    result = calibrator.run()

    print()
    print("=== Zeno Calibration Complete ===")
    print(f"Run ID:      {result['run_id']}")
    print(f"Run Folder:  {result['run_dir']}")
    print(f"Session Mode:{result['assigned_mode']}")
    print("Scores:")
    for k, v in result["scores"].items():
        print(f"  {k:10s}: {v:.2f}")
    print()
    print("Proof packet:")
    print(f"  {result['run_dir']}")
    print("Open the *_test.txt files there to see prompts, outputs, and verdicts.")


if __name__ == "__main__":
    main()
