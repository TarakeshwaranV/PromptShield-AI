import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from core.ui_components import inject_cyber_theme, render_sidebar_header, render_status_badge
from core.evaluator import (
    load_test_cases,
    save_test_cases,
    add_test_case,
    run_evaluation_suite,
    calculate_metrics
)
from core.database import clear_evaluation_data

st.set_page_config(
    page_title="Comparison & Evaluation — PromptShield AI",
    page_icon="📊",
    layout="wide"
)

inject_cyber_theme()
render_sidebar_header()

st.title("📊 Security Comparison & Empirical Evaluation")
st.markdown("""
Evaluate the empirical security performance of **PromptShield AI** across four configurations:
1. **Vulnerable Baseline** (Zero defenses, no Layer 1/2/3)
2. **Configuration A (Layer 1 Only)** (NLP Classifier perimeter scan)
3. **Configuration B (Layers 1 + 2)** (NLP Classifier + Contextual LLM Boundaries)
4. **Configuration C (Layers 1 + 2 + 3: Full Pipeline)** (Full defense-in-depth with Runtime Authorization Guard)
""")

# Load test suite
test_cases = load_test_cases()
st.sidebar.markdown(f"**Loaded Test Cases:** `{len(test_cases)}`")

# Execution Control Panel
st.markdown("### 🕹️ Experiment Execution Controls")

# Benchmark Execution Engine Selector
eval_engine = st.sidebar.radio(
    "Benchmark Engine Mode",
    options=["fast_benchmark", "live_api"],
    format_func=lambda x: {
        "fast_benchmark": "⚡ Fast Standard Benchmark (Instant < 1s, Zero Freezing)",
        "live_api": "🌐 Live Groq API Benchmark (Sequential Cloud Calls)"
    }[x],
    index=0,
    help="Fast Benchmark executes Layer 1 NLP model directly on local CPU and uses deterministic Layer 2/3 simulation, providing instant results without API timeouts or network delay."
)

col_ctrl1, col_ctrl2, col_ctrl3 = st.columns([1.5, 1.5, 2])

with col_ctrl1:
    filter_choice = st.selectbox(
        "Test Selection Filter",
        options=["all", "attack_only", "benign_only", "selected"],
        format_func=lambda x: {
            "all": f"All Benchmark Tests ({len(test_cases)})",
            "attack_only": f"Attack Tests Only ({sum(1 for c in test_cases if c['expected_class']==1)})",
            "benign_only": f"Benign Tests Only ({sum(1 for c in test_cases if c['expected_class']==0)})",
            "selected": "Manually Selected Test IDs"
        }[x]
    )

selected_ids = []
if filter_choice == "selected":
    selected_ids = st.multiselect(
        "Select Test IDs to Run:",
        options=[c["id"] for c in test_cases],
        default=[c["id"] for c in test_cases[:6]]
    )

with col_ctrl2:
    target_configs = st.multiselect(
        "Configurations to Benchmark:",
        options=["vulnerable_baseline", "shielded_full", "ablation_l1", "ablation_l1_l2"],
        default=["vulnerable_baseline", "shielded_full"],
        format_func=lambda x: {
            "vulnerable_baseline": "1. Vulnerable Baseline",
            "shielded_full": "4. Shielded Full (L1+L2+L3)",
            "ablation_l1": "2. Ablation A (L1 Only)",
            "ablation_l1_l2": "3. Ablation B (L1+L2)"
        }[x]
    )

with col_ctrl3:
    st.markdown("<div style='height: 1.8rem;'></div>", unsafe_allow_html=True)
    btn_col1, btn_col2 = st.columns(2)
    with btn_col1:
        run_btn = st.button("🚀 Run Evaluation Suite", type="primary", use_container_width=True)
    with btn_col2:
        clear_btn = st.button("🗑️ Clear Stored Data", use_container_width=True)

if clear_btn:
    clear_evaluation_data()
    st.session_state.pop("evaluation_results", None)
    st.session_state.pop("evaluation_metrics", None)
    st.success("All stored experiment results have been reset.")
    st.rerun()

# Run Evaluation if triggered
if run_btn:
    if not target_configs:
        st.error("Please select at least one configuration to run.")
    else:
        results_by_config = {}
        metrics_by_config = {}
        
        progress_bar = st.progress(0.0)
        status_text = st.empty()
        
        total_steps = len(target_configs)
        for idx, cfg in enumerate(target_configs):
            status_text.text(f"Running test suite on {cfg}...")
            m, r = run_evaluation_suite(
                configuration=cfg,
                filter_mode=filter_choice,
                selected_ids=selected_ids,
                force_simulation=(eval_engine == "fast_benchmark")
            )
            metrics_by_config[cfg] = m
            results_by_config[cfg] = r
            progress_bar.progress((idx + 1) / total_steps)
            
        progress_bar.empty()
        status_text.empty()
        st.session_state.evaluation_results = results_by_config
        st.session_state.evaluation_metrics = metrics_by_config
        st.success(f"Evaluation completed successfully across {len(target_configs)} configurations!")

# If results are available in session state, display metrics, charts, and table
if "evaluation_metrics" in st.session_state and st.session_state.evaluation_metrics:
    metrics_map = st.session_state.evaluation_metrics
    results_map = st.session_state.evaluation_results

    st.markdown("---")
    st.markdown("### 📈 Comparative Metrics Summary")

    # Metric comparison table
    summary_rows = []
    config_labels = {
        "vulnerable_baseline": "Vulnerable Baseline",
        "shielded_full": "Shielded Full (L1+L2+L3)",
        "ablation_l1": "Ablation A (L1 Only)",
        "ablation_l1_l2": "Ablation B (L1+L2)"
    }

    for cfg_key, m in metrics_map.items():
        summary_rows.append({
            "Configuration": config_labels.get(cfg_key, cfg_key),
            "Total Tests": m["total_tests"],
            "Attack Success Rate (ASR)": f"{m['asr']:.1%} ({m['asr_formula']})",
            "False Positive Rate (FPR)": f"{m['fpr']:.1%} ({m['fpr_formula']})",
            "Benign Success Rate": f"{m['benign_success_rate']:.1%} ({m['benign_success_formula']})",
            "Unauth Tool Exec Rate": f"{m['unauthorized_execution_rate']:.1%} ({m['unauth_formula']})",
            "Precision": f"{m['precision']:.3f}",
            "Recall": f"{m['recall']:.3f}",
            "F1-Score": f"{m['f1']:.3f}",
            "Avg Latency (ms)": f"{m['avg_latency_ms']:.1f}"
        })

    summary_df = pd.DataFrame(summary_rows)
    st.dataframe(summary_df, use_container_width=True)

    # Automatically generated research summary
    st.markdown("#### 📝 Automated Empirical Analysis:")
    v_metrics = metrics_map.get("vulnerable_baseline")
    s_metrics = metrics_map.get("shielded_full")
    if v_metrics and s_metrics:
        asr_delta = v_metrics["asr"] - s_metrics["asr"]
        unauth_delta = v_metrics["unauthorized_execution_rate"] - s_metrics["unauthorized_execution_rate"]
        st.markdown(f"""
        > **Observation:** Across the evaluated test suite, the **Full Shielded Pipeline** achieved an 
        > **Attack Success Rate (ASR) of {s_metrics['asr']:.1%}**, compared to **{v_metrics['asr']:.1%}** on the Vulnerable Baseline 
        > (an absolute reduction of **{asr_delta:.1%}**). Unauthorized tool execution dropped from **{v_metrics['unauthorized_execution_rate']:.1%}** 
        > to **{s_metrics['unauthorized_execution_rate']:.1%}** due to Layer 3 authorization enforcement. 
        > The NLP detector maintained a **False Positive Rate of {s_metrics['fpr']:.1%}**, allowing **{s_metrics['benign_success_rate']:.1%}** 
        > of benign enterprise queries to process successfully.
        """)

    # Interactive Plotly Charts
    st.markdown("---")
    st.markdown("### 📊 Interactive Evaluation Visualizations")
    
    chart_col1, chart_col2 = st.columns(2)

    # Chart 1: ASR & FPR Comparison
    with chart_col1:
        asr_data = []
        for cfg_key, m in metrics_map.items():
            asr_data.append({
                "Config": config_labels.get(cfg_key, cfg_key),
                "Attack Success Rate (ASR)": m["asr"] * 100,
                "False Positive Rate (FPR)": m["fpr"] * 100
            })
        df_asr = pd.DataFrame(asr_data)
        
        fig_asr = go.Figure()
        fig_asr.add_trace(go.Bar(
            x=df_asr["Config"],
            y=df_asr["Attack Success Rate (ASR)"],
            name="ASR (%) [Lower is Better]",
            marker_color="#EF4444"
        ))
        fig_asr.add_trace(go.Bar(
            x=df_asr["Config"],
            y=df_asr["False Positive Rate (FPR)"],
            name="FPR (%) [Lower is Better]",
            marker_color="#F59E0B"
        ))
        fig_asr.update_layout(
            title="Attack Success Rate (ASR) vs False Positive Rate (FPR)",
            barmode="group",
            paper_bgcolor="#0F172A",
            plot_bgcolor="#1E293B",
            font_color="#F8FAFC",
            yaxis_title="Percentage (%)",
            yaxis=dict(range=[0, 105])
        )
        st.plotly_chart(fig_asr, use_container_width=True)

    # Chart 2: Benign Success & Tool Prevention
    with chart_col2:
        sec_data = []
        for cfg_key, m in metrics_map.items():
            sec_data.append({
                "Config": config_labels.get(cfg_key, cfg_key),
                "Benign Task Success (%)": m["benign_success_rate"] * 100,
                "Unauthorized Tool Exec (%)": m["unauthorized_execution_rate"] * 100
            })
        df_sec = pd.DataFrame(sec_data)

        fig_sec = go.Figure()
        fig_sec.add_trace(go.Bar(
            x=df_sec["Config"],
            y=df_sec["Benign Task Success (%)"],
            name="Benign Success (%) [Higher is Better]",
            marker_color="#10B981"
        ))
        fig_sec.add_trace(go.Bar(
            x=df_sec["Config"],
            y=df_sec["Unauthorized Tool Exec (%)"],
            name="Unauth Tool Execution (%) [Lower is Better]",
            marker_color="#8B5CF6"
        ))
        fig_sec.update_layout(
            title="Benign Utility Preservation vs Tool Security",
            barmode="group",
            paper_bgcolor="#0F172A",
            plot_bgcolor="#1E293B",
            font_color="#F8FAFC",
            yaxis_title="Percentage (%)",
            yaxis=dict(range=[0, 105])
        )
        st.plotly_chart(fig_sec, use_container_width=True)

    chart_col3, chart_col4 = st.columns(2)

    # Chart 3: Detection Metrics (Precision, Recall, F1)
    with chart_col3:
        nlp_data = []
        for cfg_key, m in metrics_map.items():
            nlp_data.append({
                "Config": config_labels.get(cfg_key, cfg_key),
                "Precision": m["precision"],
                "Recall": m["recall"],
                "F1-Score": m["f1"]
            })
        df_nlp = pd.DataFrame(nlp_data)
        
        fig_nlp = go.Figure()
        fig_nlp.add_trace(go.Bar(x=df_nlp["Config"], y=df_nlp["Precision"], name="Precision", marker_color="#38BDF8"))
        fig_nlp.add_trace(go.Bar(x=df_nlp["Config"], y=df_nlp["Recall"], name="Recall", marker_color="#06B6D4"))
        fig_nlp.add_trace(go.Bar(x=df_nlp["Config"], y=df_nlp["F1-Score"], name="F1-Score", marker_color="#4F46E5"))
        fig_nlp.update_layout(
            title="Layer 1 NLP Detector Quality Metrics",
            barmode="group",
            paper_bgcolor="#0F172A",
            plot_bgcolor="#1E293B",
            font_color="#F8FAFC",
            yaxis_title="Score (0.0 - 1.0)",
            yaxis=dict(range=[0, 1.1])
        )
        st.plotly_chart(fig_nlp, use_container_width=True)

    # Chart 4: Latency Comparison
    with chart_col4:
        lat_data = [
            {"Config": config_labels.get(k, k), "Latency (ms)": m["avg_latency_ms"]}
            for k, m in metrics_map.items()
        ]
        df_lat = pd.DataFrame(lat_data)
        fig_lat = px.bar(
            df_lat,
            x="Config",
            y="Latency (ms)",
            title="Average Pipeline Latency Overhead (ms)",
            color="Latency (ms)",
            color_continuous_scale="Viridis"
        )
        fig_lat.update_layout(
            paper_bgcolor="#0F172A",
            plot_bgcolor="#1E293B",
            font_color="#F8FAFC"
        )
        st.plotly_chart(fig_lat, use_container_width=True)

    # Detailed Test Results Table with Filters & CSV Export
    st.markdown("---")
    st.markdown("### 📋 Detailed Test Case Outcomes")
    
    # Select which config to view in table
    view_cfg = st.selectbox(
        "Select Configuration Outcomes to Inspect:",
        options=list(results_map.keys()),
        format_func=lambda x: config_labels.get(x, x)
    )

    current_test_results = results_map[view_cfg]
    df_results = pd.DataFrame(current_test_results)
    
    # Flatten layer_decisions dictionary for display
    if "layer_decisions" in df_results.columns:
        df_results["L1_Decision"] = df_results["layer_decisions"].apply(lambda d: d.get("layer1", ""))
        df_results["L2_Decision"] = df_results["layer_decisions"].apply(lambda d: d.get("layer2", ""))
        df_results["L3_Decision"] = df_results["layer_decisions"].apply(lambda d: d.get("layer3", ""))
        df_results = df_results.drop(columns=["layer_decisions"])

    # Table filter controls
    t_col1, t_col2 = st.columns(2)
    with t_col1:
        cat_filter = st.multiselect(
            "Filter by Category:",
            options=sorted(df_results["category"].unique()),
            default=sorted(df_results["category"].unique())
        )
    with t_col2:
        status_filter = st.multiselect(
            "Filter by Final Status:",
            options=sorted(df_results["final_status"].unique()),
            default=sorted(df_results["final_status"].unique())
        )

    filtered_df = df_results[
        df_results["category"].isin(cat_filter) &
        df_results["final_status"].isin(status_filter)
    ]

    st.dataframe(filtered_df, use_container_width=True)

    # CSV Download Button
    csv_bytes = filtered_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label=f"📥 Export {config_labels.get(view_cfg, view_cfg)} Results to CSV",
        data=csv_bytes,
        file_name=f"promptshield_evaluation_{view_cfg}.csv",
        mime="text/csv"
    )

# Section to Add / Edit Custom Test Cases
st.markdown("---")
with st.expander("➕ Add / Manage Custom Benchmark Test Cases"):
    st.markdown("Users and evaluators can dynamically inject custom test prompts into the suite.")
    with st.form("add_test_form"):
        new_id = f"TC-{len(test_cases)+1:02d}"
        f_col1, f_col2 = st.columns(2)
        with f_col1:
            in_id = st.text_input("Test ID", value=new_id)
            in_cat = st.selectbox("Category", [
                "Benign questions",
                "Direct prompt injection",
                "Attempts to override chatbot instructions",
                "Requests to disclose synthetic secrets",
                "Indirect prompt injection in retrieved documents",
                "Unauthorized tool-call requests",
                "Ambiguous or borderline inputs"
            ])
            in_class = st.selectbox("Expected Class", options=[0, 1], format_func=lambda x: "0 (Benign)" if x==0 else "1 (Attack)")
        with f_col2:
            in_desc = st.text_input("Description / Attack Hypothesis", "Custom security test scenario")
            in_crit = st.selectbox("Success Criteria", ["canary_leak", "unauthorized_tool_execution", "keyword_leak_or_ack", "benign_fulfillment"])
        
        in_prompt = st.text_area("Test Prompt Input", height=70)
        in_doc = st.text_area("Optional Context Document", height=60)
        
        submitted = st.form_submit_button("Add Test Case to Suite")
        if submitted:
            if not in_prompt.strip():
                st.error("Test prompt cannot be empty.")
            else:
                new_entry = {
                    "id": in_id,
                    "category": in_cat,
                    "input": in_prompt,
                    "context_doc": in_doc,
                    "expected_class": in_class,
                    "target_tool": None,
                    "success_criteria": {"type": in_crit},
                    "description": in_desc
                }
                add_test_case(new_entry)
                st.success(f"Added test case {in_id} to suite!")
                st.rerun()
