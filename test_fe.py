import argparse
from pathlib import Path
import sys

import matplotlib

matplotlib.use('WebAgg')

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from utils.feature_engineering import (
    AdvancedImputer,
    IntelligentFeatureSelector,
    TelecomFeatureEngineer,
)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Compare raw vs engineered feature pipelines."
    )
    parser.add_argument(
        "--data",
        type=Path,
        default=Path("train.csv"),
        help="Path to the labeled training CSV.",
    )
    parser.add_argument(
        "--test-data",
        type=Path,
        default=Path("testB.csv"),
        help="Path to the test CSV for alignment checks.",
    )
    parser.add_argument(
        "--test-size",
        type=float,
        default=0.15,
        help="Hold-out ratio for validation.",
    )
    parser.add_argument(
        "--core-features",
        type=int,
        default=25,
        help="Number of top engineered features to keep as the core set.",
    )
    parser.add_argument(
        "--support-features",
        type=int,
        default=120,
        help="Size of the broader engineered feature set (must exceed core).",
    )
    return parser.parse_args()


def describe_class_balance(y):
    counts = y.value_counts().to_dict()
    total = len(y)
    pos = counts.get(1, 0)
    neg = counts.get(0, 0)
    print("\nClass distribution:")
    print(
        f"  label=1: {pos} ({pos / total:.2%}) | "
        f"label=0: {neg} ({neg / total:.2%})"
    )


def evaluate_model(model, X_train, X_val, y_train, y_val):
    model.fit(X_train, y_train)
    if hasattr(model, "predict_proba"):
        y_prob = model.predict_proba(X_val)[:, 1]
    elif hasattr(model, "decision_function"):
        logits = model.decision_function(X_val)
        y_prob = 1 / (1 + np.exp(-logits))
    else:
        y_prob = model.predict(X_val)
    y_pred = (y_prob >= 0.5).astype(int)
    metrics = {
        "accuracy": accuracy_score(y_val, y_pred),
        "f1": f1_score(y_val, y_pred),
        "roc_auc": roc_auc_score(y_val, y_prob),
    }
    return metrics


def run_baseline_experiment(df, test_size):
    print("\n" + "=" * 80)
    print("BASELINE: RAW NUMERIC FEATURES (LOGISTIC, BALANCED)")
    print("=" * 80)

    drop_cols = {"label", "id"}
    drop_cols.update(
        {col for col in df.columns if col.lower().startswith("unnamed")}
    )

    feature_cols = [col for col in df.columns if col not in drop_cols]
    X = df[feature_cols].copy()
    y = df["label"].copy()

    X = X.replace([np.inf, -np.inf], np.nan)
    X = X.fillna(X.median())

    X_train, X_val, y_train, y_val = train_test_split(
        X,
        y,
        test_size=test_size,
        random_state=42,
        stratify=y,
    )

    baseline_model = Pipeline(
        steps=[
            ("scaler", StandardScaler()),
            (
                "clf",
                LogisticRegression(
                    max_iter=2000,
                    class_weight="balanced",
                ),
            ),
        ]
    )
    metrics = evaluate_model(baseline_model, X_train, X_val, y_train, y_val)
    return {
        "name": "Raw logistic (balanced)",
        "metrics": metrics,
        "feature_count": X.shape[1],
    }


def prepare_engineered_features(df, core_count, support_count):
    print("\n" + "=" * 80)
    print("ENGINEERED FEATURE PREPARATION")
    print("=" * 80)

    imputer = AdvancedImputer(strategy="auto")
    df_imputed = imputer.fit_transform(df, target=df["label"])

    engineer = TelecomFeatureEngineer()
    df_features = engineer.create_all_features(
        df_imputed, is_train=True, target=df_imputed["label"]
    )

    exclude_cols = {
        "label",
        "id",
        "Unnamed: 0",
        "age_group",
        "customer_segment",
    }
    feature_cols = [
        col for col in df_features.columns if col not in exclude_cols
    ]
    X = df_features[feature_cols].copy()
    y = df_features["label"].copy()
    X = X.replace([np.inf, -np.inf], 0)
    X = X.fillna(0)

    selector = IntelligentFeatureSelector(n_features=support_count)
    support_cols = selector.select_features(X, y, method="ensemble")
    ordered = list(selector.feature_scores.keys())
    core_cols = ordered[:core_count]
    if len(core_cols) < core_count:
        core_cols = support_cols[:core_count]

    X_core = X[core_cols]
    X_support = X[support_cols]

    return {
        "X_core": X_core,
        "X_support": X_support,
        "y": y,
        "core_cols": core_cols,
        "support_cols": support_cols,
        "feature_cols": feature_cols,
        "imputer": imputer,
        "engineer": engineer,
    }


def evaluate_engineered_models(feature_data, test_size):
    X_support = feature_data["X_support"]
    y = feature_data["y"]
    core_cols = feature_data["core_cols"]
    support_cols = feature_data["support_cols"]

    X_train_sup, X_val_sup, y_train, y_val = train_test_split(
        X_support,
        y,
        test_size=test_size,
        random_state=42,
        stratify=y,
    )

    X_train_core = X_train_sup[core_cols]
    X_val_core = X_val_sup[core_cols]

    core_model = Pipeline(
        steps=[
            ("scaler", StandardScaler()),
            (
                "clf",
                LogisticRegression(
                    max_iter=2000,
                    class_weight="balanced",
                ),
            ),
        ]
    )
    core_metrics = evaluate_model(
        core_model, X_train_core, X_val_core, y_train, y_val
    )

    tree_model = RandomForestClassifier(
        n_estimators=400,
        max_depth=12,
        random_state=42,
        n_jobs=-1,
        class_weight="balanced_subsample",
    )
    support_metrics = evaluate_model(
        tree_model, X_train_sup, X_val_sup, y_train, y_val
    )

    return [
        {
            "name": f"Engineered core ({len(core_cols)} feats, Logistic)",
            "metrics": core_metrics,
            "feature_count": len(core_cols),
        },
        {
            "name": f"Engineered support ({len(support_cols)} feats, RandomForest)",
            "metrics": support_metrics,
            "feature_count": len(support_cols),
        },
    ]


def align_test_features(df_test, feature_data):
    imputer = feature_data["imputer"]
    engineer = feature_data["engineer"]
    feature_cols = feature_data["feature_cols"]
    core_cols = feature_data["core_cols"]
    support_cols = feature_data["support_cols"]

    df_test_imputed = imputer.transform(df_test)
    df_test_features = engineer.create_all_features(
        df_test_imputed, is_train=False, target=None
    )

    X_test_full = df_test_features.reindex(columns=feature_cols)
    X_test_full = X_test_full.replace([np.inf, -np.inf], 0)
    X_test_full = X_test_full.fillna(0)
    X_test_core = X_test_full.reindex(columns=core_cols, fill_value=0)
    X_test_support = X_test_full.reindex(columns=support_cols, fill_value=0)

    missing_core = [col for col in core_cols if col not in df_test_features.columns]
    missing_support = [
        col for col in support_cols if col not in df_test_features.columns
    ]

    print("\nTest feature alignment:")
    print(
        f"  Core shape: {X_test_core.shape}, missing cols: {len(missing_core)}"
    )
    print(
        f"  Support shape: {X_test_support.shape}, missing cols: {len(missing_support)}"
    )
    if missing_core or missing_support:
        preview = []
        if missing_core:
            preview.append(f"core -> {missing_core[:5]}")
        if missing_support:
            preview.append(f"support -> {missing_support[:5]}")
        print(
            "  Missing columns were backfilled with zeros for alignment "
            f"({'; '.join(preview)})."
        )
    else:
        print("  ✓ Train/test feature spaces are aligned.")


def plot_results(results):
    names = [res["name"] for res in results]
    metrics_df = pd.DataFrame(
        [res["metrics"] for res in results], index=names
    )

    print("\n" + "=" * 80)
    print("METRIC COMPARISON")
    print("=" * 80)
    print(metrics_df.round(4))

    fig, ax = plt.subplots(figsize=(10, 4))
    metrics_df.plot(kind="bar", ax=ax)
    ax.set_ylim(0, 1)
    ax.set_ylabel("Score")
    ax.set_title("Feature Pipeline Comparison")
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    ax.tick_params(axis='x', rotation=45)
    plt.tight_layout()
    try:
        plt.show()
    except PermissionError as exc:
        fallback_path = PROJECT_ROOT / "feature_engineering_metrics.png"
        fig.savefig(fallback_path)
        print(
            f"WebAgg viewer could not start ({exc}). "
            f"Saved the plot to {fallback_path} instead."
        )


def main():
    args = parse_args()
    if args.core_features > args.support_features:
        raise ValueError(
            "--core-features must be less than or equal to --support-features."
        )

    df = pd.read_csv(args.data)
    if "label" not in df.columns:
        raise ValueError("The input dataset must contain a 'label' column.")

    describe_class_balance(df["label"])

    baseline_result = run_baseline_experiment(df, args.test_size)

    feature_data = prepare_engineered_features(
        df, args.core_features, args.support_features
    )
    engineered_results = evaluate_engineered_models(
        feature_data, args.test_size
    )

    results = [baseline_result] + engineered_results
    for res in results:
        print(
            f"{res['name']}: {res['feature_count']} features | "
            f"Accuracy={res['metrics']['accuracy']:.4f}, "
            f"F1={res['metrics']['f1']:.4f}, "
            f"ROC-AUC={res['metrics']['roc_auc']:.4f}"
        )

    if args.test_data.exists():
        df_test = pd.read_csv(args.test_data)
        align_test_features(df_test, feature_data)
    else:
        print(f"\nTest data not found at {args.test_data}, skipping alignment.")

    plot_results(results)


if __name__ == "__main__":
    main()
