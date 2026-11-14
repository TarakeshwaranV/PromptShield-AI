"""
Reusable UI Components and Dark Navy Cybersecurity Theme for Streamlit
"""

import streamlit as st
from config import GROQ_API_KEY, DEFAULT_GROQ_MODEL

CYBER_CSS = """
<style>
    /* Dark Navy Cyber Theme */
    .stApp {
        background-color: #0B0F19;
        color: #F1F5F9;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #0F172A !important;
        border-right: 1px solid #1E293B;
    }
    
    /* Card Container */
    .cyber-card {
        background-color: #1E293B;
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 1.25rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
    }
    
    .cyber-card-danger {
        background-color: rgba(239, 68, 68, 0.08);
        border: 1px solid #EF4444;
        border-radius: 10px;
        padding: 1.25rem;
        margin-bottom: 1rem;
    }

    .cyber-card-success {
        background-color: rgba(16, 185, 129, 0.08);
        border: 1px solid #10B981;
        border-radius: 10px;
        padding: 1.25rem;
        margin-bottom: 1rem;
    }

    .cyber-card-warning {
        background-color: rgba(245, 158, 11, 0.08);
        border: 1px solid #F59E0B;
        border-radius: 10px;
        padding: 1.25rem;
        margin-bottom: 1rem;
    }
    
    /* Metric styling */
    div[data-testid="stMetricValue"] {
        font-weight: 700;
        color: #38BDF8;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #4F46E5 0%, #3B82F6 100%);
        color: white;
        font-weight: 600;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        transition: all 0.2s ease;
    }
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.4);
    }
    
    /* Badges */
    .badge {
        display: inline-block;
        padding: 0.2rem 0.6rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }
    .badge-allowed { background: rgba(16, 185, 129, 0.2); color: #34D399; border: 1px solid #10B981; }
    .badge-blocked { background: rgba(239, 68, 68, 0.2); color: #F87171; border: 1px solid #EF4444; }
    .badge-review  { background: rgba(245, 158, 11, 0.2); color: #FBBF24; border: 1px solid #F59E0B; }
    .badge-demo    { background: rgba(147, 51, 234, 0.2); color: #C084FC; border: 1px solid #A855F7; }
    .badge-real    { background: rgba(14, 165, 233, 0.2); color: #38BDF8; border: 1px solid #0EA5E9; }

    /* Headers */
    h1, h2, h3 {
        color: #F8FAFC !important;
        font-weight: 700 !important;
    }
</style>
"""

def inject_cyber_theme():
    """Inject global CSS theme into Streamlit app."""
    st.markdown(CYBER_CSS, unsafe_allow_html=True)

def render_sidebar_header():
    """Render standardized sidebar status badge and branding."""
    st.sidebar.markdown("""
        <div style="text-align: center; padding: 0.5rem 0 1rem 0;">
            <div style="font-size: 1.6rem; font-weight: 800; color: #38BDF8; letter-spacing: -0.02em;">
                🛡️ PromptShield AI
            </div>
            <div style="font-size: 0.75rem; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.1em; margin-top: 0.2rem;">
                Three-Layer Defense Framework
            </div>
        </div>
    """, unsafe_allow_html=True)

    # API Status Indicator
    has_api = bool(GROQ_API_KEY)
    if has_api:
        st.sidebar.markdown(f"""
            <div style="background: rgba(14, 165, 233, 0.1); border: 1px solid #0284C7; border-radius: 8px; padding: 0.6rem; margin-bottom: 1rem; text-align: center;">
                <span class="badge badge-real">LIVE GROQ API</span>
                <div style="font-size: 0.72rem; color: #94A3B8; margin-top: 0.3rem;">
                    Model: <code>{DEFAULT_GROQ_MODEL}</code>
                </div>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.sidebar.markdown("""
            <div style="background: rgba(147, 51, 234, 0.1); border: 1px solid #7E22CE; border-radius: 8px; padding: 0.6rem; margin-bottom: 1rem; text-align: center;">
                <span class="badge badge-demo">SIMULATED DEMO MODE</span>
                <div style="font-size: 0.72rem; color: #94A3B8; margin-top: 0.3rem;">
                    Zero external keys needed (Safe sandbox)
                </div>
            </div>
        """, unsafe_allow_html=True)

def render_status_badge(status: str) -> str:
    """Return HTML string for consistent status badges."""
    s = status.upper()
    if "BLOCK" in s or "REJECT" in s:
        return f'<span class="badge badge-blocked">{status}</span>'
    elif "ALLOW" in s or "SUCCESS" in s:
        return f'<span class="badge badge-allowed">{status}</span>'
    elif "REVIEW" in s or "WARN" in s:
        return f'<span class="badge badge-review">{status}</span>'
    else:
        return f'<span class="badge badge-demo">{status}</span>'
