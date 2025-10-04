#!/usr/bin/env python3
"""
OSUSAPPS Odoo 17 - Code Quality Metrics Dashboard

This script creates an interactive HTML dashboard for tracking code quality metrics
across all modules in the OSUSAPPS project. It aggregates data from various
analysis tools and presents comprehensive quality insights.
"""

import os
import sys
import json
import re
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import sqlite3
from dataclasses import dataclass, asdict
import argparse

@dataclass
class QualityMetrics:
    """Quality metrics for a module"""
    module_name: str
    timestamp: str
    overall_score: float
    structure_score: float
    security_score: float
    performance_score: float
    style_score: float
    test_coverage: float
    lines_of_code: int
    cyclomatic_complexity: float
    technical_debt_ratio: float
    issues_count: Dict[str, int]
    vulnerability_count: Dict[str, int]

class QualityDashboard:
    """Code Quality Dashboard Generator"""
    
    def __init__(self, workspace_path: str, db_path: str = None):
        self.workspace_path = Path(workspace_path)
        self.db_path = db_path or str(self.workspace_path / "quality_metrics.db")
        self.init_database()
        
    def init_database(self):
        """Initialize SQLite database for metrics storage"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS quality_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                module_name TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                overall_score REAL,
                structure_score REAL,
                security_score REAL,
                performance_score REAL,
                style_score REAL,
                test_coverage REAL,
                lines_of_code INTEGER,
                cyclomatic_complexity REAL,
                technical_debt_ratio REAL,
                issues_count TEXT,
                vulnerability_count TEXT,
                UNIQUE(module_name, timestamp)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trend_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                total_modules INTEGER,
                avg_quality_score REAL,
                total_issues INTEGER,
                total_vulnerabilities INTEGER,
                UNIQUE(date)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def store_metrics(self, metrics: QualityMetrics):
        """Store quality metrics in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO quality_metrics 
            (module_name, timestamp, overall_score, structure_score, security_score,
             performance_score, style_score, test_coverage, lines_of_code,
             cyclomatic_complexity, technical_debt_ratio, issues_count, vulnerability_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            metrics.module_name,
            metrics.timestamp,
            metrics.overall_score,
            metrics.structure_score,
            metrics.security_score,
            metrics.performance_score,
            metrics.style_score,
            metrics.test_coverage,
            metrics.lines_of_code,
            metrics.cyclomatic_complexity,
            metrics.technical_debt_ratio,
            json.dumps(metrics.issues_count),
            json.dumps(metrics.vulnerability_count)
        ))
        
        conn.commit()
        conn.close()
    
    def get_latest_metrics(self) -> List[QualityMetrics]:
        """Get latest metrics for all modules"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM quality_metrics qm1
            WHERE timestamp = (
                SELECT MAX(timestamp) FROM quality_metrics qm2 
                WHERE qm2.module_name = qm1.module_name
            )
            ORDER BY overall_score DESC
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        metrics_list = []
        for row in rows:
            metrics = QualityMetrics(
                module_name=row[1],
                timestamp=row[2],
                overall_score=row[3],
                structure_score=row[4],
                security_score=row[5],
                performance_score=row[6],
                style_score=row[7],
                test_coverage=row[8],
                lines_of_code=row[9],
                cyclomatic_complexity=row[10],
                technical_debt_ratio=row[11],
                issues_count=json.loads(row[12] or '{}'),
                vulnerability_count=json.loads(row[13] or '{}')
            )
            metrics_list.append(metrics)
        
        return metrics_list
    
    def get_historical_data(self, days: int = 30) -> Dict[str, List]:
        """Get historical trend data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        start_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        cursor.execute('''
            SELECT date, total_modules, avg_quality_score, total_issues, total_vulnerabilities
            FROM trend_data 
            WHERE date >= ?
            ORDER BY date
        ''', (start_date,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return {
            'dates': [row[0] for row in rows],
            'modules': [row[1] for row in rows],
            'quality_scores': [row[2] for row in rows],
            'issues': [row[3] for row in rows],
            'vulnerabilities': [row[4] for row in rows]
        }
    
    def generate_dashboard(self, output_file: str = None) -> str:
        """Generate HTML dashboard"""
        output_file = output_file or str(self.workspace_path / "quality_dashboard.html")
        
        # Collect current metrics
        latest_metrics = self.get_latest_metrics()
        historical_data = self.get_historical_data()
        
        # Calculate summary statistics
        total_modules = len(latest_metrics)
        avg_score = sum(m.overall_score for m in latest_metrics) / total_modules if total_modules > 0 else 0
        total_issues = sum(sum(m.issues_count.values()) for m in latest_metrics)
        total_vulnerabilities = sum(sum(m.vulnerability_count.values()) for m in latest_metrics)
        
        # Generate HTML content
        html_content = self._generate_html_template(
            latest_metrics, historical_data, {
                'total_modules': total_modules,
                'avg_score': avg_score,
                'total_issues': total_issues,
                'total_vulnerabilities': total_vulnerabilities
            }
        )
        
        # Write to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return output_file
    
    def _generate_html_template(self, metrics: List[QualityMetrics], 
                              historical_data: Dict, summary: Dict) -> str:
        """Generate HTML dashboard template"""
        
        # Convert metrics to JSON for JavaScript
        metrics_json = json.dumps([asdict(m) for m in metrics], indent=2)
        historical_json = json.dumps(historical_data, indent=2)
        
        html_template = f'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OSUSAPPS Code Quality Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }}
        
        .header {{
            background: rgba(255, 255, 255, 0.95);
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }}
        
        .header h1 {{
            color: #2c3e50;
            text-align: center;
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        .header .subtitle {{
            text-align: center;
            color: #7f8c8d;
            font-size: 1.2em;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 0 20px;
        }}
        
        .summary-cards {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .card {{
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 8px 25px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }}
        
        .card:hover {{
            transform: translateY(-5px);
        }}
        
        .card-header {{
            display: flex;
            align-items: center;
            margin-bottom: 15px;
        }}
        
        .card-icon {{
            font-size: 2em;
            margin-right: 15px;
        }}
        
        .card-title {{
            font-size: 1.1em;
            color: #2c3e50;
            font-weight: 600;
        }}
        
        .card-value {{
            font-size: 2.5em;
            font-weight: bold;
            color: #3498db;
            margin-bottom: 5px;
        }}
        
        .card-subtitle {{
            color: #7f8c8d;
            font-size: 0.9em;
        }}
        
        .charts-container {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .chart-card {{
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        }}
        
        .chart-title {{
            font-size: 1.3em;
            color: #2c3e50;
            margin-bottom: 20px;
            text-align: center;
        }}
        
        .modules-table {{
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 8px 25px rgba(0,0,0,0.1);
            overflow-x: auto;
        }}
        
        .table-title {{
            font-size: 1.3em;
            color: #2c3e50;
            margin-bottom: 20px;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ecf0f1;
        }}
        
        th {{
            background-color: #f8f9fa;
            font-weight: 600;
            color: #2c3e50;
        }}
        
        tr:hover {{
            background-color: #f8f9fa;
        }}
        
        .score {{
            padding: 5px 10px;
            border-radius: 20px;
            color: white;
            font-weight: bold;
            text-align: center;
        }}
        
        .score-excellent {{ background-color: #27ae60; }}
        .score-good {{ background-color: #3498db; }}
        .score-fair {{ background-color: #f39c12; }}
        .score-poor {{ background-color: #e74c3c; }}
        
        .issues-critical {{ color: #e74c3c; font-weight: bold; }}
        .issues-high {{ color: #f39c12; font-weight: bold; }}
        .issues-medium {{ color: #3498db; }}
        .issues-low {{ color: #27ae60; }}
        
        .footer {{
            text-align: center;
            padding: 20px;
            color: rgba(255, 255, 255, 0.8);
            margin-top: 30px;
        }}
        
        @media (max-width: 768px) {{
            .charts-container {{
                grid-template-columns: 1fr;
            }}
            
            .header h1 {{
                font-size: 2em;
            }}
            
            .card-value {{
                font-size: 2em;
            }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🔍 OSUSAPPS Code Quality Dashboard</h1>
        <p class="subtitle">Odoo 17 Enterprise - Real-time Quality Metrics & Analysis</p>
    </div>
    
    <div class="container">
        <!-- Summary Cards -->
        <div class="summary-cards">
            <div class="card">
                <div class="card-header">
                    <div class="card-icon">📊</div>
                    <div class="card-title">Total Modules</div>
                </div>
                <div class="card-value">{summary['total_modules']}</div>
                <div class="card-subtitle">Active modules analyzed</div>
            </div>
            
            <div class="card">
                <div class="card-header">
                    <div class="card-icon">⭐</div>
                    <div class="card-title">Average Quality Score</div>
                </div>
                <div class="card-value">{summary['avg_score']:.1f}</div>
                <div class="card-subtitle">Out of 100 points</div>
            </div>
            
            <div class="card">
                <div class="card-header">
                    <div class="card-icon">🐛</div>
                    <div class="card-title">Total Issues</div>
                </div>
                <div class="card-value">{summary['total_issues']}</div>
                <div class="card-subtitle">Code quality issues</div>
            </div>
            
            <div class="card">
                <div class="card-header">
                    <div class="card-icon">🔒</div>
                    <div class="card-title">Security Vulnerabilities</div>
                </div>
                <div class="card-value">{summary['total_vulnerabilities']}</div>
                <div class="card-subtitle">Security issues found</div>
            </div>
        </div>
        
        <!-- Charts -->
        <div class="charts-container">
            <div class="chart-card">
                <h3 class="chart-title">Quality Score Distribution</h3>
                <canvas id="qualityChart"></canvas>
            </div>
            
            <div class="chart-card">
                <h3 class="chart-title">Quality Trends (30 Days)</h3>
                <canvas id="trendChart"></canvas>
            </div>
        </div>
        
        <!-- Modules Table -->
        <div class="modules-table">
            <h3 class="table-title">📋 Module Quality Overview</h3>
            <table id="modulesTable">
                <thead>
                    <tr>
                        <th>Module Name</th>
                        <th>Overall Score</th>
                        <th>Security</th>
                        <th>Performance</th>
                        <th>Structure</th>
                        <th>Issues</th>
                        <th>Last Updated</th>
                    </tr>
                </thead>
                <tbody id="moduleTableBody">
                    <!-- Table rows will be populated by JavaScript -->
                </tbody>
            </table>
        </div>
    </div>
    
    <div class="footer">
        <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | OSUSAPPS Quality Dashboard v1.0</p>
    </div>
    
    <script>
        // Data from Python
        const metricsData = {metrics_json};
        const historicalData = {historical_json};
        
        // Initialize dashboard
        document.addEventListener('DOMContentLoaded', function() {{
            initializeCharts();
            populateModulesTable();
        }});
        
        function initializeCharts() {{
            // Quality Score Distribution Chart
            const qualityCtx = document.getElementById('qualityChart').getContext('2d');
            
            const qualityScores = metricsData.map(m => m.overall_score);
            const moduleNames = metricsData.map(m => m.module_name);
            
            new Chart(qualityCtx, {{
                type: 'bar',
                data: {{
                    labels: moduleNames.slice(0, 10), // Top 10 modules
                    datasets: [{{
                        label: 'Quality Score',
                        data: qualityScores.slice(0, 10),
                        backgroundColor: qualityScores.slice(0, 10).map(score => {{
                            if (score >= 90) return '#27ae60';
                            if (score >= 75) return '#3498db';
                            if (score >= 60) return '#f39c12';
                            return '#e74c3c';
                        }}),
                        borderWidth: 1
                    }}]
                }},
                options: {{
                    responsive: true,
                    plugins: {{
                        legend: {{
                            display: false
                        }}
                    }},
                    scales: {{
                        y: {{
                            beginAtZero: true,
                            max: 100
                        }}
                    }}
                }}
            }});
            
            // Trend Chart
            if (historicalData.dates && historicalData.dates.length > 0) {{
                const trendCtx = document.getElementById('trendChart').getContext('2d');
                
                new Chart(trendCtx, {{
                    type: 'line',
                    data: {{
                        labels: historicalData.dates,
                        datasets: [{{
                            label: 'Average Quality Score',
                            data: historicalData.quality_scores,
                            borderColor: '#3498db',
                            backgroundColor: 'rgba(52, 152, 219, 0.1)',
                            tension: 0.4
                        }}, {{
                            label: 'Total Issues',
                            data: historicalData.issues,
                            borderColor: '#e74c3c',
                            backgroundColor: 'rgba(231, 76, 60, 0.1)',
                            tension: 0.4,
                            yAxisID: 'y1'
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        interaction: {{
                            mode: 'index',
                            intersect: false,
                        }},
                        scales: {{
                            y: {{
                                type: 'linear',
                                display: true,
                                position: 'left',
                                beginAtZero: true,
                                max: 100
                            }},
                            y1: {{
                                type: 'linear',
                                display: true,
                                position: 'right',
                                beginAtZero: true,
                                grid: {{
                                    drawOnChartArea: false,
                                }},
                            }}
                        }}
                    }}
                }});
            }}
        }}
        
        function populateModulesTable() {{
            const tableBody = document.getElementById('moduleTableBody');
            
            metricsData.forEach(module => {{
                const row = document.createElement('tr');
                
                const totalIssues = Object.values(module.issues_count).reduce((a, b) => a + b, 0);
                const criticalIssues = module.issues_count.CRITICAL || 0;
                const highIssues = module.issues_count.HIGH || 0;
                
                row.innerHTML = `
                    <td><strong>${{module.module_name}}</strong></td>
                    <td><span class="score ${{getScoreClass(module.overall_score)}}">${{module.overall_score.toFixed(1)}}</span></td>
                    <td><span class="score ${{getScoreClass(module.security_score)}}">${{module.security_score.toFixed(1)}}</span></td>
                    <td><span class="score ${{getScoreClass(module.performance_score)}}">${{module.performance_score.toFixed(1)}}</span></td>
                    <td><span class="score ${{getScoreClass(module.structure_score)}}">${{module.structure_score.toFixed(1)}}</span></td>
                    <td>
                        <span class="issues-critical">${{criticalIssues}}</span> /
                        <span class="issues-high">${{highIssues}}</span> /
                        <span class="issues-medium">${{totalIssues - criticalIssues - highIssues}}</span>
                    </td>
                    <td>${{new Date(module.timestamp).toLocaleDateString()}}</td>
                `;
                
                tableBody.appendChild(row);
            }});
        }}
        
        function getScoreClass(score) {{
            if (score >= 90) return 'score-excellent';
            if (score >= 75) return 'score-good';
            if (score >= 60) return 'score-fair';
            return 'score-poor';
        }}
    </script>
</body>
</html>
        '''
        
        return html_template.strip()
    
    def update_trend_data(self):
        """Update daily trend data"""
        metrics = self.get_latest_metrics()
        
        if not metrics:
            return
        
        today = datetime.now().strftime('%Y-%m-%d')
        total_modules = len(metrics)
        avg_score = sum(m.overall_score for m in metrics) / total_modules
        total_issues = sum(sum(m.issues_count.values()) for m in metrics)
        total_vulnerabilities = sum(sum(m.vulnerability_count.values()) for m in metrics)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO trend_data
            (date, total_modules, avg_quality_score, total_issues, total_vulnerabilities)
            VALUES (?, ?, ?, ?, ?)
        ''', (today, total_modules, avg_score, total_issues, total_vulnerabilities))
        
        conn.commit()
        conn.close()
    
    def collect_module_metrics(self, module_path: Path) -> QualityMetrics:
        """Collect metrics for a single module"""
        # This would integrate with the code analyzer
        # For now, return sample data
        return QualityMetrics(
            module_name=module_path.name,
            timestamp=datetime.now().isoformat(),
            overall_score=75.5,
            structure_score=80.0,
            security_score=70.0,
            performance_score=85.0,
            style_score=65.0,
            test_coverage=60.0,
            lines_of_code=1500,
            cyclomatic_complexity=8.5,
            technical_debt_ratio=0.15,
            issues_count={"CRITICAL": 0, "HIGH": 2, "MEDIUM": 5, "LOW": 8},
            vulnerability_count={"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
        )

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="OSUSAPPS Quality Dashboard Generator")
    parser.add_argument("workspace", help="Path to OSUSAPPS workspace")
    parser.add_argument("--output", help="Output HTML file path")
    parser.add_argument("--update", action="store_true", help="Update metrics before generating dashboard")
    parser.add_argument("--db", help="Database file path")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.workspace):
        print(f"❌ Workspace not found: {args.workspace}")
        sys.exit(1)
    
    dashboard = QualityDashboard(args.workspace, args.db)
    
    if args.update:
        print("📊 Updating quality metrics...")
        # In a real implementation, this would run the code analyzer
        # and store results in the database
        dashboard.update_trend_data()
    
    print("🚀 Generating quality dashboard...")
    output_file = dashboard.generate_dashboard(args.output)
    
    print(f"✅ Dashboard generated: {output_file}")
    print(f"🌐 Open in browser: file://{os.path.abspath(output_file)}")

if __name__ == "__main__":
    main()