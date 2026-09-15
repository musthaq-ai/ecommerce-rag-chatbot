import json
from pathlib import Path

from utils.rag.generator import generate_rag_answer
from utils.rag.retrieval import search_knowledge


# ============================================================
# CONFIGURATION
# ============================================================

EVALUATION_FILE = Path("data/rag_evaluation.json")
RESULT_FILE = Path("data/rag_evaluation_results.json")

MATCH_COUNT = 5


# ============================================================
# LOAD EVALUATION DATASET
# ============================================================

def load_dataset():

    if not EVALUATION_FILE.exists():
        print(
            f"Evaluation file not found: {EVALUATION_FILE}"
        )
        return []

    with open(
        EVALUATION_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


# ============================================================
# EVALUATE RETRIEVAL
# ============================================================

def evaluate_retrieval(question):

    try:

        results = search_knowledge(
            question,
            match_count=MATCH_COUNT
        )

        if not results:

            return {
                "retrieved": False,
                "result_count": 0,
                "average_similarity": 0
            }

        similarities = []

        for result in results:

            similarity = result.get(
                "similarity"
            )

            if similarity is not None:
                similarities.append(
                    float(similarity)
                )

        average_similarity = (
            sum(similarities) / len(similarities)
            if similarities
            else 0
        )

        return {
            "retrieved": True,
            "result_count": len(results),
            "average_similarity": round(
                average_similarity,
                4
            )
        }

    except Exception as error:

        print(
            f"Retrieval error: {error}"
        )

        return {
            "retrieved": False,
            "result_count": 0,
            "average_similarity": 0,
            "error": str(error)
        }


# ============================================================
# EVALUATE GENERATION
# ============================================================

def evaluate_generation(question):

    try:

        result = generate_rag_answer(
            question,
            match_count=MATCH_COUNT,
            user_id=None
        )

        answer = result.get(
            "answer",
            ""
        )

        sources = result.get(
            "sources",
            []
        )

        return {
            "answer": answer,
            "source_count": len(sources)
        }

    except Exception as error:

        print(
            f"Generation error: {error}"
        )

        return {
            "answer": "",
            "source_count": 0,
            "error": str(error)
        }


# ============================================================
# RUN EVALUATION
# ============================================================

def run_evaluation():

    dataset = load_dataset()

    if not dataset:

        print(
            "No evaluation questions found."
        )

        return

    results = []

    print("\n")
    print("=" * 60)
    print("SHOPX RAG EVALUATION")
    print("=" * 60)

    print(
        f"\nTotal questions: {len(dataset)}"
    )

    for index, item in enumerate(
        dataset,
        start=1
    ):

        question = item.get(
            "question",
            ""
        )

        question_type = item.get(
            "type",
            "unknown"
        )

        print("\n")
        print("-" * 60)
        print(
            f"Question {index}/{len(dataset)}"
        )
        print(
            f"Type: {question_type}"
        )
        print(
            f"Question: {question}"
        )

        # ----------------------------------------------------
        # Retrieval evaluation
        # ----------------------------------------------------

        retrieval = evaluate_retrieval(
            question
        )

        print(
            f"Retrieved chunks: "
            f"{retrieval.get('result_count', 0)}"
        )

        print(
            f"Average similarity: "
            f"{retrieval.get('average_similarity', 0)}"
        )

        # ----------------------------------------------------
        # Generation evaluation
        # ----------------------------------------------------

        generation = evaluate_generation(
            question
        )

        answer = generation.get(
            "answer",
            ""
        )

        print(
            f"\nAnswer:\n{answer}"
        )

        # ----------------------------------------------------
        # Store result
        # ----------------------------------------------------

        results.append(
            {
                "question": question,
                "type": question_type,
                "expected_answer": item.get(
                    "expected_answer",
                    ""
                ),
                "retrieval": retrieval,
                "generation": generation
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
    # SUMMARY
    # ========================================================

    successful_retrievals = sum(
        1
        for result in results
        if result["retrieval"].get("retrieved")
    )

    total_similarity = sum(
        result["retrieval"].get(
            "average_similarity",
            0
        )
        for result in results
    )

    average_similarity = (
        total_similarity / len(results)
        if results
        else 0
    )

    print("\n")
    print("=" * 60)
    print("EVALUATION SUMMARY")
    print("=" * 60)

    print(
        f"Total questions: "
        f"{len(results)}"
    )

    print(
        f"Successful retrievals: "
        f"{successful_retrievals}/"
        f"{len(results)}"
    )

    print(
        f"Retrieval rate: "
        f"{successful_retrievals / len(results) * 100:.2f}%"
    )

    print(
        f"Average similarity: "
        f"{average_similarity:.4f}"
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