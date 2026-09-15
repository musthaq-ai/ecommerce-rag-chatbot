import streamlit as st

from utils.auth import require_admin
from utils.nav import render_sidebar
from utils.rag.ingestion import (
    ingest_document,
    extract_text_from_file
)


require_admin()

render_sidebar("admin")

st.title("🧠 Knowledge Base")

st.write(
    "Add information that the ShopX AI chatbot "
    "can use to answer customer questions."
)

st.divider()


# ==========================================
# Input Method
# ==========================================

input_method = st.radio(
    "Choose Knowledge Source",
    [
        "✍️ Manual Text",
        "📁 Upload File"
    ],
    horizontal=True
)


# ==========================================
# MANUAL TEXT
# ==========================================

if input_method == "✍️ Manual Text":

    st.subheader("✍️ Add Manual Knowledge")

    title = st.text_input(
        "Document Title",
        placeholder="Example: ShopX Shipping Policy"
    )

    source_type = st.selectbox(
        "Source Type",
        [
            "manual",
            "policy",
            "faq",
            "product",
            "website"
        ]
    )

    source_url = st.text_input(
        "Source URL (optional)"
    )

    content = st.text_area(
        "Knowledge Content",
        height=300,
        placeholder="""Example:

ShopX provides standard delivery within
3-5 business days.

Customers can track their orders from
the Orders page.

Delivery times may vary depending on
the customer's location."""
    )

    if st.button(
        "🧠 Add to Knowledge Base",
        type="primary"
    ):

        try:

            result = ingest_document(
                title=title,
                content=content,
                source_type=source_type,
                source_url=source_url or None
            )

            st.success(
                f"✅ Document added successfully! "
                f"Created {result['chunks_created']} chunks."
            )

        except Exception as e:

            st.error(
                f"❌ Failed to add document: {e}"
            )


# ==========================================
# FILE UPLOAD
# ==========================================

else:

    st.subheader("📁 Upload Knowledge File")

    uploaded_file = st.file_uploader(
        "Upload a knowledge document",
        type=[
            "pdf",
            "txt",
            "docx"
        ],
        help="Supported formats: PDF, TXT, DOCX"
    )

    if uploaded_file:

        st.success(
            f"📄 File selected: {uploaded_file.name}"
        )

        title = st.text_input(
            "Document Title",
            value=uploaded_file.name
        )

        source_type = st.selectbox(
            "Source Type",
            [
                "policy",
                "faq",
                "product",
                "website",
                "manual"
            ],
            key="file_source_type"
        )

        st.info(
            "The file will be converted to text, "
            "split into chunks, embedded, and stored "
            "in the RAG knowledge base."
        )

        if st.button(
            "🚀 Process & Add File",
            type="primary"
        ):

            try:

                with st.spinner(
                    "Extracting text and creating embeddings..."
                ):

                    extracted_text = (
                        extract_text_from_file(
                            uploaded_file
                        )
                    )

                    if not extracted_text.strip():

                        raise ValueError(
                            "No readable text was found "
                            "in the uploaded file."
                        )

                    result = ingest_document(
                        title=title,
                        content=extracted_text,
                        source_type=source_type
                    )

                st.success(
                    f"✅ File processed successfully!"
                )

                st.write(
                    f"**Document:** {title}"
                )

                st.write(
                    f"**Characters extracted:** "
                    f"{len(extracted_text):,}"
                )

                st.write(
                    f"**Chunks created:** "
                    f"{result['chunks_created']}"
                )

            except Exception as e:

                st.error(
                    f"❌ Failed to process file: {e}"
                )