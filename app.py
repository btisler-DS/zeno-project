import os
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from flask import Flask, jsonify, render_template, request

# If these imports differ in your package, we will adjust after you run it once.
try:
    from zeno_calibration.calibrator import ZenoCalibrator
    from zeno_calibration.model_adapter import ModelAdapter
except ImportError:
    # Fallback so the web app can still start in pure demo mode even
    # if the calibration engine is not importable for some reason.
    ZenoCalibrator = None  # type: ignore
    ModelAdapter = None  # type: ignore

app = Flask(__name__, template_folder="templates")

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
RUNS_DIR = BASE_DIR / "runs"

# Demo mode: ON by default for hosted app.
# Set ZENO_DEMO_MODE=false to enable live calibration.
DEMO_MODE = os.getenv("ZENO_DEMO_MODE", "true").lower() == "true"


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------

def load_json(path: Path) -> Optional[Dict[str, Any]]:
    if not path.is_file():
        return None
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def list_runs() -> List[Dict[str, Any]]:
    """
    Enumerate run folders under runs/, reading meta.json and summary.json
    where present. This is what populates the 'Recent Calibration Runs' list.
    """
    runs: List[Dict[str, Any]] = []
    if not RUNS_DIR.exists():
        return runs

    for entry in RUNS_DIR.iterdir():
        if not entry.is_dir():
            continue

        run_id = entry.name
        meta = load_json(entry / "meta.json") or {}
        summary = load_json(entry / "summary.json") or {}

        runs.append(
            {
                "run_id": run_id,
                "meta": meta,
                "summary": summary,
            }
        )

    # Optional: sort newest first if meta has a timestamp field
    def sort_key(item: Dict[str, Any]) -> Any:
        ts = item.get("meta", {}).get("timestamp")
        return ts or ""

    runs.sort(key=sort_key, reverse=True)
    return runs


def load_run_details(run_id: str) -> Optional[Dict[str, Any]]:
    """
    Load full details for a given run. We expect at minimum meta.json and
    summary.json; optionally a full_result.json with transcripts.
    """
    run_dir = RUNS_DIR / run_id
    if not run_dir.is_dir():
        return None

    meta = load_json(run_dir / "meta.json") or {}
    summary = load_json(run_dir / "summary.json") or {}
    # Name this file however you like; here we assume full_result.json
    details = load_json(run_dir / "full_result.json") or {}

    return {
        "run_id": run_id,
        "meta": meta,
        "summary": summary,
        "details": details,
    }


def make_model_adapter(endpoint: str, model_name: str, api_key: Optional[str]) -> Any:
    """
    Thin wrapper so we have a single place to adjust if your ModelAdapter
    constructor signature is slightly different.
    """
    if ModelAdapter is None:
        raise RuntimeError("ModelAdapter is not available in this environment")

    # Adjust this dict to match your actual adapter config if needed.
    config = {
        "endpoint": endpoint,
        "model_name": model_name,
        "api_key": api_key,
    }
    return ModelAdapter(config)


# -----------------------------------------------------------------------------
# Routes
# -----------------------------------------------------------------------------

@app.route("/")
def index() -> Any:
    # The UI JS will call /api/runs after load.
    return render_template("index.html")


@app.route("/api/runs", methods=["GET"])
def api_runs() -> Any:
    runs = list_runs()
    return jsonify({"runs": runs})


@app.route("/api/run/<run_id>", methods=["GET"])
def api_run(run_id: str) -> Any:
    data = load_run_details(run_id)
    if data is None:
        return jsonify({"error": f"run '{run_id}' not found"}), 404
    return jsonify(data)


@app.route("/api/test-connection", methods=["POST"])
def api_test_connection() -> Any:
    """
    Simple liveness test for a model endpoint. Sends a minimal chat-style
    request through the ModelAdapter and checks for any response.
    """
    if ModelAdapter is None:
        return jsonify(
            {
                "status": "error",
                "message": "ModelAdapter is not available in this environment.",
            }
        ), 500

    payload = request.get_json(force=True, silent=True) or {}
    endpoint = payload.get("endpoint") or payload.get("model_endpoint")
    model_name = payload.get("model_name")
    api_key = payload.get("api_key") or payload.get("api_key_env")

    if not endpoint or not model_name:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "endpoint and model_name are required.",
                }
            ),
            400,
        )

    try:
        adapter = make_model_adapter(endpoint, model_name, api_key)
        # Minimal probe; adjust to match your adapter's method name.
        # We assume an OpenAI-style interface.
        _ = adapter.chat(
            messages=[{"role": "user", "content": "Test connection from Zeno."}],
            max_tokens=8,
        )
    except Exception as e:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": f"Failed to reach model endpoint: {e}",
                }
            ),
            502,
        )

    return jsonify({"status": "ok", "message": "Model endpoint responded successfully."})


@app.route("/api/calibrate", methods=["POST"])
def api_calibrate() -> Any:
    """
    Run a full Zeno calibration. In demo mode this is disabled to avoid
    burning API credits on a public instance. Locally, set
    ZENO_DEMO_MODE=false to enable full runs.
    """
    if DEMO_MODE:
        return (
            jsonify(
                {
                    "status": "disabled",
                    "message": "Live calibration is disabled in demo mode. "
                    "Clone the repository or run with ZENO_DEMO_MODE=false to enable it.",
                }
            ),
            403,
        )

    if ZenoCalibrator is None:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "ZenoCalibrator is not available in this environment.",
                }
            ),
            500,
        )

    payload = request.get_json(force=True, silent=True) or {}
    endpoint = payload.get("endpoint") or payload.get("model_endpoint")
    model_name = payload.get("model_name")
    api_key = payload.get("api_key") or payload.get("api_key_env")

    if not endpoint or not model_name:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "endpoint and model_name are required.",
                }
            ),
            400,
        )

    # This config dict will likely need to match your existing CLI/config
    # schema. Adjust keys to align with your ZenoCalibrator implementation.
    config = {
        "model_endpoint": endpoint,
        "model_name": model_name,
        "api_key": api_key,
        "runs_folder": str(RUNS_DIR),
    }

    try:
        calibrator = ZenoCalibrator(config)
        result = calibrator.run()  # Expecting something like {"run_id": "...", ...}
    except Exception as e:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": f"Calibration failed: {e}",
                }
            ),
            500,
        )

    # Optionally, you can re-read the run from disk to keep the JSON schema
    # identical to what /api/run/<id> returns.
    run_id = result.get("run_id")
    if run_id:
        details = load_run_details(run_id)
    else:
        details = None

    return jsonify(
        {
            "status": "ok",
            "run_id": run_id,
            "result": result,
            "details": details,
        }
    )


# -----------------------------------------------------------------------------
# Entry point (useful for local dev)
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    # Local development server; DigitalOcean will use gunicorn/app:app instead.
    app.run(host="0.0.0.0", port=8080, debug=True)
