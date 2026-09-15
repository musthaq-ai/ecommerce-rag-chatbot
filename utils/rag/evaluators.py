from google import genai
from google.genai import types
import streamlit as st
import json


client = genai.Client(
    api_key=st.secrets["GEMINI_API_KEY"]
)


def _judge(prompt):
    """
    Send an evaluation prompt to Gemini and
    return a structured evaluation result.
    """

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0,
            response_mime_type="application/json"
        )
    )

    text = response.text.strip()

    try:
        return json.loads(text)

    except json.JSONDecodeError:

        text = text.replace(
            "```json",
            ""
        ).replace(
            "```",
            ""
        ).strip()

        return json.loads(text)


def evaluate_faithfulness(
    question,
    context,
    answer
):
    """
    Measures whether the answer is supported
    by the retrieved context.
    """

    prompt = f"""
You are evaluating the faithfulness of an
e-commerce RAG chatbot.

QUESTION:
{question}

RETRIEVED CONTEXT:
{context}

CHATBOT ANSWER:
{answer}

Determine whether the chatbot answer is supported
by the retrieved context.

Return ONLY JSON:

{{
    "score": 0.0,
    "reason": "short explanation"
}}

Scoring:

1.0 = completely supported
0.5 = partially supported
0.0 = unsupported or hallucinated
"""

    return _judge(prompt)


def evaluate_answer_relevance(
    question,
    answer
):
    """
    Measures whether the chatbot answer
    directly answers the user's question.
    """

    prompt = f"""
You are evaluating answer relevance for an
e-commerce chatbot.

QUESTION:
{question}

CHATBOT ANSWER:
{answer}

Determine whether the answer directly addresses
the user's question.

Return ONLY JSON:

{{
    "score": 0.0,
    "reason": "short explanation"
}}

Scoring:

1.0 = directly answers the question
0.5 = partially answers the question
0.0 = does not answer the question
"""

    return _judge(prompt)


def evaluate_context_relevance(
    question,
    context
):
    """
    Measures whether the retrieved context
    is relevant to the user's question.
    """

    prompt = f"""
You are evaluating retrieval quality for an
e-commerce RAG system.

QUESTION:
{question}

RETRIEVED CONTEXT:
{context}

Determine whether the retrieved context is
useful for answering the question.

Return ONLY JSON:

{{
    "score": 0.0,
    "reason": "short explanation"
}}

Scoring:

1.0 = highly relevant
0.5 = partially relevant
0.0 = irrelevant
"""

    return _judge(prompt)