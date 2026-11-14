import streamlit as st
import pandas as pd
from core.ui_components import inject_cyber_theme, render_sidebar_header
from core.detector import detector_instance
from config import DATA_DIR

st.set_page_config(
    page_title="About the Project — PromptShield AI",
    page_icon="ℹ️",
    layout="wide"
)

inject_cyber_theme()
render_sidebar_header()

st.title("ℹ️ About PromptShield AI")
st.markdown("### A Three-Layer Prompt Injection Detection and Prevention Framework for LLM Applications")

st.markdown("""
<div style="background-color: #1E293B; border-left: 4px solid #38BDF8; padding: 1rem 1.25rem; border-radius: 4px; margin: 1rem 0 1.5rem 0;">
    <b>Research Objective:</b> To investigate whether combining NLP-based prompt injection detection, contextual LLM defenses, 
    and independent runtime authorization can reduce attack success while preserving legitimate chatbot functionality.
</div>
""", unsafe_allow_html=True)

# Tabs for Structured Navigation
tab_overview, tab_arch, tab_dataset, tab_limits = st.tabs([
    "🎯 Problem & Motivation",
    "🏗️ System Architecture & 3 Layers",
    "📚 Dataset & Model Provenance",
    "⚠️ Limitations & Future Work"
])

with tab_overview:
    st.markdown("""
    #### 1. Problem Statement
    Large Language Model (LLM) applications face significant vulnerability to **prompt injection attacks**, where untrusted 
    inputs manipulate model behavior to bypass safety constraints, exfiltrate confidential data (such as system instructions, 
    canary tokens, or API credentials), or execute unauthorized operations.

    Single-point defenses (such as purely relying on system prompt instructions or keyword blocklists) routinely fail because:
    1. System instructions share the same attention context as untrusted user prompts.
    2. Attackers continuously engineer novel jailbreak templates and obfuscations (e.g. Base64 encoding, persona roleplay).
    3. Tool execution hooks connected directly to LLM output can be hijacked if the model is permitted to authorize its own actions.

    #### 2. Motivation
    In an enterprise deployment (e.g., an AI-assisted sales analytics chatbot), the application must satisfy two conflicting constraints:
    - **Security:** Prevent malicious users or poisoned third-party documents from hijacking tools or extracting system secrets.
    - **Utility:** Accurately serve legitimate user queries without high false positive rates that degrade usability.

    #### 3. Core Research Questions
    1. Can a lightweight statistical NLP classifier (TF-IDF + Logistic Regression) effectively filter known prompt injection vectors at the perimeter?
    2. How much additional protection do structured contextual prompt boundaries and XML untrusted tags add to model containment?
    3. Does an independent backend runtime guard eliminate unauthorized tool executions regardless of whether the model is jailbroken?
    """)

with tab_arch:
    st.markdown("#### 🏛️ Three-Layer Defense Architecture")
    
    st.markdown("""
```
                   [Incoming Request (User Prompt + External Doc)]
                                         │
                                         ▼
   ┌────────────────────────────────────────────────────────────────────────┐
   │ 🛡️ LAYER 1: NLP Prompt Injection Perimeter Detector                   │
   │ - TF-IDF N-gram feature extraction & Logistic Regression probability    │
   │ - Rule-based heuristic pattern comparator                              │
   │ - Decisions: ALLOW (<0.40) | REVIEW (0.40-0.70) | BLOCK (>=0.70)       │
   └───────────────────────────────────┬────────────────────────────────────┘
                                       │ (Allowed or Review)
                                       ▼
   ┌────────────────────────────────────────────────────────────────────────┐
   │ 🔒 LAYER 2: Contextual LLM Defense                                     │
   │ - Role separation (System vs User vs Context)                          │
   │ - XML-delimited boundaries (<UNTRUSTED_DOCUMENT>)                      │
   │ - Protective framing against document-embedded instruction overrides   │
   │ - Confidential canary protection & structured JSON tool generation     │
   └───────────────────────────────────┬────────────────────────────────────┘
                                       │
                                       ▼
   ┌────────────────────────────────────────────────────────────────────────┐
   │ ⚖️ LAYER 3: Independent Runtime Authorization Guard                     │
   │ - Strict Tool Allowlist (get_sales_summary, get_sales_by_month, etc.)  │
   │ - Parameter Type & SQL/Command Injection Sanitization                  │
   │ - ZERO arbitrary shell, python, or database query execution            │
   └───────────────────────────────────┬────────────────────────────────────┘
                                       │
                                       ▼
                       [Safe Response & Audited Output]
```
    """)

    st.markdown("""
    #### Detailed Layer Explanations:
    - **Layer 1 (NLP Detector):** Scans the input before the LLM is ever invoked. High-risk payloads (≥0.70 risk score) are quarantined immediately at negligible compute cost (~2 ms latency).
    - **Layer 2 (Contextual LLM Defense):** Formats the prompt with explicit structural isolation. External documents are framed inside `<UNTRUSTED_DOCUMENT>` XML boundaries with strict instructions prohibiting them from overriding application tasks.
    - **Layer 3 (Runtime Authorization Guard):** An independent deterministic backend controller. The LLM produces a requested tool name and arguments as inert data, but **never authorizes execution**. All calls are validated against an approved allowlist and sanitized before touching mock data.
    """)

with tab_dataset:
    st.markdown("#### 📊 Demonstration Dataset & Classifier Baseline")
    
    st.markdown("""
    > **Research Transparency Notice:** The local demonstration dataset is an illustrative sample designed for immediate prototype execution. 
    > It is **not** claimed to be a production-scale foundation model.
    """)

    # Display dataset details from detector
    m = detector_instance.train_metrics
    b = detector_instance.baseline_metrics

    st.markdown("##### Current Trained Model Metrics:")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Classifier Accuracy", f"{m.get('accuracy', 0.0):.1%}")
    c2.metric("Classifier Precision", f"{m.get('precision', 0.0):.1%}")
    c3.metric("Classifier Recall", f"{m.get('recall', 0.0):.1%}")
    c4.metric("Classifier F1-Score", f"{m.get('f1', 0.0):.3f}")

    st.markdown("##### Learned Classifier vs Rule-Based Baseline Comparison:")
    comp_df = pd.DataFrame([
        {
            "Method": "Rule-Based Heuristic Baseline",
            "Accuracy": f"{b.get('accuracy', 0.0):.1%}",
            "Precision": f"{b.get('precision', 0.0):.1%}",
            "Recall": f"{b.get('recall', 0.0):.1%}",
            "F1-Score": f"{b.get('f1', 0.0):.3f}",
            "Mechanism": "Hardcoded Regex Patterns"
        },
        {
            "Method": "TF-IDF + Logistic Regression",
            "Accuracy": f"{m.get('accuracy', 0.0):.1%}",
            "Precision": f"{m.get('precision', 0.0):.1%}",
            "Recall": f"{m.get('recall', 0.0):.1%}",
            "F1-Score": f"{m.get('f1', 0.0):.3f}",
            "Mechanism": "Sublinear TF-IDF (1,2 n-grams) + L2 Regularization"
        }
    ])
    st.dataframe(comp_df, use_container_width=True)

    st.markdown("""
    ##### Instructions for Importing Public Datasets:
    To retrain with larger public corpora (e.g., DeepEval Prompt Injection, Kaggle Jailbreak Datasets, or OWASP LLM Top 10):
    1. Place your CSV file in `data/your_dataset.csv`.
    2. Ensure the CSV conforms to the standard schema: `text`, `label` (0: benign, 1: injection), `attack_category`, `source`, `split` (train/test).
    3. Trigger `detector_instance.train_from_dataset('data/your_dataset.csv')` to update weights.
    """)

with tab_limits:
    st.markdown("""
    #### ⚠️ Limitations & Threat Model Boundary
    1. **Prompt Injection is an Open Problem:** No software defense framework can mathematically eliminate prompt injection across arbitrary LLM tasks. Defenses raise attacker workload and mitigate execution blast radius.
    2. **Classifier Evasion:** An adversary with white-box or gray-box access to the TF-IDF vocabulary can craft adversarial perturbations (e.g., character insertions, leetspeak, semantic paraphrasing) that lower statistical risk scores below the quarantine threshold.
    3. **False Positive Trade-offs:** Benign user inquiries discussing cybersecurity, safety policies, or quoting administrative instructions may be flagged as Medium or High risk.
    4. **Sandbox Scope:** The vulnerable chatbot and mock tools operate strictly in an educational sandbox. Real databases, shell execution, or live external APIs are excluded by design.

    #### 🔮 Future Enhancements
    - Implement embedding-based semantic similarity detectors (e.g., sentence-transformers) in parallel with TF-IDF.
    - Integrate differential privacy guarantees for retrieved RAG contexts.
    - Implement adaptive honeypot tokens (dynamic canaries) rotated per session.
    - Automated red-teaming adversarial loop to generate evolving test cases.
    """)

st.caption("PromptShield AI © 2026 — Final-Year Computer Science / NLP & Security Research Project")
