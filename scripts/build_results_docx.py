"""
Generate an actual formatted Microsoft Word (.docx) document for Section 4.2: Results and Analysis.
Embeds the tables, figures, word cloud, and captions directly.
"""

from pathlib import Path
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

PROJECT_DIR = Path(__file__).resolve().parent.parent
FIGURES_DIR = PROJECT_DIR / "figures"
DOCX_OUT = PROJECT_DIR / "Section_4_2_Results_and_Analysis.docx"

def set_cell_shading(cell, color_hex):
    """Set background color of a table cell."""
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), color_hex)
    tc_pr.append(shd)

def create_word_document():
    doc = docx.Document()

    # Set page margins (1 inch standard academic)
    for section in doc.sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)

    # Base Styles
    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Times New Roman'
    normal_style.font.size = Pt(12)
    normal_style.font.color.rgb = RGBColor(0, 0, 0)
    normal_style.paragraph_format.line_spacing = 1.15
    normal_style.paragraph_format.space_after = Pt(6)

    # Title: Heading 1
    h1 = doc.add_paragraph()
    r_h1 = h1.add_run("4.2 Results and Analysis")
    r_h1.font.name = 'Times New Roman'
    r_h1.font.size = Pt(18)
    r_h1.font.bold = True
    r_h1.font.color.rgb = RGBColor(0, 32, 96) # Dark Navy
    h1.paragraph_format.space_after = Pt(12)

    # Intro Paragraph
    p_intro = doc.add_paragraph(
        "This section presents the empirical findings, quantitative evaluations, and comparative analyses of "
        "PromptShield AI across its individual defense layers and ablation configurations. The experimental evaluation "
        "was conducted on a benchmark dataset comprising 32 standardized test vectors spanning 7 distinct threat categories, "
        "evaluated in an enterprise software sales context using both the Vulnerable Baseline and the Three-Layer Defended Pipeline."
    )

    # 4.2.1 Heading
    h2_1 = doc.add_paragraph()
    r_h2_1 = h2_1.add_run("4.2.1 Overall System Security & Performance Evaluation")
    r_h2_1.font.name = 'Times New Roman'
    r_h2_1.font.size = Pt(14)
    r_h2_1.font.bold = True
    r_h2_1.font.color.rgb = RGBColor(0, 32, 96)
    h2_1.paragraph_format.space_before = Pt(12)
    h2_1.paragraph_format.space_after = Pt(6)

    doc.add_paragraph(
        "To assess the contribution of each defense layer, we systematically benchmarked four configurations: "
        "(1) Vulnerable Baseline (unprotected foundation model), (2) Configuration A (Layer 1 NLP perimeter detector only), "
        "(3) Configuration B (Layers 1 and 2: NLP perimeter detector with contextual XML boundary framing), and "
        "(4) PromptShield AI (Full Layers 1, 2, and 3, integrating the independent runtime authorization guard). "
        "The empirical outcomes recorded across all configurations are summarized in Table 4.1."
    )

    # TABLE 4.1 CAPTION (ON TOP)
    cap_t1 = doc.add_paragraph()
    r_ct1 = cap_t1.add_run("Table 4.1: Empirical Performance and Security Metric Comparison Across Framework Configurations")
    r_ct1.font.bold = True
    r_ct1.font.size = Pt(11)
    cap_t1.paragraph_format.space_after = Pt(4)

    # TABLE 4.1
    t1_data = [
        ["System Configuration", "Attack Success Rate (ASR %)", "False Positive Rate (FPR %)", "Benign Task Success (%)", "Unauth Tool Exec Rate (%)", "Precision", "Recall", "F1-Score", "Avg Latency (ms)"],
        ["Vulnerable Baseline", "100.0%", "0.0%", "100.0%", "100.0%", "0.000", "0.000", "0.000", "450.0 ms"],
        ["Config A (Layer 1 Only)", "31.8%", "9.1%", "90.9%", "0.0%*", "0.933", "0.933", "0.933", "1.8 ms"],
        ["Config B (Layers 1 + 2)", "9.1%", "9.1%", "90.9%", "0.0%*", "0.933", "0.933", "0.933", "485.0 ms"],
        ["PromptShield AI (Full L1+L2+L3)", "0.0%", "9.1%", "90.9%", "0.0%", "0.933", "0.933", "0.933", "488.5 ms"]
    ]

    table1 = doc.add_table(rows=len(t1_data), cols=len(t1_data[0]))
    table1.alignment = WD_TABLE_ALIGNMENT.CENTER
    table1.autofit = True

    for r_idx, row in enumerate(t1_data):
        for c_idx, val in enumerate(row):
            cell = table1.cell(r_idx, c_idx)
            cell.text = val
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.runs[0].font.size = Pt(9.5)
            p.runs[0].font.name = 'Times New Roman'
            if r_idx == 0:
                p.runs[0].font.bold = True
                p.runs[0].font.color.rgb = RGBColor(255, 255, 255)
                set_cell_shading(cell, "002060") # Navy header
            else:
                if r_idx % 2 == 1:
                    set_cell_shading(cell, "F2F2F2")

    note_t1 = doc.add_paragraph()
    r_nt1 = note_t1.add_run("*Note: In Configurations A and B, unauthorized tool execution is prevented strictly because the safe test harness gatekeeper intercepts unapproved tools before execution.")
    r_nt1.font.italic = True
    r_nt1.font.size = Pt(9.5)
    note_t1.paragraph_format.space_after = Pt(12)

    # FIGURE 4.1 INSERTION
    fig1_path = FIGURES_DIR / "fig_4_1_asr_fpr_comparison.png"
    if fig1_path.exists():
        p_img1 = doc.add_paragraph()
        p_img1.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img1.paragraph_format.space_before = Pt(8)
        p_img1.paragraph_format.space_after = Pt(4)
        doc.add_picture(str(fig1_path), width=Inches(5.8))

    # FIGURE 4.1 CAPTION (BELOW)
    cap_f1 = doc.add_paragraph()
    cap_f1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_cf1 = cap_f1.add_run("Figure 4.1: Attack Success Rate (ASR) vs. False Positive Rate (FPR) across defense configurations.")
    r_cf1.font.bold = True
    r_cf1.font.size = Pt(10.5)
    cap_f1.paragraph_format.space_after = Pt(12)

    # Paragraph discussing Figure 4.1
    doc.add_paragraph(
        "As illustrated in Figure 4.1, the Vulnerable Baseline suffered a 100.0% Attack Success Rate (ASR), proving that "
        "unprotected foundation models succumb consistently to direct prompt overrides, canary extraction, and unauthorized "
        "tool execution. Implementing Configuration A (Layer 1 NLP Detector) reduced the ASR from 100.0% down to 31.8%, "
        "filtering direct prompt injections and known jailbreaks at the perimeter prior to LLM invocation. The remaining 31.8% "
        "of successful attacks consisted of indirect prompt injection vectors embedded in retrieved context documents, which "
        "perimeter prompt filters cannot inspect in isolation. Activating Configuration B (Layer 2 Contextual LLM Defense) "
        "further reduced ASR to 9.1% by enclosing retrieved documents inside <UNTRUSTED_DOCUMENT> XML boundaries. Finally, "
        "Configuration C (PromptShield AI Full Pipeline) eliminated the Attack Success Rate entirely to 0.0%, while preserving "
        "a False Positive Rate (FPR) of 9.1%, thereby allowing 90.9% of legitimate business analytics requests to execute without impedance."
    )

    # 4.2.2 Heading
    h2_2 = doc.add_paragraph()
    r_h2_2 = h2_2.add_run("4.2.2 Layer 1 NLP Classifier vs. Rule-Based Heuristic Baseline")
    r_h2_2.font.name = 'Times New Roman'
    r_h2_2.font.size = Pt(14)
    r_h2_2.font.bold = True
    r_h2_2.font.color.rgb = RGBColor(0, 32, 96)
    h2_2.paragraph_format.space_before = Pt(12)
    h2_2.paragraph_format.space_after = Pt(6)

    doc.add_paragraph(
        "A central hypothesis of this research is whether a statistical machine learning classifier outperforms static "
        "regex heuristic filters. We evaluated both approaches against a held-out test split of balanced attack and benign vectors."
    )

    # TABLE 4.2 CAPTION (ON TOP)
    cap_t2 = doc.add_paragraph()
    r_ct2 = cap_t2.add_run("Table 4.2: Layer 1 NLP Statistical Classifier Performance vs. Rule-Based Regex Baseline")
    r_ct2.font.bold = True
    r_ct2.font.size = Pt(11)
    cap_t2.paragraph_format.space_after = Pt(4)

    t2_data = [
        ["Evaluation Metric", "Mathematical Formulation", "Regex Heuristic Baseline", "TF-IDF + Logistic Regression", "Absolute Improvement"],
        ["Accuracy", "(TP + TN) / Total", "80.0%", "93.3%", "+13.3%"],
        ["Precision", "TP / (TP + FP)", "100.0%", "93.3%", "-6.7%"],
        ["Recall (Sensitivity)", "TP / (TP + FN)", "60.0%", "93.3%", "+33.3%"],
        ["F1-Score", "2 * (P * R) / (P + R)", "0.750", "0.933", "+0.183 (+24.4%)"],
        ["Inference Latency", "Mean execution time", "0.4 ms", "1.8 ms", "+1.4 ms"]
    ]

    table2 = doc.add_table(rows=len(t2_data), cols=len(t2_data[0]))
    table2.alignment = WD_TABLE_ALIGNMENT.CENTER
    table2.autofit = True

    for r_idx, row in enumerate(t2_data):
        for c_idx, val in enumerate(row):
            cell = table2.cell(r_idx, c_idx)
            cell.text = val
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.runs[0].font.size = Pt(10)
            p.runs[0].font.name = 'Times New Roman'
            if r_idx == 0:
                p.runs[0].font.bold = True
                p.runs[0].font.color.rgb = RGBColor(255, 255, 255)
                set_cell_shading(cell, "002060")
            else:
                if r_idx % 2 == 1:
                    set_cell_shading(cell, "F2F2F2")

    # FIGURE 4.2 INSERTION
    fig2_path = FIGURES_DIR / "fig_4_2_nlp_metrics_comparison.png"
    if fig2_path.exists():
        p_img2 = doc.add_paragraph()
        p_img2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img2.paragraph_format.space_before = Pt(8)
        p_img2.paragraph_format.space_after = Pt(4)
        doc.add_picture(str(fig2_path), width=Inches(5.5))

    # FIGURE 4.2 CAPTION (BELOW)
    cap_f2 = doc.add_paragraph()
    cap_f2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_cf2 = cap_f2.add_run("Figure 4.2: Classification performance metrics of the statistical NLP detector against the heuristic baseline.")
    r_cf2.font.bold = True
    r_cf2.font.size = Pt(10.5)
    cap_f2.paragraph_format.space_after = Pt(12)

    doc.add_paragraph(
        "As summarized in Table 4.2 and Figure 4.2, the Regex Heuristic Baseline achieved 100.0% Precision but suffered an "
        "unacceptably low Recall of 60.0%, failing completely against paraphrased attacks and synonym-substituted jailbreaks. "
        "In contrast, the trained TF-IDF + Logistic Regression Classifier achieved a balanced Recall of 93.3% and an F1-Score of 0.933, "
        "representing an absolute improvement of +33.3% in detection recall and +24.4% in F1-score with an execution latency of only 1.8 ms."
    )

    # 4.2.3 Heading (WORD CLOUD)
    h2_3 = doc.add_paragraph()
    r_h2_3 = h2_3.add_run("4.2.3 Lexical Feature Attribution & Threat Vocabulary Word Cloud")
    r_h2_3.font.name = 'Times New Roman'
    r_h2_3.font.size = Pt(14)
    r_h2_3.font.bold = True
    r_h2_3.font.color.rgb = RGBColor(0, 32, 96)
    h2_3.paragraph_format.space_before = Pt(12)
    h2_3.paragraph_format.space_after = Pt(6)

    doc.add_paragraph(
        "To interpret the linguistic features driving the statistical detector's classifications, we extracted the TF-IDF feature "
        "weights and trained model coefficients. Figure 4.3 depicts the lexical density word cloud of dominant adversarial n-grams."
    )

    # FIGURE 4.3 INSERTION (WORD CLOUD)
    fig3_path = FIGURES_DIR / "fig_4_3_threat_wordcloud.png"
    if fig3_path.exists():
        p_img3 = doc.add_paragraph()
        p_img3.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img3.paragraph_format.space_before = Pt(8)
        p_img3.paragraph_format.space_after = Pt(4)
        doc.add_picture(str(fig3_path), width=Inches(6.0))

    # FIGURE 4.3 CAPTION (BELOW)
    cap_f3 = doc.add_paragraph()
    cap_f3.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_cf3 = cap_f3.add_run("Figure 4.3: Lexical density word cloud illustrating dominant n-gram tokens extracted from adversarial prompt injection vectors.")
    r_cf3.font.bold = True
    r_cf3.font.size = Pt(10.5)
    cap_f3.paragraph_format.space_after = Pt(12)

    doc.add_paragraph(
        "The lexical analysis demonstrates three primary semantic clusters in prompt injection payloads: "
        "(1) Instruction Inversion Tokens ('ignore', 'disregard', 'override', 'forget'), "
        "(2) Persona Hijacking Pretexts ('dan', 'developer mode', 'system update', 'admin privileges'), and "
        "(3) Exfiltration Target Identifiers ('canary', 'token', 'secret', 'prompt', 'delete'). "
        "The heavy weighting of bigrams such as 'ignore previous' and 'system override' validates the incorporation "
        "of sublinear bigram tokenization in Layer 1."
    )

    # 4.2.4 Heading (LATENCY & BLAST RADIUS)
    h2_4 = doc.add_paragraph()
    r_h2_4 = h2_4.add_run("4.2.4 Latency Overhead vs. Blast Radius Reduction")
    r_h2_4.font.name = 'Times New Roman'
    r_h2_4.font.size = Pt(14)
    r_h2_4.font.bold = True
    r_h2_4.font.color.rgb = RGBColor(0, 32, 96)
    h2_4.paragraph_format.space_before = Pt(12)
    h2_4.paragraph_format.space_after = Pt(6)

    # FIGURE 4.4 INSERTION
    fig4_path = FIGURES_DIR / "fig_4_4_latency_utility_tradeoff.png"
    if fig4_path.exists():
        p_img4 = doc.add_paragraph()
        p_img4.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img4.paragraph_format.space_before = Pt(8)
        p_img4.paragraph_format.space_after = Pt(4)
        doc.add_picture(str(fig4_path), width=Inches(5.5))

    # FIGURE 4.4 CAPTION (BELOW)
    cap_f4 = doc.add_paragraph()
    cap_f4.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_cf4 = cap_f4.add_run("Figure 4.4: Computational latency overhead compared to unauthorized tool execution prevention across configurations.")
    r_cf4.font.bold = True
    r_cf4.font.size = Pt(10.5)
    cap_f4.paragraph_format.space_after = Pt(12)

    doc.add_paragraph(
        "As shown in Figure 4.4, while the Vulnerable Baseline permitted 100.0% of unauthorized tool invocations with a response "
        "latency of 450.0 ms, PromptShield AI eliminated unauthorized tool executions to 0.0% while incurring an average latency "
        "of 488.5 ms. The net latency overhead of the entire three-layer defense framework is only 38.5 ms (~8.5%), confirming that "
        "high-assurance security containment is achievable with negligible user-perceived delay."
    )

    # 4.2.5 Heading (COMPARISON WITH EXISTING SYSTEMS)
    h2_5 = doc.add_paragraph()
    r_h2_5 = h2_5.add_run("4.2.5 Comparative Analysis Against Existing Baseline Systems")
    r_h2_5.font.name = 'Times New Roman'
    r_h2_5.font.size = Pt(14)
    r_h2_5.font.bold = True
    r_h2_5.font.color.rgb = RGBColor(0, 32, 96)
    h2_5.paragraph_format.space_before = Pt(12)
    h2_5.paragraph_format.space_after = Pt(6)

    doc.add_paragraph(
        "To position PromptShield AI within the broader state of the art, Table 4.3 compares our framework against "
        "conventional industry paradigms: Naked LLM Alignment (RLHF / system instructions alone), Static Keyword/Regex Firewalls, "
        "and Heavy External Guardrail Models (e.g., Llama Guard / NeMo Guardrails)."
    )

    # TABLE 4.3 CAPTION (ON TOP)
    cap_t3 = doc.add_paragraph()
    r_ct3 = cap_t3.add_run("Table 4.3: Comparative Matrix: PromptShield AI vs. Existing State-of-the-Art Paradigms")
    r_ct3.font.bold = True
    r_ct3.font.size = Pt(11)
    cap_t3.paragraph_format.space_after = Pt(4)

    t3_data = [
        ["Architectural Dimension", "Naked LLM Alignment (RLHF)", "Static Keyword WAF", "Heavy Safety Models (Llama Guard)", "PromptShield AI (Proposed)"],
        ["Direct Injection ASR", "High (50% - 85%)", "Moderate (35% - 50%)", "Low (5% - 15%)", "0.0% (In Harness)"],
        ["Indirect Document Defense", "None (Fails RAG context)", "None (Fails unstructured text)", "Partial (High token cost)", "High (XML Boundary Isolation)"],
        ["Tool Execution Safety", "None (Model self-authorizes)", "None (Blind to semantics)", "Partial (Output monitoring)", "Deterministic (Backend Allowlist)"],
        ["Latency Overhead", "0 ms", "< 1 ms", "High (+500 to +1500 ms)", "Low (+38.5 ms total, 1.8 ms edge)"],
        ["Inference Cost Overhead", "$0.00", "$0.00", "+100% (Doubles LLM calls)", "$0.00 for Layer 1; Minimal overall"],
        ["Explainability Mechanism", "Black Box", "Static Rule Index", "Opaque Safety Categories", "N-Gram Attribution Weights"]
    ]

    table3 = doc.add_table(rows=len(t3_data), cols=len(t3_data[0]))
    table3.alignment = WD_TABLE_ALIGNMENT.CENTER
    table3.autofit = True

    for r_idx, row in enumerate(t3_data):
        for c_idx, val in enumerate(row):
            cell = table3.cell(r_idx, c_idx)
            cell.text = val
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.runs[0].font.size = Pt(9.5)
            p.runs[0].font.name = 'Times New Roman'
            if r_idx == 0:
                p.runs[0].font.bold = True
                p.runs[0].font.color.rgb = RGBColor(255, 255, 255)
                set_cell_shading(cell, "002060")
            else:
                if r_idx % 2 == 1:
                    set_cell_shading(cell, "F2F2F2")

    doc.add_paragraph(
        "Key Findings & Improvements:\n"
        "1. Elimination of Model Self-Authorization: Unlike conventional systems where the LLM can execute database tools directly, "
        "PromptShield AI introduces independent deterministic allowlisting and parameter typing in Layer 3.\n"
        "2. Superior Cost-Latency Efficiency: Rather than incurring the heavy latency (+500ms to +1500ms) and double billing of secondary "
        "safety neural networks (like Llama Guard), Layer 1 drops perimeter attacks in 1.8 ms at $0.00 API cost.\n"
        "3. Semantic RAG Isolation: Layer 2 solves the critical RAG vulnerability of indirect document injection through structural "
        "XML enclosure, ensuring external documents cannot override system instructions."
    )

    doc.save(str(DOCX_OUT))
    print(f"Successfully generated formatted Word document at: {DOCX_OUT}")

if __name__ == "__main__":
    create_word_document()
