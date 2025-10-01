"""
CodeTantra Automation Tool - Advanced Web UI
Enhanced version with more features and better UX
"""

import streamlit as st
import asyncio
import sys
import os
from pathlib import Path
import json
import time
from datetime import datetime
import subprocess
import threading
import queue
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Page configuration
st.set_page_config(
    page_title="CodeTantra Automation Tool",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for ultra-modern look
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        padding: 3rem 2rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
        box-shadow: 0 20px 40px rgba(102, 126, 234, 0.3);
    }
    
    .main-header h1 {
        font-family: 'Inter', sans-serif;
        font-weight: 700;
        font-size: 3rem;
        margin: 0;
        text-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
    }
    
    .main-header p {
        font-family: 'Inter', sans-serif;
        font-weight: 300;
        font-size: 1.2rem;
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
    }
    
    .metric-card {
        background: white;
        padding: 2rem;
        border-radius: 16px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        margin: 1rem 0;
        transition: all 0.3s ease;
        backdrop-filter: blur(10px);
    }
    
    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
    }
    
    .status-running {
        color: #10b981;
        font-weight: 600;
        font-size: 1.1rem;
    }
    
    .status-stopped {
        color: #ef4444;
        font-weight: 600;
        font-size: 1.1rem;
    }
    
    .status-pending {
        color: #f59e0b;
        font-weight: 600;
        font-size: 1.1rem;
    }
    
    .log-container {
        background: linear-gradient(135deg, #1f2937 0%, #111827 100%);
        color: #f9fafb;
        padding: 1.5rem;
        border-radius: 12px;
        font-family: 'JetBrains Mono', 'Courier New', monospace;
        max-height: 500px;
        overflow-y: auto;
        border: 1px solid #374151;
        box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.3);
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #f8fafc 0%, #e2e8f0 100%);
        border-radius: 0 20px 20px 0;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-family: 'Inter', sans-serif;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.6);
    }
    
    .success-message {
        background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
        color: #065f46;
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 4px solid #10b981;
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.2);
    }
    
    .error-message {
        background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
        color: #991b1b;
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 4px solid #ef4444;
        box-shadow: 0 4px 15px rgba(239, 68, 68, 0.2);
    }
    
    .info-message {
        background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
        color: #1e40af;
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 4px solid #3b82f6;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.2);
    }
    
    .feature-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        border: 1px solid #e5e7eb;
        margin: 0.5rem 0;
        transition: all 0.3s ease;
    }
    
    .feature-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
    }
    
    .chart-container {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        margin: 1rem 0;
    }
    
    .tabs {
        background: white;
        border-radius: 12px;
        padding: 1rem;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'automation_running' not in st.session_state:
    st.session_state.automation_running = False
if 'automation_logs' not in st.session_state:
    st.session_state.automation_logs = []
if 'automation_stats' not in st.session_state:
    st.session_state.automation_stats = {
        'problems_solved': 0,
        'problems_failed': 0,
        'problems_skipped': 0,
        'start_time': None,
        'end_time': None,
        'total_runtime': 0
    }
if 'problem_history' not in st.session_state:
    st.session_state.problem_history = []

def check_requirements():
    """Check if all requirements are met"""
    issues = []
    
    if not Path("credentials.py").exists():
        issues.append("❌ credentials.py not found")
    
    if not Path("codetantra_playwright.py").exists():
        issues.append("❌ codetantra_playwright.py not found")
    
    try:
        import playwright
    except ImportError:
        issues.append("❌ Playwright not installed")
    
    return issues

def run_automation():
    """Run the automation in a separate thread"""
    try:
        from codetantra_playwright import CodeTantraPlaywrightAutomation
        
        automation = CodeTantraPlaywrightAutomation(auto_login=True)
        asyncio.run(automation.run_automation())
        
        st.session_state.automation_running = False
        st.session_state.automation_stats['end_time'] = datetime.now()
        st.session_state.automation_logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Automation completed successfully!")
        
    except Exception as e:
        st.session_state.automation_running = False
        st.session_state.automation_logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Error: {str(e)}")

def create_progress_chart():
    """Create a progress chart"""
    stats = st.session_state.automation_stats
    
    if stats['problems_solved'] + stats['problems_failed'] + stats['problems_skipped'] > 0:
        labels = ['Solved', 'Failed', 'Skipped']
        values = [stats['problems_solved'], stats['problems_failed'], stats['problems_skipped']]
        colors = ['#10b981', '#ef4444', '#f59e0b']
        
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            marker_colors=colors,
            hole=0.4
        )])
        
        fig.update_layout(
            title="Problem Resolution Status",
            font=dict(family="Inter", size=14),
            showlegend=True,
            height=300
        )
        
        return fig
    return None

def main():
    """Main UI function"""
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🚀 CodeTantra Automation Tool</h1>
        <p>Intelligent Code Completion Automation with Modern UI</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("## ⚙️ Control Panel")
        
        # Status indicator with animation
        if st.session_state.automation_running:
            st.markdown('<p class="status-running">🟢 Status: Running</p>', unsafe_allow_html=True)
        else:
            st.markdown('<p class="status-stopped">🔴 Status: Stopped</p>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Control buttons
        st.markdown("### 🎯 Automation Controls")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("▶️ Start", disabled=st.session_state.automation_running, use_container_width=True):
                issues = check_requirements()
                if issues:
                    for issue in issues:
                        st.error(issue)
                else:
                    st.session_state.automation_running = True
                    st.session_state.automation_stats['start_time'] = datetime.now()
                    st.session_state.automation_logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] 🚀 Starting automation...")
                    
                    thread = threading.Thread(target=run_automation)
                    thread.daemon = True
                    thread.start()
                    st.rerun()
        
        with col2:
            if st.button("⏹️ Stop", disabled=not st.session_state.automation_running, use_container_width=True):
                st.session_state.automation_running = False
                st.session_state.automation_logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] ⏹️ Automation stopped by user")
                st.rerun()
        
        st.markdown("---")
        
        # Real-time statistics
        st.markdown("### 📊 Live Statistics")
        stats = st.session_state.automation_stats
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("✅ Solved", stats['problems_solved'])
            st.metric("❌ Failed", stats['problems_failed'])
        with col2:
            st.metric("⏭️ Skipped", stats['problems_skipped'])
        
        if stats['start_time']:
            duration = datetime.now() - stats['start_time'] if st.session_state.automation_running else (stats['end_time'] - stats['start_time'] if stats['end_time'] else None)
            if duration:
                st.metric("⏱️ Duration", f"{duration.seconds // 60}m {duration.seconds % 60}s")
        
        st.markdown("---")
        
        # Quick tools
        st.markdown("### 🛠️ Quick Tools")
        if st.button("🧹 Comment Remover", use_container_width=True):
            st.info("💡 Run: `python utils/comment_remover.py`")
        
        if st.button("🔍 Question Detector", use_container_width=True):
            st.info("💡 Run: `python utils/question_type_detector.py`")
        
        if st.button("🐛 Debug Tools", use_container_width=True):
            st.info("💡 Check `debug_scripts/` folder")
        
        st.markdown("---")
        
        # Settings
        st.markdown("### ⚙️ Settings")
        auto_refresh = st.checkbox("Auto-refresh logs", value=True)
        if auto_refresh and st.session_state.automation_running:
            time.sleep(1)
            st.rerun()
    
    # Main content with tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Dashboard", "📊 Analytics", "📝 Logs", "🛠️ Tools"])
    
    with tab1:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("## 📋 Real-time Dashboard")
            
            # Log display
            if st.session_state.automation_logs:
                log_text = "\n".join(st.session_state.automation_logs[-15:])
                st.markdown(f'<div class="log-container">{log_text}</div>', unsafe_allow_html=True)
            else:
                st.info("No logs yet. Click 'Start' to begin automation.")
        
        with col2:
            st.markdown("## 🎯 Key Features")
            
            features = [
                "🔍 Smart Code Type Detection",
                "📝 Intelligent Code Extraction", 
                "🧹 Automatic Comment Removal",
                "🔄 Robust Error Handling",
                "🌍 Multi-Language Support",
                "⚡ Auto-Close Bracket Handling",
                "📊 Progress Tracking",
                "🔒 Secure Credential Management"
            ]
            
            for feature in features:
                st.markdown(f"<div class='feature-card'>{feature}</div>", unsafe_allow_html=True)
    
    with tab2:
        st.markdown("## 📊 Analytics Dashboard")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Progress chart
            chart = create_progress_chart()
            if chart:
                st.plotly_chart(chart, use_container_width=True)
            else:
                st.info("No data available yet. Start automation to see analytics.")
        
        with col2:
            # Performance metrics
            st.markdown("### ⚡ Performance Metrics")
            
            if st.session_state.automation_stats['start_time']:
                duration = datetime.now() - st.session_state.automation_stats['start_time'] if st.session_state.automation_running else (st.session_state.automation_stats['end_time'] - st.session_state.automation_stats['start_time'] if st.session_state.automation_stats['end_time'] else None)
                
                if duration:
                    total_problems = st.session_state.automation_stats['problems_solved'] + st.session_state.automation_stats['problems_failed'] + st.session_state.automation_stats['problems_skipped']
                    if total_problems > 0:
                        avg_time = duration.seconds / total_problems
                        st.metric("Average Time per Problem", f"{avg_time:.1f}s")
                    
                    st.metric("Total Runtime", f"{duration.seconds // 60}m {duration.seconds % 60}s")
    
    with tab3:
        st.markdown("## 📝 Detailed Logs")
        
        if st.session_state.automation_logs:
            # Full log display
            log_text = "\n".join(st.session_state.automation_logs)
            st.markdown(f'<div class="log-container">{log_text}</div>', unsafe_allow_html=True)
            
            # Log controls
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("🗑️ Clear Logs"):
                    st.session_state.automation_logs = []
                    st.rerun()
            with col2:
                if st.button("💾 Export Logs"):
                    log_data = "\n".join(st.session_state.automation_logs)
                    st.download_button(
                        label="Download Logs",
                        data=log_data,
                        file_name=f"automation_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                        mime="text/plain"
                    )
        else:
            st.info("No logs available yet.")
    
    with tab4:
        st.markdown("## 🛠️ Utility Tools")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🧹 Comment Remover")
            st.markdown("Remove comments from code in various programming languages.")
            
            if st.button("Launch Comment Remover", use_container_width=True):
                st.info("💡 Open terminal and run: `python utils/comment_remover.py`")
        
        with col2:
            st.markdown("### 🔍 Question Type Detector")
            st.markdown("Analyze and detect different types of coding questions.")
            
            if st.button("Launch Question Detector", use_container_width=True):
                st.info("💡 Open terminal and run: `python utils/question_type_detector.py`")
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🐛 Debug Tools")
            st.markdown("Various debugging and testing utilities.")
            
            debug_tools = [
                "codemirror_test.py - Test CodeMirror extraction",
                "debug_page.py - Debug page elements",
                "test_connection.py - Test browser connection"
            ]
            
            for tool in debug_tools:
                st.markdown(f"• {tool}")
        
        with col2:
            st.markdown("### 📚 Documentation")
            st.markdown("Comprehensive guides and documentation.")
            
            doc_links = [
                "QUICK_START.md - Quick setup guide",
                "SETUP_GUIDE.md - Detailed setup instructions",
                "README.md - Complete documentation"
            ]
            
            for doc in doc_links:
                st.markdown(f"• {doc}")
    
    # Auto-refresh when running
    if st.session_state.automation_running:
        time.sleep(2)
        st.rerun()

if __name__ == "__main__":
    main()
