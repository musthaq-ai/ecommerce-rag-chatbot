import json
from pathlib import Path

from utils.rag.retrieval import search_knowledge
from utils.rag.generator import generate_rag_answer

from utils.rag.evaluators import (
    evaluate_faithfulness,
    evaluate_answer_relevance,
    evaluate_context_relevance,
)


# ============================================================
# CONFIGURATION
# ============================================================

DATASET_FILE = Path(
    "data/rag_evaluation.json"
)

RESULT_FILE = Path(
    "data/rag_evaluation_final.json"
)

MATCH_COUNT = 5


# ============================================================
# LOAD DATASET
# ============================================================

def load_dataset():

    with open(
        DATASET_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


# ============================================================
# RUN EVALUATION
# ============================================================

def run_evaluation():

    dataset = load_dataset()

    results = []

    print()
    print("=" * 70)
    print("SHOPX RAG EVALUATION")
    print("=" * 70)

    print(
        f"\nEvaluation questions: {len(dataset)}"
    )

    for index, item in enumerate(
        dataset,
        start=1
    ):

        question = item["question"]
        question_type = item.get(
            "type",
            "knowledge"
        )

        print()
        print("-" * 70)
        print(
            f"Question {index}/{len(dataset)}"
        )
        print(
            f"Type: {question_type}"
        )
        print(
            f"Question: {question}"
        )

        # ====================================================
        # ONLY EVALUATE KNOWLEDGE-BASE QUESTIONS
        # ====================================================

        if question_type != "knowledge":

            print(
                "Skipping: tool/database question."
            )

            results.append(
                {
                    "question": question,
                    "type": question_type,
                    "status": "skipped",
                    "reason": (
                        "Tool/database question "
                        "requires agent/tool evaluation."
                    )
                }
            )

            continue

        # ====================================================
        # RETRIEVE CONTEXT
        # ====================================================

        retrieved = search_knowledge(
            question,
            match_count=MATCH_COUNT
        )

        if not retrieved:

            print(
                "No knowledge chunks retrieved."
            )

            results.append(
                {
                    "question": question,
                    "type": question_type,
                    "status": "failed",
                    "reason": "No context retrieved."
                }
            )

            continue

        context = "\n\n".join(
            result["content"]
            for result in retrieved
        )

        # ====================================================
        # GENERATE ANSWER
        # ====================================================

        rag_result = generate_rag_answer(
            question,
            match_count=MATCH_COUNT,
            user_id=None
        )

        answer = rag_result.get(
            "answer",
            ""
        )

        # ====================================================
        # FAITHFULNESS
        # ====================================================

        print(
            "\nEvaluating faithfulness..."
        )

        faithfulness = evaluate_faithfulness(
            question,
            context,
            answer
        )

        # ====================================================
        # ANSWER RELEVANCE
        # ====================================================

        print(
            "Evaluating answer relevance..."
        )

        answer_relevance = (
            evaluate_answer_relevance(
                question,
                answer
            )
        )

        # ====================================================
        # CONTEXT RELEVANCE
        # ====================================================

        print(
            "Evaluating context relevance..."
        )

        context_relevance = (
            evaluate_context_relevance(
                question,
                context
            )
        )

        # ====================================================
        # DISPLAY SCORES
        # ====================================================

        print(
            f"\nFaithfulness: "
            f"{faithfulness['score']}"
        )

        print(
            f"Answer Relevance: "
            f"{answer_relevance['score']}"
        )

        print(
            f"Context Relevance: "
            f"{context_relevance['score']}"
        )

        # ====================================================
        # SAVE RESULT
        # ====================================================

        results.append(
            {
                "question": question,
                "type": question_type,
                "status": "evaluated",
                "span_id": span_id,

                "retrieved_chunks": len(
                    retrieved
                ),

                "answer": answer,

                "evaluation": {
                    "faithfulness": faithfulness,
                    "answer_relevance": answer_relevance,
                    "context_relevance": context_relevance
                }
            }
        )

    # ========================================================
    # SAVE RESULTS
    # ========================================================

    RESULT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        RESULT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            results,
            file,
            indent=4,
            ensure_ascii=False
        )

    # ========================================================
    # CALCULATE AVERAGES
    # ========================================================

    evaluated = [
        result
        for result in results
        if result.get("status") == "evaluated"
    ]

    if not evaluated:

        print(
            "\nNo questions were successfully evaluated."
        )

        return

    avg_faithfulness = sum(
        result["evaluation"]["faithfulness"]["score"]
        for result in evaluated
    ) / len(evaluated)

    avg_answer_relevance = sum(
        result["evaluation"]["answer_relevance"]["score"]
        for result in evaluated
    ) / len(evaluated)

    avg_context_relevance = sum(
        result["evaluation"]["context_relevance"]["score"]
        for result in evaluated
    ) / len(evaluated)

    overall_score = (
        avg_faithfulness
        + avg_answer_relevance
        + avg_context_relevance
    ) / 3

    # ========================================================
    # FINAL REPORT
    # ========================================================

    print()
    print("=" * 70)
    print("FINAL RAG QUALITY REPORT")
    print("=" * 70)

    print(
        f"\nQuestions evaluated: "
        f"{len(evaluated)}"
    )

    print(
        f"Average Faithfulness: "
        f"{avg_faithfulness:.3f}"
    )

    print(
        f"Average Answer Relevance: "
        f"{avg_answer_relevance:.3f}"
    )

    print(
        f"Average Context Relevance: "
        f"{avg_context_relevance:.3f}"
    )

    print(
        f"\nOverall RAG Quality Score: "
        f"{overall_score:.3f}"
    )

    print(
        f"\nResults saved to:"
        f"\n{RESULT_FILE}"
    )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    run_evaluation()