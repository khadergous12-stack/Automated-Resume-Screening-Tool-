# =============================================================
# notebooks/eval.py
# Model Evaluation: ROC-AUC, PR-AUC, Top-K Precision
# Run: python notebooks/eval.py
# =============================================================

import sys
import json
import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# Add src/ to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    from sklearn.metrics import (
        roc_auc_score, average_precision_score,
        roc_curve, precision_recall_curve
    )
    SKLEARN_OK = True
except ImportError:
    SKLEARN_OK = False

DB_PATH      = "db/screening.db"
LABELS_FILE  = "data/labeled_pairs.csv"


def evaluate(db_path: str = DB_PATH, labels_file: str = LABELS_FILE):
    """
    Joins model scores with human labels and computes metrics.
    """
    print("\n" + "=" * 50)
    print("  EVALUATION RESULTS")
    print("=" * 50)

    # Load labels
    if not Path(labels_file).exists():
        print(f"Labels file not found: {labels_file}")
        return

    labels_df = pd.read_csv(labels_file)
    print(f"\nLabeled samples: {len(labels_df)}")
    print(f"Positive (selected): {labels_df['label'].sum()}")

    # Load scores from DB
    con = sqlite3.connect(db_path)
    rows = con.execute(
        "SELECT candidate_id, score FROM rankings ORDER BY score DESC"
    ).fetchall()
    con.close()

    if not rows:
        print("No rankings found in DB. Run main.py first.")
        return

    scores_df = pd.DataFrame(rows, columns=["candidate_id", "score"])

    # Merge
    merged = pd.merge(labels_df, scores_df, on="candidate_id", how="inner")
    print(f"\nMatched {len(merged)} candidates for evaluation\n")

    if len(merged) < 2:
        print("Not enough matched data for metrics.")
        return

    y_true = merged["label"].values
    y_score = merged["score"].values

    if SKLEARN_OK and len(set(y_true)) > 1:
        roc_auc = roc_auc_score(y_true, y_score)
        pr_auc  = average_precision_score(y_true, y_score)

        # Top-K precision (top 3)
        k = min(3, len(merged))
        top_k = merged.sort_values("score", ascending=False).head(k)
        top_k_prec = top_k["label"].mean()

        print(f"  ROC-AUC Score     : {roc_auc:.4f}")
        print(f"  PR-AUC Score      : {pr_auc:.4f}")
        print(f"  Top-{k} Precision : {top_k_prec:.4f}")

        # ── PLOTS ──────────────────────────────────────
        fig, axes = plt.subplots(1, 3, figsize=(14, 4))

        # 1. ROC Curve
        fpr, tpr, _ = roc_curve(y_true, y_score)
        axes[0].plot(fpr, tpr, color="#4f46e5", label=f"ROC (AUC={roc_auc:.2f})")
        axes[0].plot([0, 1], [0, 1], "k--")
        axes[0].set_title("ROC Curve")
        axes[0].set_xlabel("False Positive Rate")
        axes[0].set_ylabel("True Positive Rate")
        axes[0].legend()

        # 2. PR Curve
        prec, rec, _ = precision_recall_curve(y_true, y_score)
        axes[1].plot(rec, prec, color="#16a34a", label=f"PR (AUC={pr_auc:.2f})")
        axes[1].set_title("Precision-Recall Curve")
        axes[1].set_xlabel("Recall")
        axes[1].set_ylabel("Precision")
        axes[1].legend()

        # 3. Score distribution
        for label_val, color, name in [(1, "#16a34a", "Selected"), (0, "#dc2626", "Rejected")]:
            subset = merged[merged["label"] == label_val]["score"]
            axes[2].hist(subset, bins=10, alpha=0.6, color=color, label=name)
        axes[2].set_title("Score Distribution by Label")
        axes[2].set_xlabel("Score")
        axes[2].legend()

        plt.tight_layout()
        Path("outputs").mkdir(exist_ok=True)
        plt.savefig("outputs/evaluation_plots.png", dpi=150, bbox_inches="tight")
        print(f"\n  Plots saved to: outputs/evaluation_plots.png")
        plt.show()

    # Full table
    print("\n  Full Scoring Table:")
    print(merged[["candidate_id", "label", "score", "notes"]].sort_values("score", ascending=False).to_string(index=False))
    print("=" * 50)


if __name__ == "__main__":
    evaluate()
