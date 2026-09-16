import os
import streamlit as st

from phoenix.otel import register
from opentelemetry import trace


# ============================================================
# Phoenix Configuration
# ============================================================

PHOENIX_API_KEY = st.secrets.get(
    "PHOENIX_API_KEY"
)

PHOENIX_COLLECTOR_ENDPOINT = st.secrets.get(
    "PHOENIX_COLLECTOR_ENDPOINT"
)

PHOENIX_PROJECT_NAME = st.secrets.get(
    "PHOENIX_PROJECT_NAME",
    "shopx-rag-chatbot"
)


# ============================================================
# Initialize Phoenix Once
# ============================================================

@st.cache_resource
def initialize_phoenix():

    # --------------------------------------------------------
    # Phoenix Cloud
    # --------------------------------------------------------

    if (
        PHOENIX_API_KEY
        and PHOENIX_COLLECTOR_ENDPOINT
    ):

        os.environ["PHOENIX_CLIENT_HEADERS"] = (
            f"api_key={PHOENIX_API_KEY}"
        )

        os.environ["PHOENIX_COLLECTOR_ENDPOINT"] = (
            PHOENIX_COLLECTOR_ENDPOINT
        )

        tracer_provider = register(
            project_name=PHOENIX_PROJECT_NAME,
            set_global_tracer_provider=True,
            auto_instrument=False,
        )

        return tracer_provider


    # --------------------------------------------------------
    # Local Phoenix fallback
    # --------------------------------------------------------

    tracer_provider = register(
        project_name=PHOENIX_PROJECT_NAME,
        endpoint="http://localhost:6006/v1/traces",
        set_global_tracer_provider=True,
        auto_instrument=False,
    )

    return tracer_provider


# ============================================================
# Start Phoenix
# ============================================================

tracer_provider = initialize_phoenix()

tracer = tracer_provider.get_tracer(
    "shopx-rag-chatbot"
)


# ============================================================
# Get Current Span ID
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