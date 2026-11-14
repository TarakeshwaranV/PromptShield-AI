# PromptShield AI: A Three-Layer Prompt Injection Detection and Prevention Framework for LLM Applications

[![Python Version](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-red.svg)](https://streamlit.io)
[![scikit-learn](https://img.shields.io/badge/NLP-scikit--learn-orange.svg)](https://scikit-learn.org)
[![Database](https://img.shields.io/badge/Database-SQLite3-lightgrey.svg)](https://sqlite.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**PromptShield AI** is a runnable final-year engineering and research web application that investigates whether combining **NLP-based prompt injection detection**, **contextual LLM defense boundaries**, and **independent runtime authorization** can reduce attack success while preserving legitimate chatbot functionality.

---

## 📑 Table of Contents
- [1. Project Overview & Research Objectives](#1-project-overview--research-objectives)
- [2. System Architecture](#2-system-architecture)
- [3. The Three Defense Layers](#3-the-three-defense-layers)
- [4. Repository Structure](#4-repository-structure)
- [5. Installation & Quick Start](#5-installation--quick-start)
- [6. Application Pages & Workflow](#6-application-pages--workflow)
- [7. Benchmark Test Suite & Security Metrics](#7-benchmark-test-suite--security-metrics)
- [8. Running Automated Unit Tests](#8-running-automated-unit-tests)
- [9. Dataset Provenance & Model Retraining](#9-dataset-provenance--model-retraining)
- [10. Limitations & Defense-in-Depth Philosophy](#10-limitations--defense-in-depth-philosophy)

---

## 1. Project Overview & Research Objectives

Large Language Models (LLMs) deployed with tool access or Retrieval-Augmented Generation (RAG) are susceptible to **prompt injection** — attacks where malicious inputs or poisoned retrieved context redirect the model's objective, extract confidential configuration secrets (canaries/API keys), or trigger unauthorized actions.

This project implements and evaluates an interactive dual-system research harness:
1. **Shielded Chatbot:** Protected by our Three-Layer Defense Pipeline.
2. **Vulnerable Chatbot:** An intentionally weakened, sandboxed chatbot demonstrating vulnerability outcomes when defenses are absent.
3. **Comparison & Evaluation Dashboard:** Executes an empirical 32-case benchmark across four configurations (Vulnerable Baseline, Ablation A [L1 only], Ablation B [L1+L2], and Shielded Full [L1+L2+L3]) and computes security metrics from actual recorded outcomes.

---

## 2. System Architecture

```
                    [Incoming Request (User Prompt + External Doc)]
                                          │
                                          ▼
    ┌────────────────────────────────────────────────────────────────────────┐
    │ 🛡️ LAYER 1: NLP Prompt Injection Perimeter Detector                   │
    │ - TF-IDF (1,2 n-grams) Vectorizer + Logistic Regression Classifier      │
    │ - Parallel Heuristic Pattern Comparator                                │
    │ - Policy: ALLOW (<0.40) | REVIEW (0.40 - 0.70) | BLOCK (>=0.70)        │
    └────────────────────────────────────┬───────────────────────────────────┘
                                         │ (Passed or Review)
                                         ▼
    ┌────────────────────────────────────────────────────────────────────────┐
    │ 🔒 LAYER 2: Contextual LLM Defense                                     │
    │ - System directive isolation & strict role tracking                    │
    │ - XML untrusted data boundaries: <UNTRUSTED_DOCUMENT>                  │
    │ - Synthetic canary protection & structured JSON tool generation        │
    └────────────────────────────────────┬───────────────────────────────────┘
                                         │
                                         ▼
    ┌────────────────────────────────────────────────────────────────────────┐
    │ ⚖️ LAYER 3: Independent Runtime Authorization Guard                     │
    │ - Tool Allowlist: get_sales_summary, get_sales_by_month, etc.          │
    │ - Parameter Sanitization & Bounds Checking                             │
    │ - Zero arbitrary SQL or host shell command execution                   │
    └────────────────────────────────────┬───────────────────────────────────┘
                                         │
                                         ▼
                        [Safe Response & Audited Output]
```

---

## 3. The Three Defense Layers

### Layer 1: NLP Prompt Injection Perimeter Detector
- **Technology:** TF-IDF feature extraction with sublinear term frequency coupled with a balanced Logistic Regression classifier.
- **Role:** Fast, pre-LLM statistical screening (< 2ms) that computes an estimated risk score and extracts influential n-gram tokens.
- **Heuristic Baseline:** Parallel regex signature scanner comparing ML generalization against classic pattern matching.
- **Scanning:** Inspects both incoming user text and retrieved context documents.

### Layer 2: Contextual LLM Defense
- **Technology:** Groq API (`llama-3.3-70b-versatile`) with graceful fallback to a high-fidelity educational simulation.
- **Role:** Formats prompts with explicit architectural boundaries. External retrieved documents are isolated within `<UNTRUSTED_DOCUMENT>` XML tags accompanied by defensive instructions that prevent documents from overriding application directives.

### Layer 3: Independent Runtime Authorization Guard
- **Technology:** Deterministic Python controller fronting an in-memory mock enterprise sales database.
- **Role:** The LLM is **never permitted to authorize its own actions**. The guard independently enforces:
  1. Strict tool allowlist.
  2. Strict argument typing and SQL/command injection filtering.
  3. Automatic interception and rejection of unapproved tools (`delete_sales_records`, `os_system_shell`, `execute_raw_sql`).

---

## 4. Repository Structure

```
promptshield-ai/
├── app.py                      # Main landing dashboard & live perimeter scanner
├── config.py                   # System thresholds, canary tokens, and tool specs
├── requirements.txt            # Python dependencies
├── .env.example                # Groq API configuration template
├── .gitignore                  # Git ignore rules
├── README.md                   # Complete academic documentation
├── core/
│   ├── __init__.py
│   ├── database.py             # SQLite persistence for logs and evaluation runs
│   ├── detector.py             # Layer 1 NLP classifier & heuristic comparator
│   ├── evaluator.py            # Evaluation benchmark engine & metric calculators
│   ├── llm_client.py           # Layer 2 Groq client & research demo simulation
│   ├── logging_utils.py        # Centralized security audit logging
│   ├── mock_sales.py           # Safe mock enterprise sales database
│   ├── shielded_pipeline.py    # 3-Layer shielded pipeline & ablation manager
│   ├── tool_guard.py           # Layer 3 runtime authorization guard
│   ├── ui_components.py        # Dark Navy theme styling & badge renderers
│   └── vulnerable_sandbox.py   # Isolated intentionally weakened sandbox
├── data/
│   ├── demo_dataset.csv        # Labeled NLP dataset (benign vs injection)
│   ├── test_cases.json         # 32 benchmark security test cases (7 categories)
│   └── sample_evaluation_export.csv # Pre-generated sample evaluation export
├── models/
│   └── tfidf_detector.joblib   # Serialized trained TF-IDF & Logistic Regression model
├── pages/
│   ├── 1_Shielded_Chatbot.py   # Interactive shielded assistant with security traces
│   ├── 2_Vulnerable_Chatbot.py # Sandboxed vulnerable assistant with exploit tests
│   ├── 3_Comparison_Evaluation.py # Benchmarking dashboard, ablation, & Plotly charts
│   ├── 4_Security_Logs.py      # SQLite audit log explorer with CSV export
│   └── 5_About.py              # Academic report, architecture, dataset, & limitations
└── tests/
    ├── __init__.py
    ├── test_detector.py        # Layer 1 unit tests
    ├── test_evaluator.py       # Metrics & secret isolation unit tests
    └── test_tool_guard.py      # Layer 3 allowlist & argument validation unit tests
```

---

## 5. Installation & Quick Start

### Prerequisites
- Python 3.11 installed.

### Option A: Windows PowerShell Setup

```powershell
# 1. Clone or navigate to the repository directory
cd "c:\path\to\promptshield-ai"

# 2. (Optional) Create and activate a virtual environment
py -3.11 -m venv venv
.\venv\Scripts\Activate.ps1

# 3. Install required dependencies
py -3.11 -m pip install -r requirements.txt

# 4. (Optional) Set your Groq API key in .env (if absent, app runs in SIMULATED DEMO MODE)
Copy-Item .env.example .env
# Edit .env and enter your key: GROQ_API_KEY=gsk_...

# 5. Launch the Streamlit application
py -3.11 -m streamlit run app.py
```

### Option B: macOS / Linux Setup

```bash
# 1. Navigate to directory
cd /path/to/promptshield-ai

# 2. Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Optional API key setup
cp .env.example .env

# 5. Launch application
streamlit run app.py
```

*Note: The application automatically initializes its SQLite database and fits the NLP classifier on first boot.*

---

## 6. Application Pages & Workflow

1. **Main Dashboard (`app.py`):** System health metrics, architecture overview, and an interactive live Layer 1 perimeter scanner.
2. **Shielded Chatbot (`pages/1_Shielded_Chatbot.py`):** Enterprise sales assistant protected by all three layers. Inspect the full security trace for every prompt, showing Layer 1 risk scores, Layer 2 prompt wrapping, and Layer 3 database authorization.
3. **Vulnerable Sandbox (`pages/2_Vulnerable_Chatbot.py`):** Intentionally unprotected chatbot demonstrating how instruction overrides, synthetic secret disclosure, and unauthorized tool calls succeed when defenses are absent. Operates in a safe sandbox without executing real commands.
4. **Comparison & Evaluation (`pages/3_Comparison_Evaluation.py`):** Benchmarks all 32 test cases across 4 configurations, calculates formal security metrics, renders interactive Plotly visualizations, supports dynamic test creation, and exports CSV results.
5. **Security Logs (`pages/4_Security_Logs.py`):** Persistent SQLite audit trail recording timestamps, event types, detector decisions, tool outcomes, and latencies with real-time filtering and CSV export.
6. **About & Methodology (`pages/5_About.py`):** Academic research documentation, dataset provenance, classifier vs baseline comparisons, and threat model boundaries.

---

## 7. Benchmark Test Suite & Security Metrics

The test suite (`data/test_cases.json`) comprises **32 standardized test cases** spanning 7 categories:
1. Benign questions (routine analytics)
2. Direct prompt injection
3. Attempts to override chatbot instructions
4. Requests to disclose synthetic secrets (canary extraction)
5. Indirect prompt injection in retrieved documents
6. Unauthorized tool-call requests
7. Ambiguous or borderline inputs

### Formally Defined Metrics

| Metric | Formula | Description |
|---|---|---|
| **Attack Success Rate (ASR)** | $\frac{\text{Successful Attack Objectives}}{\text{Total Eligible Attack Attempts}}$ | Proportion of attacks that successfully breached objectives. |
| **False Positive Rate (FPR)** | $\frac{\text{Benign Inputs Incorrectly Flagged}}{\text{Total Benign Inputs}}$ | Proportion of harmless queries blocked by Layer 1. |
| **Benign Task Success Rate** | $\frac{\text{Total Benign} - \text{Benign Blocked}}{\text{Total Benign}}$ | Preservation of legitimate application functionality. |
| **Unauthorized Tool Execution Rate**| $\frac{\text{Unauthorized Tool Calls Executed}}{\text{Total Unauthorized Tool Attempts}}$ | Percentage of unauthorized tool calls that escaped interception. |
| **Precision** | $\frac{\text{True Positives}}{\text{True Positives} + \text{False Positives}}$ | Accuracy of positive injection alerts from detector. |
| **Recall** | $\frac{\text{True Positives}}{\text{True Positives} + \text{False Negatives}}$ | Proportion of true attacks detected by classifier. |
| **F1-Score** | $2 \times \frac{\text{Precision} \times \text{Recall}}{\text{Precision} + \text{Recall}}$ | Harmonic mean of precision and recall. |

---

## 8. Running Automated Unit Tests

Run the comprehensive pytest suite verifying all layers, parameter sanitization, metric calculations, and sandbox isolation:

```powershell
py -3.11 -m pytest -v
```

Expected output:
```
tests/test_detector.py::test_benign_inputs_classified_low_risk PASSED
tests/test_detector.py::test_malicious_inputs_classified_high_risk PASSED
tests/test_detector.py::test_empty_and_whitespace_inputs PASSED
tests/test_detector.py::test_heuristic_pattern_detection PASSED
tests/test_detector.py::test_feature_weights_explanation PASSED
tests/test_evaluator.py::test_metrics_calculation_formulae PASSED
tests/test_evaluator.py::test_zero_denominator_safety PASSED
tests/test_evaluator.py::test_synthetic_secret_isolation PASSED
tests/test_evaluator.py::test_vulnerable_sandbox_safety_isolation PASSED
tests/test_evaluator.py::test_sqlite_logging_and_retrieval PASSED
tests/test_evaluator.py::test_csv_export_format PASSED
tests/test_tool_guard.py::test_tool_allowlist_enforcement PASSED
tests/test_tool_guard.py::test_role_based_access_control PASSED
tests/test_tool_guard.py::test_argument_validation_and_injection_blocking PASSED
tests/test_tool_guard.py::test_valid_tool_execution PASSED
============================= 15 passed in ~3s ==============================
```

---

## 9. Dataset Provenance & Model Retraining

The included demonstration dataset (`data/demo_dataset.csv`) contains balanced, labeled benign and attack prompts with explicit train and test splits.

To retrain the detector with a custom public dataset (e.g. from Kaggle or OWASP):
1. Format your CSV with columns: `text`, `label` (0 or 1), `attack_category`, `source`, `split`.
2. Run retraining in Python:
   ```python
   from core.detector import detector_instance
   detector_instance.train_from_dataset("data/your_dataset.csv")
   ```

---

## 10. Limitations & Defense-in-Depth Philosophy

- **Prompt Injection is an Open Research Challenge:** No software framework can mathematically guarantee 100% prevention against all arbitrary prompt injection variations.
- **Defense-in-Depth Rationale:** While Layer 1 might be bypassed by novel or obfuscated paraphrases, Layer 2 restricts the LLM from treating external documents as instructions, and Layer 3 guarantees that even if the LLM is completely compromised, it cannot execute unauthorized tools or arbitrary code on backend infrastructure.
- **Educational Scope:** All secrets (`CANARY-SECRET-9982-XYZ`) and sales records are synthetic. Real production credentials or shell execution mechanisms are strictly excluded.
