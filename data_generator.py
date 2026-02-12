#!/usr/bin/env python3
"""
Advanced Semiconductor Fab Data Generator
Generates realistic, comprehensive operational data for capacity management system
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class SemiconductorDataGenerator:
    def __init__(self, random_seed=42):
        np.random.seed(random_seed)
        self.start_date = datetime(2023, 1, 1)
        self.end_date = datetime(2024, 6, 30)
        
        # Realistic semiconductor tool specifications
        self.tool_specs = {
            'Lithography_EUV': {
                'cost_usd': 180000000,
                'throughput_wph': 120,
                'util_target': 0.80,
                'count_range': (8, 15),
                'mtbf_hours': 500,
                'critical': True,
                'process_steps': 25
            },
            'Lithography_DUV': {
                'cost_usd': 45000000,
                'throughput_wph': 180,
                'util_target': 0.85,
                'count_range': (15, 25),
                'mtbf_hours': 600,
                'critical': True,
                'process_steps': 40
            },
            'Etch_Plasma': {
                'cost_usd': 8000000,
                'throughput_wph': 60,
                'util_target': 0.82,
                'count_range': (20, 30),
                'mtbf_hours': 450,
                'critical': False,
                'process_steps': 65
            },
            'Deposition_CVD': {
                'cost_usd': 6000000,
                'throughput_wph': 90,
                'util_target': 0.85,
                'count_range': (18, 28),
                'mtbf_hours': 500,
                'critical': False,
                'process_steps': 45
            },
            'Deposition_PVD': {
                'cost_usd': 5500000,
                'throughput_wph': 100,
                'util_target': 0.85,
                'count_range': (12, 20),
                'mtbf_hours': 550,
                'critical': False,
                'process_steps': 20
            },
            'CMP': {
                'cost_usd': 3500000,
                'throughput_wph': 120,
                'util_target': 0.88,
                'count_range': (15, 22),
                'mtbf_hours': 600,
                'critical': False,
                'process_steps': 25
            },
            'Metrology_SEM': {
                'cost_usd': 2500000,
                'throughput_wph': 40,
                'util_target': 0.75,
                'count_range': (25, 35),
                'mtbf_hours': 700,
                'critical': True,
                'process_steps': 80
            },
            'Metrology_Optical': {
                'cost_usd': 1200000,
                'throughput_wph': 80,
                'util_target': 0.80,
                'count_range': (20, 30),
                'mtbf_hours': 650,
                'critical': False,
                'process_steps': 40
            },
            'Ion_Implant': {
                'cost_usd': 7000000,
                'throughput_wph': 50,
                'util_target': 0.80,
                'count_range': (10, 18),
                'mtbf_hours': 520,
                'critical': False,
                'process_steps': 15
            },
            'Wet_Process': {
                'cost_usd': 1800000,
                'throughput_wph': 150,
                'util_target': 0.90,
                'count_range': (15, 25),
                'mtbf_hours': 800,
                'critical': False,
                'process_steps': 35
            }
        }
    
    def generate_equipment_master(self):
        """Generate comprehensive equipment master data"""
        print("🔧 Generating equipment master data...")
        
        equipment_data = []
        tool_id_counter = 1000
        
        for tool_type, specs in self.tool_specs.items():
            count = np.random.randint(specs['count_range'][0], specs['count_range'][1] + 1)
            
            for i in range(count):
                install_date = self.start_date + timedelta(days=np.random.randint(-730, 0))
                age_days = (datetime.now() - install_date).days
                
                equipment_data.append({
                    'tool_id': f"{tool_type[:3].upper()}{tool_id_counter}",
                    'tool_type': tool_type,
                    'tool_category': tool_type.split('_')[0],
                    'cost_usd': specs['cost_usd'],
                    'throughput_wph': specs['throughput_wph'],
                    'install_date': install_date,
                    'age_years': round(age_days / 365, 1),
                    'status': np.random.choice(
                        ['Active', 'Active', 'Active', 'Active', 'Maintenance', 'Upgrade'],
                        p=[0.75, 0.10, 0.05, 0.05, 0.03, 0.02]
                    ),
                    'cleanroom_bay': f"Bay_{np.random.randint(1, 9)}",
                    'cleanroom_class': np.random.choice(['Class_1', 'Class_10', 'Class_100']),
                    'utilization_target': specs['util_target'],
                    'pm_schedule_hours': np.random.choice([168, 336, 720]),
                    'next_pm_date': datetime.now() + timedelta(days=np.random.randint(7, 60)),
                    'mtbf_hours': specs['mtbf_hours'],
                    'is_critical': specs['critical'],
                    'vendor': np.random.choice(['ASML', 'Applied Materials', 'LAM Research', 'Tokyo Electron', 'KLA']),
                    'warranty_expiry': install_date + timedelta(days=365*3),
                    'depreciation_years': 7
                })
                tool_id_counter += 1
        
        df = pd.DataFrame(equipment_data)
        df.to_csv('data/raw/equipment_master.csv', index=False)
        print(f"   ✅ Generated {len(df)} equipment records across {len(self.tool_specs)} tool types")
        return df
    
    def generate_fab_operations(self, equipment_df):
        """Generate detailed daily operations data"""
        print("\n🏭 Generating fab operations data...")
        
        date_range = pd.date_range(start=self.start_date, end=self.end_date, freq='D')
        operations_data = []
        
        for idx, date in enumerate(date_range):
            if idx % 30 == 0:
                print(f"   Processing {date.strftime('%Y-%m-%d')}...")
            
            for _, tool in equipment_df.iterrows():
                # Calculate realistic utilization based on multiple factors
                day_of_week = date.weekday()
                is_weekend = day_of_week >= 5
                
                # Base utilization
                base_util = tool['utilization_target']
                
                # Trend component (gradual improvement over time)
                trend = 0.03 * ((date - self.start_date).days / 365)
                
                # Seasonal component
                seasonal = 0.08 * np.sin(2 * np.pi * date.month / 12)
                
                # Random events (equipment failures, yield excursions)
                if tool['is_critical']:
                    event = np.random.choice([0, -0.20, -0.10, 0.05], p=[0.85, 0.05, 0.07, 0.03])
                else:
                    event = np.random.choice([0, -0.15, 0.05], p=[0.90, 0.08, 0.02])
                
                # Weekend factor
                weekend_factor = 0.65 if is_weekend else 1.0
                
                # Age degradation
                age_factor = max(0.85, 1.0 - (tool['age_years'] * 0.02))
                
                # Calculate final utilization
                utilization = (base_util + trend + seasonal + event) * weekend_factor * age_factor
                utilization = np.clip(utilization, 0.25, 0.98)
                
                # OEE components
                availability = np.random.uniform(0.88, 0.99) if tool['status'] == 'Active' else np.random.uniform(0.50, 0.75)
                performance = np.random.uniform(0.92, 0.98)
                quality = np.random.uniform(0.93, 0.995)
                oee = availability * performance * quality
                
                # Output calculation
                theoretical_output = tool['throughput_wph'] * 24 * utilization
                actual_output = theoretical_output * performance * quality
                
                # WIP and cycle time
                if 'Lithography' in tool['tool_type']:
                    wip_wafers = np.random.randint(100, 600)
                    cycle_time_hours = round(np.random.uniform(4, 48), 2)
                elif 'Metrology' in tool['tool_type']:
                    wip_wafers = np.random.randint(200, 800)
                    cycle_time_hours = round(np.random.uniform(1, 8), 2)
                else:
                    wip_wafers = np.random.randint(50, 300)
                    cycle_time_hours = round(np.random.uniform(2, 16), 2)
                
                # Downtime
                if np.random.random() < 0.12:
                    unplanned_downtime = round(np.random.exponential(3), 2)
                else:
                    unplanned_downtime = 0
                
                operations_data.append({
                    'date': date,
                    'tool_id': tool['tool_id'],
                    'tool_type': tool['tool_type'],
                    'tool_category': tool['tool_category'],
                    'cleanroom_bay': tool['cleanroom_bay'],
                    'utilization_rate': round(utilization, 4),
                    'availability': round(availability, 4),
                    'performance_efficiency': round(performance, 4),
                    'quality_rate': round(quality, 4),
                    'oee': round(oee, 4),
                    'wip_wafers': wip_wafers,
                    'output_wafers': round(actual_output),
                    'cycle_time_hours': cycle_time_hours,
                    'unplanned_downtime_hours': unplanned_downtime,
                    'scheduled_downtime_hours': 2.0 if day_of_week == 6 else 0.0,
                    'operating_hours': round(24 - unplanned_downtime - (2.0 if day_of_week == 6 else 0.0), 2)
                })
        
        df = pd.DataFrame(operations_data)
        df.to_csv('data/raw/fab_operations.csv', index=False)
        print(f"   ✅ Generated {len(df):,} daily operation records")
        return df
    
    def generate_demand_forecast(self):
        """Generate multi-product demand forecast"""
        print("\n📊 Generating demand forecast data...")
        
        products = {
            'Mobile_SoC_3nm': {'base': 18000, 'growth': 0.18, 'volatility': 0.12},
            'Mobile_SoC_5nm': {'base': 28000, 'growth': 0.06, 'volatility': 0.08},
            'HPC_CPU_5nm': {'base': 9500, 'growth': 0.28, 'volatility': 0.15},
            'HPC_GPU_5nm': {'base': 7200, 'growth': 0.35, 'volatility': 0.18},
            'Automotive_5nm': {'base': 3500, 'growth': 0.48, 'volatility': 0.20},
            'IoT_7nm': {'base': 15000, 'growth': 0.12, 'volatility': 0.10}
        }
        
        quarters = pd.date_range(start='2023-01-01', end='2027-12-31', freq='QE')
        forecast_data = []
        
        for quarter in quarters:
            for product, specs in products.items():
                q_idx = len([q for q in quarters if q <= quarter])
                
                # Growth trend
                trend = specs['base'] * (1 + specs['growth']) ** (q_idx / 4)
                
                # Seasonal component
                seasonal_factor = 1 + 0.12 * np.sin(2 * np.pi * quarter.month / 12)
                
                # Random noise
                noise = np.random.normal(0, specs['volatility'])
                
                demand = trend * seasonal_factor * (1 + noise)
                demand = max(0, demand)
                
                # Revenue calculation ($/wafer varies by product)
                revenue_per_wafer = {
                    'Mobile_SoC_3nm': 12500,
                    'Mobile_SoC_5nm': 8500,
                    'HPC_CPU_5nm': 15000,
                    'HPC_GPU_5nm': 18000,
                    'Automotive_5nm': 6500,
                    'IoT_7nm': 4200
                }[product]
                
                forecast_data.append({
                    'quarter': quarter,
                    'product': product,
                    'demand_wafers': round(demand),
                    'revenue_millions': round(demand * revenue_per_wafer / 1e6, 2),
                    'confidence_interval_low': round(demand * 0.82),
                    'confidence_interval_high': round(demand * 1.18),
                    'market_segment': product.split('_')[0],
                    'process_node': product.split('_')[-1],
                    'avg_selling_price_usd': revenue_per_wafer
                })
        
        df = pd.DataFrame(forecast_data)
        df.to_csv('data/raw/demand_forecast.csv', index=False)
        print(f"   ✅ Generated {len(df)} demand forecast records")
        return df
    
    def generate_capex_projects(self):
        """Generate realistic CapEx investment portfolio"""
        print("\n💰 Generating CapEx projects...")
        
        projects = [
            {
                'name': 'EUV_Litho_Expansion_Phase1',
                'type': 'Capacity Expansion',
                'investment': 650000000,
                'start': '2023-03-01',
                'duration': 18,
                'annual_benefit': 145000000,
                'priority': 'Critical',
                'risk': 'Medium'
            },
            {
                'name': 'Advanced_Packaging_Line',
                'type': 'New Capability',
                'investment': 380000000,
                'start': '2023-06-01',
                'duration': 24,
                'annual_benefit': 72000000,
                'priority': 'High',
                'risk': 'Medium'
            },
            {
                'name': 'Cleanroom_Bay_Expansion',
                'type': 'Infrastructure',
                'investment': 220000000,
                'start': '2023-09-01',
                'duration': 20,
                'annual_benefit': 38000000,
                'priority': 'High',
                'risk': 'Low'
            },
            {
                'name': 'EUV_Litho_Expansion_Phase2',
                'type': 'Capacity Expansion',
                'investment': 850000000,
                'start': '2024-01-01',
                'duration': 18,
                'annual_benefit': 195000000,
                'priority': 'Critical',
                'risk': 'High'
            },
            {
                'name': 'AI_Accelerator_Dedicated_Line',
                'type': 'New Capability',
                'investment': 520000000,
                'start': '2024-06-01',
                'duration': 22,
                'annual_benefit': 118000000,
                'priority': 'High',
                'risk': 'Medium'
            },
            {
                'name': 'Automotive_Qualification_Facility',
                'type': 'New Capability',
                'investment': 340000000,
                'start': '2024-09-01',
                'duration': 16,
                'annual_benefit': 88000000,
                'priority': 'Medium',
                'risk': 'Low'
            },
            {
                'name': 'Next_Gen_Metrology_Suite',
                'type': 'Technology Upgrade',
                'investment': 125000000,
                'start': '2025-01-01',
                'duration': 12,
                'annual_benefit': 35000000,
                'priority': 'Medium',
                'risk': 'Low'
            },
            {
                'name': 'High_NA_EUV_Tools',
                'type': 'Technology Upgrade',
                'investment': 450000000,
                'start': '2025-06-01',
                'duration': 15,
                'annual_benefit': 98000000,
                'priority': 'Critical',
                'risk': 'High'
            }
        ]
        
        capex_data = []
        discount_rate = 0.10
        
        for project in projects:
            start = datetime.strptime(project['start'], '%Y-%m-%d')
            end = start + timedelta(days=30 * project['duration'])
            
            # Calculate NPV
            cash_flows = [-project['investment']]
            for year in range(1, 8):
                cash_flows.append(project['annual_benefit'])
            
            npv = sum([cf / (1 + discount_rate) ** i for i, cf in enumerate(cash_flows)])
            
            # Calculate IRR (approximation)
            irr = (project['annual_benefit'] / project['investment']) * 100
            
            # Payback period
            payback = project['investment'] / project['annual_benefit']
            
            # Progress
            today = datetime(2024, 6, 15)
            if end < today:
                status = 'Completed'
                progress = 100
            elif start < today < end:
                status = 'In Progress'
                elapsed = (today - start).days
                total = (end - start).days
                progress = int((elapsed / total) * 100)
            else:
                status = 'Planning'
                progress = min(10, np.random.randint(0, 15))
            
            capex_data.append({
                'project_id': f"CPX{1000 + len(capex_data)}",
                'project_name': project['name'],
                'project_type': project['type'],
                'investment_usd': project['investment'],
                'start_date': start,
                'expected_completion': end,
                'duration_months': project['duration'],
                'status': status,
                'progress_percent': progress,
                'npv_usd': round(npv, 2),
                'irr_percent': round(irr, 2),
                'payback_period_years': round(payback, 2),
                'annual_benefit_usd': project['annual_benefit'],
                'strategic_priority': project['priority'],
                'risk_level': project['risk'],
                'approved_by': 'CFO',
                'business_case_roi': round((npv / project['investment']) * 100, 1)
            })
        
        df = pd.DataFrame(capex_data)
        df.to_csv('data/raw/capex_projects.csv', index=False)
        print(f"   ✅ Generated {len(df)} CapEx projects (${df['investment_usd'].sum()/1e9:.2f}B total)")
        return df
    
    def generate_npi_milestones(self):
        """Generate NPI program tracking data"""
        print("\n🚀 Generating NPI milestone data...")
        
        programs = [
            {'name': 'A17_Pro_Mobile_SoC', 'node': '3nm', 'start': '2023-01-15', 'mp_target': '2023-09-01'},
            {'name': 'M3_Ultra_HPC_Chip', 'node': '3nm', 'start': '2023-03-01', 'mp_target': '2023-11-01'},
            {'name': 'A18_Mobile_SoC', 'node': '3nm', 'start': '2024-01-10', 'mp_target': '2024-09-01'},
            {'name': 'HPC_AI_Accelerator_Gen1', 'node': '5nm', 'start': '2023-06-01', 'mp_target': '2024-03-01'},
            {'name': 'Automotive_Sensor_Fusion', 'node': '5nm', 'start': '2023-09-01', 'mp_target': '2024-08-01'},
            {'name': 'Next_Gen_GPU_Architecture', 'node': '3nm', 'start': '2024-03-01', 'mp_target': '2025-01-01'}
        ]
        
        npi_data = []
        phases = ['EVT', 'DVT', 'PVT', 'MP']
        phase_duration = {'EVT': 3, 'DVT': 4, 'PVT': 3, 'MP': 2}
        yield_targets = {'EVT': 0.68, 'DVT': 0.82, 'PVT': 0.90, 'MP': 0.94}
        
        for program in programs:
            current_date = datetime.strptime(program['start'], '%Y-%m-%d')
            
            for phase in phases:
                duration = phase_duration[phase]
                start = current_date
                end = start + timedelta(days=30 * duration)
                
                # Status determination
                today = datetime(2024, 6, 15)
                if end < today:
                    status = 'Completed'
                    progress = 100
                    yield_pct = yield_targets[phase] * np.random.uniform(0.98, 1.08)
                elif start < today < end:
                    status = 'In Progress'
                    elapsed = (today - start).days
                    total = (end - start).days
                    progress = int((elapsed / total) * 100)
                    yield_pct = yield_targets[phase] * np.random.uniform(0.88, 1.02)
                else:
                    status = 'Not Started'
                    progress = 0
                    yield_pct = 0
                
                # Infrastructure gates
                gates = {
                    'EVT': ['Tool_Install_Complete', 'Process_Qualification_Start', 'First_Wafer_Out'],
                    'DVT': ['Process_Stability_Demo', 'Yield_Target_70pct', 'Design_Validation_Complete'],
                    'PVT': ['Yield_Target_85pct', 'Cycle_Time_Qualified', 'Reliability_Validation'],
                    'MP': ['Full_Capacity_Qualified', 'Cost_Target_Met', 'Supply_Chain_Ready']
                }
                
                gates_passed = len(gates[phase]) if status == 'Completed' else \
                               int(len(gates[phase]) * (progress / 100)) if status == 'In Progress' else 0
                
                npi_data.append({
                    'program_name': program['name'],
                    'process_node': program['node'],
                    'phase': phase,
                    'phase_start': start,
                    'phase_end': end,
                    'status': status,
                    'progress_percent': progress,
                    'yield_percent': round(yield_pct * 100, 2) if yield_pct > 0 else 0,
                    'cycle_time_weeks': round(np.random.uniform(8, 16) * (1.2 if phase == 'EVT' else 1.0), 2),
                    'wafers_per_week': np.random.randint(4000, 9000) if phase == 'MP' else \
                                       np.random.randint(1500, 4000) if phase == 'PVT' else \
                                       np.random.randint(400, 1500),
                    'infrastructure_gates': '; '.join(gates[phase]),
                    'gates_passed': gates_passed,
                    'total_gates': len(gates[phase]),
                    'risk_level': np.random.choice(['Low', 'Medium', 'High'], p=[0.5, 0.35, 0.15]),
                    'investment_millions': np.random.randint(50, 200)
                })
                
                current_date = end
        
        df = pd.DataFrame(npi_data)
        df.to_csv('data/raw/npi_milestones.csv', index=False)
        print(f"   ✅ Generated {len(df)} NPI milestone records")
        return df
    
    def generate_all(self):
        """Generate complete dataset"""
        print("="*80)
        print("🔷 SEMICONDUCTOR FAB DATA GENERATION")
        print("="*80)
        
        equipment_df = self.generate_equipment_master()
        operations_df = self.generate_fab_operations(equipment_df)
        forecast_df = self.generate_demand_forecast()
        capex_df = self.generate_capex_projects()
        npi_df = self.generate_npi_milestones()
        
        print("\n" + "="*80)
        print("✅ DATA GENERATION COMPLETE")
        print("="*80)
        print(f"\n📊 Summary:")
        print(f"   Equipment Assets: {len(equipment_df)} tools")
        print(f"   Operation Records: {len(operations_df):,} daily snapshots")
        print(f"   Demand Forecasts: {len(forecast_df)} quarter-product combinations")
        print(f"   CapEx Projects: {len(capex_df)} investments (${capex_df['investment_usd'].sum()/1e9:.2f}B)")
        print(f"   NPI Milestones: {len(npi_df)} phase-gate checkpoints")
        print(f"\n   Total Data Size: ~{(len(operations_df) + len(forecast_df) + len(capex_df) + len(npi_df)):,} records")

if __name__ == "__main__":
    generator = SemiconductorDataGenerator(random_seed=42)
    generator.generate_all()
