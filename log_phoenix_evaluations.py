import json
import os
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

RESULT_FILE = Path(
    "data/rag_evaluation_final.json"
)

EVALUATIONS = [
    "faithfulness",
    "answer_relevance",
    "context_relevance",
]


# ============================================================
# PHOENIX CONFIGURATION
# ============================================================

def get_phoenix_config():

    api_key = os.getenv("PHOENIX_API_KEY")

    endpoint = os.getenv(
        "PHOENIX_COLLECTOR_ENDPOINT"
    )

    if not api_key:
        raise ValueError(
            "PHOENIX_API_KEY is not set."
        )

    if not endpoint:
        raise ValueError(
            "PHOENIX_COLLECTOR_ENDPOINT is not set."
        )

    # Remove /v1/traces if it was included
    endpoint = endpoint.rstrip("/")

    if endpoint.endswith("/v1/traces"):
        endpoint = endpoint[:-10]

    annotation_url = (
        f"{endpoint}/v1/span_annotations"
    )

    return api_key, annotation_url


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

        span_id = result.get("span_id")

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

        score = float(score)

        rows.append(
            {
                "span_id": span_id,
                "score": score,
                "label": (
                    "pass"
                    if score >= 0.7
                    else "fail"
                ),
                "explanation": reason,
            }
        )

    if not rows:
        return None

    return pd.DataFrame(rows)


# ============================================================
# SEND ONE ANNOTATION TO PHOENIX
# ============================================================

def send_annotation(
    annotation_url,
    api_key,
    span_id,
    evaluation_name,
    score,
    label,
    explanation,
):

    payload = {
        "span_id": span_id,
        "name": evaluation_name,
        "annotator_kind": "LLM",
        "result": {
            "label": label,
            "score": score,
            "explanation": explanation,
        },
    }

    request = Request(
        annotation_url,
        data=json.dumps(payload).encode(
            "utf-8"
        ),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
            "api_key": api_key,
        },
        method="POST",
    )

    try:

        with urlopen(
            request,
            timeout=30
        ) as response:

            return response.status

    except HTTPError as error:

        body = error.read().decode(
            "utf-8",
            errors="replace"
        )

        print(
            f"\nPhoenix API error "
            f"{error.code}:"
        )

        print(body)

        return None

    except URLError as error:

        print(
            "\nCould not connect to Phoenix:"
        )

        print(error)

        return None


# ============================================================
# LOG EVALUATION
# ============================================================

def log_evaluation(
    annotation_url,
    api_key,
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

    print(
        dataframe[
            [
                "span_id",
                "score",
                "label"
            ]
        ]
    )

    success_count = 0

    for _, row in dataframe.iterrows():

        status = send_annotation(
            annotation_url=annotation_url,
            api_key=api_key,
            span_id=row["span_id"],
            evaluation_name=evaluation_name,
            score=float(row["score"]),
            label=row["label"],
            explanation=row["explanation"],
        )

        if status and 200 <= status < 300:

            success_count += 1

    print(
        f"{evaluation_name}: "
        f"{success_count}/{len(dataframe)} "
        f"annotations uploaded."
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
    # Load evaluation results
    # --------------------------------------------------------

    results = load_results()

    print(
        f"\nLoaded {len(results)} evaluation results."
    )

    # --------------------------------------------------------
    # Phoenix configuration
    # --------------------------------------------------------

    api_key, annotation_url = (
        get_phoenix_config()
    )

    print(
        "\nPhoenix annotation endpoint:"
    )

    print(
        annotation_url
    )

    # --------------------------------------------------------
    # Log evaluations
    # --------------------------------------------------------

    for evaluation_name in EVALUATIONS:

        log_evaluation(
            annotation_url=annotation_url,
            api_key=api_key,
            results=results,
            evaluation_name=evaluation_name,
        )

    # --------------------------------------------------------
    # Finished
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print("DONE")
    print("=" * 70)

    print(
        "\nEvaluations have been sent to Phoenix."
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()