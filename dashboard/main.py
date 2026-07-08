"""Real-time evolution dashboard for Grounded Agent Forge.

FastAPI-based web application providing visualization of the evolution process,
agent population, fitness trajectories, and blueprint inspection.
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Grounded Agent Forge Dashboard",
    description="Real-time visualization of agent blueprint evolution",
    version="1.0.0",
)

DATA_DIR = Path(os.environ.get("FORGE_DATA_DIR", "memory"))
POPULATION_FILE = DATA_DIR / "population.json"
META_STATE_FILE = DATA_DIR / "meta_state.json"


def load_json(path: Path) -> dict[str, Any]:
    """Load and return JSON data from a file, or empty dict on failure."""
    try:
        if path.exists():
            with open(path) as f:
                return json.load(f)
    except Exception as exc:
        logger.warning("Failed to load %s: %s", path, exc)
    return {}


@app.get("/", response_class=HTMLResponse)
async def index() -> str:
    """Serve the dashboard home page."""
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Grounded Agent Forge Dashboard</title>
    <style>
        :root {
            --bg: #0d1117;
            --card: #161b22;
            --border: #30363d;
            --text: #c9d1d9;
            --accent: #58a6ff;
            --green: #3fb950;
            --orange: #d29922;
            --red: #f85149;
        }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: var(--bg);
            color: var(--text);
            padding: 20px;
        }
        .header {
            display: flex; justify-content: space-between; align-items: center;
            padding: 16px 0; border-bottom: 1px solid var(--border); margin-bottom: 24px;
        }
        .header h1 { font-size: 24px; color: var(--accent); }
        .header .subtitle { color: #8b949e; font-size: 14px; }
        .grid { display: grid; gap: 16px; }
        .grid-4 { grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); }
        .grid-2 { grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); }
        .card {
            background: var(--card); border: 1px solid var(--border);
            border-radius: 8px; padding: 20px;
        }
        .card h3 { font-size: 14px; color: #8b949e; margin-bottom: 8px; text-transform: uppercase; }
        .card .value { font-size: 32px; font-weight: 600; }
        .card .value.green { color: var(--green); }
        .card .value.orange { color: var(--orange); }
        .card .value.red { color: var(--red); }
        .card .value.blue { color: var(--accent); }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 8px 12px; text-align: left; border-bottom: 1px solid var(--border); }
        th { color: #8b949e; font-size: 12px; text-transform: uppercase; }
        td { font-size: 14px; }
        .badge {
            display: inline-block; padding: 2px 8px; border-radius: 12px;
            font-size: 12px; background: rgba(88, 166, 255, 0.15); color: var(--accent);
        }
        .badge.green { background: rgba(63, 185, 80, 0.15); color: var(--green); }
        .status-bar { display: flex; gap: 16px; padding: 12px 0; }
        .status-dot { width: 8px; height: 8px; border-radius: 50%; display: inline-block; margin-right: 6px; }
        .status-dot.green { background: var(--green); }
        .status-dot.red { background: var(--red); }
        .bar-chart { display: flex; align-items: end; gap: 4px; height: 100px; margin-top: 12px; }
        .bar { flex: 1; border-radius: 3px 3px 0 0; min-height: 4px; transition: height 0.3s; }
    </style>
</head>
<body>
    <div class="header">
        <div>
            <h1>⚒️ Grounded Agent Forge</h1>
            <div class="subtitle">Real-time evolution dashboard</div>
        </div>
        <div class="status-bar">
            <span><span class="status-dot green"></span>Evolving</span>
            <span id="gen-display">Generation: --</span>
            <span id="pop-display">Population: --</span>
        </div>
    </div>

    <div class="grid grid-4" id="stats-grid">
        <div class="card"><h3>Best Fitness</h3><div class="value green" id="best-fitness">--</div></div>
        <div class="card"><h3>Generation</h3><div class="value blue" id="generation">0</div></div>
        <div class="card"><h3>Population</h3><div class="value orange" id="population-size">0</div></div>
        <div class="card"><h3>Operators</h3><div class="value" id="operator-count">0</div></div>
    </div>

    <div class="grid grid-2" style="margin-top: 16px;">
        <div class="card">
            <h3>Fitness History</h3>
            <div class="bar-chart" id="fitness-chart"></div>
        </div>
        <div class="card">
            <h3>Operator Weights</h3>
            <table>
                <thead><tr><th>Operator</th><th>Weight</th><th>Success Rate</th></tr></thead>
                <tbody id="operator-table"></tbody>
            </table>
        </div>
    </div>

    <div class="card" style="margin-top: 16px;">
        <h3>Fitness Dimensions</h3>
        <table>
            <thead><tr><th>Dimension</th><th>Score</th><th>Weight</th></tr></thead>
            <tbody id="dimension-table">
                <tr><td colspan="3">No evaluation data yet</td></tr>
            </tbody>
        </table>
    </div>

    <script>
        async function refresh() {
            try {
                const res = await fetch('/api/status');
                const data = await res.json();

                document.getElementById('best-fitness').textContent =
                    data.best_fitness != null ? data.best_fitness.toFixed(2) : '--';
                document.getElementById('generation').textContent =
                    data.generation ?? '--';
                document.getElementById('population-size').textContent =
                    data.population_size ?? '--';
                document.getElementById('gen-display').textContent =
                    'Generation: ' + (data.generation ?? '--');
                document.getElementById('pop-display').textContent =
                    'Population: ' + (data.population_size ?? '--');

                // Operator table
                const ops = data.operators || {};
                const opKeys = Object.keys(ops);
                document.getElementById('operator-count').textContent = opKeys.length;
                const opTbody = document.getElementById('operator-table');
                opTbody.innerHTML = opKeys.map(name => {
                    const op = ops[name];
                    const rate = op.uses > 0 ? (op.successes / op.uses * 100).toFixed(0) + '%' : '--';
                    return '<tr><td>' + name + '</td><td>' + op.weight.toFixed(2) + '</td><td>' + rate + '</td></tr>';
                }).join('');

                // Fitness chart
                const history = data.fitness_history || [];
                const chart = document.getElementById('fitness-chart');
                if (history.length > 0) {
                    const max = Math.max(...history, 1);
                    chart.innerHTML = history.map((v, i) => {
                        const h = Math.max(4, (v / max) * 100);
                        return '<div class="bar" style="height:' + h + 'px;background:var(--accent)" title="Gen ' + i + ': ' + v.toFixed(2) + '"></div>';
                    }).join('');
                } else {
                    chart.innerHTML = '<div style="color:#8b949e;font-size:13px;padding:20px 0">No data yet</div>';
                }
            } catch (e) {
                console.error('Refresh failed:', e);
            }
        }

        refresh();
        setInterval(refresh, 5000);
    </script>
</body>
</html>"""


@app.get("/api/status")
async def api_status() -> JSONResponse:
    """Return current evolution status as JSON."""
    meta_state = load_json(META_STATE_FILE)
    operators = meta_state.get("operators", {})
    fitness_history = meta_state.get("fitness_history", [])

    return JSONResponse({
        "best_fitness": max(fitness_history) if fitness_history else None,
        "generation": meta_state.get("generation", 0),
        "population_size": meta_state.get("population_size", 0),
        "stagnation_counter": meta_state.get("stagnation_counter", 0),
        "operators": operators,
        "fitness_history": fitness_history,
    })


@app.get("/health")
async def health() -> JSONResponse:
    """Simple health check endpoint."""
    return JSONResponse({"status": "ok", "service": "grounded-agent-forge-dashboard"})


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("DASHBOARD_PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
