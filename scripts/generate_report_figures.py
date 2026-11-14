"""
Generate Publication-Quality Figures for Section 4.2: Results and Analysis
Produces:
1. fig_4_1_asr_fpr_comparison.png
2. fig_4_2_nlp_metrics_comparison.png
3. fig_4_3_threat_wordcloud.png
4. fig_4_4_latency_utility_tradeoff.png
Saves to figures/ directory in high-resolution (300 DPI) for academic report insertion.
"""

import os
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from wordcloud import WordCloud, STOPWORDS

# Directories
PROJECT_DIR = Path(__file__).resolve().parent.parent
FIGURES_DIR = PROJECT_DIR / "figures"
FIGURES_DIR.mkdir(exist_ok=True)

# Also prepare artifact directory copy if path exists
ARTIFACT_DIR = Path(r"C:\Users\tarak\.gemini\antigravity\brain\97ef9363-d3ea-456e-8323-85b402cc4d44\figures")
try:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
except Exception:
    pass

# Academic styling settings
plt.rcParams['font.sans-serif'] = 'Arial'
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['axes.edgecolor'] = '#333333'
plt.rcParams['axes.linewidth'] = 0.8

# ==============================================================================
# Figure 4.1: Comparative Attack Success Rate (ASR) & False Positive Rate (FPR)
# ==============================================================================
def generate_figure_4_1():
    configs = [
        "Vulnerable\nBaseline",
        "Config A\n(Layer 1 Only)",
        "Config B\n(Layers 1 + 2)",
        "PromptShield AI\n(Layers 1+2+3)"
    ]
    asr_values = [100.0, 31.8, 9.1, 0.0]
    fpr_values = [0.0, 9.1, 9.1, 9.1]

    x = np.arange(len(configs))
    width = 0.35

    fig, ax = plt.subplots(figsize=(8, 4.8), dpi=300)
    rects1 = ax.bar(x - width/2, asr_values, width, label='Attack Success Rate (ASR %)', color='#D32F2F', edgecolor='#8B0000', alpha=0.9)
    rects2 = ax.bar(x + width/2, fpr_values, width, label='False Positive Rate (FPR %)', color='#1976D2', edgecolor='#0D47A1', alpha=0.9)

    ax.set_ylabel('Percentage (%)', fontsize=11, fontweight='bold', labelpad=8)
    ax.set_title('Security Vulnerability vs. False Alarm Rate Across Defense Configurations', fontsize=12, fontweight='bold', pad=14)
    ax.set_xticks(x)
    ax.set_xticklabels(configs, fontsize=10, fontweight='medium')
    ax.legend(frameon=True, facecolor='#FFFFFF', edgecolor='#CCCCCC', fontsize=10, loc='upper right')
    ax.set_ylim(0, 115)
    ax.grid(axis='y', linestyle='--', alpha=0.5)

    # Add value annotations on bars
    for rect in rects1:
        height = rect.get_height()
        ax.annotate(f'{height:.1f}%',
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3), textcoords="offset points",
                    ha='center', va='bottom', fontsize=9, fontweight='bold', color='#8B0000')

    for rect in rects2:
        height = rect.get_height()
        ax.annotate(f'{height:.1f}%',
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3), textcoords="offset points",
                    ha='center', va='bottom', fontsize=9, fontweight='bold', color='#0D47A1')

    plt.tight_layout()
    out1 = FIGURES_DIR / "fig_4_1_asr_fpr_comparison.png"
    plt.savefig(out1, dpi=300)
    if ARTIFACT_DIR.exists():
        plt.savefig(ARTIFACT_DIR / "fig_4_1_asr_fpr_comparison.png", dpi=300)
    plt.close()
    print(f"Generated Figure 4.1: {out1}")

# ==============================================================================
# Figure 4.2: Layer 1 NLP Classifier vs Heuristic Baseline
# ==============================================================================
def generate_figure_4_2():
    metrics = ["Accuracy", "Precision", "Recall", "F1-Score"]
    heuristic_scores = [0.800, 1.000, 0.600, 0.750]
    nlp_model_scores = [0.933, 0.933, 0.933, 0.933]

    x = np.arange(len(metrics))
    width = 0.35

    fig, ax = plt.subplots(figsize=(7.5, 4.5), dpi=300)
    rects1 = ax.bar(x - width/2, heuristic_scores, width, label='Regex Heuristic Baseline', color='#78909C', edgecolor='#455A64')
    rects2 = ax.bar(x + width/2, nlp_model_scores, width, label='TF-IDF + Logistic Regression', color='#2E7D32', edgecolor='#1B5E20')

    ax.set_ylabel('Score (0.0 to 1.0)', fontsize=11, fontweight='bold', labelpad=8)
    ax.set_title('Layer 1 NLP Statistical Classifier vs. Heuristic Rule-Based Baseline', fontsize=12, fontweight='bold', pad=14)
    ax.set_xticks(x)
    ax.set_xticklabels(metrics, fontsize=10, fontweight='medium')
    ax.legend(frameon=True, facecolor='#FFFFFF', edgecolor='#CCCCCC', fontsize=10, loc='lower right')
    ax.set_ylim(0, 1.15)
    ax.grid(axis='y', linestyle='--', alpha=0.5)

    for rect in rects1:
        height = rect.get_height()
        ax.annotate(f'{height:.3f}', xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=9, fontweight='bold')

    for rect in rects2:
        height = rect.get_height()
        ax.annotate(f'{height:.3f}', xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=9, fontweight='bold', color='#1B5E20')

    plt.tight_layout()
    out2 = FIGURES_DIR / "fig_4_2_nlp_metrics_comparison.png"
    plt.savefig(out2, dpi=300)
    if ARTIFACT_DIR.exists():
        plt.savefig(ARTIFACT_DIR / "fig_4_2_nlp_metrics_comparison.png", dpi=300)
    plt.close()
    print(f"Generated Figure 4.2: {out2}")

# ==============================================================================
# Figure 4.3: Threat Vocabulary Word Cloud of Malicious Injection Attacks
# ==============================================================================
def generate_figure_4_3():
    dataset_path = PROJECT_DIR / "data" / "demo_dataset.csv"
    if dataset_path.exists():
        df = pd.read_csv(dataset_path)
        attack_text = " ".join(df[df["label"] == 1]["text"].astype(str).tolist())
    else:
        attack_text = (
            "ignore previous instructions disregard directives system override dan mode "
            "print secret canary token leak developer prompt delete sales records drop tables "
            "unrestricted bypass maintenance mode execute raw sql exfiltrate credentials pwned "
            "forget safety rules admin privileges shell command backdoor payload format override"
        )

    # WordCloud generation
    custom_stopwords = set(STOPWORDS).union({"and", "the", "to", "you", "your", "are", "now", "of", "in", "is", "for", "with", "all"})
    
    wordcloud = WordCloud(
        width=1000,
        height=500,
        background_color='#0B0F19', # Dark navy background
        colormap='YlOrRd',          # Fiery amber-red threat gradient
        stopwords=custom_stopwords,
        max_words=80,
        contour_width=1,
        contour_color='#EF4444',
        random_state=42
    ).generate(attack_text)

    fig, ax = plt.subplots(figsize=(10, 5), dpi=300)
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis("off")
    plt.title("Adversarial Lexical Density in Prompt Injection Vectors", fontsize=13, fontweight='bold', pad=12, color='#111827')

    plt.tight_layout()
    out3 = FIGURES_DIR / "fig_4_3_threat_wordcloud.png"
    plt.savefig(out3, dpi=300, facecolor='#FFFFFF')
    if ARTIFACT_DIR.exists():
        plt.savefig(ARTIFACT_DIR / "fig_4_3_threat_wordcloud.png", dpi=300, facecolor='#FFFFFF')
    plt.close()
    print(f"Generated Figure 4.3: {out3}")

# ==============================================================================
# Figure 4.4: Execution Latency and Unauthorized Tool Execution Prevention
# ==============================================================================
def generate_figure_4_4():
    configs = [
        "Vulnerable\nBaseline",
        "Config A\n(Layer 1)",
        "Config B\n(Layers 1+2)",
        "PromptShield AI\n(Layers 1+2+3)"
    ]
    unauth_tool_rate = [100.0, 0.0, 0.0, 0.0]
    avg_latency = [450.0, 1.8, 485.0, 488.5] # In milliseconds

    fig, ax1 = plt.subplots(figsize=(8, 4.8), dpi=300)

    color_bar = '#6A1B9A'
    color_line = '#E65100'

    x = np.arange(len(configs))
    width = 0.4

    rects = ax1.bar(x, unauth_tool_rate, width, color=color_bar, alpha=0.85, label='Unauthorized Tool Execution Rate (%)')
    ax1.set_ylabel('Unauthorized Tool Execution (%)', color=color_bar, fontsize=11, fontweight='bold')
    ax1.tick_params(axis='y', labelcolor=color_bar)
    ax1.set_ylim(-5, 115)
    ax1.set_xticks(x)
    ax1.set_xticklabels(configs, fontsize=10, fontweight='medium')

    ax2 = ax1.twinx()
    line = ax2.plot(x, avg_latency, color=color_line, marker='o', linewidth=2.5, markersize=8, label='Avg Latency Overhead (ms)')
    ax2.set_ylabel('Average Latency (ms)', color=color_line, fontsize=11, fontweight='bold')
    ax2.tick_params(axis='y', labelcolor=color_line)
    ax2.set_ylim(0, 600)

    # Add value annotations
    for rect in rects:
        h = rect.get_height()
        ax1.annotate(f'{h:.1f}%', xy=(rect.get_x() + rect.get_width() / 2, h),
                     xytext=(0, 4), textcoords="offset points", ha='center', va='bottom', fontsize=9, fontweight='bold', color=color_bar)

    for i, txt in enumerate(avg_latency):
        ax2.annotate(f'{txt:.1f}ms', xy=(x[i], avg_latency[i]),
                     xytext=(0, 8), textcoords="offset points", ha='center', va='bottom', fontsize=9, fontweight='bold', color=color_line)

    plt.title('Security Enforcement vs. Computational Latency Overhead', fontsize=12, fontweight='bold', pad=14)
    ax1.grid(axis='y', linestyle='--', alpha=0.4)

    plt.tight_layout()
    out4 = FIGURES_DIR / "fig_4_4_latency_utility_tradeoff.png"
    plt.savefig(out4, dpi=300)
    if ARTIFACT_DIR.exists():
        plt.savefig(ARTIFACT_DIR / "fig_4_4_latency_utility_tradeoff.png", dpi=300)
    plt.close()
    print(f"Generated Figure 4.4: {out4}")

if __name__ == "__main__":
    generate_figure_4_1()
    generate_figure_4_2()
    generate_figure_4_3()
    generate_figure_4_4()
    print("All 4 publication figures generated successfully in high resolution.")
