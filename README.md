# 🔷 Semiconductor Capacity Management System

**Advanced Analytics Platform for Fab Operations & Infrastructure Readiness**

A production-ready capacity planning and optimization system specifically designed for semiconductor manufacturing, featuring real-time operations monitoring, Monte Carlo risk simulation, linear programming optimization, and interactive dashboards.

---

## 🎯 Overview

This system provides end-to-end capacity management capabilities for semiconductor fabrication facilities, with a focus on:

- **Real-time Operations Monitoring**: OEE analysis, utilization tracking, and bottleneck identification
- **Capacity Planning & Optimization**: Linear programming for CapEx allocation, scenario analysis
- **Risk Assessment**: 10,000-iteration Monte Carlo simulations for capacity risk
- **NPI Readiness Tracking**: Phase-gate management (EVT/DVT/PVT/MP) and yield learning curves
- **Interactive Dashboards**: Professional-grade visualizations with 5 analytical views
- **Predictive Analytics**: Demand forecasting, MTBF analysis, and reliability metrics

---

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone <[your-repo-url](https://github.com/QuantuMaster007/Semiconductor_Capacity_Management_System.git)>
cd semiconductor-capacity-system

# Install dependencies
pip install -r requirements.txt
```

### Run Complete System

```bash
# Option 1: Interactive menu
python main.py --menu

# Option 2: Full pipeline (generate data, run analytics, launch dashboard)
python main.py --full

# Option 3: Individual components
python main.py --generate    # Generate synthetic data only
python main.py --analyze     # Run analytics only
python main.py --dashboard   # Launch dashboard only
python main.py --report      # Generate summary report only
```

### Access Dashboard

Once launched, open your browser to:
```
http://localhost:8050
```

---

## 📊 System Architecture

```
semiconductor-capacity-system/
├── data/
│   ├── raw/                      # Generated synthetic fab data
│   │   ├── equipment_master.csv  # 161 tool specifications
│   │   ├── fab_operations.csv    # 235K+ daily operation records
│   │   ├── demand_forecast.csv   # Multi-year demand projections
│   │   ├── capex_projects.csv    # $2.5B+ investment portfolio
│   │   └── npi_milestones.csv    # 6 NPI programs across 4 phases
│   └── processed/                # Analytics outputs
│
├── models/
│   └── capacity_planning.py      # Advanced analytical models
│       ├── CapacityPlanningModel
│       │   ├── Bottleneck Analysis (Theory of Constraints)
│       │   ├── Monte Carlo Simulation (10K iterations)
│       │   ├── Linear Programming Optimization
│       │   └── Scenario Analysis
│       └── ToolReliabilityModel
│           └── MTBF & Availability Analysis
│
├── dashboards/
│   └── interactive_dashboard.py  # Professional Dash app
│       ├── Operations Dashboard
│       ├── Capacity Planning
│       ├── CapEx Portfolio
│       ├── NPI Readiness
│       └── Risk Analytics
│
├── data_generator.py             # Synthetic data generator
├── main.py                       # Main orchestrator
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

---

## 🎨 Dashboard Features

### 1. **Operations Dashboard**
- Real-time OEE trend analysis with component breakdown (Availability, Performance, Quality)
- Tool utilization heatmap by cleanroom bay and category
- Daily output analysis by tool type
- Equipment status monitoring

### 2. **Capacity Planning**
- Bottleneck analysis using Theory of Constraints
- Utilization forecasting at target output levels
- Multi-scenario capacity planning (Conservative, Base Case, Aggressive, Stretch)
- Quarterly demand trend visualization

### 3. **CapEx Portfolio**
- Project timeline with Gantt-style visualization
- Risk-Return scatter matrix (NPV vs Investment)
- IRR analysis with hurdle rate benchmarking
- Portfolio optimization results ($1.5B+ optimized allocation)

### 4. **NPI Readiness**
- Program progress tracking across EVT/DVT/PVT/MP phases
- Yield learning curves by program
- Infrastructure gate completion matrix
- Phase-specific KPI tracking

### 5. **Risk Analytics**
- Monte Carlo capacity risk distribution (10,000 simulations)
- Service level probability metrics
- Tool reliability and MTBF analysis
- Scenario-based capacity gap assessment

---

## 📈 Key Analytical Models

### Bottleneck Analysis
Uses **Theory of Constraints** to identify capacity-limiting tool types:
- Calculates utilization at target output (18K wafers/week)
- Accounts for process step complexity by tool type
- Identifies constraint severity and capacity gaps

### Monte Carlo Simulation
10,000-iteration simulation varying:
- **Demand** (±15% volatility)
- **Yield** (75-98% range, mean 92%)
- **Availability** (Beta distribution, skewed high)
- **Cycle Time** (log-normal distribution)

Output metrics:
- Mean/Median/P95/P99 shortfall
- Service level probability
- Capacity at risk (P95)

### Linear Programming Optimization
Maximizes portfolio NPV subject to:
- Budget constraints ($1.5B default)
- Risk-weighted investment limits
- Binary/continuous project selection

Uses `scipy.optimize.linprog` with HiGHS solver.

### Scenario Analysis
Four scenarios (Conservative, Base Case, Aggressive, Stretch) with varying:
- Demand growth rates (5% to 35%)
- Yield assumptions (88% to 95%)
- Capacity gap calculations

---

## 🔧 Data Specifications

### Equipment Master (161 Tools)
- **Tool Types**: EUV/DUV Lithography, Etch, Deposition (CVD/PVD), CMP, Metrology (SEM/Optical), Ion Implant, Wet Process
- **Key Fields**: Cost ($1.2M to $180M), Throughput, MTBF, Install Date, Status

### Fab Operations (235K+ Records)
- **Metrics**: OEE, Utilization, Availability, Performance, Quality, WIP, Cycle Time, Downtime
- **Time Span**: 18 months (Jan 2023 - Jun 2024)
- **Granularity**: Daily, per tool, with realistic variability

### Demand Forecast
- **Products**: 6 SKUs (Mobile SoC 3nm/5nm, HPC CPU/GPU 5nm, Automotive 5nm, IoT 7nm)
- **Horizon**: 5 years quarterly projections
- **Revenue**: $4.2K to $18K per wafer depending on product

### CapEx Portfolio ($2.5B+)
- **Projects**: 8 major investments (EUV expansions, new capabilities, upgrades)
- **Metrics**: NPV, IRR, Payback Period, Risk Level, Strategic Priority
- **Timeline**: 2023-2026

### NPI Milestones
- **Programs**: 6 new product introductions
- **Phases**: EVT → DVT → PVT → MP (3-4 months each)
- **Tracking**: Yield curves, gate completion, infrastructure readiness

---

## 💡 Use Cases

### For Capacity Managers:
- Identify capacity constraints before they impact delivery
- Model demand scenarios and capacity responses
- Optimize CapEx allocation across competing projects
- Track tool reliability and predict maintenance needs

### For Program Managers:
- Monitor NPI readiness across multiple programs
- Track yield learning curves and phase-gate progress
- Align infrastructure readiness with product ramps
- Assess critical path risks

### For Executives:
- Portfolio-level financial metrics (NPV, IRR, Payback)
- Risk-adjusted investment decisions
- Strategic capacity roadmap visualization
- ROI analysis and budget utilization tracking

---

## 🛠️ Technologies Used

| Category | Technology |
|----------|------------|
| **Language** | Python 3.9+ |
| **Data Processing** | pandas, numpy |
| **Optimization** | scipy (Linear Programming) |
| **Visualization** | Plotly, Dash |
| **Statistical Analysis** | scipy.stats (Monte Carlo) |
| **Machine Learning** | scikit-learn |

---

## 📊 Sample Output

### KPI Summary
```
Fleet OEE:                  84.3% (↑ 2.3%)
Daily Output:               127,548 wafers
Average Utilization:        85.6%
Active Tools:               161 assets
Portfolio NPV:              $640M on $2.5B investment
```

### Top Bottlenecks
```
1. Metrology_SEM:           94.2% utilization → CRITICAL
2. Lithography_EUV:         91.8% utilization → CRITICAL
3. Ion_Implant:             88.5% utilization → Warning
```

### Monte Carlo Risk
```
Service Level Probability:  87.3%
Mean Shortfall:             1,247 WPW
P95 Shortfall:              4,892 WPW
Capacity at Risk (P95):     124,156 WPW
```

---

## 🚢 Deployment Options

### Local Development
```bash
python main.py --full
```

### Docker
```bash
# Build image
docker build -t capacity-management .

# Run container
docker run -p 8050:8050 capacity-management
```

### Cloud Deployment
Compatible with:
- Heroku
- AWS Elastic Beanstalk
- Google App Engine
- Azure App Service

---

## 📝 Configuration

Edit `config.yaml` (optional) to customize:
- Target utilization rates
- Bottleneck thresholds
- CapEx budget constraints
- Simulation parameters
- Risk weights

---

## 🤝 Contributing

This is a demonstration project for portfolio/interview purposes. If you'd like to extend it:

1. Fork the repository
2. Create a feature branch
3. Add enhancements (new models, visualizations, data sources)
4. Submit a pull request

---

## 📧 Contact

Let's connect! Whether you have a question or just want to say hi, feel free to reach out.

| Platform | Link |
| :--- | :--- |
| **👤 Name** | Sourabh Tarodekar |
| **✉️ Email** | [sourabh232@gmail.com](mailto:sourabh232@gmail.com) |
| **💼 LinkedIn** | [linkedin.com/in/sourabh232](https://www.linkedin.com/in/sourabh232) |
| **🚀 Portfolio** | [QuantuMaster007 Portfolio](https://github.com/QuantuMaster007/sourabh232.git) |

---

## 📄 License

MIT License - See LICENSE file for details

---

## 🎓 Educational Note

This system uses **synthetic data** generated programmatically to demonstrate capacity management concepts for semiconductor manufacturing. The models, algorithms, and visualizations are production-grade, but data is simulated for demonstration purposes.

---

## 🔗 References

- Theory of Constraints (Goldratt)
- Semiconductor Manufacturing Handbook (Quirk & Serda)
- Factory Physics (Hopp & Spearman)
- Applied Optimization with MATLAB (Venkataraman)

---

**Built with ❤️ for semiconductor manufacturing excellence**
