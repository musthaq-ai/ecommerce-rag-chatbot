from google import genai
from google.genai import types
import streamlit as st
import json


client = genai.Client(
    api_key=st.secrets["GEMINI_API_KEY"]
)


def _judge(prompt):

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0,
            response_mime_type="application/json"
        )
    )

    text = response.text.strip()

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
            "score": 0.0,
            "reason": "Invalid evaluator response."
        }


def evaluate_tool_selection(
    question,
    expected_tool,
    actual_tool
):
    """
    Evaluate whether the correct tool was selected.
    """

    prompt = f"""
You are evaluating tool selection for an
e-commerce AI assistant.

USER QUESTION:
{question}

EXPECTED TOOL:
{expected_tool}

ACTUAL TOOL:
{actual_tool}

Determine whether the correct tool was selected.

Return ONLY JSON:

{{
    "score": 0.0,
    "reason": "short explanation"
}}

Scoring:

1.0 = correct tool
0.5 = partially appropriate
0.0 = incorrect tool
"""

    return _judge(prompt)


def evaluate_tool_result(
    question,
    tool_result,
    answer
):
    """
    Evaluate whether the chatbot answer correctly
    reflects the result returned by the tool.
    """

    prompt = f"""
You are evaluating an e-commerce AI assistant.

USER QUESTION:
{question}

TOOL RESULT:
{tool_result}

CHATBOT ANSWER:
{answer}

Determine whether the chatbot answer correctly
uses the information returned by the tool.

Return ONLY JSON:

{{
    "score": 0.0,
    "reason": "short explanation"
}}

Scoring:

1.0 = answer correctly reflects the tool result
0.5 = partially correct
0.0 = contradicts or ignores the tool result
"""

    return _judge(prompt)