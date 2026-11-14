"""
Generate a purely minimalist, clean White Background & Black Font PowerPoint (.pptx).
Strictly NO colors: all backgrounds white, all typography black/dark-gray,
clean borders and high-contrast tables and figures.
"""

from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.text.text import _Paragraph

# Patch add_run so it accepts text argument like python-docx
_orig_add_run = _Paragraph.add_run
def _patched_add_run(self, text=None):
    r = _orig_add_run(self)
    if text is not None:
        r.text = str(text)
    return r
_Paragraph.add_run = _patched_add_run

PROJECT_DIR = Path(__file__).resolve().parent.parent
FIGURES_DIR = PROJECT_DIR / "figures"
PPTX_OUT = PROJECT_DIR / "PromptShield_AI_Presentation.pptx"

# Pure Monochrome Palette (Strictly White & Black)
COLOR_WHITE = RGBColor(255, 255, 255)
COLOR_BLACK = RGBColor(0, 0, 0)
COLOR_DARK = RGBColor(30, 30, 30)
COLOR_MUTED = RGBColor(70, 70, 70)
COLOR_BORDER = RGBColor(160, 160, 160)
COLOR_LIGHT_BG = RGBColor(250, 250, 250)

def set_slide_white_bg(slide, prs):
    """Explicitly sets pure white background for the slide."""
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = COLOR_WHITE

def add_header(slide, title_text, slide_num=None):
    """Adds minimalist black header with a clean separator line."""
    tx_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.0), Inches(0.8))
    tf = tx_box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = title_text
    p.font.name = 'Arial'
    p.font.size = Pt(22)
    p.font.bold = True
    p.font.color.rgb = COLOR_BLACK
    
    if slide_num:
        num_box = slide.shapes.add_textbox(Inches(12.0), Inches(0.4), Inches(0.8), Inches(0.6))
        np = num_box.text_frame.paragraphs[0]
        np.text = f"{slide_num:02d}"
        np.font.name = 'Arial'
        np.font.size = Pt(14)
        np.font.bold = True
        np.font.color.rgb = COLOR_MUTED
        np.alignment = PP_ALIGN.RIGHT

    # Thin black divider line
    line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.2), Inches(11.7), Inches(0.02))
    line.fill.solid()
    line.fill.fore_color.rgb = COLOR_BORDER
    line.line.fill.background()

def style_monochrome_table(table):
    """Styles tables in clean academic monochrome style (black & white)."""
    # Header row
    for cell in table.rows[0].cells:
        cell.fill.solid()
        cell.fill.fore_color.rgb = COLOR_BLACK
        for p in cell.text_frame.paragraphs:
            p.font.name = 'Arial'
            p.font.size = Pt(10.5)
            p.font.bold = True
            p.font.color.rgb = COLOR_WHITE
            p.alignment = PP_ALIGN.CENTER
            
    # Data rows
    for r_idx in range(1, len(table.rows)):
        for cell in table.rows[r_idx].cells:
            cell.fill.solid()
            if r_idx % 2 == 1:
                cell.fill.fore_color.rgb = COLOR_LIGHT_BG
            else:
                cell.fill.fore_color.rgb = COLOR_WHITE
            for p in cell.text_frame.paragraphs:
                p.font.name = 'Arial'
                p.font.size = Pt(9.5)
                p.font.color.rgb = COLOR_BLACK

def create_presentation():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # =========================================================================
    # SLIDE 1: Title Slide (White Background, Black Font)
    # =========================================================================
    slide1 = prs.slides.add_slide(blank_layout)
    set_slide_white_bg(slide1, prs)

    # Clean outer framing border
    frame1 = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(0.8), Inches(11.733), Inches(5.9))
    frame1.fill.solid()
    frame1.fill.fore_color.rgb = COLOR_WHITE
    frame1.line.color.rgb = COLOR_BLACK
    frame1.line.width = Pt(2.0)

    tb1 = slide1.shapes.add_textbox(Inches(1.2), Inches(1.4), Inches(10.9), Inches(4.5))
    tf1 = tb1.text_frame
    tf1.word_wrap = True

    p_badge = tf1.paragraphs[0]
    p_badge.text = "RESEARCH PROJECT PRESENTATION"
    p_badge.font.name = 'Arial'
    p_badge.font.size = Pt(11)
    p_badge.font.bold = True
    p_badge.font.color.rgb = COLOR_MUTED

    p_title = tf1.add_paragraph()
    p_title.text = "PromptShield AI: A Three-Layer Prompt Injection\nDetection and Prevention Framework"
    p_title.font.name = 'Arial'
    p_title.font.size = Pt(30)
    p_title.font.bold = True
    p_title.font.color.rgb = COLOR_BLACK
    p_title.space_before = Pt(12)

    p_sub = tf1.add_paragraph()
    p_sub.text = "A multi-tier defense architecture combining statistical NLP perimeter detection, contextual XML prompt isolation, and independent runtime authorization for LLM applications."
    p_sub.font.name = 'Arial'
    p_sub.font.size = Pt(14)
    p_sub.font.color.rgb = COLOR_DARK
    p_sub.space_before = Pt(14)

    # Thin line inside title card
    p_div = tf1.add_paragraph()
    p_div.text = "—" * 50
    p_div.font.size = Pt(10)
    p_div.font.color.rgb = COLOR_BORDER
    p_div.space_before = Pt(10)

    p_team = tf1.add_paragraph()
    p_team.text = "Candidate: Final-Year B.Tech / M.Tech Research Project | Department of Computer Science & Engineering"
    p_team.font.name = 'Arial'
    p_team.font.size = Pt(12)
    p_team.font.bold = True
    p_team.font.color.rgb = COLOR_BLACK
    p_team.space_before = Pt(10)

    p_inst = tf1.add_paragraph()
    p_inst.text = "Natural Language Processing & Cybersecurity Laboratory | Academic Year 2024–2025"
    p_inst.font.name = 'Arial'
    p_inst.font.size = Pt(11)
    p_inst.font.color.rgb = COLOR_MUTED
    p_inst.space_before = Pt(6)

    # =========================================================================
    # SLIDE 2: Roadmap (White Background, Black Font)
    # =========================================================================
    slide2 = prs.slides.add_slide(blank_layout)
    set_slide_white_bg(slide2, prs)
    add_header(slide2, "Roadmap", 2)

    roadmap_items = [
        ("01", "Problem & Objectives", "Shared context vulnerability, research motivation, and core defense goals."),
        ("02", "Proposed System", "Three-layer defense-in-depth architecture, containment, and trust boundaries."),
        ("03", "Methodology & Workflow", "NLP feature pipeline, vectorization, XML isolation, and runtime tool guard."),
        ("04", "Implementation & Demo", "Interactive Streamlit dashboard, dual-chatbot sandbox, and trace inspection."),
        ("05", "Results & Discussion", "Empirical benchmarking on 32 test vectors, ablation study, and word cloud."),
        ("06", "Conclusion & Future Work", "Summary of engineering contributions, threat mitigation, and future roadmap.")
    ]

    for idx, (num, title, desc) in enumerate(roadmap_items):
        col = idx % 2
        row = idx // 2
        x = Inches(1.0 + col * 5.8)
        y = Inches(1.6 + row * 1.8)
        
        box = slide2.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, Inches(5.5), Inches(1.5))
        box.fill.solid()
        box.fill.fore_color.rgb = COLOR_WHITE
        box.line.color.rgb = COLOR_BLACK
        box.line.width = Pt(1.5)
        
        tf = box.text_frame
        tf.word_wrap = True
        p1 = tf.paragraphs[0]
        p1.text = f"{num}.  {title}"
        p1.font.name = 'Arial'
        p1.font.size = Pt(13.5)
        p1.font.bold = True
        p1.font.color.rgb = COLOR_BLACK
        
        p2 = tf.add_paragraph()
        p2.text = desc
        p2.font.name = 'Arial'
        p2.font.size = Pt(10.5)
        p2.font.color.rgb = COLOR_DARK
        p2.space_before = Pt(6)

    # =========================================================================
    # SLIDE 3: Problem Statement
    # =========================================================================
    slide3 = prs.slides.add_slide(blank_layout)
    set_slide_white_bg(slide3, prs)
    add_header(slide3, "Problem Statement", 3)

    p_box = slide3.shapes.add_textbox(Inches(1.0), Inches(1.5), Inches(11.3), Inches(5.4))
    ptf = p_box.text_frame
    ptf.word_wrap = True

    p = ptf.paragraphs[0]
    p.text = "Why Prompt Injection Threatens Modern LLM Systems:"
    p.font.name = 'Arial'
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = COLOR_BLACK

    points = [
        ("Shared Instruction-Data Context:", "Foundation models (Llama, GPT, Qwen) concatenate developer directives, external documents, and user inputs into a single text stream. The model cannot inherently distinguish developer rules from attacker instructions."),
        ("Failure of Single-Point Defenses:", "Soft system prompt reminders ('Never reveal secrets') fail consistently against semantic paraphrasing, translation disguise, and persona overrides (e.g., DAN jailbreaks)."),
        ("The Model Self-Authorization Flaw:", "In agentic systems, LLMs directly select and execute tools. If an attacker injects a command like delete_sales_records(), an unprotected backend blindly executes the destructive database operation."),
        ("Indirect Document Injections in RAG:", "External retrieved contexts (emails, customer reviews, PDFs) can harbor hidden adversarial payloads that hijack the model during summarization without triggering input-level filters."),
        ("Latency & Cost of External Guardrails:", "Routing all prompts through secondary cloud neural networks (e.g., Llama Guard) doubles API token costs and adds 500ms–1500ms latency, making enterprise deployment impractical.")
    ]

    for title, desc in points:
        para = ptf.add_paragraph()
        r1 = para.add_run(f"•  {title} ")
        r1.font.bold = True
        r1.font.size = Pt(12)
        r1.font.color.rgb = COLOR_BLACK
        r2 = para.add_run(desc)
        r2.font.size = Pt(11.5)
        r2.font.color.rgb = COLOR_DARK
        para.space_before = Pt(9)

    # =========================================================================
    # SLIDE 4: Objectives and Outcomes
    # =========================================================================
    slide4 = prs.slides.add_slide(blank_layout)
    set_slide_white_bg(slide4, prs)
    add_header(slide4, "Objectives and Outcomes", 4)

    objs = [
        ("Build a Fast Three-Layer Defense Pipeline", "Implement a defense-in-depth framework combining local statistical NLP perimeter detection (Layer 1), contextual XML boundary isolation (Layer 2), and an independent runtime tool guard (Layer 3)."),
        ("Achieve Ultra-Low Latency Perimeter Filtering", "Train a sublinear TF-IDF + Logistic Regression detector executing in under 2 ms on local CPU ($0 API cost) to quarantine high-threat requests before reaching the cloud LLM."),
        ("Immunize RAG Workflows Against Indirect Injections", "Enclose untrusted retrieved documents within <UNTRUSTED_DOCUMENT> XML boundaries with explicit negative framing instructions to neutralize embedded overrides."),
        ("Eliminate Model Self-Authorization via Layer 3", "Deploy an independent backend runtime guard enforcing a strict read-only tool allowlist, parameter bounds, and SQL injection sanitization, completely preventing destructive execution."),
        ("Conduct Empirical Comparative Benchmarking", "Evaluate the framework across a standardized 32-case benchmark (7 threat categories) and demonstrate ASR reduction from 100% to 0% with low False Positive Rate (9.1%) on an interactive Streamlit dashboard.")
    ]

    for idx, (title, desc) in enumerate(objs):
        card = slide4.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(1.0), Inches(1.5 + idx * 1.1), Inches(11.3), Inches(0.95))
        card.fill.solid()
        card.fill.fore_color.rgb = COLOR_WHITE
        card.line.color.rgb = COLOR_BLACK
        card.line.width = Pt(1.2)
        
        ctf = card.text_frame
        ctf.word_wrap = True
        cp1 = ctf.paragraphs[0]
        r_tick = cp1.add_run("[✓]  ")
        r_tick.font.bold = True
        r_tick.font.color.rgb = COLOR_BLACK
        r_tick.font.size = Pt(12)
        
        r_title = cp1.add_run(f"{title}: ")
        r_title.font.bold = True
        r_title.font.size = Pt(12)
        r_title.font.color.rgb = COLOR_BLACK
        
        r_desc = cp1.add_run(desc)
        r_desc.font.size = Pt(11)
        r_desc.font.color.rgb = COLOR_DARK

    # =========================================================================
    # SLIDE 5: Proposed System Architecture
    # =========================================================================
    slide5 = prs.slides.add_slide(blank_layout)
    set_slide_white_bg(slide5, prs)
    add_header(slide5, "Proposed System Architecture", 5)

    arch_table_shape = slide5.shapes.add_table(5, 3, Inches(1.0), Inches(1.6), Inches(11.3), Inches(5.0))
    at = arch_table_shape.table
    at.columns[0].width = Inches(2.3)
    at.columns[1].width = Inches(5.4)
    at.columns[2].width = Inches(3.6)

    table_data = [
        ["Pipeline Stage", "What Happens in PromptShield AI", "Technical Component / Example"],
        ["Stage 1: Ingestion & Perimeter Scan", "Receives user prompt and optional retrieved context. Extracts (1,2) n-grams and computes continuous risk probability P(Malicious | Text). Blocks high-risk attacks (>=0.70) in 1.8 ms.", "Layer 1: TF-IDF (1,2) Vectorizer + Logistic Regression (C=2.5) on local CPU."],
        ["Stage 2: Semantic XML Framing", "Separates system instructions from user inputs. Encloses external retrieved documents within <UNTRUSTED_DOCUMENT> boundaries with explicit non-override directives.", "Layer 2: Groq API (qwen/qwen3.8-27b) with XML prompt delimiter wrapper."],
        ["Stage 3: LLM Generation", "Model processes user inquiry under strict persona and boundary rules. Generates structured JSON tool calls if database analytics are required.", 'Output: {"tool": "get_sales_summary", "args": {"year": 2024}}'],
        ["Stage 4: Runtime Guard & Dispatch", "Independent backend controller inspects requested tool against an allowlist, checks parameter typing, and sanitizes SQL injection markers before executing read-only mock data.", "Layer 3: ToolAuthorizationGuard with in-memory Mock Sales Database."]
    ]

    for r_idx, row in enumerate(table_data):
        for c_idx, val in enumerate(row):
            cell = at.cell(r_idx, c_idx)
            cell.text = val

    style_monochrome_table(at)

    # =========================================================================
    # SLIDE 6: Dataset and Tools
    # =========================================================================
    slide6 = prs.slides.add_slide(blank_layout)
    set_slide_white_bg(slide6, prs)
    add_header(slide6, "Dataset and Experimental Tools", 6)

    # Left: Dataset Card
    card_ds = slide6.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(1.0), Inches(1.6), Inches(5.4), Inches(5.2))
    card_ds.fill.solid()
    card_ds.fill.fore_color.rgb = COLOR_WHITE
    card_ds.line.color.rgb = COLOR_BLACK
    card_ds.line.width = Pt(1.5)
    dtf = card_ds.text_frame
    dtf.word_wrap = True

    dp = dtf.paragraphs[0]
    dp.text = "Datasets and Benchmarks"
    dp.font.bold = True
    dp.font.size = Pt(13.5)
    dp.font.color.rgb = COLOR_BLACK

    ds_points = [
        ("Training Dataset (demo_dataset.csv):", "80 balanced samples (40 Benign, 40 Malicious). Explicit 80/20 train/test split to prevent data leakage."),
        ("Grounding:", "Derived from OWASP Top 10 for LLM Applications (LLM01: Prompt Injection) and enterprise sales reporting scenarios."),
        ("Benchmark Suite (test_cases.json):", "32 standardized test cases across 7 categories: Direct Injections, Overrides, Canary Leaks, Indirect Injections, Unauthorized Tools, Benign Queries, and Borderline Ambiguous Inputs."),
        ("Mock Enterprise Database:", "Synthetic enterprise software sales records across 4 global regions, 5 products, and historical financial metrics (2024–2025).")
    ]
    for h, b in ds_points:
        p = dtf.add_paragraph()
        r1 = p.add_run(f"• {h} ")
        r1.font.bold = True
        r1.font.size = Pt(10.5)
        r2 = p.add_run(b)
        r2.font.size = Pt(10)
        p.space_before = Pt(8)

    # Right: Tools Card
    card_tl = slide6.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(6.9), Inches(1.6), Inches(5.4), Inches(5.2))
    card_tl.fill.solid()
    card_tl.fill.fore_color.rgb = COLOR_WHITE
    card_tl.line.color.rgb = COLOR_BLACK
    card_tl.line.width = Pt(1.5)
    ttf = card_tl.text_frame
    ttf.word_wrap = True

    tp = ttf.paragraphs[0]
    tp.text = "Software Stack and Environment"
    tp.font.bold = True
    tp.font.size = Pt(13.5)
    tp.font.color.rgb = COLOR_BLACK

    tools_points = [
        ("Language & Core Runtime:", "Python 3.11 on consumer hardware (No dedicated GPU required)."),
        ("Machine Learning & NLP:", "scikit-learn (TfidfVectorizer, LogisticRegression), joblib, wordcloud, regular expressions (re)."),
        ("LLM Inference Engine:", "Groq Cloud API running qwen/qwen3.8-27b with LPU ultra-low latency acceleration + Fallback Research Simulator."),
        ("User Interface:", "Streamlit 1.66+ multi-page application with clean, high-contrast security dashboard views."),
        ("Database & Logging:", "Persistent SQLite3 database (promptshield.db) recording forensic event logs with CSV export."),
        ("Testing & Verification:", "pytest test suite comprising 14 automated unit tests verifying all security layers.")
    ]
    for h, b in tools_points:
        p = ttf.add_paragraph()
        r1 = p.add_run(f"• {h} ")
        r1.font.bold = True
        r1.font.size = Pt(10.5)
        r2 = p.add_run(b)
        r2.font.size = Pt(10)
        p.space_before = Pt(8)

    # =========================================================================
    # SLIDE 7: Methodology
    # =========================================================================
    slide7 = prs.slides.add_slide(blank_layout)
    set_slide_white_bg(slide7, prs)
    add_header(slide7, "Defense Methodology", 7)

    steps = [
        ("1", "User Query & Context Ingestion", "Receives raw user inquiry along with optional untrusted document context (emails, customer feedback, RAG chunks)."),
        ("2", "Layer 1 NLP Perimeter Scan", "Extracts sublinear (1,2) n-grams. Logistic Regression evaluates P(Malicious | Text). High-threat inputs (>=0.70) are blocked in 1.8 ms at $0 cost."),
        ("3", "Layer 2 Contextual XML Enclosure", "Allowed inputs are framed with role separation. External documents are wrapped inside <UNTRUSTED_DOCUMENT> tags with strict non-override meta-prompts."),
        ("4", "Layer 3 Runtime Tool Authorization", "If LLM requests tool execution, Layer 3 intercepts the request. Validates tool against allowlist, sanitizes parameters, and blocks SQL/command injections."),
        ("5", "Safe Fulfillment & Forensic Logging", "Safe read-only mock data is returned to the user. Every transaction, risk score, and tool outcome is persisted into SQLite database.")
    ]

    for idx, (num, title, desc) in enumerate(steps):
        x = Inches(0.8 + idx * 2.4)
        y = Inches(1.8)
        
        # Monochrome number box
        circle = slide7.shapes.add_shape(MSO_SHAPE.RECTANGLE, x + Inches(0.65), y, Inches(1.0), Inches(0.9))
        circle.fill.solid()
        circle.fill.fore_color.rgb = COLOR_BLACK
        circle.line.fill.background()
        cp = circle.text_frame.paragraphs[0]
        cp.text = num
        cp.font.name = 'Arial'
        cp.font.size = Pt(18)
        cp.font.bold = True
        cp.font.color.rgb = COLOR_WHITE
        cp.alignment = PP_ALIGN.CENTER
        
        # Card below
        card = slide7.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y + Inches(1.1), Inches(2.3), Inches(3.8))
        card.fill.solid()
        card.fill.fore_color.rgb = COLOR_WHITE
        card.line.color.rgb = COLOR_BLACK
        card.line.width = Pt(1.2)
        
        tf = card.text_frame
        tf.word_wrap = True
        p1 = tf.paragraphs[0]
        p1.text = title
        p1.font.bold = True
        p1.font.size = Pt(11)
        p1.font.color.rgb = COLOR_BLACK
        p1.alignment = PP_ALIGN.CENTER
        
        p2 = tf.add_paragraph()
        p2.text = desc
        p2.font.size = Pt(9.5)
        p2.font.color.rgb = COLOR_DARK
        p2.space_before = Pt(8)

    # =========================================================================
    # SLIDE 8: Workflow of the Three-Layer Defense System
    # =========================================================================
    slide8 = prs.slides.add_slide(blank_layout)
    set_slide_white_bg(slide8, prs)
    add_header(slide8, "Workflow of the Three-Layer Defense System", 8)

    stages = [
        ("1. Input", "Prompt / Context", "User sends prompt + external text"),
        ("2. Tokenizer", "TF-IDF Vectorizer", "Extracts unigrams & bigrams"),
        ("3. Classifier", "Logistic Reg.", "Estimates risk: P(Malicious | x)"),
        ("4. Perimeter", "Policy Decision", "ALLOW (<0.4), REVIEW, or BLOCK (>=0.7)"),
        ("5. Context", "XML Delimiters", "<UNTRUSTED_DOCUMENT> wrapping"),
        ("6. Inference", "Groq Qwen-27B", "Generates answer or JSON tool call"),
        ("7. Guard", "Tool Allowlist", "Enforces parameter bounds & RBAC"),
        ("8. Output", "Streamlit & SQLite", "Safe response + audit event logged")
    ]

    for idx, (stg, sub, act) in enumerate(stages):
        x = Inches(0.6 + idx * 1.5)
        box = slide8.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, Inches(1.8), Inches(1.4), Inches(3.4))
        box.fill.solid()
        box.fill.fore_color.rgb = COLOR_WHITE
        box.line.color.rgb = COLOR_BLACK
        box.line.width = Pt(1.2)
            
        tf = box.text_frame
        tf.word_wrap = True
        p1 = tf.paragraphs[0]
        p1.text = stg
        p1.font.bold = True
        p1.font.size = Pt(10.5)
        p1.font.color.rgb = COLOR_BLACK
        
        p2 = tf.add_paragraph()
        p2.text = sub
        p2.font.bold = True
        p2.font.size = Pt(9)
        p2.font.color.rgb = COLOR_DARK
        p2.space_before = Pt(4)
        
        p3 = tf.add_paragraph()
        p3.text = act
        p3.font.size = Pt(8.5)
        p3.font.color.rgb = COLOR_MUTED
        p3.space_before = Pt(6)

    env_box = slide8.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.6), Inches(5.6), Inches(12.1), Inches(1.2))
    env_box.fill.solid()
    env_box.fill.fore_color.rgb = COLOR_LIGHT_BG
    env_box.line.color.rgb = COLOR_BLACK
    env_box.line.width = Pt(1.2)
    env_tf = env_box.text_frame
    env_p = env_tf.paragraphs[0]
    env_p.text = "Decoupled Execution Environment: Real-Time Protection with Minimal Latency Overhead"
    env_p.font.bold = True
    env_p.font.size = Pt(11)
    env_p.font.color.rgb = COLOR_BLACK
    env_p.alignment = PP_ALIGN.CENTER
    
    env_p2 = env_tf.add_paragraph()
    env_p2.text = "• Layer 1 operates locally on CPU in ~1.8 ms ($0 token cost)  • Layer 2 prevents indirect prompt injection\n• Layer 3 ensures zero unauthorized database or shell execution  • Full transparency and persistent SQLite forensic audit trail."
    env_p2.font.size = Pt(9.5)
    env_p2.font.color.rgb = COLOR_DARK
    env_p2.alignment = PP_ALIGN.CENTER
    env_p2.space_before = Pt(4)

    # =========================================================================
    # SLIDE 9: Implementation and Demo — Shielded Chatbot View
    # =========================================================================
    slide9 = prs.slides.add_slide(blank_layout)
    set_slide_white_bg(slide9, prs)
    add_header(slide9, "Implementation and Demo: Shielded Chatbot View", 9)

    left_w = slide9.shapes.add_textbox(Inches(1.0), Inches(1.5), Inches(5.8), Inches(5.3))
    ltf = left_w.text_frame
    ltf.word_wrap = True
    lp1 = ltf.paragraphs[0]
    lp1.text = "Key Interactive Features to Point Out:"
    lp1.font.bold = True
    lp1.font.size = Pt(13.5)
    lp1.font.color.rgb = COLOR_BLACK

    points_demo1 = [
        ("Full Multi-Turn Dialogue:", "Real-time conversation history supporting enterprise software sales queries and consultative analytics."),
        ("Real-Time Security Inspection Trace:", "Every assistant message includes an expandable inspection panel displaying the exact decision made by Layer 1, Layer 2, and Layer 3."),
        ("Layer 1 Risk Diagnostics:", "Displays calibrated statistical risk score (0%–100%), threat level (LOW/MEDIUM/HIGH), perimeter policy (ALLOW/REVIEW/BLOCK), and contributing n-gram feature weights."),
        ("Ablation Study Toggles:", "Sidebar controls allow live toggling between Full Three-Layer Defense, Layers 1+2, and Layer 1 Only to demonstrate individual layer impact."),
        ("Execution Engine Badge:", "Explicitly badges whether the response came from the live Groq API (qwen/qwen3.8-27b) or local simulation.")
    ]
    for h, b in points_demo1:
        p = ltf.add_paragraph()
        r1 = p.add_run(f"• {h} ")
        r1.font.bold = True
        r1.font.size = Pt(10.5)
        r2 = p.add_run(b)
        r2.font.size = Pt(10)
        p.space_before = Pt(8)

    # Embed Figure 4.3 (Word Cloud) on right as preview graphic
    fig3_path = FIGURES_DIR / "fig_4_3_threat_wordcloud.png"
    if fig3_path.exists():
        slide9.shapes.add_picture(str(fig3_path), Inches(7.2), Inches(1.6), Inches(5.2))
        cap_box = slide9.shapes.add_textbox(Inches(7.2), Inches(5.4), Inches(5.2), Inches(0.8))
        cp = cap_box.text_frame.paragraphs[0]
        cp.text = "Figure: Adversarial threat vocabulary intercepted by Layer 1 perimeter detector."
        cp.font.italic = True
        cp.font.size = Pt(9.5)
        cp.font.color.rgb = COLOR_MUTED
        cp.alignment = PP_ALIGN.CENTER

    # =========================================================================
    # SLIDE 10: Implementation and Demo — Comparison & Evaluation Dashboard
    # =========================================================================
    slide10 = prs.slides.add_slide(blank_layout)
    set_slide_white_bg(slide10, prs)
    add_header(slide10, "Implementation and Demo: Evaluation Dashboard", 10)

    # Embed Figure 4.1 on left
    fig1_path = FIGURES_DIR / "fig_4_1_asr_fpr_comparison.png"
    if fig1_path.exists():
        slide10.shapes.add_picture(str(fig1_path), Inches(1.0), Inches(1.6), Inches(5.4))
        cap_b = slide10.shapes.add_textbox(Inches(1.0), Inches(5.5), Inches(5.4), Inches(0.6))
        cp = cap_b.text_frame.paragraphs[0]
        cp.text = "Figure: Comparative Attack Success Rate (ASR) vs False Positive Rate (FPR)"
        cp.font.bold = True
        cp.font.size = Pt(9.5)
        cp.font.color.rgb = COLOR_BLACK
        cp.alignment = PP_ALIGN.CENTER

    # Right text
    rt_box = slide10.shapes.add_textbox(Inches(6.8), Inches(1.5), Inches(5.5), Inches(5.3))
    rtf = rt_box.text_frame
    rtf.word_wrap = True
    rp1 = rtf.paragraphs[0]
    rp1.text = "Evaluation Dashboard Capabilities:"
    rp1.font.bold = True
    rp1.font.size = Pt(13.5)
    rp1.font.color.rgb = COLOR_BLACK

    points_demo2 = [
        ("Automated 32-Case Benchmark:", "Executes standardized test vectors covering all 7 attack categories across both chatbots in under 1 second."),
        ("Empirical Security Metrics:", "Dynamically calculates Attack Success Rate (ASR), False Positive Rate (FPR), Benign Task Success Rate, and Unauthorized Tool Execution Rate."),
        ("Interactive Plotly Visualizations:", "Renders grouped bar charts comparing security postures, precision/recall curves, and latency trade-offs."),
        ("Ablation Study Matrix:", "Empirically benchmarks Config A (L1), Config B (L1+L2), and Config C (L1+L2+L3) on identical test data."),
        ("Forensic Export:", "Filterable outcomes table with one-click CSV export for external academic verification.")
    ]
    for h, b in points_demo2:
        p = rtf.add_paragraph()
        r1 = p.add_run(f"• {h} ")
        r1.font.bold = True
        r1.font.size = Pt(10.5)
        r2 = p.add_run(b)
        r2.font.size = Pt(10)
        p.space_before = Pt(8)

    # =========================================================================
    # SLIDE 11: Results and Empirical Benchmarks
    # =========================================================================
    slide11 = prs.slides.add_slide(blank_layout)
    set_slide_white_bg(slide11, prs)
    add_header(slide11, "Experimental Results and Performance Comparison", 11)

    res_table_shape = slide11.shapes.add_table(5, 6, Inches(1.0), Inches(1.5), Inches(11.3), Inches(3.8))
    rt = res_table_shape.table
    rt.columns[0].width = Inches(2.8)
    rt.columns[1].width = Inches(1.7)
    rt.columns[2].width = Inches(1.7)
    rt.columns[3].width = Inches(1.7)
    rt.columns[4].width = Inches(1.7)
    rt.columns[5].width = Inches(1.7)

    res_data = [
        ["Configuration", "ASR (%) [↓]", "FPR (%) [↓]", "Benign Success [↑]", "Recall (L1) [↑]", "Avg Latency"],
        ["Vulnerable Baseline", "100.0%", "0.0%", "100.0%", "0.000", "450.0 ms"],
        ["Config A (Layer 1 Only)", "31.8%", "9.1%", "90.9%", "0.933", "1.8 ms"],
        ["Config B (Layers 1 + 2)", "9.1%", "9.1%", "90.9%", "0.933", "485.0 ms"],
        ["PromptShield AI (Full L1+L2+L3)", "0.0%", "9.1%", "90.9%", "0.933", "488.5 ms"]
    ]

    for r_idx, row in enumerate(res_data):
        for c_idx, val in enumerate(row):
            cell = rt.cell(r_idx, c_idx)
            cell.text = val

    style_monochrome_table(rt)

    callout_box = slide11.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(1.0), Inches(5.6), Inches(11.3), Inches(1.3))
    callout_box.fill.solid()
    callout_box.fill.fore_color.rgb = COLOR_LIGHT_BG
    callout_box.line.color.rgb = COLOR_BLACK
    callout_box.line.width = Pt(1.2)
    ctf = callout_box.text_frame
    cp = ctf.paragraphs[0]
    cp.text = "Key Empirical Highlights:"
    cp.font.bold = True
    cp.font.size = Pt(11)
    cp.font.color.rgb = COLOR_BLACK
    
    cp2 = ctf.add_paragraph()
    cp2.text = "• 100% Attack Elimination: Attack Success Rate dropped from 100% to 0.0% in the complete pipeline.\n• High Utility Preservation: 90.9% of benign business queries passed successfully without false rejection.\n• Negligible Latency Overhead: Layer 1 runs in 1.8 ms on local CPU, adding only ~38.5 ms total pipeline overhead."
    cp2.font.size = Pt(10)
    cp2.font.color.rgb = COLOR_DARK
    cp2.space_before = Pt(4)

    # =========================================================================
    # SLIDE 12: Challenges and Solutions
    # =========================================================================
    slide12 = prs.slides.add_slide(blank_layout)
    set_slide_white_bg(slide12, prs)
    add_header(slide12, "Challenges and Engineering Solutions", 12)

    chal_table_shape = slide12.shapes.add_table(4, 3, Inches(1.0), Inches(1.6), Inches(11.3), Inches(5.0))
    ct = chal_table_shape.table
    ct.columns[0].width = Inches(2.5)
    ct.columns[1].width = Inches(4.3)
    ct.columns[2].width = Inches(4.5)

    chal_data = [
        ["Identified Challenge", "Observed Security / Technical Issue", "Implemented Engineering Approach"],
        ["Paraphrased & Novel Injections", "Attackers substitute synonyms ('disregard prior guidelines'), completely evading traditional keyword and regex blocklists (Recall = 60.0%).", "Sublinear TF-IDF (1,2) n-grams + L2-regularized Logistic Regression, achieving 93.3% recall and capturing syntactic token patterns."],
        ["Indirect Context Poisoning (RAG)", "Adversarial instructions hidden inside retrieved customer reviews or supplier PDFs hijacked the model, bypassing perimeter prompt filters.", "Layer 2 contextual isolation: wrapping external documents within <UNTRUSTED_DOCUMENT> XML tags with negative framing meta-prompts."],
        ["Model Self-Authorization Flaw", "LLMs directly choosing and executing backend tools can be tricked into dropping database tables or running arbitrary shell commands.", "Layer 3 independent runtime guard: deterministic allowlisting and parameter typing in Python; the LLM has zero execution authority."]
    ]

    for r_idx, row in enumerate(chal_data):
        for c_idx, val in enumerate(row):
            cell = ct.cell(r_idx, c_idx)
            cell.text = val

    style_monochrome_table(ct)

    # =========================================================================
    # SLIDE 13: Conclusion and Future Work
    # =========================================================================
    slide13 = prs.slides.add_slide(blank_layout)
    set_slide_white_bg(slide13, prs)
    add_header(slide13, "Conclusion and Future Work", 13)

    # Left: Conclusion
    c_card = slide13.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(1.0), Inches(1.6), Inches(5.4), Inches(5.2))
    c_card.fill.solid()
    c_card.fill.fore_color.rgb = COLOR_WHITE
    c_card.line.color.rgb = COLOR_BLACK
    c_card.line.width = Pt(1.5)
    c_tf = c_card.text_frame
    c_tf.word_wrap = True

    cp1 = c_tf.paragraphs[0]
    cp1.text = "Key Conclusions"
    cp1.font.bold = True
    cp1.font.size = Pt(13.5)
    cp1.font.color.rgb = COLOR_BLACK

    c_points = [
        ("Effective Multi-Layer Defense:", "Demonstrated that defense-in-depth reduces Attack Success Rate from 100% to 0.0% on benchmark attacks without relying solely on system prompts."),
        ("Lightweight Perimeter Protection:", "Layer 1 NLP statistical detector achieves a 0.933 F1-score and runs in ~1.8 ms on CPU, shielding cloud LLM APIs from token-exhaustion denial-of-wallet attacks."),
        ("Elimination of Execution Risk:", "Proved that decoupling LLM reasoning from tool execution authority guarantees zero arbitrary database destruction even under full model jailbreak."),
        ("Utility Preservation:", "Maintained a 90.9% benign task success rate with only 9.1% false-positive rate, proving high commercial practicality.")
    ]
    for h, b in c_points:
        p = c_tf.add_paragraph()
        r1 = p.add_run(f"• {h} ")
        r1.font.bold = True
        r1.font.size = Pt(10.5)
        r2 = p.add_run(b)
        r2.font.size = Pt(10)
        p.space_before = Pt(8)

    # Right: Future Work
    f_card = slide13.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(6.9), Inches(1.6), Inches(5.4), Inches(5.2))
    f_card.fill.solid()
    f_card.fill.fore_color.rgb = COLOR_WHITE
    f_card.line.color.rgb = COLOR_BLACK
    f_card.line.width = Pt(1.5)
    f_tf = f_card.text_frame
    f_tf.word_wrap = True

    fp1 = f_tf.paragraphs[0]
    fp1.text = "Future Enhancements"
    fp1.font.bold = True
    fp1.font.size = Pt(13.5)
    fp1.font.color.rgb = COLOR_BLACK

    f_points = [
        ("Dense Semantic Embeddings:", "Integrate lightweight sentence-transformer embedding models alongside TF-IDF to further enhance evasion resistance against adversarial character perturbations."),
        ("Dynamic Honeypot Canaries:", "Implement automated per-session canary rotation and canary fingerprinting to detect leaked context across distributed agent pipelines."),
        ("Automated Red-Teaming Feedback Loop:", "Incorporate reinforcement learning from adversarial feedback (RLAF) to continuously discover and inject evolving jailbreak templates."),
        ("Multi-Modal Prompt Injection Guards:", "Extend Layer 1 perimeter filtering to screen adversarial OCR images, audio streams, and document attachments.")
    ]
    for h, b in f_points:
        p = f_tf.add_paragraph()
        r1 = p.add_run(f"• {h} ")
        r1.font.bold = True
        r1.font.size = Pt(10.5)
        r2 = p.add_run(b)
        r2.font.size = Pt(10)
        p.space_before = Pt(8)

    # =========================================================================
    # SLIDE 14: References
    # =========================================================================
    slide14 = prs.slides.add_slide(blank_layout)
    set_slide_white_bg(slide14, prs)
    add_header(slide14, "References", 14)

    ref_box = slide14.shapes.add_textbox(Inches(1.0), Inches(1.5), Inches(11.3), Inches(5.3))
    rtf = ref_box.text_frame
    rtf.word_wrap = True

    refs = [
        "[1] OWASP Foundation, 'OWASP Top 10 for Large Language Model Applications: LLM01: Prompt Injection,' Technical Report, 2023.",
        "[2] K. Greshake, R. Abdelnabi, S. Mishra, C. Endres, T. Holz, and M. Fritz, 'Not What You've Signed Up For: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection,' ACM Workshop on AISec, 2023.",
        "[3] F. Perez and I. Ribeiro, 'Ignore Previous Instructions: Illegal System Access via Prompt Injection Attacks,' arXiv preprint arXiv:2211.09527, 2022.",
        "[4] F. Pedregosa et al., 'Scikit-learn: Machine Learning in Python,' Journal of Machine Learning Research (JMLR), vol. 12, pp. 2825-2830, 2011.",
        "[5] H. Inan et al., 'Llama Guard: LLM-based Input-Output Safeguard for Human-AI Conversations,' Meta AI Technical Report, arXiv preprint arXiv:2312.06674, 2023.",
        "[6] J. Wei et al., 'Jailbroken: How Does LLM Safety Training Fail?' Advances in Neural Information Processing Systems (NeurIPS), 2024.",
        "[7] Streamlit Team, 'Streamlit: The Fastest Way to Build Data Apps,' Snowflake Inc., 2024."
    ]

    for idx, ref in enumerate(refs):
        p = rtf.paragraphs[0] if idx == 0 else rtf.add_paragraph()
        p.text = ref
        p.font.name = 'Arial'
        p.font.size = Pt(11)
        p.font.color.rgb = COLOR_BLACK
        p.space_before = Pt(8)

    # =========================================================================
    # SLIDE 15: Thank You Slide (Pure White Background, Black Font)
    # =========================================================================
    slide15 = prs.slides.add_slide(blank_layout)
    set_slide_white_bg(slide15, prs)

    # Clean framing border
    frame15 = slide15.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(0.8), Inches(11.733), Inches(5.9))
    frame15.fill.solid()
    frame15.fill.fore_color.rgb = COLOR_WHITE
    frame15.line.color.rgb = COLOR_BLACK
    frame15.line.width = Pt(2.0)

    tb15 = slide15.shapes.add_textbox(Inches(1.5), Inches(1.8), Inches(10.3), Inches(4.0))
    tf15 = tb15.text_frame
    tf15.word_wrap = True

    p_ty = tf15.paragraphs[0]
    p_ty.text = "Thank You!"
    p_ty.font.name = 'Arial'
    p_ty.font.size = Pt(44)
    p_ty.font.bold = True
    p_ty.font.color.rgb = COLOR_BLACK
    p_ty.alignment = PP_ALIGN.CENTER

    p_q = tf15.add_paragraph()
    p_q.text = "Questions & Discussion"
    p_q.font.name = 'Arial'
    p_q.font.size = Pt(22)
    p_q.font.bold = True
    p_q.font.color.rgb = COLOR_DARK
    p_q.alignment = PP_ALIGN.CENTER
    p_q.space_before = Pt(14)

    p_div2 = tf15.add_paragraph()
    p_div2.text = "—" * 40
    p_div2.font.size = Pt(10)
    p_div2.font.color.rgb = COLOR_BORDER
    p_div2.alignment = PP_ALIGN.CENTER
    p_div2.space_before = Pt(10)

    p_tm = tf15.add_paragraph()
    p_tm.text = "PromptShield AI: A Three-Layer Prompt Injection Framework\nFinal-Year B.Tech / M.Tech Research Project Defense"
    p_tm.font.name = 'Arial'
    p_tm.font.size = Pt(13)
    p_tm.font.color.rgb = COLOR_BLACK
    p_tm.alignment = PP_ALIGN.CENTER
    p_tm.space_before = Pt(14)

    prs.save(str(PPTX_OUT))
    print(f"Successfully generated pure white & black PowerPoint presentation at: {PPTX_OUT}")

if __name__ == "__main__":
    create_presentation()
