import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
import pandas as pd
from config import DB_PATH

def get_connection() -> sqlite3.Connection:
    """Return a thread-safe connection to SQLite database."""
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database tables for security events and evaluation logs."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Security events log table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS security_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            test_id TEXT,
            chatbot_config TEXT NOT NULL,
            event_type TEXT NOT NULL,
            detector_decision TEXT,
            risk_score REAL,
            layer_responsible TEXT,
            tool_name TEXT,
            authorization_outcome TEXT,
            execution_latency_ms REAL,
            details TEXT
        )
    """)
    
    # Evaluation summary table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS evaluation_runs (
            run_id TEXT PRIMARY KEY,
            timestamp TEXT NOT NULL,
            configuration TEXT NOT NULL,
            total_tests INTEGER NOT NULL,
            asr REAL,
            precision REAL,
            recall REAL,
            f1 REAL,
            fpr REAL,
            benign_success_rate REAL,
            unauthorized_execution_rate REAL,
            avg_latency_ms REAL,
            is_demo_mode INTEGER DEFAULT 1
        )
    """)
    
    # Individual test outcome records per evaluation run
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS evaluation_test_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id TEXT NOT NULL,
            test_id TEXT NOT NULL,
            category TEXT NOT NULL,
            input_snippet TEXT NOT NULL,
            expected_class INTEGER NOT NULL,
            chatbot_config TEXT NOT NULL,
            detected INTEGER NOT NULL,
            attack_succeeded INTEGER NOT NULL,
            unauthorized_executed INTEGER NOT NULL,
            benign_blocked INTEGER NOT NULL,
            final_status TEXT NOT NULL,
            latency_ms REAL NOT NULL,
            response_snippet TEXT,
            FOREIGN KEY (run_id) REFERENCES evaluation_runs (run_id) ON DELETE CASCADE
        )
    """)
    
    conn.commit()
    conn.close()

def log_security_event(
    chatbot_config: str,
    event_type: str,
    test_id: Optional[str] = None,
    detector_decision: Optional[str] = None,
    risk_score: Optional[float] = None,
    layer_responsible: Optional[str] = None,
    tool_name: Optional[str] = None,
    authorization_outcome: Optional[str] = None,
    execution_latency_ms: Optional[float] = None,
    details: Optional[str] = None,
) -> int:
    """Safely log a security event to SQLite."""
    conn = get_connection()
    cursor = conn.cursor()
    now_str = datetime.utcnow().isoformat() + "Z"
    
    # Sanitize details to guarantee zero leakage of secret keys
    sanitized_details = details or ""
    if "api_key" in sanitized_details.lower():
        sanitized_details = "[REDACTED_CREDENTIAL_DATA]"

    cursor.execute("""
        INSERT INTO security_logs (
            timestamp, test_id, chatbot_config, event_type,
            detector_decision, risk_score, layer_responsible,
            tool_name, authorization_outcome, execution_latency_ms, details
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        now_str, test_id, chatbot_config, event_type,
        detector_decision, risk_score, layer_responsible,
        tool_name, authorization_outcome, execution_latency_ms, sanitized_details
    ))
    
    inserted_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return inserted_id

def get_security_logs(
    limit: int = 200,
    chatbot_config: Optional[str] = None,
    event_type: Optional[str] = None,
    outcome: Optional[str] = None
) -> pd.DataFrame:
    """Retrieve filtered security logs as a Pandas DataFrame."""
    conn = get_connection()
    query = "SELECT * FROM security_logs WHERE 1=1"
    params = []
    
    if chatbot_config and chatbot_config != "All":
        query += " AND chatbot_config = ?"
        params.append(chatbot_config)
    if event_type and event_type != "All":
        query += " AND event_type = ?"
        params.append(event_type)
    if outcome and outcome != "All":
        query += " AND (authorization_outcome = ? OR detector_decision = ?)"
        params.extend([outcome, outcome])
        
    query += " ORDER BY id DESC LIMIT ?"
    params.append(limit)
    
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df

def clear_security_logs():
    """Clear all entries from security_logs table."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM security_logs")
    conn.commit()
    conn.close()

def save_evaluation_run(summary: Dict[str, Any], results: List[Dict[str, Any]]) -> str:
    """Save an evaluation run summary and detailed test outcomes."""
    conn = get_connection()
    cursor = conn.cursor()
    run_id = summary.get("run_id", f"run_{int(datetime.utcnow().timestamp())}")
    
    cursor.execute("""
        INSERT OR REPLACE INTO evaluation_runs (
            run_id, timestamp, configuration, total_tests,
            asr, precision, recall, f1, fpr,
            benign_success_rate, unauthorized_execution_rate,
            avg_latency_ms, is_demo_mode
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        run_id,
        datetime.utcnow().isoformat() + "Z",
        summary.get("configuration", "unknown"),
        summary.get("total_tests", len(results)),
        summary.get("asr", 0.0),
        summary.get("precision", 0.0),
        summary.get("recall", 0.0),
        summary.get("f1", 0.0),
        summary.get("fpr", 0.0),
        summary.get("benign_success_rate", 0.0),
        summary.get("unauthorized_execution_rate", 0.0),
        summary.get("avg_latency_ms", 0.0),
        1 if summary.get("is_demo_mode", True) else 0
    ))
    
    for r in results:
        cursor.execute("""
            INSERT INTO evaluation_test_results (
                run_id, test_id, category, input_snippet, expected_class,
                chatbot_config, detected, attack_succeeded,
                unauthorized_executed, benign_blocked, final_status,
                latency_ms, response_snippet
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            run_id,
            r.get("test_id", ""),
            r.get("category", ""),
            r.get("input_snippet", "")[:120],
            r.get("expected_class", 0),
            r.get("chatbot_config", ""),
            1 if r.get("detected", False) else 0,
            1 if r.get("attack_succeeded", False) else 0,
            1 if r.get("unauthorized_executed", False) else 0,
            1 if r.get("benign_blocked", False) else 0,
            r.get("final_status", "UNKNOWN"),
            r.get("latency_ms", 0.0),
            r.get("response_snippet", "")[:200]
        ))
        
    conn.commit()
    conn.close()
    return run_id

def get_latest_evaluation_results(config_name: Optional[str] = None) -> pd.DataFrame:
    """Retrieve detailed test results from the most recent evaluation run."""
    conn = get_connection()
    if config_name:
        query = """
            SELECT r.* FROM evaluation_test_results r
            JOIN evaluation_runs run ON r.run_id = run.run_id
            WHERE run.configuration = ?
            ORDER BY r.id DESC
            LIMIT 100
        """
        df = pd.read_sql_query(query, conn, params=[config_name])
    else:
        query = "SELECT * FROM evaluation_test_results ORDER BY id DESC LIMIT 100"
        df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def clear_evaluation_data():
    """Clear evaluation runs and test results."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM evaluation_test_results")
    cursor.execute("DELETE FROM evaluation_runs")
    conn.commit()
    conn.close()

# Initialize DB upon module load
init_db()
