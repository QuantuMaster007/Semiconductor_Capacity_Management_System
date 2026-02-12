"""
Advanced Capacity Planning & Optimization Models
Implements bottleneck analysis, Monte Carlo simulation, and linear programming
"""

import pandas as pd
import numpy as np
from scipy.optimize import linprog, minimize
from scipy.stats import norm
import warnings
warnings.filterwarnings('ignore')

class CapacityPlanningModel:
    """
    Advanced capacity planning model for semiconductor fab
    """
    
    def __init__(self, equipment_df, operations_df, forecast_df):
        self.equipment = equipment_df
        self.operations = operations_df
        self.forecast = forecast_df
        
        # Load tool specifications with process steps
        self.process_steps = {
            'Lithography_EUV': 25,
            'Lithography_DUV': 40,
            'Etch_Plasma': 65,
            'Deposition_CVD': 45,
            'Deposition_PVD': 20,
            'CMP': 25,
            'Metrology_SEM': 80,
            'Metrology_Optical': 40,
            'Ion_Implant': 15,
            'Wet_Process': 35
        }
        
        # Total process steps for complete wafer
        self.total_steps = sum(self.process_steps.values())
    
    def calculate_theoretical_capacity(self):
        """Calculate maximum theoretical fab capacity"""
        capacity_by_type = self.equipment.groupby('tool_type').agg({
            'throughput_wph': 'sum',
            'utilization_target': 'mean'
        }).reset_index()
        
        hours_per_week = 168  # 24/7 operation
        
        capacity_by_type['effective_wafers_per_week'] = (
            capacity_by_type['throughput_wph'] * 
            hours_per_week * 
            capacity_by_type['utilization_target']
        )
        
        return capacity_by_type
    
    def calculate_bottleneck_analysis(self, target_output_wpw=15000):
        """
        Perform Theory of Constraints bottleneck analysis
        
        Parameters:
        -----------
        target_output_wpw : int
            Target weekly wafer output
            
        Returns:
        --------
        pd.DataFrame : Bottleneck analysis by tool type
        """
        capacity_by_type = self.calculate_theoretical_capacity()
        
        results = []
        
        for _, row in capacity_by_type.iterrows():
            tool_type = row['tool_type']
            
            # Get number of process steps for this tool type
            steps_for_this_tool = self.process_steps.get(tool_type, 50)
            
            # Calculate what percentage of the total process this tool handles
            tool_process_fraction = steps_for_this_tool / self.total_steps
            
            # Calculate required capacity for this tool type to support target output
            # Each wafer needs to go through this tool 'steps_for_this_tool' times
            wafers_needed_wpw = target_output_wpw * (steps_for_this_tool / 10)  # Normalized
            
            # Calculate utilization at target output
            utilization_at_target = wafers_needed_wpw / row['effective_wafers_per_week']
            
            # Calculate constraint level (how much this tool constrains overall capacity)
            max_wafers_this_tool_can_support = row['effective_wafers_per_week'] / (steps_for_this_tool / 10)
            
            results.append({
                'tool_type': tool_type,
                'total_tools': len(self.equipment[self.equipment['tool_type'] == tool_type]),
                'total_throughput_wph': row['throughput_wph'],
                'process_steps': steps_for_this_tool,
                'effective_capacity_wpw': round(row['effective_wafers_per_week']),
                'utilization_at_target': round(min(utilization_at_target, 1.0), 4),
                'max_supportable_output_wpw': round(max_wafers_this_tool_can_support),
                'is_bottleneck': utilization_at_target > 0.90,
                'constraint_severity': round(utilization_at_target, 3) if utilization_at_target > 0.90 else 0,
                'capacity_gap_wpw': round(max(0, wafers_needed_wpw - row['effective_wafers_per_week']))
            })
        
        df = pd.DataFrame(results).sort_values('utilization_at_target', ascending=False)
        return df
    
    def monte_carlo_capacity_risk(self, n_simulations=10000, forecast_horizon_quarters=4):
        """
        Advanced Monte Carlo simulation for capacity risk assessment
        
        Varies: demand, yield, availability, cycle time
        
        Parameters:
        -----------
        n_simulations : int
            Number of Monte Carlo iterations
        forecast_horizon_quarters : int
            Number of quarters to forecast
            
        Returns:
        --------
        dict : Risk metrics and simulation results
        """
        # Get current capacity baseline
        latest_ops = self.operations[self.operations['date'] == self.operations['date'].max()]
        
        # Calculate current weekly capacity by tool type
        current_daily_capacity = latest_ops.groupby('tool_type')['output_wafers'].sum()
        current_weekly_capacity = current_daily_capacity * 7
        
        # Total fab capacity
        total_capacity_baseline = current_weekly_capacity.sum()
        
        # Get demand forecast
        forecast_latest = self.forecast[
            self.forecast['quarter'] == self.forecast['quarter'].max()
        ]
        
        # Weekly demand (convert quarterly to weekly)
        mean_weekly_demand = forecast_latest['demand_wafers'].sum() / 13  # ~13 weeks per quarter
        demand_volatility = 0.15
        
        # Simulation arrays
        simulations = []
        
        for _ in range(n_simulations):
            # Simulate demand variation
            demand_shock = np.random.normal(1.0, demand_volatility)
            simulated_demand = mean_weekly_demand * demand_shock
            
            # Simulate yield variation (affects effective capacity)
            yield_shock = np.random.normal(0.92, 0.05)  # Mean 92%, std 5%
            yield_shock = np.clip(yield_shock, 0.75, 0.98)
            
            # Simulate availability variation (equipment uptime)
            availability_shock = np.random.beta(9, 1)  # Skewed toward high availability
            
            # Simulate cycle time variation (affects throughput)
            cycle_time_multiplier = np.random.lognormal(0, 0.15)
            throughput_impact = 1 / cycle_time_multiplier
            
            # Calculate effective capacity with all variations
            effective_capacity = (
                total_capacity_baseline * 
                yield_shock * 
                availability_shock * 
                throughput_impact
            )
            
            # Calculate shortfall or surplus
            shortfall = max(0, simulated_demand - effective_capacity)
            surplus = max(0, effective_capacity - simulated_demand)
            utilization = min(simulated_demand / effective_capacity, 1.0)
            
            simulations.append({
                'demand': simulated_demand,
                'capacity': effective_capacity,
                'shortfall': shortfall,
                'surplus': surplus,
                'utilization': utilization,
                'yield': yield_shock,
                'availability': availability_shock
            })
        
        sim_df = pd.DataFrame(simulations)
        
        # Calculate risk metrics
        risk_metrics = {
            'baseline_capacity_wpw': round(total_capacity_baseline),
            'mean_demand_wpw': round(mean_weekly_demand),
            'mean_shortfall_wpw': round(sim_df['shortfall'].mean()),
            'median_shortfall_wpw': round(sim_df['shortfall'].median()),
            'p95_shortfall_wpw': round(sim_df['shortfall'].quantile(0.95)),
            'p99_shortfall_wpw': round(sim_df['shortfall'].quantile(0.99)),
            'probability_of_shortfall': round(sim_df['shortfall'].gt(0).mean(), 4),
            'service_level_probability': round(sim_df['shortfall'].eq(0).mean(), 4),
            'mean_utilization': round(sim_df['utilization'].mean(), 4),
            'p95_utilization': round(sim_df['utilization'].quantile(0.95), 4),
            'capacity_at_risk_p95': round(sim_df['capacity'].quantile(0.05)),
            'demand_at_risk_p95': round(sim_df['demand'].quantile(0.95)),
            'simulation_count': n_simulations
        }
        
        return risk_metrics, sim_df
    
    def optimize_capex_allocation(self, capex_df, budget_constraint=1000000000):
        """
        Linear programming optimization for CapEx project portfolio
        
        Maximizes NPV subject to budget and risk constraints
        
        Parameters:
        -----------
        capex_df : pd.DataFrame
            CapEx projects with NPV and investment amounts
        budget_constraint : float
            Maximum budget available
            
        Returns:
        --------
        dict : Optimization results
        """
        n_projects = len(capex_df)
        
        # Objective: Maximize NPV (negative because linprog minimizes)
        c = -capex_df['npv_usd'].values
        
        # Constraint 1: Budget constraint
        # Sum of (investment × decision_variable) <= budget
        A_budget = [capex_df['investment_usd'].values]
        b_budget = [budget_constraint]
        
        # Constraint 2: Risk-weighted constraint
        # Penalize high-risk projects
        risk_weights = capex_df['risk_level'].map({
            'Low': 1.0,
            'Medium': 1.3,
            'High': 1.6
        }).values
        
        risk_adjusted_investment = capex_df['investment_usd'].values * risk_weights
        A_risk = [risk_adjusted_investment]
        b_risk = [budget_constraint * 1.2]  # Allow 20% more in risk-adjusted terms
        
        # Combine constraints
        A_ub = np.vstack([A_budget, A_risk])
        b_ub = np.array([b_budget[0], b_risk[0]])
        
        # Bounds: Each project can be selected (1) or not (0)
        # For continuous relaxation, allow fractional investment
        bounds = [(0, 1) for _ in range(n_projects)]
        
        # Solve optimization
        result = linprog(
            c=c,
            A_ub=A_ub,
            b_ub=b_ub,
            bounds=bounds,
            method='highs'
        )
        
        if result.success:
            # Create results dataframe
            capex_results = capex_df.copy()
            capex_results['selected'] = result.x
            capex_results['allocated_investment'] = capex_results['investment_usd'] * result.x
            capex_results['allocated_npv'] = capex_results['npv_usd'] * result.x
            
            # Round to binary decisions for practical implementation
            capex_results['binary_decision'] = (result.x > 0.5).astype(int)
            
            optimization_summary = {
                'total_npv': -result.fun,
                'total_investment': capex_results['allocated_investment'].sum(),
                'budget_utilized_pct': (capex_results['allocated_investment'].sum() / budget_constraint) * 100,
                'projects_selected': capex_results['binary_decision'].sum(),
                'avg_irr': capex_results[capex_results['binary_decision'] == 1]['irr_percent'].mean(),
                'optimization_status': 'Optimal',
                'selected_projects': capex_results[capex_results['binary_decision'] == 1]['project_name'].tolist()
            }
            
            return optimization_summary, capex_results
        else:
            return {'optimization_status': 'Failed', 'message': result.message}, None
    
    def calculate_capacity_scenarios(self):
        """
        Calculate capacity under different demand scenarios
        
        Returns:
        --------
        pd.DataFrame : Capacity gaps under different scenarios
        """
        scenarios = {
            'Conservative': {'growth': 0.05, 'yield': 0.88},
            'Base Case': {'growth': 0.12, 'yield': 0.91},
            'Aggressive': {'growth': 0.22, 'yield': 0.93},
            'Stretch': {'growth': 0.35, 'yield': 0.95}
        }
        
        # Current capacity
        latest_ops = self.operations[self.operations['date'] == self.operations['date'].max()]
        current_capacity_wpw = latest_ops['output_wafers'].sum() * 7
        
        # Current demand
        latest_forecast = self.forecast[self.forecast['quarter'] == self.forecast['quarter'].max()]
        current_demand_wpw = latest_forecast['demand_wafers'].sum() / 13
        
        scenario_results = []
        
        for scenario_name, params in scenarios.items():
            # Project demand 12 months out
            future_demand = current_demand_wpw * (1 + params['growth'])
            
            # Effective capacity with yield
            effective_capacity = current_capacity_wpw * params['yield']
            
            # Calculate gap
            capacity_gap = future_demand - effective_capacity
            utilization = min(future_demand / effective_capacity, 1.0)
            
            scenario_results.append({
                'scenario': scenario_name,
                'demand_growth_rate': params['growth'],
                'assumed_yield': params['yield'],
                'projected_demand_wpw': round(future_demand),
                'effective_capacity_wpw': round(effective_capacity),
                'capacity_gap_wpw': round(capacity_gap),
                'utilization_rate': round(utilization, 3),
                'capacity_sufficient': capacity_gap <= 0,
                'additional_capacity_needed_pct': round(max(0, (capacity_gap / effective_capacity) * 100), 1)
            })
        
        return pd.DataFrame(scenario_results)

class ToolReliabilityModel:
    """
    Advanced tool reliability and MTBF analysis
    """
    
    def __init__(self, equipment_df, operations_df):
        self.equipment = equipment_df
        self.operations = operations_df
    
    def calculate_mtbf_analysis(self):
        """Calculate Mean Time Between Failures by tool type"""
        # Get downtime events
        downtime_df = self.operations[self.operations['unplanned_downtime_hours'] > 0].copy()
        
        if len(downtime_df) == 0:
            return pd.DataFrame()
        
        # Group by tool type
        reliability_metrics = []
        
        for tool_type in self.equipment['tool_type'].unique():
            tool_downtime = downtime_df[downtime_df['tool_type'] == tool_type]
            
            if len(tool_downtime) > 0:
                total_failures = len(tool_downtime)
                total_downtime = tool_downtime['unplanned_downtime_hours'].sum()
                mean_downtime = tool_downtime['unplanned_downtime_hours'].mean()
                
                # Calculate operating hours
                tool_ops = self.operations[self.operations['tool_type'] == tool_type]
                total_operating_hours = tool_ops['operating_hours'].sum()
                
                # MTBF calculation
                mtbf_actual = total_operating_hours / total_failures if total_failures > 0 else 0
                
                # Get theoretical MTBF
                mtbf_theoretical = self.equipment[
                    self.equipment['tool_type'] == tool_type
                ]['mtbf_hours'].iloc[0]
                
                reliability_metrics.append({
                    'tool_type': tool_type,
                    'total_failures': total_failures,
                    'total_downtime_hours': round(total_downtime, 2),
                    'mean_downtime_hours': round(mean_downtime, 2),
                    'mtbf_actual_hours': round(mtbf_actual, 2),
                    'mtbf_theoretical_hours': mtbf_theoretical,
                    'mtbf_performance': round((mtbf_actual / mtbf_theoretical) * 100, 1) if mtbf_theoretical > 0 else 0,
                    'availability_impact_pct': round((total_downtime / total_operating_hours) * 100, 2)
                })
        
        return pd.DataFrame(reliability_metrics).sort_values('availability_impact_pct', ascending=False)

if __name__ == "__main__":
    # Load data
    equipment = pd.read_csv("data/raw/equipment_master.csv")
    operations = pd.read_csv("data/raw/fab_operations.csv", parse_dates=['date'])
    forecast = pd.read_csv("data/raw/demand_forecast.csv", parse_dates=['quarter'])
    capex = pd.read_csv("data/raw/capex_projects.csv", parse_dates=['start_date', 'expected_completion'])
    
    # Initialize model
    model = CapacityPlanningModel(equipment, operations, forecast)
    
    # Run analyses
    print("="*80)
    print("CAPACITY PLANNING ANALYSIS")
    print("="*80)
    
    print("\n📊 Bottleneck Analysis:")
    bottleneck = model.calculate_bottleneck_analysis(target_output_wpw=18000)
    print(bottleneck.head(10).to_string(index=False))
    
    print("\n\n🎲 Monte Carlo Risk Assessment:")
    risk_metrics, _ = model.monte_carlo_capacity_risk(n_simulations=10000)
    for key, value in risk_metrics.items():
        print(f"   {key}: {value}")
    
    print("\n\n💰 CapEx Portfolio Optimization:")
    opt_summary, _ = model.optimize_capex_allocation(capex, budget_constraint=1500000000)
    for key, value in opt_summary.items():
        print(f"   {key}: {value}")
    
    print("\n\n📈 Scenario Analysis:")
    scenarios = model.calculate_capacity_scenarios()
    print(scenarios.to_string(index=False))
