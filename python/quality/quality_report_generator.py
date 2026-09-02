import json
from pathlib import Path
from typing import Dict, Any

def generate_html_report(results: Dict[str, Any], output_path: str = None) -> str:
    summary = results.get("summary", {})
    details = results.get("test_details", [])
    
    score = summary.get("score_pct", 0)
    score_color = "#10B981" if score >= 90 else "#F59E0B" if score >= 75 else "#EF4444"

    rows_html = ""
    for test in details:
        status = test.get("status", "UNKNOWN")
        badge_cls = "badge-pass" if status == "PASSED" else "badge-fail"
        rows_html += f"""
        <tr>
            <td><span class="layer-pill layer-{test.get('layer')}">{test.get('layer').upper()}</span></td>
            <td><strong>{test.get('test_name')}</strong></td>
            <td>{test.get('description')}</td>
            <td><span class="badge {badge_cls}">{status}</span></td>
            <td>{test.get('executed_at')}</td>
        </tr>
        """

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Supply Chain Digital Twin - Data Quality Report</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #0f172a; color: #f8fafc; margin: 0; padding: 2rem; }}
        .card {{ background-color: #1e293b; border-radius: 12px; padding: 1.5rem; box-shadow: 0 4px 20px rgba(0,0,0,0.3); margin-bottom: 2rem; }}
        h1 {{ color: #38bdf8; margin-top: 0; }}
        .metrics-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; margin-bottom: 1.5rem; }}
        .metric-box {{ background-color: #334155; padding: 1rem; border-radius: 8px; text-align: center; }}
        .metric-value {{ font-size: 2rem; font-weight: bold; margin-top: 0.5rem; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 1rem; }}
        th, td {{ padding: 0.75rem 1rem; text-align: left; border-bottom: 1px solid #334155; }}
        th {{ background-color: #334155; color: #94a3b8; text-transform: uppercase; font-size: 0.8rem; letter-spacing: 0.05em; }}
        .badge {{ padding: 0.25rem 0.6rem; border-radius: 4px; font-weight: bold; font-size: 0.8rem; }}
        .badge-pass {{ background-color: #064e3b; color: #34d399; }}
        .badge-fail {{ background-color: #7f1d1d; color: #f87171; }}
        .layer-pill {{ padding: 0.2rem 0.5rem; border-radius: 4px; font-size: 0.75rem; font-weight: 600; }}
        .layer-bronze {{ background-color: #78350f; color: #fde68a; }}
        .layer-silver {{ background-color: #334155; color: #e2e8f0; }}
        .layer-gold {{ background-color: #713f12; color: #fef08a; }}
    </style>
</head>
<body>
    <div class="card">
        <h1>🛡️ Data Quality & Integrity Audit</h1>
        <p style="color: #94a3b8;">Automated Validation Engine Report • Generated at {results.get('timestamp')}</p>
        
        <div class="metrics-grid">
            <div class="metric-box">
                <div style="color: #94a3b8;">Overall Score</div>
                <div class="metric-value" style="color: {score_color};">{score}%</div>
            </div>
            <div class="metric-box">
                <div style="color: #94a3b8;">Total Tests</div>
                <div class="metric-value">{summary.get('total_tests', 0)}</div>
            </div>
            <div class="metric-box">
                <div style="color: #94a3b8;">Passed</div>
                <div class="metric-value" style="color: #34d399;">{summary.get('passed', 0)}</div>
            </div>
            <div class="metric-box">
                <div style="color: #94a3b8;">Failed</div>
                <div class="metric-value" style="color: #f87171;">{summary.get('failed', 0)}</div>
            </div>
        </div>

        <table>
            <thead>
                <tr>
                    <th>Layer</th>
                    <th>Test Name</th>
                    <th>Description</th>
                    <th>Status</th>
                    <th>Executed At</th>
                </tr>
            </thead>
            <tbody>
                {rows_html}
            </tbody>
        </table>
    </div>
</body>
</html>
"""
    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)
            
    return html_content
