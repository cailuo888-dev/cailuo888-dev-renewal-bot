#!/usr/bin/env python3
"""Renewal bot - auto keepalive and renewal for free VPS services."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import logging
from datetime import datetime
from flask import Flask, jsonify
from apscheduler.schedulers.background import BackgroundScheduler

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
results = {}

def run_lunes():
    from scripts.lunes_renew import renew_lunes
    try:
        result = renew_lunes()
        results['lunes'] = {'time': datetime.now().isoformat(), 'result': result}
        logger.info(f"Lunes renewal: {result}")
    except Exception as e:
        results['lunes'] = {'time': datetime.now().isoformat(), 'error': str(e)}
        logger.error(f"Lunes renewal failed: {e}")

def run_katabump():
    from scripts.katabump_renew import renew_katabump
    try:
        result = renew_katabump()
        results['katabump'] = {'time': datetime.now().isoformat(), 'result': result}
        logger.info(f"Katabump renewal: {result}")
    except Exception as e:
        results['katabump'] = {'time': datetime.now().isoformat(), 'error': str(e)}
        logger.error(f"Katabump renewal failed: {e}")

@app.route('/')
def index():
    return jsonify({'service': 'renewal-bot', 'status': 'running', 'results': results})

@app.route('/health')
def health():
    return jsonify({'status': 'ok'})

@app.route('/trigger/<service>')
def trigger(service):
    if service == 'lunes':
        run_lunes()
    elif service == 'katabump':
        run_katabump()
    else:
        return jsonify({'error': 'unknown service'}), 404
    return jsonify(results.get(service, {}))

if __name__ == '__main__':
    scheduler = BackgroundScheduler()
    scheduler.add_job(run_lunes, 'interval', days=10, id='lunes')
    scheduler.add_job(run_katabump, 'interval', days=3, id='katabump')
    scheduler.start()
    logger.info("Scheduler started")
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
