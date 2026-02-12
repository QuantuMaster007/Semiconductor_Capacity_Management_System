"""
Semiconductor Capacity Management — Executive Dashboard
Corporate design language: clean, data-dense, Power BI / Tableau aesthetic
"""

import os, sys
import dash
from dash import dcc, html, Input, Output, callback
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# ── Absolute paths so it works locally AND on Railway ─────────────────────────
BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, 'models')
DATA_DIR   = os.path.join(BASE_DIR, 'data', 'raw')
sys.path.insert(0, MODELS_DIR)

from capacity_planning import CapacityPlanningModel, ToolReliabilityModel

# ── Corporate color palette ───────────────────────────────────────────────────
C = {
    'bg':           '#F4F6F9',   # page background
    'panel':        '#FFFFFF',   # card background
    'border':       '#E1E5EA',
    'blue':         '#1B6EC2',   # primary accent
    'blue_lt':      '#EBF3FB',
    'teal':         '#117A8B',
    'green':        '#198754',
    'green_lt':     '#D1F0E0',
    'amber':        '#D4860B',
    'amber_lt':     '#FEF3DC',
    'red':          '#C0392B',
    'red_lt':       '#FDECEA',
    'text':         '#1A1D23',
    'text_muted':   '#6C757D',
    'white':        '#FFFFFF',
    # chart palette
    'p1': '#1B6EC2', 'p2': '#117A8B', 'p3': '#198754',
    'p4': '#D4860B', 'p5': '#7952B3', 'p6': '#C0392B',
}

FONT = '"Segoe UI", Inter, -apple-system, sans-serif'

# ── Load data ─────────────────────────────────────────────────────────────────
print("  Loading data...")
equipment  = pd.read_csv(os.path.join(DATA_DIR, 'equipment_master.csv'))
operations = pd.read_csv(os.path.join(DATA_DIR, 'fab_operations.csv'),  parse_dates=['date'])
forecast   = pd.read_csv(os.path.join(DATA_DIR, 'demand_forecast.csv'), parse_dates=['quarter'])
capex      = pd.read_csv(os.path.join(DATA_DIR, 'capex_projects.csv'),  parse_dates=['start_date','expected_completion'])
npi        = pd.read_csv(os.path.join(DATA_DIR, 'npi_milestones.csv'),  parse_dates=['phase_start','phase_end'])

# ── Run analytics ─────────────────────────────────────────────────────────────
print("  Running analytics...")
cap_model   = CapacityPlanningModel(equipment, operations, forecast)
rel_model   = ToolReliabilityModel(equipment, operations)
bottleneck  = cap_model.calculate_bottleneck_analysis(target_output_wpw=18000)
risk_m, risk_sim = cap_model.monte_carlo_capacity_risk(n_simulations=10000)
scenarios   = cap_model.calculate_capacity_scenarios()
opt_sum, opt_det = cap_model.optimize_capex_allocation(capex, budget_constraint=1_500_000_000)
mtbf        = rel_model.calculate_mtbf_analysis()

# ── KPIs ──────────────────────────────────────────────────────────────────────
latest_day  = operations[operations['date'] == operations['date'].max()]
kpi_oee     = latest_day['oee'].mean()
kpi_output  = latest_day['output_wafers'].sum()
kpi_util    = latest_day['utilization_rate'].mean()
kpi_tools   = len(equipment[equipment['status'] == 'Active'])
kpi_capex   = capex['investment_usd'].sum() / 1e9
kpi_npv     = capex['npv_usd'].sum() / 1e9
kpi_irr     = capex['irr_percent'].mean()

# ── Dash app ──────────────────────────────────────────────────────────────────
app = dash.Dash(
    __name__,
    suppress_callback_exceptions=True,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}]
)
app.title = "Semiconductor Capacity — Executive Dashboard"
server = app.server   # ← gunicorn entry point

# ── Helper: plotly layout defaults ───────────────────────────────────────────
def chart_layout(**kw):
    base = dict(
        template='plotly_white',
        font=dict(family=FONT, size=11, color=C['text']),
        paper_bgcolor=C['panel'],
        plot_bgcolor=C['panel'],
        margin=dict(l=48, r=20, t=28, b=40),
        legend=dict(
            orientation='h', x=0, y=1.12,
            font=dict(size=10), bgcolor='rgba(0,0,0,0)'
        ),
        hoverlabel=dict(bgcolor='#1A1D23', font_color='white', font_size=11),
        xaxis=dict(showgrid=True, gridcolor='#EAECEF', zeroline=False),
        yaxis=dict(showgrid=True, gridcolor='#EAECEF', zeroline=False),
    )
    base.update(kw)
    return base

# ── Helper: card wrapper ──────────────────────────────────────────────────────
def card(title, body, col_span=1):
    return html.Div([
        html.Div(title, style={
            'fontSize': '11px', 'fontWeight': '700', 'color': C['text_muted'],
            'textTransform': 'uppercase', 'letterSpacing': '0.7px',
            'paddingBottom': '10px', 'marginBottom': '4px',
            'borderBottom': f'2px solid {C["blue"]}',
        }),
        body
    ], style={
        'background': C['panel'],
        'border': f'1px solid {C["border"]}',
        'borderRadius': '6px',
        'padding': '18px 20px',
        'boxShadow': '0 1px 4px rgba(0,0,0,0.06)',
        'gridColumn': f'span {col_span}',
    })

def kpi_card(label, value, sub, badge_color, badge_text=None):
    badge = []
    if badge_text:
        badge = [html.Span(badge_text, style={
            'fontSize': '11px', 'fontWeight': '700',
            'color': badge_color, 'marginLeft': '8px',
            'background': badge_color + '18',
            'padding': '2px 7px', 'borderRadius': '10px'
        })]
    return html.Div([
        html.Div(label, style={
            'fontSize': '10px', 'fontWeight': '700', 'color': C['text_muted'],
            'textTransform': 'uppercase', 'letterSpacing': '0.8px', 'marginBottom': '6px'
        }),
        html.Div([html.Span(value, style={
            'fontSize': '28px', 'fontWeight': '800', 'color': C['text']
        })] + badge),
        html.Div(sub, style={'fontSize': '11px', 'color': C['text_muted'], 'marginTop': '4px'})
    ], style={
        'background': C['panel'],
        'border': f'1px solid {C["border"]}',
        'borderLeft': f'4px solid {badge_color}',
        'borderRadius': '6px',
        'padding': '16px 18px',
        'boxShadow': '0 1px 4px rgba(0,0,0,0.06)',
    })

# ─────────────────────────────────────────────────────────────────────────────
# CHART BUILDERS
# ─────────────────────────────────────────────────────────────────────────────
def build_oee_trend():
    agg = operations.groupby('date').agg(
        oee=('oee','mean'),
        availability=('availability','mean'),
        performance=('performance_efficiency','mean'),
        quality=('quality_rate','mean')
    ).reset_index()
    fig = go.Figure()
    traces = [
        ('oee', 'Fleet OEE', C['p1'], None),
        ('availability', 'Availability', C['p2'], 'dot'),
        ('performance', 'Performance', C['p3'], 'dot'),
        ('quality', 'Quality', C['p4'], 'dot'),
    ]
    for col, name, color, dash in traces:
        fig.add_trace(go.Scatter(
            x=agg['date'], y=agg[col]*100,
            name=name, mode='lines',
            line=dict(color=color, width=2, dash=dash),
        ))
    fig.update_layout(**chart_layout(
        height=320,
        yaxis=dict(ticksuffix='%', range=[70, 100], showgrid=True, gridcolor='#EAECEF'),
        hovermode='x unified',
        legend=dict(orientation='h', x=0, y=1.14)
    ))
    return fig

def build_utilization_heatmap():
    pivot = operations.pivot_table(
        values='utilization_rate', index='tool_type',
        columns=pd.Grouper(key='date', freq='ME'), aggfunc='mean'
    )
    pivot.columns = [c.strftime("%b %Y") for c in pivot.columns]
    fig = go.Figure(go.Heatmap(
        z=pivot.values * 100,
        x=pivot.columns.tolist(),
        y=pivot.index.tolist(),
        colorscale=[[0,'#EBF3FB'],[0.5,'#1B6EC2'],[1,'#0A2E5A']],
        zmin=60, zmax=100,
        text=[[f"{v:.0f}%" for v in row] for row in pivot.values*100],
        texttemplate='%{text}',
        textfont=dict(size=9),
        colorbar=dict(title='Util %', ticksuffix='%', thickness=12)
    ))
    fig.update_layout(**chart_layout(
        height=300,
        margin=dict(l=140, r=40, t=28, b=60),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=False),
    ))
    return fig

def build_bottleneck():
    df = bottleneck.head(10).sort_values('utilization_at_target')
    colors = [
        C['red'] if v > 0.90 else C['amber'] if v > 0.80 else C['green']
        for v in df['utilization_at_target']
    ]
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df['utilization_at_target']*100, y=df['tool_type'],
        orientation='h',
        marker=dict(color=colors, line=dict(width=0)),
        text=[f"{v:.1f}%" for v in df['utilization_at_target']*100],
        textposition='outside', textfont=dict(size=10)
    ))
    fig.add_vline(x=90, line_dash='dash', line_color=C['red'],
                  annotation_text='⚠ Bottleneck 90%',
                  annotation_font=dict(size=10, color=C['red']),
                  annotation_position='top left')
    fig.update_layout(**chart_layout(
        height=320, margin=dict(l=140, r=60, t=28, b=40),
        xaxis=dict(ticksuffix='%', range=[0, 110], showgrid=True, gridcolor='#EAECEF'),
        yaxis=dict(showgrid=False),
        showlegend=False
    ))
    return fig

def build_scenario():
    df = scenarios
    fig = go.Figure()
    fig.add_trace(go.Bar(
        name='Projected Demand', x=df['scenario'], y=df['projected_demand_wpw'],
        marker=dict(color=C['p1']), width=0.35,
        offset=-0.18, text=df['projected_demand_wpw'].apply(lambda v: f"{v:,.0f}"),
        textposition='outside', textfont=dict(size=9)
    ))
    fig.add_trace(go.Bar(
        name='Effective Capacity', x=df['scenario'], y=df['effective_capacity_wpw'],
        marker=dict(color=C['p2']), width=0.35,
        offset=0.18, text=df['effective_capacity_wpw'].apply(lambda v: f"{v:,.0f}"),
        textposition='outside', textfont=dict(size=9)
    ))
    fig.update_layout(**chart_layout(
        height=320, barmode='overlay',
        yaxis=dict(title='WPW', showgrid=True, gridcolor='#EAECEF'),
    ))
    return fig

def build_demand_forecast():
    agg = forecast.groupby('quarter')['demand_wafers'].sum().reset_index()
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=agg['quarter'], y=agg['demand_wafers'],
        mode='lines+markers',
        line=dict(color=C['p1'], width=2.5),
        marker=dict(size=6, color=C['p1']),
        fill='tozeroy', fillcolor='rgba(27,110,194,0.08)',
        name='Total Demand'
    ))
    fig.update_layout(**chart_layout(
        height=260,
        yaxis=dict(title='Wafers / Quarter', showgrid=True, gridcolor='#EAECEF'),
        showlegend=False
    ))
    return fig

def build_output_by_category():
    df = latest_day.groupby('tool_category')['output_wafers'].sum().sort_values(ascending=False).reset_index()
    fig = go.Figure(go.Bar(
        x=df['tool_category'], y=df['output_wafers'],
        marker=dict(color=[C['p1'],C['p2'],C['p3'],C['p4'],C['p5']][:len(df)]),
        text=df['output_wafers'].apply(lambda v: f"{v:,.0f}"),
        textposition='outside', textfont=dict(size=10)
    ))
    fig.update_layout(**chart_layout(
        height=260, showlegend=False,
        yaxis=dict(title='Wafers / Day', showgrid=True, gridcolor='#EAECEF'),
    ))
    return fig

def build_capex_timeline():
    active = capex[capex['status'].isin(['In Progress','Planning'])].copy()
    priority_color = {'Critical': C['p1'], 'High': C['p2'], 'Medium': C['p4'], 'Low': C['p3']}
    fig = go.Figure()
    for _, row in active.iterrows():
        col = priority_color.get(row.get('strategic_priority','Medium'), C['p1'])
        fig.add_trace(go.Scatter(
            x=[row['start_date'], row['expected_completion']],
            y=[row['project_name'], row['project_name']],
            mode='lines+markers',
            line=dict(color=col, width=14),
            marker=dict(size=8, color=col, symbol='line-ew'),
            showlegend=False,
            hovertemplate=(
                f"<b>{row['project_name']}</b><br>"
                f"Priority: {row.get('strategic_priority','—')}<br>"
                f"Progress: {row['progress_percent']}%<br>"
                f"Investment: ${row['investment_usd']/1e6:.0f}M<extra></extra>"
            )
        ))
    fig.update_layout(**chart_layout(
        height=340, margin=dict(l=200, r=20, t=28, b=40),
        xaxis=dict(showgrid=True, gridcolor='#EAECEF'),
        yaxis=dict(showgrid=False),
        showlegend=False
    ))
    return fig

def build_npv_scatter():
    fig = go.Figure()
    size_ref = max(capex['irr_percent']) / 40
    fig.add_trace(go.Scatter(
        x=capex['investment_usd']/1e6, y=capex['npv_usd']/1e6,
        mode='markers+text',
        marker=dict(
            size=capex['irr_percent'], sizemode='diameter', sizeref=size_ref,
            color=capex['irr_percent'],
            colorscale=[[0, C['p3']],[0.5, C['p1']],[1, C['p5']]],
            showscale=True, colorbar=dict(title='IRR %', thickness=12),
            line=dict(width=1, color='white')
        ),
        text=capex['project_id'],
        textposition='top center', textfont=dict(size=8),
        hovertemplate=(
            "<b>%{text}</b><br>"
            "Investment: $%{x:.0f}M<br>"
            "NPV: $%{y:.0f}M<extra></extra>"
        )
    ))
    fig.update_layout(**chart_layout(
        height=340,
        xaxis=dict(title='Investment ($M)', showgrid=True, gridcolor='#EAECEF'),
        yaxis=dict(title='NPV ($M)',         showgrid=True, gridcolor='#EAECEF'),
        showlegend=False
    ))
    return fig

def build_irr():
    df = capex.sort_values('irr_percent', ascending=False)
    colors = [C['green'] if v >= 15 else C['amber'] for v in df['irr_percent']]
    fig = go.Figure(go.Bar(
        x=df['project_name'], y=df['irr_percent'],
        marker=dict(color=colors, line=dict(width=0)),
        text=[f"{v:.1f}%" for v in df['irr_percent']],
        textposition='outside', textfont=dict(size=10)
    ))
    fig.add_hline(y=15, line_dash='dash', line_color=C['red'],
                  annotation_text='Hurdle Rate 15%',
                  annotation_font=dict(size=10, color=C['red']),
                  annotation_position='top right')
    fig.update_layout(**chart_layout(
        height=340,
        xaxis=dict(tickangle=-30, showgrid=False),
        yaxis=dict(ticksuffix='%', showgrid=True, gridcolor='#EAECEF'),
        showlegend=False
    ))
    return fig

def build_monte_carlo():
    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=risk_sim['shortfall'], nbinsx=60,
        marker=dict(color=C['p1'], opacity=0.85, line=dict(color='white', width=0.5)),
        name='Simulations'
    ))
    p95 = risk_m['p95_shortfall_wpw']
    fig.add_vline(x=p95, line_dash='dash', line_color=C['red'],
                  annotation_text=f"P95: {p95:,.0f} WPW",
                  annotation_font=dict(size=10, color=C['red']))
    fig.update_layout(**chart_layout(
        height=320,
        xaxis=dict(title='Capacity Shortfall (WPW)', showgrid=True, gridcolor='#EAECEF'),
        yaxis=dict(title='Frequency',                showgrid=True, gridcolor='#EAECEF'),
        showlegend=False
    ))
    return fig

def build_risk_scenario():
    df = scenarios
    colors = [
        C['green'] if v == 0 else C['amber'] if v < 10 else C['red']
        for v in df['additional_capacity_needed_pct']
    ]
    fig = go.Figure(go.Bar(
        x=df['scenario'], y=df['additional_capacity_needed_pct'],
        marker=dict(color=colors, line=dict(width=0)),
        text=[f"{v:.1f}%" for v in df['additional_capacity_needed_pct']],
        textposition='outside', textfont=dict(size=11)
    ))
    fig.update_layout(**chart_layout(
        height=280, showlegend=False,
        yaxis=dict(title='Additional Capacity Needed (%)', showgrid=True, gridcolor='#EAECEF'),
    ))
    return fig

def build_mtbf():
    if len(mtbf) == 0:
        return go.Figure()
    df = mtbf.sort_values('mtbf_performance', ascending=True)
    fig = go.Figure(go.Bar(
        x=df['mtbf_performance'], y=df['tool_type'],
        orientation='h',
        marker=dict(
            color=[C['green'] if v >= 90 else C['amber'] if v >= 70 else C['red']
                   for v in df['mtbf_performance']],
            line=dict(width=0)
        ),
        text=[f"{v:.0f}%" for v in df['mtbf_performance']],
        textposition='outside', textfont=dict(size=10)
    ))
    fig.add_vline(x=100, line_dash='dash', line_color=C['text_muted'], line_width=1)
    fig.update_layout(**chart_layout(
        height=300, margin=dict(l=140, r=60, t=28, b=40),
        xaxis=dict(ticksuffix='%', showgrid=True, gridcolor='#EAECEF'),
        yaxis=dict(showgrid=False),
        showlegend=False
    ))
    return fig

def build_demand_by_product():
    agg = forecast.groupby('product')['demand_wafers'].sum().sort_values(ascending=False).reset_index()
    fig = go.Figure(go.Bar(
        x=agg['product'], y=agg['demand_wafers'],
        marker=dict(color=[C['p1'],C['p2'],C['p3'],C['p4'],C['p5'],C['p6']][:len(agg)]),
        text=agg['demand_wafers'].apply(lambda v: f"{v/1e3:.1f}K"),
        textposition='outside', textfont=dict(size=10)
    ))
    fig.update_layout(**chart_layout(
        height=280, showlegend=False,
        xaxis=dict(tickangle=-20, showgrid=False),
        yaxis=dict(title='Total Wafers', showgrid=True, gridcolor='#EAECEF'),
    ))
    return fig

# ─────────────────────────────────────────────────────────────────────────────
# RISK METRICS TABLE
# ─────────────────────────────────────────────────────────────────────────────
def risk_metrics_table():
    rows = [
        ("Baseline Capacity",     f"{risk_m['baseline_capacity_wpw']:,} WPW",   C['blue']),
        ("Mean Weekly Demand",    f"{risk_m['mean_demand_wpw']:,} WPW",         C['text']),
        ("Mean Shortfall",        f"{risk_m['mean_shortfall_wpw']:,} WPW",      C['text']),
        ("P95 Shortfall",         f"{risk_m['p95_shortfall_wpw']:,} WPW",       C['amber']),
        ("P99 Shortfall",         f"{risk_m['p99_shortfall_wpw']:,} WPW",       C['red']),
        ("Service Level",         f"{risk_m['service_level_probability']:.1%}", C['green']),
        ("Shortfall Probability", f"{risk_m['probability_of_shortfall']:.1%}",  C['red']),
        ("Mean Utilization",      f"{risk_m['mean_utilization']:.1%}",          C['blue']),
        ("P95 Utilization",       f"{risk_m['p95_utilization']:.1%}",           C['amber']),
        ("Simulations Run",       f"{risk_m['simulation_count']:,}",            C['text']),
    ]
    return html.Table([
        html.Thead(html.Tr([
            html.Th("Metric",  style={'textAlign':'left',  'padding':'9px 12px',
                                     'fontSize':'11px','fontWeight':'700','color':C['text_muted'],
                                     'textTransform':'uppercase','borderBottom':f'2px solid {C["border"]}'}),
            html.Th("Value",   style={'textAlign':'right', 'padding':'9px 12px',
                                     'fontSize':'11px','fontWeight':'700','color':C['text_muted'],
                                     'textTransform':'uppercase','borderBottom':f'2px solid {C["border"]}'}),
        ])),
        html.Tbody([
            html.Tr([
                html.Td(label, style={'padding':'8px 12px','fontSize':'12px','color':C['text'],
                                      'borderBottom':f'1px solid {C["border"]}'}),
                html.Td(val,   style={'padding':'8px 12px','fontSize':'12px','fontWeight':'700',
                                      'color':color,'textAlign':'right',
                                      'borderBottom':f'1px solid {C["border"]}'}),
            ]) for label, val, color in rows
        ])
    ], style={
        'width':'100%','borderCollapse':'collapse',
        'fontFamily': FONT
    })

# ─────────────────────────────────────────────────────────────────────────────
# LAYOUT
# ─────────────────────────────────────────────────────────────────────────────
NAV_TAB = dict(
    padding='11px 22px',
    fontWeight='600',
    fontSize='12px',
    letterSpacing='0.3px',
    border='none',
    borderBottom='3px solid transparent',
    background='transparent',
    color=C['text_muted'],
    cursor='pointer',
)
NAV_TAB_ACTIVE = {**NAV_TAB,
    'borderBottom': f'3px solid {C["blue"]}',
    'color': C['blue'],
}

app.layout = html.Div([

    # ── Top bar ───────────────────────────────────────────────────────────────
    html.Div([
        html.Div([
            html.Div([
                html.Div("▣", style={'fontSize':'22px','color':C['blue'],'marginRight':'10px'}),
                html.Div([
                    html.H1("Semiconductor Capacity Management",
                            style={'margin':0,'fontSize':'18px','fontWeight':'700','color':C['text']}),
                    html.P("Executive Analytics Dashboard · Fab Operations & Infrastructure Readiness",
                           style={'margin':0,'fontSize':'11px','color':C['text_muted'],'marginTop':'2px'})
                ])
            ], style={'display':'flex','alignItems':'center'}),
            html.Div([
                html.Span("● LIVE", style={
                    'fontSize':'11px','fontWeight':'700','color':C['green'],
                    'background':C['green_lt'],'padding':'4px 12px',
                    'borderRadius':'20px','letterSpacing':'0.5px'
                }),
                html.Span("Data: Jun 2024", style={
                    'fontSize':'11px','color':C['text_muted'],'marginLeft':'16px'
                })
            ], style={'display':'flex','alignItems':'center'})
        ], style={
            'display':'flex','justifyContent':'space-between','alignItems':'center',
            'maxWidth':'1440px','margin':'0 auto','padding':'0 32px'
        })
    ], style={
        'background':C['panel'],'borderBottom':f'1px solid {C["border"]}',
        'height':'56px','display':'flex','alignItems':'center',
        'boxShadow':'0 1px 3px rgba(0,0,0,0.06)'
    }),

    # ── KPI strip ─────────────────────────────────────────────────────────────
    html.Div([
        html.Div([
            kpi_card("Fleet OEE",      f"{kpi_oee:.1%}",    "Overall Equipment Effectiveness", C['blue'],   "▲ 2.3%"),
            kpi_card("Daily Output",   f"{kpi_output:,.0f}","Wafers Per Day",                  C['green'],  "▲ 5.7%"),
            kpi_card("Utilization",    f"{kpi_util:.1%}",   "Average Tool Utilization",        C['teal'],   "▼ 1.2%"),
            kpi_card("Active Tools",   str(kpi_tools),      "Equipment Assets",                C['p5'],     None),
            kpi_card("CapEx Portfolio",f"${kpi_capex:.2f}B","Total Investment",                C['amber'],  None),
            kpi_card("Portfolio NPV",  f"${kpi_npv:.2f}B",  f"Avg IRR {kpi_irr:.1f}%",        C['p6'],     "▲ 8.5%"),
        ], style={
            'display':'grid',
            'gridTemplateColumns':'repeat(6,1fr)',
            'gap':'14px',
            'maxWidth':'1440px','margin':'0 auto','padding':'0 32px'
        })
    ], style={'padding':'18px 0','background':C['bg']}),

    # ── Nav tabs ──────────────────────────────────────────────────────────────
    html.Div([
        html.Div([
            dcc.Tabs(id='tabs', value='exec', children=[
                dcc.Tab(label='Executive Summary', value='exec',
                        style=NAV_TAB, selected_style=NAV_TAB_ACTIVE),
                dcc.Tab(label='Operations',        value='ops',
                        style=NAV_TAB, selected_style=NAV_TAB_ACTIVE),
                dcc.Tab(label='Capacity Planning', value='cap',
                        style=NAV_TAB, selected_style=NAV_TAB_ACTIVE),
                dcc.Tab(label='CapEx Portfolio',   value='capex',
                        style=NAV_TAB, selected_style=NAV_TAB_ACTIVE),
                dcc.Tab(label='Risk & Analytics',  value='risk',
                        style=NAV_TAB, selected_style=NAV_TAB_ACTIVE),
            ], style={'borderBottom':'none'})
        ], style={'maxWidth':'1440px','margin':'0 auto','padding':'0 24px'})
    ], style={
        'background':C['panel'],
        'borderBottom':f'1px solid {C["border"]}',
        'borderTop':f'1px solid {C["border"]}',
    }),

    # ── Page content ──────────────────────────────────────────────────────────
    html.Div(id='page-content', style={
        'maxWidth':'1440px','margin':'0 auto',
        'padding':'24px 32px','minHeight':'600px'
    }),

    # ── Footer ────────────────────────────────────────────────────────────────
    html.Div(
        "Semiconductor Capacity Management System  ·  Advanced Analytics Platform  ·  All data synthetic for demonstration",
        style={
            'textAlign':'center','padding':'16px',
            'fontSize':'10px','color':C['text_muted'],
            'borderTop':f'1px solid {C["border"]}',
            'background':C['panel'],'marginTop':'32px'
        }
    ),

], style={'background':C['bg'],'minHeight':'100vh','fontFamily':FONT})

# ─────────────────────────────────────────────────────────────────────────────
# TAB RENDERERS
# ─────────────────────────────────────────────────────────────────────────────
def _graph(fig, h=None):
    if h:
        fig.update_layout(height=h)
    return dcc.Graph(figure=fig, config={'displayModeBar': True,
                                          'modeBarButtonsToRemove':['lasso2d','select2d'],
                                          'displaylogo': False})

def render_exec():
    return html.Div([
        html.Div([
            card("Fleet OEE Trend — 18-Month Performance",
                 _graph(build_oee_trend()), col_span=2),
            card("Quarterly Demand Forecast",
                 _graph(build_demand_forecast())),
        ], style={'display':'grid','gridTemplateColumns':'2fr 1fr','gap':'16px','marginBottom':'16px'}),

        html.Div([
            card("Bottleneck Analysis — Theory of Constraints",
                 _graph(build_bottleneck())),
            card("Scenario Analysis — Demand vs Capacity",
                 _graph(build_scenario())),
            card("Output by Tool Category",
                 _graph(build_output_by_category())),
        ], style={'display':'grid','gridTemplateColumns':'repeat(3,1fr)','gap':'16px'}),
    ])

def render_ops():
    return html.Div([
        card("OEE Components — Daily Fleet Average (18 Months)",
             _graph(build_oee_trend(), h=340)),
        html.Div([
            card("Utilization Heatmap — Tool Type × Month",
                 _graph(build_utilization_heatmap())),
        ], style={'marginTop':'16px'}),
        html.Div([
            card("Daily Output by Category", _graph(build_output_by_category())),
            card("Demand by Product SKU",    _graph(build_demand_by_product())),
        ], style={'display':'grid','gridTemplateColumns':'1fr 1fr','gap':'16px','marginTop':'16px'}),
    ])

def render_cap():
    return html.Div([
        html.Div([
            card("Bottleneck Analysis — Utilization at 18K WPW Target",
                 _graph(build_bottleneck()), col_span=2),
            card("Capacity Scenarios",
                 _graph(build_scenario())),
        ], style={'display':'grid','gridTemplateColumns':'2fr 1fr','gap':'16px','marginBottom':'16px'}),
        html.Div([
            card("Quarterly Demand Forecast by Total Volume",
                 _graph(build_demand_forecast())),
            card("Demand Distribution by Product",
                 _graph(build_demand_by_product())),
        ], style={'display':'grid','gridTemplateColumns':'1fr 1fr','gap':'16px'}),
    ])

def render_capex():
    return html.Div([
        card("Project Timeline — Active & Planned CapEx",
             _graph(build_capex_timeline())),
        html.Div([
            card("NPV vs Investment (Bubble = IRR)", _graph(build_npv_scatter())),
            card("Project IRR vs Hurdle Rate",       _graph(build_irr())),
        ], style={'display':'grid','gridTemplateColumns':'1fr 1fr','gap':'16px','marginTop':'16px'}),
    ])

def render_risk():
    return html.Div([
        html.Div([
            card("Monte Carlo Simulation — 10,000 Iterations",
                 _graph(build_monte_carlo()), col_span=2),
            card("Risk Metrics Summary", risk_metrics_table()),
        ], style={'display':'grid','gridTemplateColumns':'2fr 1fr','gap':'16px','marginBottom':'16px'}),
        html.Div([
            card("Capacity Gap by Scenario",        _graph(build_risk_scenario())),
            card("MTBF Performance vs Theoretical", _graph(build_mtbf())),
        ], style={'display':'grid','gridTemplateColumns':'1fr 1fr','gap':'16px'}),
    ])

# ─────────────────────────────────────────────────────────────────────────────
# CALLBACK
# ─────────────────────────────────────────────────────────────────────────────
@callback(Output('page-content','children'), Input('tabs','value'))
def render_tab(tab):
    if tab == 'exec':  return render_exec()
    if tab == 'ops':   return render_ops()
    if tab == 'cap':   return render_cap()
    if tab == 'capex': return render_capex()
    if tab == 'risk':  return render_risk()

# ─────────────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8050))
    print(f"  Dashboard -> http://localhost:{port}")
    app.run(debug=False, host='0.0.0.0', port=port)
