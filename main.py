#!/usr/bin/env python3
"""
Main Orchestrator - Semiconductor Capacity Management System
"""

import os
import sys
import argparse
from datetime import datetime
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def print_banner():
    print("="*80)
    print("  SEMICONDUCTOR CAPACITY MANAGEMENT SYSTEM")
    print("="*80)
    print("  Advanced Analytics Platform for Fab Operations & Infrastructure Readiness")
    print("="*80)

def check_dependencies():
    required = ['pandas', 'numpy', 'plotly', 'dash', 'scipy', 'sklearn']
    missing = []
    for package in required:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    if missing:
        print(f"\n  Missing: {', '.join(missing)}")
        print(f"  Install: pip install {' '.join(missing)}")
        return False
    return True

def generate_data():
    print("\n" + "="*80)
    print("  STEP 1: DATA GENERATION")
    print("="*80)
    sys.path.insert(0, BASE_DIR)
    from data_generator import SemiconductorDataGenerator
    generator = SemiconductorDataGenerator(random_seed=42)
    generator.generate_all()
    return True

def run_analytics():
    print("\n" + "="*80)
    print("  STEP 2: CAPACITY ANALYSIS")
    print("="*80)
    sys.path.insert(0, os.path.join(BASE_DIR, 'models'))
    from capacity_planning import CapacityPlanningModel, ToolReliabilityModel

    equipment = pd.read_csv(os.path.join(BASE_DIR, "data/raw/equipment_master.csv"))
    operations = pd.read_csv(os.path.join(BASE_DIR, "data/raw/fab_operations.csv"), parse_dates=['date'])
    forecast   = pd.read_csv(os.path.join(BASE_DIR, "data/raw/demand_forecast.csv"), parse_dates=['quarter'])
    capex      = pd.read_csv(os.path.join(BASE_DIR, "data/raw/capex_projects.csv"),  parse_dates=['start_date','expected_completion'])

    capacity_model   = CapacityPlanningModel(equipment, operations, forecast)
    reliability_model = ToolReliabilityModel(equipment, operations)

    print("\n  Bottleneck analysis...")
    bottleneck = capacity_model.calculate_bottleneck_analysis(target_output_wpw=18000)
    print(f"  Top bottleneck: {bottleneck.iloc[0]['tool_type']} ({bottleneck.iloc[0]['utilization_at_target']:.1%})")

    print("  Monte Carlo simulation (10,000 iterations)...")
    risk_metrics, _ = capacity_model.monte_carlo_capacity_risk(n_simulations=10000)
    print(f"  Service Level: {risk_metrics['service_level_probability']:.1%} | P95 Shortfall: {risk_metrics['p95_shortfall_wpw']:,} WPW")

    print("  CapEx optimization...")
    opt, _ = capacity_model.optimize_capex_allocation(capex, budget_constraint=1500000000)
    print(f"  Projects Selected: {opt['projects_selected']} | NPV: ${opt['total_npv']/1e9:.2f}B")

    print("  Scenario analysis...")
    scenarios = capacity_model.calculate_capacity_scenarios()
    print(f"  {len(scenarios)} scenarios analyzed")

    print("  Reliability / MTBF analysis...")
    mtbf = reliability_model.calculate_mtbf_analysis()
    if len(mtbf) > 0:
        print(f"  {len(mtbf)} tool types analyzed")

    return True

def launch_dashboard():
    print("\n" + "="*80)
    print("  STEP 3: LAUNCHING DASHBOARD")
    print("="*80)
    port = int(os.environ.get("PORT", 8050))
    print(f"\n  Dashboard -> http://0.0.0.0:{port}")
    print("  Press Ctrl+C to stop\n")

    sys.path.insert(0, os.path.join(BASE_DIR, 'dashboards'))
    from interactive_dashboard import app
    app.run(debug=False, host='0.0.0.0', port=port)   # ← FIXED: app.run (not app.run_server)

def generate_report():
    print("\n" + "="*80)
    print("  GENERATING SUMMARY REPORT")
    print("="*80)

    equipment  = pd.read_csv(os.path.join(BASE_DIR, "data/raw/equipment_master.csv"))
    operations = pd.read_csv(os.path.join(BASE_DIR, "data/raw/fab_operations.csv"), parse_dates=['date'])
    forecast   = pd.read_csv(os.path.join(BASE_DIR, "data/raw/demand_forecast.csv"), parse_dates=['quarter'])
    capex      = pd.read_csv(os.path.join(BASE_DIR, "data/raw/capex_projects.csv"),  parse_dates=['start_date','expected_completion'])
    npi        = pd.read_csv(os.path.join(BASE_DIR, "data/raw/npi_milestones.csv"),  parse_dates=['phase_start','phase_end'])

    latest_ops = operations[operations['date'] == operations['date'].max()]

    report = f"""
{'='*80}
SEMICONDUCTOR CAPACITY MANAGEMENT — EXECUTIVE SUMMARY
{'='*80}
Generated : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

FLEET STATUS
  Total Tools     : {len(equipment)}
  Active          : {len(equipment[equipment['status']=='Active'])}
  Avg Fleet Age   : {equipment['age_years'].mean():.1f} years
  Asset Value     : ${equipment['cost_usd'].sum()/1e9:.2f}B

OPERATIONAL PERFORMANCE
  Fleet OEE       : {latest_ops['oee'].mean():.1%}
  Utilization     : {latest_ops['utilization_rate'].mean():.1%}
  Daily Output    : {latest_ops['output_wafers'].sum():,} wafers
  Avg Cycle Time  : {latest_ops['cycle_time_hours'].mean():.1f} hours

CAPEX PORTFOLIO
  Total Investment: ${capex['investment_usd'].sum()/1e9:.2f}B
  Portfolio NPV   : ${capex['npv_usd'].sum()/1e9:.2f}B
  Average IRR     : {capex['irr_percent'].mean():.1f}%
  In Progress     : {len(capex[capex['status']=='In Progress'])} projects

NPI PROGRAMS
  Active Programs : {len(npi['program_name'].unique())}
  Avg Progress    : {npi['progress_percent'].mean():.0f}%
{'='*80}
"""
    print(report)
    os.makedirs(os.path.join(BASE_DIR, 'reports'), exist_ok=True)
    fname = os.path.join(BASE_DIR, f"reports/report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
    with open(fname, 'w') as f:
        f.write(report)
    print(f"  Saved -> {fname}")

def main():
    parser = argparse.ArgumentParser(description='Semiconductor Capacity Management System')
    parser.add_argument('--full',      action='store_true', help='Full pipeline + dashboard')
    parser.add_argument('--generate',  action='store_true', help='Generate synthetic data')
    parser.add_argument('--analyze',   action='store_true', help='Run capacity analysis')
    parser.add_argument('--dashboard', action='store_true', help='Launch dashboard')
    parser.add_argument('--report',    action='store_true', help='Generate report')
    args = parser.parse_args()

    print_banner()
    if not check_dependencies():
        return

    if args.full:
        generate_data()
        run_analytics()
        generate_report()
        launch_dashboard()
    else:
        if args.generate:  generate_data()
        if args.analyze:   run_analytics()
        if args.report:    generate_report()
        if args.dashboard: launch_dashboard()
        if not any(vars(args).values()):
            # No flags → default: generate + dashboard (Railway-safe)
            generate_data()
            launch_dashboard()

if __name__ == "__main__":
    main()
