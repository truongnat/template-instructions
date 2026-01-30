"""
Streamlit Dashboard for Agentic SDLC.
Provides a central UI for monitoring and managing AI agents.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import os
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
root_dir = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(root_dir))

# Import brain modules
try:
    from agentic_sdlc.intelligence.monitoring.hitl.hitl_manager import HITLManager, ApprovalGate
    from agentic_sdlc.intelligence.collaborating.state.state_manager import StateManager
    from agentic_sdlc.intelligence.learning.cost.cost_tracker import CostTracker
    from agentic_sdlc.intelligence.monitoring.evaluation.benchmark import BenchmarkRunner
    from agentic_sdlc.intelligence.learning.self_healing.self_healer import FeedbackLoop
    from agentic_sdlc.intelligence.monitoring.monitor.health_monitor import HealthMonitor
except ImportError as e:
    st.error(f"Failed to import brain modules: {e}")

# Set Page Config
st.set_page_config(
    page_title="Agentic SDLC | Brain Dashboard",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Liquid Glass Aesthetic
st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: #f8fafc;
    }
    .stMetric {
        background: rgba(255, 255, 255, 0.05);
        padding: 15px;
        border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .stSidebar {
        background-color: #0f172a !important;
    }
    h1, h2, h3 {
        color: #38bdf8 !important;
    }
</style>
""", unsafe_allow_html=True)

# sidebar
with st.sidebar:
    st.title("🧠 Brain Control")
    st.markdown("---")
    menu = st.radio(
        "Navigation",
        ["Overview", "Approvals (HITL)", "Cost & Tokens", "Workflow State", "Benchmarks", "Self-Healing"]
    )
    
    st.markdown("---")
    st.info("System Version: 1.1 (Reinforced)")
    if st.button("Refresh Data"):
        st.rerun()

# Initialize Managers
hitl = HITLManager()
state_mgr = StateManager()
cost_tracker = CostTracker()
bench_runner = BenchmarkRunner()
healing = FeedbackLoop()

# --- Page: Overview ---
if menu == "Overview":
    st.title("🚀 System Overview")
    
    # Summary Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    cost_data = cost_tracker.get_report("daily")
    col1.metric("Daily Spend", f"${cost_data.total_cost:.4f}", "-$0.02")
    
    pending_approvals = len(hitl.list_pending())
    col2.metric("Pending Approvals", pending_approvals, "+1")
    
    active_sessions = len(state_mgr.list_sessions(status="active"))
    col3.metric("Active Sessions", active_sessions)
    
    bench_stats = bench_runner.get_performance_stats()
    avg_score = bench_stats.get("avg_score", 0) * 100
    col4.metric("Agent Score", f"{avg_score:.1f}%", "+2.5%")
    
    st.markdown("---")
    
    # Cost Trend (Mock Chart)
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        st.subheader("📊 Token Usage Distribution")
        if cost_data.by_model:
            df_model = pd.DataFrame([
                {"Model": k, "Tokens": v["tokens"]} for k, v in cost_data.by_model.items()
            ])
            fig = px.pie(df_model, values='Tokens', names='Model', hole=.3, 
                         color_discrete_sequence=px.colors.sequential.RdBu)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No token data collected today yet.")
            
    with col_right:
        st.subheader("🔔 Budget Alerts")
        if hitl.storage_dir.parent.joinpath(".cost/budget_alerts.json").exists():
            alerts = json.loads(hitl.storage_dir.parent.joinpath(".cost/budget_alerts.json").read_text())
            for alert in alerts[-5:]:
                st.warning(f"**{alert['date']}**: Reached {alert['percentage']:.1f}% of budget (${alert['current_cost']:.2f})")
        else:
            st.success("No budget alerts triggered.")

# --- Page: Approvals (HITL) ---
elif menu == "Approvals (HITL)":
    st.title("🛑 Approval Gates (HITL)")
    
    pending = hitl.list_pending()
    
    if not pending:
        st.success("🎉 All clear! No pending approvals.")
    else:
        for req in pending:
            req_id = req.id
            with st.expander(f"REQ-{req_id}: {req.gate.upper()} - {req.status.upper()}", expanded=True):
                st.write(f"**Session:** {req.session_id}")
                st.write(f"**Requested:** {req.created_at}")
                st.json(req.context)
                
                c1, c2, c3 = st.columns([1, 1, 2])
                comment = st.text_input("Comment", key=f"cmt_{req_id}")
                if c1.button("✅ Approve", key=f"app_{req_id}"):
                    hitl.approve(req_id, comment)
                    st.success(f"Approved REQ-{req_id}")
                    st.rerun()
                if c2.button("❌ Reject", key=f"rej_{req_id}"):
                    hitl.reject(req_id, comment)
                    st.error(f"Rejected REQ-{req_id}")
                    st.rerun()

# --- Page: Cost & Tokens ---
elif menu == "Cost & Tokens":
    st.title("💰 Cost & Token Dashboard")
    
    report_type = st.selectbox("Period", ["daily", "weekly", "monthly"])
    report = cost_tracker.get_report(report_type)
    
    st.subheader(f"Summary ({report_type.capitalize()})")
    sc1, sc2, sc3 = st.columns(3)
    sc1.metric("Total Cost", f"${report.total_cost:.4f}")
    sc2.metric("Input Tokens", f"{report.total_input_tokens:,}")
    sc3.metric("Output Tokens", f"{report.total_output_tokens:,}")
    
    # Model Costs
    if report.by_model:
        df_model = pd.DataFrame([
            {"Model": k, "Cost ($)": v["cost"], "Tokens": v["tokens"]} 
            for k, v in report.by_model.items()
        ])
        st.subheader("Costs by Model")
        fig_cost = px.bar(df_model, x='Model', y='Cost ($)', color='Model', 
                         title="Cost Distribution per Model")
        st.plotly_chart(fig_cost, use_container_width=True)
        
        st.subheader("Token Volume")
        fig_token = px.bar(df_model, x='Model', y='Tokens', color='Model', 
                          title="Token Volume per Model")
        st.plotly_chart(fig_token, use_container_width=True)

# --- Page: Workflow State ---
elif menu == "Workflow State":
    st.title("🔄 Workflow Sessions & Checkpoints")
    
    sessions = state_mgr.list_sessions()
    if not sessions:
        st.info("No workflow sessions found.")
    else:
        df_sessions = pd.DataFrame(sessions)
        st.dataframe(df_sessions, use_container_width=True)
        
        target_session = st.selectbox("Select Session to Inspect", [s["id"] for s in sessions])
        if target_session:
            session_data = state_mgr.get_session(target_session)
            checkpoints = state_mgr.get_checkpoints(target_session)
            
            st.subheader(f"Checkpoints for {target_session}")
            if checkpoints:
                for cp in checkpoints:
                    with st.expander(f"📍 {cp['phase']} - {cp['timestamp']}"):
                        st.json(cp["data"])
            else:
                st.write("No checkpoints found for this session.")

# --- Page: Benchmarks ---
elif menu == "Benchmarks":
    st.title("🏆 Agent Performance Benchmarks")
    
    stats = bench_runner.get_performance_stats()
    
    if "by_role" in stats:
        st.subheader("Role Performance Comparison")
        df_role = pd.DataFrame([
            {"Role": k, "Avg Score": v["avg_score"]} for k, v in stats["by_role"].items()
        ])
        fig_role = px.bar(df_role, x='Role', y='Avg Score', range_y=[0, 1], 
                         color='Avg Score', color_continuous_scale='RdYlGn')
        st.plotly_chart(fig_role, use_container_width=True)
        
        # Details
        st.subheader("Role Insights")
        for role, data in stats["by_role"].items():
            with st.expander(f"Review {role} Stats"):
                st.write(f"**Total Tests:** {data['count']}")
                st.write(f"**Trend:** {data['history']}")
                st.line_chart(data['history'])
    else:
        st.info("No benchmark data yet. Run `python tools/intelligence/evaluation/benchmark.py run` to generate data.")

# --- Page: Self-Healing ---
elif menu == "Self-Healing":
    st.title("🩹 Self-Healing Performance")
    
    healing_stats = healing.get_stats()
    
    hcol1, hcol2, hcol3 = st.columns(3)
    hcol1.metric("Total Sessions", healing_stats["total_sessions"])
    hcol2.metric("Success Rate", f"{healing_stats.get('success_rate', 0)*100:.1f}%")
    hcol3.metric("Escalation Rate", f"{healing_stats.get('escalation_rate', 0)*100:.1f}%")
    
    st.markdown("---")
    
    st.subheader("🧠 Learned Error Patterns")
    if healing.patterns_file.exists():
        patterns = json.loads(healing.patterns_file.read_text())
        for p in patterns[-10:]:
            st.info(f"**{p['type']}** ({p['severity']}): {p['description_match'][:100]}...")
            st.code(f"Fix: {p['fix']}")
    else:
        st.write("No patterns learned yet.")

st.sidebar.markdown("---")
st.sidebar.caption("Agentic SDLC Brain System Dashboard")
