from phoenix.otel import register
from opentelemetry import trace


tracer_provider = register(
    project_name="shopx-rag-chatbot",
    endpoint="http://localhost:6006/v1/traces",
)

tracer = tracer_provider.get_tracer(
    "shopx-rag-chatbot"
)


def get_current_span_id():
    """
    Return the Phoenix/OpenTelemetry span ID
    for the currently active trace.
    """

    span = trace.get_current_span()

    if not span:
        return None

    context = span.get_span_context()

    if not context.is_valid:
        return None

    return format(
        context.span_id,
        "016x"
    )