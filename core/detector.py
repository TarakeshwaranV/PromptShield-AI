"""
Layer 1: NLP-Based Prompt Injection Detector
Combines TF-IDF vectorization with Logistic Regression,
supported by a parallel rule-based heuristic baseline for defense-in-depth comparison.
"""

import os
import re
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
import pandas as pd
import numpy as np
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from config import DATA_DIR, MODELS_DIR, RISK_THRESHOLD_LOW, RISK_THRESHOLD_HIGH

MODEL_FILE_PATH = MODELS_DIR / "tfidf_detector.joblib"
DEMO_DATASET_PATH = DATA_DIR / "demo_dataset.csv"

# Heuristic patterns for the baseline comparator
BASELINE_PATTERNS = [
    r"ignore\s+(all\s+)?(previous|prior|above)\s+(instructions|directives|prompts)",
    r"disregard\s+(all\s+)?(prior|previous|system|current)\s+(rules|guidelines|instructions)",
    r"system\s+override",
    r"you\s+are\s+now\s+(in\s+)?(dan|developer|debug|unfiltered|jailbreak)\s+mode",
    r"output\s+(the\s+)?(secret|canary|token|hidden|internal)\s+(key|prompt|instructions)",
    r"print\s+(the\s+)?(canary|system\s+prompt|developer\s+prompt|api\s+key)",
    r"execute\s+(raw\s+sql|shell_command|delete_sales|drop\s+table)",
    r"repeat\s+the\s+words?\s+above",
    r"base64\s+decode.*execute",
]

@dataclass
class DetectionResult:
    predicted_class: int # 0: Benign, 1: Prompt Injection
    risk_score: float # 0.0 - 1.0 (estimated probability of injection)
    risk_level: str # "LOW", "MEDIUM", "HIGH"
    policy_decision: str # "ALLOW", "REVIEW", "BLOCK"
    model_explanation: str
    top_features: List[Tuple[str, float]] = field(default_factory=list)
    heuristic_flag: bool = False
    heuristic_matches: List[str] = field(default_factory=list)
    latency_ms: float = 0.0

class PromptInjectionDetector:
    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path or MODEL_FILE_PATH
        self.vectorizer: Optional[TfidfVectorizer] = None
        self.classifier: Optional[LogisticRegression] = None
        self.is_trained: bool = False
        self.train_metrics: Dict[str, Any] = {}
        self.baseline_metrics: Dict[str, Any] = {}
        
        # Load or initialize
        if os.path.exists(self.model_path):
            self.load_model()
        else:
            self.train_from_dataset()

    def _check_heuristics(self, text: str) -> Tuple[bool, List[str]]:
        """Run regex heuristic baseline scanner."""
        matches = []
        clean = text.lower()
        for pat in BASELINE_PATTERNS:
            found = re.findall(pat, clean)
            if found:
                matches.append(pat)
        return len(matches) > 0, matches

    def train_from_dataset(self, csv_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Train TF-IDF + Logistic Regression on labeled dataset.
        Prevents data leakage by respecting explicit train/test split.
        """
        path = csv_path or DEMO_DATASET_PATH
        if not os.path.exists(path):
            raise FileNotFoundError(f"Dataset not found at {path}")
            
        df = pd.read_csv(path)
        if "text" not in df.columns or "label" not in df.columns:
            raise ValueError("Dataset must contain 'text' and 'label' columns.")
            
        # Train / test split
        if "split" in df.columns:
            train_df = df[df["split"] == "train"]
            test_df = df[df["split"] == "test"]
            if test_df.empty:
                train_df = df.sample(frac=0.8, random_state=42)
                test_df = df.drop(train_df.index)
        else:
            train_df = df.sample(frac=0.8, random_state=42)
            test_df = df.drop(train_df.index)
            
        X_train_raw = train_df["text"].astype(str).tolist()
        y_train = train_df["label"].astype(int).values
        X_test_raw = test_df["text"].astype(str).tolist()
        y_test = test_df["label"].astype(int).values
        
        # TF-IDF Vectorizer with unigrams and bigrams
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            sublinear_tf=True,
            min_df=1,
            lowercase=True,
            token_pattern=r"(?u)\b\w+\b|[#\-_:]"
        )
        
        X_train_vec = self.vectorizer.fit_transform(X_train_raw)
        X_test_vec = self.vectorizer.transform(X_test_raw)
        
        # Train Logistic Regression
        self.classifier = LogisticRegression(
            C=2.5,
            class_weight="balanced",
            max_iter=500,
            random_state=42
        )
        self.classifier.fit(X_train_vec, y_train)
        
        # Evaluate ML model
        y_pred = self.classifier.predict(X_test_vec)
        self.train_metrics = {
            "accuracy": float(accuracy_score(y_test, y_pred)),
            "precision": float(precision_score(y_test, y_pred, zero_division=0)),
            "recall": float(recall_score(y_test, y_pred, zero_division=0)),
            "f1": float(f1_score(y_test, y_pred, zero_division=0)),
            "train_samples": len(train_df),
            "test_samples": len(test_df),
            "class_distribution": dict(df["label"].value_counts().to_dict())
        }
        
        # Evaluate baseline heuristic on test split
        baseline_preds = []
        for t in X_test_raw:
            flagged, _ = self._check_heuristics(t)
            baseline_preds.append(1 if flagged else 0)
            
        self.baseline_metrics = {
            "accuracy": float(accuracy_score(y_test, baseline_preds)),
            "precision": float(precision_score(y_test, baseline_preds, zero_division=0)),
            "recall": float(recall_score(y_test, baseline_preds, zero_division=0)),
            "f1": float(f1_score(y_test, baseline_preds, zero_division=0)),
        }
        
        self.is_trained = True
        self.save_model()
        return self.train_metrics

    def save_model(self):
        """Save vectorizer, classifier, and evaluation metrics to disk."""
        if not self.is_trained:
            return
        payload = {
            "vectorizer": self.vectorizer,
            "classifier": self.classifier,
            "train_metrics": self.train_metrics,
            "baseline_metrics": self.baseline_metrics
        }
        joblib.dump(payload, self.model_path)

    def load_model(self):
        """Load trained model artifacts from disk."""
        if os.path.exists(self.model_path):
            payload = joblib.load(self.model_path)
            self.vectorizer = payload.get("vectorizer")
            self.classifier = payload.get("classifier")
            self.train_metrics = payload.get("train_metrics", {})
            self.baseline_metrics = payload.get("baseline_metrics", {})
            self.is_trained = (self.vectorizer is not None and self.classifier is not None)

    def predict(self, text: Optional[str]) -> DetectionResult:
        """
        Classify text and generate risk score, policy decision, and feature explanations.
        Handles empty or malformed input safely.
        """
        start_time = time.perf_counter()
        
        # Handle empty/whitespace input
        if not text or not str(text).strip():
            return DetectionResult(
                predicted_class=0,
                risk_score=0.01,
                risk_level="LOW",
                policy_decision="ALLOW",
                model_explanation="Input is empty or null. Assigned default baseline risk score (0.01).",
                top_features=[],
                heuristic_flag=False,
                heuristic_matches=[],
                latency_ms=(time.perf_counter() - start_time) * 1000
            )
            
        raw_text = str(text)
        
        # Run heuristic check
        h_flag, h_matches = self._check_heuristics(raw_text)
        
        if not self.is_trained:
            self.train_from_dataset()
            
        # Transform and classify
        X_vec = self.vectorizer.transform([raw_text])
        proba = self.classifier.predict_proba(X_vec)[0]
        # proba[1] is the estimated probability of class 1 (prompt injection)
        injection_prob = float(proba[1])
        
        # Extract top contributing features (n-grams) from model coefficients
        feature_names = self.vectorizer.get_feature_names_out()
        nonzero_indices = X_vec.nonzero()[1]
        feature_weights = []
        for idx in nonzero_indices:
            feat_name = feature_names[idx]
            tfidf_val = X_vec[0, idx]
            coef = self.classifier.coef_[0][idx]
            weight = tfidf_val * coef
            feature_weights.append((feat_name, float(weight)))
            
        # Sort by influence towards injection (positive weights)
        feature_weights.sort(key=lambda x: x[1], reverse=True)
        top_positive_features = [f for f in feature_weights if f[1] > 0][:5]
        
        # Determine risk level and operational policy decision
        # We also factor heuristic flags to raise scrutiny for ambiguous items
        if injection_prob >= RISK_THRESHOLD_HIGH:
            risk_level = "HIGH"
            policy_decision = "BLOCK"
        elif injection_prob >= RISK_THRESHOLD_LOW or h_flag:
            risk_level = "MEDIUM"
            policy_decision = "REVIEW"
        else:
            risk_level = "LOW"
            policy_decision = "ALLOW"
            
        # Explanatory narrative
        if top_positive_features:
            features_str = ", ".join([f"'{f[0]}' ({f[1]:+.2f})" for f in top_positive_features])
            explanation = f"Model statistical score: {injection_prob:.1%}. Key n-gram contributions: {features_str}."
        else:
            explanation = f"Model statistical score: {injection_prob:.1%}. No strongly malicious n-gram indicators observed."
            
        if h_flag:
            explanation += f" [Heuristic Rule Alert: Matched {len(h_matches)} known signature(s)]."
            
        latency = (time.perf_counter() - start_time) * 1000
        
        return DetectionResult(
            predicted_class=1 if injection_prob >= 0.50 else 0,
            risk_score=round(injection_prob, 4),
            risk_level=risk_level,
            policy_decision=policy_decision,
            model_explanation=explanation,
            top_features=top_positive_features,
            heuristic_flag=h_flag,
            heuristic_matches=h_matches,
            latency_ms=round(latency, 2)
        )

# Global detector instance
detector_instance = PromptInjectionDetector()
