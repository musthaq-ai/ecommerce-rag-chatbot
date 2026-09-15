import json
from pathlib import Path

from google import genai
import streamlit as st

from utils.rag.retrieval import search_knowledge
from utils.rag.generator import generate_rag_answer


# ============================================================
# CONFIGURATION
# ============================================================

EVALUATION_FILE = Path(
    "data/rag_evaluation.json"
)

RESULT_FILE = Path(
    "data/rag_quality_results.json"
)

MODEL = "gemini-3.6-flash"
MATCH_COUNT = 5


# ============================================================
# GEMINI CLIENT
# ============================================================

client = genai.Client(
    api_key=st.secrets["GEMINI_API_KEY"]
)


# ============================================================
# LOAD DATASET
# ============================================================

def load_dataset():

    with open(
        EVALUATION_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


# ============================================================
# GEMINI JUDGE
# ============================================================

def judge(question, context, answer):

    prompt = f"""
You are evaluating an e-commerce RAG chatbot.

Evaluate the chatbot answer using the provided
question, retrieved context, and answer.

QUESTION:
{question}

RETRIEVED CONTEXT:
{context}

CHATBOT ANSWER:
{answer}

Return ONLY valid JSON in this format:

{{
    "faithfulness": 0.0,
    "answer_relevance": 0.0,
    "context_relevance": 0.0,
    "reason": "short explanation"
}}

Scoring:

FAITHFULNESS:
1.0 = answer is completely supported by the context.
0.5 = partially supported.
0.0 = unsupported or hallucinated.

ANSWER_RELEVANCE:
1.0 = directly answers the question.
0.5 = partially answers it.
0.0 = does not answer the question.

CONTEXT_RELEVANCE:
1.0 = retrieved context is highly relevant.
0.5 = partially relevant.
0.0 = irrelevant.

Do not use information outside the supplied context
when judging faithfulness.
"""

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt
    )

    text = response.text.strip()

    # Remove markdown JSON fences if Gemini returns them
    text = text.replace(
        "```json",
        ""
    ).replace(
        "```",
        ""
    ).strip()

    try:

        return json.loads(text)

    except json.JSONDecodeError:

        return {
            "faithfulness": 0,
            "answer_relevance": 0,
            "context_relevance": 0,
            "reason": "Evaluator returned invalid JSON."
        }


# ============================================================
# RUN EVALUATION
# ============================================================

def run_quality_evaluation():

    dataset = load_dataset()

    results = []

    print()
    print("=" * 70)
    print("SHOPX RAG QUALITY EVALUATION")
    print("=" * 70)

    for index, item in enumerate(
        dataset,
        start=1
    ):

        question = item["question"]

        print()
        print("-" * 70)
        print(
            f"Question {index}/{len(dataset)}"
        )
        print(
            f"Question: {question}"
        )

        # ----------------------------------------------------
        # Retrieve context
        # ----------------------------------------------------

        retrieved = search_knowledge(
            question,
            match_count=MATCH_COUNT
        )

        context = "\n\n".join(
            result["content"]
            for result in retrieved
        )

        # ----------------------------------------------------
        # Generate answer
        # ----------------------------------------------------

        rag_result = generate_rag_answer(
            question,
            match_count=MATCH_COUNT,
            user_id=None
        )

        answer = rag_result.get(
            "answer",
            ""
        )

        # ----------------------------------------------------
        # Judge answer
        # ----------------------------------------------------

        evaluation = judge(
            question,
            context,
            answer
        )

        print(
            f"\nFaithfulness: "
            f"{evaluation['faithfulness']}"
        )

        print(
            f"Answer Relevance: "
            f"{evaluation['answer_relevance']}"
        )

        print(
            f"Context Relevance: "
            f"{evaluation['context_relevance']}"
        )

        print(
            f"Reason: "
            f"{evaluation['reason']}"
        )

        # ----------------------------------------------------
        # Save result
        # ----------------------------------------------------

        results.append(
            {
                "question": question,
                "type": item.get(
                    "type",
                    "unknown"
                ),
                "answer": answer,
                "retrieved_chunks": len(
                    retrieved
                ),
                "evaluation": evaluation
            }
        )

    # ========================================================
    # SAVE RESULTS
    # ========================================================

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

    total = len(results)

    avg_faithfulness = sum(
        r["evaluation"]["faithfulness"]
        for r in results
    ) / total

    avg_answer_relevance = sum(
        r["evaluation"]["answer_relevance"]
        for r in results
    ) / total

    avg_context_relevance = sum(
        r["evaluation"]["context_relevance"]
        for r in results
    ) / total

    # ========================================================
    # FINAL REPORT
    # ========================================================

    print()
    print("=" * 70)
    print("FINAL RAG QUALITY REPORT")
    print("=" * 70)

    print(
        f"\nAverage Faithfulness: "
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

    overall = (
        avg_faithfulness
        + avg_answer_relevance
        + avg_context_relevance
    ) / 3

    print(
        f"\nOverall RAG Score: "
        f"{overall:.3f}"
    )

    print(
        f"\nResults saved to:"
        f"\n{RESULT_FILE}"
    )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    run_quality_evaluation()