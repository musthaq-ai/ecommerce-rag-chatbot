import json
from pathlib import Path

import pandas as pd
import phoenix as px
from phoenix.trace import SpanEvaluations


# ============================================================
# CONFIGURATION
# ============================================================

RESULT_FILE = Path(
    "data/rag_evaluation_final.json"
)

PHOENIX_URL = "http://localhost:6006"

EVALUATIONS = [
    "faithfulness",
    "answer_relevance",
    "context_relevance",
]


# ============================================================
# LOAD EVALUATION RESULTS
# ============================================================

def load_results():

    if not RESULT_FILE.exists():

        raise FileNotFoundError(
            f"Evaluation file not found: {RESULT_FILE}"
        )

    with open(
        RESULT_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


# ============================================================
# CONNECT TO PHOENIX
# ============================================================

def get_phoenix_client():

    print(
        "Connecting to Phoenix..."
    )

    return px.Client(
        base_url=PHOENIX_URL
    )


# ============================================================
# CREATE EVALUATION DATAFRAME
# ============================================================

def create_evaluation_dataframe(
    results,
    evaluation_name
):

    rows = []

    for result in results:

        # Only use successfully evaluated questions
        if result.get("status") != "evaluated":
            continue

        span_id = result.get(
            "span_id"
        )

        if not span_id:
            continue

        evaluation = result.get(
            "evaluation",
            {}
        )

        evaluator_result = evaluation.get(
            evaluation_name
        )

        if not evaluator_result:
            continue

        score = evaluator_result.get(
            "score"
        )

        reason = evaluator_result.get(
            "reason",
            ""
        )

        if score is None:
            continue

        rows.append(
            {
                "context.span_id": span_id,
                "score": float(score),
                "label": (
                    "pass"
                    if float(score) >= 0.7
                    else "fail"
                ),
                "explanation": reason,
            }
        )

    if not rows:
        return None

    return pd.DataFrame(rows)


# ============================================================
# SEND EVALUATION TO PHOENIX
# ============================================================

def log_evaluation(
    client,
    results,
    evaluation_name
):

    dataframe = create_evaluation_dataframe(
        results,
        evaluation_name
    )

    if dataframe is None:

        print(
            f"No data available for "
            f"{evaluation_name}."
        )

        return

    print()
    print(
        f"Logging {evaluation_name}..."
    )

    print(dataframe)

    client.log_evaluations(
        SpanEvaluations(
            eval_name=evaluation_name,
            dataframe=dataframe
        )
    )

    print(
        f"{evaluation_name} logged successfully."
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 70)
    print("SHOPX → PHOENIX EVALUATION UPLOAD")
    print("=" * 70)

    # --------------------------------------------------------
    # Load results
    # --------------------------------------------------------

    results = load_results()

    print(
        f"\nLoaded {len(results)} evaluation results."
    )

    # --------------------------------------------------------
    # Connect to Phoenix
    # --------------------------------------------------------

    client = get_phoenix_client()

    # --------------------------------------------------------
    # Log each evaluator separately
    # --------------------------------------------------------

    for evaluation_name in EVALUATIONS:

        log_evaluation(
            client,
            results,
            evaluation_name
        )

    # --------------------------------------------------------
    # Finished
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print("DONE")
    print("=" * 70)

    print(
        "\nOpen Phoenix:"
    )

    print(
        PHOENIX_URL
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()