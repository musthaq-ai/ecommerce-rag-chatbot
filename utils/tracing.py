import os
import streamlit as st

from phoenix.otel import register
from opentelemetry import trace


# ============================================================
# Phoenix Cloud Configuration
# ============================================================

PHOENIX_API_KEY = st.secrets.get("PHOENIX_API_KEY")

PHOENIX_COLLECTOR_ENDPOINT = st.secrets.get(
    "PHOENIX_COLLECTOR_ENDPOINT"
)

PHOENIX_PROJECT_NAME = st.secrets.get(
    "PHOENIX_PROJECT_NAME",
    "shopx-rag-chatbot"
)


# ============================================================
# Configure Phoenix
# ============================================================

if PHOENIX_API_KEY and PHOENIX_COLLECTOR_ENDPOINT:

    # Phoenix authentication
    os.environ["PHOENIX_CLIENT_HEADERS"] = (
        f"api_key={PHOENIX_API_KEY}"
    )

    # Phoenix collector
    os.environ["PHOENIX_COLLECTOR_ENDPOINT"] = (
        PHOENIX_COLLECTOR_ENDPOINT
    )

    tracer_provider = register(
        project_name=PHOENIX_PROJECT_NAME,
        auto_instrument=False,
    )

else:

    # Local Phoenix
    tracer_provider = register(
        project_name=PHOENIX_PROJECT_NAME,
        endpoint="http://localhost:6006/v1/traces",
        auto_instrument=False,
    )


# ============================================================
# Tracer
# ============================================================

tracer = tracer_provider.get_tracer(
    "shopx-rag-chatbot"
)


# ============================================================
# Current Span ID
# ============================================================

def get_current_span_id():

    span = trace.get_current_span()

    if span is None:
        return None

    context = span.get_span_context()

    if not context.is_valid:
        return None

    return format(
        context.span_id,
        "016x"
    )