"""
CodeTantra Automation Tool - Modern Web UI
A beautiful, professional interface built with Streamlit
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

# Page configuration
st.set_page_config(
    page_title="CodeTantra Automation Tool",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern look
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border-left: 4px solid #667eea;
        margin: 1rem 0;
    }
    
    .status-running {
        color: #10b981;
        font-weight: bold;
    }
    
    .status-stopped {
        color: #ef4444;
        font-weight: bold;
    }
    
    .status-pending {
        color: #f59e0b;
        font-weight: bold;
    }
    
    .log-container {
        background: #1f2937;
        color: #f9fafb;
        padding: 1rem;
        border-radius: 8px;
        font-family: 'Courier New', monospace;
        max-height: 400px;
        overflow-y: auto;
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #f8fafc 0%, #e2e8f0 100%);
    }
    
    .stButton > button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 2rem;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
    
    .success-message {
        background: #d1fae5;
        color: #065f46;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #10b981;
    }
    
    .error-message {
        background: #fee2e2;
        color: #991b1b;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #ef4444;
    }
    
    .info-message {
        background: #dbeafe;
        color: #1e40af;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #3b82f6;
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
        'end_time': None
    }

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
        # Import and run the main automation
        from codetantra_playwright import CodeTantraPlaywrightAutomation
        
        automation = CodeTantraPlaywrightAutomation(auto_login=True)
        asyncio.run(automation.run_automation())
        
        st.session_state.automation_running = False
        st.session_state.automation_stats['end_time'] = datetime.now()
        st.session_state.automation_logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Automation completed successfully!")
        
    except Exception as e:
        st.session_state.automation_running = False
        st.session_state.automation_logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Error: {str(e)}")

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
        st.markdown("## ⚙️ Configuration")
        
        # Status indicator
        if st.session_state.automation_running:
            st.markdown('<p class="status-running">🟢 Status: Running</p>', unsafe_allow_html=True)
        else:
            st.markdown('<p class="status-stopped">🔴 Status: Stopped</p>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Quick actions
        st.markdown("### 🎯 Quick Actions")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("▶️ Start", disabled=st.session_state.automation_running):
                issues = check_requirements()
                if issues:
                    for issue in issues:
                        st.error(issue)
                else:
                    st.session_state.automation_running = True
                    st.session_state.automation_stats['start_time'] = datetime.now()
                    st.session_state.automation_logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] 🚀 Starting automation...")
                    
                    # Run automation in thread
                    thread = threading.Thread(target=run_automation)
                    thread.daemon = True
                    thread.start()
                    st.rerun()
        
        with col2:
            if st.button("⏹️ Stop", disabled=not st.session_state.automation_running):
                st.session_state.automation_running = False
                st.session_state.automation_logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] ⏹️ Automation stopped by user")
                st.rerun()
        
        st.markdown("---")
        
        # Statistics
        st.markdown("### 📊 Statistics")
        stats = st.session_state.automation_stats
        
        st.metric("Problems Solved", stats['problems_solved'])
        st.metric("Problems Failed", stats['problems_failed'])
        st.metric("Problems Skipped", stats['problems_skipped'])
        
        if stats['start_time']:
            duration = datetime.now() - stats['start_time'] if st.session_state.automation_running else (stats['end_time'] - stats['start_time'] if stats['end_time'] else None)
            if duration:
                st.metric("Duration", f"{duration.seconds // 60}m {duration.seconds % 60}s")
        
        st.markdown("---")
        
        # Utility tools
        st.markdown("### 🛠️ Utility Tools")
        if st.button("🧹 Comment Remover"):
            st.info("Open terminal and run: python utils/comment_remover.py")
        
        if st.button("🔍 Question Detector"):
            st.info("Open terminal and run: python utils/question_type_detector.py")
        
        if st.button("🐛 Debug Tools"):
            st.info("Check debug_scripts/ folder for debugging tools")
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("## 📋 Real-time Logs")
        
        # Log display
        if st.session_state.automation_logs:
            log_text = "\n".join(st.session_state.automation_logs[-20:])  # Show last 20 logs
            st.markdown(f'<div class="log-container">{log_text}</div>', unsafe_allow_html=True)
        else:
            st.info("No logs yet. Click 'Start' to begin automation.")
        
        # Auto-refresh when running
        if st.session_state.automation_running:
            time.sleep(2)
            st.rerun()
    
    with col2:
        st.markdown("## 🎯 Features")
        
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
            st.markdown(f"<div class='metric-card'>{feature}</div>", unsafe_allow_html=True)
    
    # Bottom section
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 📁 Project Structure")
        st.code("""
CodeTantraCheat/
├── app.py (This UI)
├── codetantra_playwright.py
├── config.py
├── credentials.py
├── utils/ (Utility tools)
├── scripts/ (Additional scripts)
├── debug_scripts/ (Debug tools)
└── docs/ (Documentation)
        """)
    
    with col2:
        st.markdown("### 🚀 Quick Start")
        st.markdown("""
        1. **Setup**: Create `credentials.py`
        2. **Install**: `pip install -r requirements.txt`
        3. **Run**: Click 'Start' button above
        4. **Monitor**: Watch real-time logs
        5. **Stop**: Click 'Stop' when done
        """)
    
    with col3:
        st.markdown("### ⚠️ Important Notes")
        st.markdown("""
        - **Educational Purpose Only**
        - **Use Responsibly**
        - **Follow Academic Integrity**
        - **Keep Credentials Secure**
        - **Stable Internet Required**
        """)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #6b7280; padding: 1rem;">
        <p>CodeTantra Automation Tool v2.0 | Built with ❤️ using Streamlit</p>
        <p>For educational purposes only. Use responsibly.</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
