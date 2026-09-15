import streamlit as st
from google import genai
from google.genai import types

from utils.tracing import (
    tracer,
    get_current_span_id,
)
from utils.rag.retrieval import search_knowledge
from utils.rag.tools import (
    search_products,
    get_product_by_name,
    get_product_price,
    get_product_stock,
    get_user_order_history,
    get_order_status,
)


def get_gemini_client():
    return genai.Client(
        api_key=st.secrets["GEMINI_API_KEY"]
    )


def generate_rag_answer(question, match_count=5, user_id=None):

    if not question.strip():
        return {
            "answer": "Please enter a question.",
            "sources": []
        }

    # ============================================================
    # ROOT RAG TRACE
    # ============================================================

    with tracer.start_as_current_span("shopx_rag_request") as root_span:
        evaluation_span_id = get_current_span_id()

        root_span.set_attribute(
            "rag.question_length",
            len(question)
        )

        root_span.set_attribute(
            "rag.match_count",
            match_count
        )

        root_span.set_attribute(
            "rag.authenticated",
            user_id is not None
        )

        # --------------------------------------------------------
        # Gemini Client
        # --------------------------------------------------------

        client = get_gemini_client()

        # --------------------------------------------------------
        # Store RAG sources used during this request
        # --------------------------------------------------------

        used_sources = []

        # ========================================================
        # RAG KNOWLEDGE BASE TOOL
        # ========================================================

        def search_shopx_knowledge(query: str) -> list:
            """
            Search the ShopX knowledge base for company policies,
            FAQs, shipping information, return policies, payment
            information, product information, and other general
            ShopX information.
            """

            with tracer.start_as_current_span(
                "rag_retrieval"
            ) as span:

                # Do not store the actual query in the trace
                # to avoid unnecessary user-data exposure.
                span.set_attribute(
                    "retrieval.query_length",
                    len(query)
                )

                results = search_knowledge(
                    query,
                    match_count=match_count
                )

                span.set_attribute(
                    "retrieval.result_count",
                    len(results)
                )

                if not results:
                    return []

                for result in results:
                    used_sources.append(result)

                return [
                    {
                        "content": result["content"],
                        "similarity": result.get("similarity")
                    }
                    for result in results
                ]

        # ========================================================
        # PRODUCT SEARCH TOOL
        # ========================================================

        def search_shopx_products(query: str) -> list:
            """
            Search the ShopX product catalog for products,
            product names, brands, categories, descriptions,
            prices, and stock availability.
            """

            with tracer.start_as_current_span(
                "product_search"
            ) as span:

                span.set_attribute(
                    "tool.name",
                    "search_shopx_products"
                )

                span.set_attribute(
                    "tool.query_length",
                    len(query)
                )

                results = search_products(
                    query,
                    limit=5
                )

                span.set_attribute(
                    "tool.result_count",
                    len(results)
                )

                return results

        # ========================================================
        # PRODUCT DETAILS TOOL
        # ========================================================

        def get_shopx_product(product_name: str) -> dict:
            """
            Get details of a specific ShopX product including
            its current price, stock, brand, category, description,
            and specifications.
            """

            with tracer.start_as_current_span(
                "product_details"
            ) as span:

                span.set_attribute(
                    "tool.name",
                    "get_shopx_product"
                )

                span.set_attribute(
                    "tool.product_name_length",
                    len(product_name)
                )

                product = get_product_by_name(
                    product_name
                )

                if not product:

                    span.set_attribute(
                        "tool.product_found",
                        False
                    )

                    return {
                        "found": False,
                        "message": "Product not found."
                    }

                span.set_attribute(
                    "tool.product_found",
                    True
                )

                return {
                    "found": True,
                    "product": product
                }

        # ========================================================
        # PRODUCT PRICE TOOL
        # ========================================================

        def get_shopx_product_price(product_name: str) -> dict:
            """
            Get the current price of a specific ShopX product.
            """

            with tracer.start_as_current_span(
                "product_price"
            ) as span:

                span.set_attribute(
                    "tool.name",
                    "get_shopx_product_price"
                )

                span.set_attribute(
                    "tool.product_name_length",
                    len(product_name)
                )

                result = get_product_price(
                    product_name
                )

                if not result:

                    span.set_attribute(
                        "tool.product_found",
                        False
                    )

                    return {
                        "found": False,
                        "message": "Product not found."
                    }

                span.set_attribute(
                    "tool.product_found",
                    True
                )

                return {
                    "found": True,
                    "product": result
                }

        # ========================================================
        # PRODUCT STOCK TOOL
        # ========================================================

        def get_shopx_product_stock(product_name: str) -> dict:
            """
            Get the current stock availability of a specific
            ShopX product.
            """

            with tracer.start_as_current_span(
                "product_stock"
            ) as span:

                span.set_attribute(
                    "tool.name",
                    "get_shopx_product_stock"
                )

                span.set_attribute(
                    "tool.product_name_length",
                    len(product_name)
                )

                result = get_product_stock(
                    product_name
                )

                if not result:

                    span.set_attribute(
                        "tool.product_found",
                        False
                    )

                    return {
                        "found": False,
                        "message": "Product not found."
                    }

                span.set_attribute(
                    "tool.product_found",
                    True
                )

                return {
                    "found": True,
                    "product": result
                }

        # ========================================================
        # USER ORDER HISTORY TOOL
        # ========================================================

        def get_my_order_history() -> dict:
            """
            Get the currently logged-in customer's complete
            order history including products, quantities,
            prices, order status, shipping information, and
            estimated delivery dates.

            This tool only accesses the authenticated user's
            own orders.
            """

            with tracer.start_as_current_span(
                "order_history"
            ) as span:

                span.set_attribute(
                    "tool.name",
                    "get_my_order_history"
                )

                if not user_id:

                    span.set_attribute(
                        "tool.authenticated",
                        False
                    )

                    return {
                        "authenticated": False,
                        "message": "The customer is not logged in."
                    }

                span.set_attribute(
                    "tool.authenticated",
                    True
                )

                orders = get_user_order_history(
                    user_id
                )

                span.set_attribute(
                    "tool.order_count",
                    len(orders)
                )

                return {
                    "authenticated": True,
                    "orders": orders
                }

        # ========================================================
        # USER ORDER STATUS TOOL
        # ========================================================

        def get_my_order_status(order_id: int) -> dict:
            """
            Get the status and delivery information for a
            specific order belonging to the currently logged-in
            customer.

            Only the authenticated customer's own order can
            be accessed.
            """

            with tracer.start_as_current_span(
                "order_status"
            ) as span:

                span.set_attribute(
                    "tool.name",
                    "get_my_order_status"
                )

                if not user_id:

                    span.set_attribute(
                        "tool.authenticated",
                        False
                    )

                    return {
                        "authenticated": False,
                        "message": "The customer is not logged in."
                    }

                span.set_attribute(
                    "tool.authenticated",
                    True
                )

                order = get_order_status(
                    order_id,
                    user_id
                )

                if not order:

                    span.set_attribute(
                        "tool.order_found",
                        False
                    )

                    return {
                        "authenticated": True,
                        "found": False,
                        "message": (
                            "Order not found or the order does not "
                            "belong to the current customer."
                        )
                    }

                span.set_attribute(
                    "tool.order_found",
                    True
                )

                return {
                    "authenticated": True,
                    "found": True,
                    "order": order
                }

        # ========================================================
        # AVAILABLE GEMINI TOOLS
        # ========================================================

        tools = [
            search_shopx_knowledge,
            search_shopx_products,
            get_shopx_product,
            get_shopx_product_price,
            get_shopx_product_stock,
            get_my_order_history,
            get_my_order_status,
        ]

        # ========================================================
        # SYSTEM INSTRUCTIONS
        # ========================================================

        system_instruction = """
You are the ShopX e-commerce AI customer support assistant.

You have access to three different information sources:

1. SHOPX KNOWLEDGE BASE

Use the knowledge-base search tool for:

- return policy
- refund policy
- shipping policy
- payment methods
- warranty
- general ShopX information
- FAQs
- company policies

2. PRODUCT CATALOG

Use product tools for:

- product price
- product availability
- product stock
- product specifications
- product details
- product search

3. CUSTOMER ORDER DATA

Use order tools for:

- customer's order history
- products the customer ordered
- order status
- order date
- order total
- payment method
- shipping address
- estimated delivery date

IMPORTANT SECURITY RULES:

- Never expose another customer's order information.
- Order tools only return information belonging to the
  currently logged-in customer.
- Never invent order information.
- Never invent product prices.
- Never invent stock quantities.
- Never invent delivery dates.
- Never guess information that is not returned by a tool.
- If information is unavailable, clearly say so.

When answering questions about the customer's orders,
use the order tools instead of the general knowledge base.

When answering questions about current product prices
or stock, use the product tools instead of the knowledge
base.

When answering general ShopX policy questions, use the
knowledge-base tool.

Be concise, helpful, and professional.
"""

        # ========================================================
        # GEMINI GENERATION
        # ========================================================

        with tracer.start_as_current_span(
            "gemini_generation"
        ) as llm_span:

            llm_span.set_attribute(
                "llm.provider",
                "Google Gemini"
            )

            llm_span.set_attribute(
                "llm.model",
                "gemini-3.6-flash"
            )

            llm_span.set_attribute(
                "llm.input_length",
                len(question)
            )

            response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=question,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    tools=tools
                )
            )

            answer = response.text or ""

            llm_span.set_attribute(
                "llm.output_length",
                len(answer)
            )

        # ========================================================
        # ROOT TRACE METADATA
        # ========================================================

        root_span.set_attribute(
            "rag.source_count",
            len(used_sources)
        )

        root_span.set_attribute(
            "rag.answer_length",
            len(answer)
        )

        # ========================================================
        # FINAL RESPONSE
        # ========================================================

        return {
    "answer": answer,
    "sources": used_sources,
    "span_id": evaluation_span_id
}