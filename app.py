"""
Zeno Web Application - Flask Backend
Main application file for the web interface
"""

from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import json
import yaml
from datetime import datetime
from pathlib import Path
import sys

# Add the zeno_calibration module to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from zeno_calibration.calibrator import ZenoCalibrator
from zeno_calibration.model_adapter import ModelAdapter

app = Flask(__name__)
app.config['RUNS_FOLDER'] = 'runs'

# Ensure runs directory exists
os.makedirs(app.config['RUNS_FOLDER'], exist_ok=True)


@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')


@app.route('/api/runs')
def get_runs():
    """Get list of all calibration runs"""
    runs_dir = Path(app.config['RUNS_FOLDER'])
    runs = []
    
    if runs_dir.exists():
        for run_folder in sorted(runs_dir.iterdir(), reverse=True):
            if run_folder.is_dir():
                meta_file = run_folder / 'meta.json'
                summary_file = run_folder / 'summary.json'
                
                if meta_file.exists() and summary_file.exists():
                    with open(meta_file) as f:
                        meta = json.load(f)
                    with open(summary_file) as f:
                        summary = json.load(f)
                    
                    runs.append({
                        'id': run_folder.name,
                        'timestamp': meta.get('timestamp'),
                        'model_name': meta.get('model_name'),
                        'session_mode': summary.get('session_mode'),
                        'scores': summary.get('scores', {})
                    })
    
    return jsonify(runs)


@app.route('/api/run/<run_id>')
def get_run_details(run_id):
    """Get detailed results for a specific run"""
    run_dir = Path(app.config['RUNS_FOLDER']) / run_id
    
    if not run_dir.exists():
        return jsonify({'error': 'Run not found'}), 404
    
    # Load all run data
    meta_file = run_dir / 'meta.json'
    summary_file = run_dir / 'summary.json'
    
    with open(meta_file) as f:
        meta = json.load(f)
    with open(summary_file) as f:
        summary = json.load(f)
    
    # Load test details
    test_files = ['shortcut_test.txt', 'fawning_test.txt', 
                  'unknowns_test.txt', 'integrity_test.txt']
    
    tests = {}
    for test_file in test_files:
        test_path = run_dir / test_file
        if test_path.exists():
            with open(test_path) as f:
                tests[test_file.replace('_test.txt', '')] = f.read()
    
    return jsonify({
        'meta': meta,
        'summary': summary,
        'tests': tests
    })


@app.route('/api/calibrate', methods=['POST'])
def run_calibration():
    """Run a new calibration test"""
    data = request.json
    
    # Create config from request data
    config = {
        'model': {
            'type': 'openai_chat',
            'endpoint': data.get('endpoint'),
            'model_name': data.get('model_name'),
            'api_key_env': data.get('api_key_env', '')
        }
    }
    
    try:
        # Initialize calibrator
        calibrator = ZenoCalibrator(config)
        
        # Run calibration
        result = calibrator.run()
        
        return jsonify({
            'success': True,
            'run_id': result['run_id'],
            'session_mode': result['session_mode'],
            'scores': result['scores']
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/test-connection', methods=['POST'])
def test_connection():
    """Test model endpoint connection"""
    data = request.json
    
    try:
        adapter = ModelAdapter({
            'type': 'openai_chat',
            'endpoint': data.get('endpoint'),
            'model_name': data.get('model_name'),
            'api_key_env': data.get('api_key_env', '')
        })
        
        # Try a simple test call
        response = adapter.send([{'role': 'user', 'content': 'test'}])
        
        return jsonify({
            'success': True,
            'message': 'Connection successful'
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    # For production, use gunicorn instead
    app.run(host='0.0.0.0', port=8080, debug=False)