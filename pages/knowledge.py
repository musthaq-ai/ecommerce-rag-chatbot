import streamlit as st

from utils.auth import require_admin
from utils.nav import render_sidebar
from utils.rag.ingestion import (
    ingest_document,
    extract_text_from_file
)
from utils.supabase_client import supabase


# ============================================================
# ADMIN ACCESS
# ============================================================

require_admin()

render_sidebar("admin")


# ============================================================
# PAGE CONFIG
# ============================================================

st.title("🧠 Knowledge Base")

st.write(
    "Manage the information used by the ShopX AI chatbot."
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .kb-card {
        padding: 18px;
        border: 1px solid rgba(128,128,128,0.25);
        border-radius: 14px;
        margin-bottom: 12px;
        background: rgba(128,128,128,0.04);
    }

    .kb-title {
        font-size: 20px;
        font-weight: 700;
        margin-bottom: 4px;
    }

    .kb-meta {
        color: #777;
        font-size: 14px;
    }

    .stat-card {
        padding: 18px;
        border-radius: 14px;
        border: 1px solid rgba(128,128,128,0.25);
        text-align: center;
        background: rgba(128,128,128,0.04);
    }

    .stat-number {
        font-size: 28px;
        font-weight: 700;
    }

    .stat-label {
        font-size: 13px;
        color: #777;
    }

    .chunk-box {
        padding: 14px;
        border-radius: 10px;
        border: 1px solid rgba(128,128,128,0.2);
        margin-bottom: 10px;
        background: rgba(128,128,128,0.03);
    }

    .chunk-number {
        font-weight: 700;
        margin-bottom: 8px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_documents():

    response = (
        supabase
        .table("knowledge_documents")
        .select("*")
        .order("created_at", desc=True)
        .execute()
    )

    return response.data or []


def get_chunks(document_id):

    response = (
        supabase
        .table("knowledge_chunks")
        .select("*")
        .eq("document_id", document_id)
        .order("chunk_index")
        .execute()
    )

    return response.data or []


def delete_document(document_id):

    # --------------------------------------------------------
    # Delete chunks first
    # --------------------------------------------------------

    supabase \
        .table("knowledge_chunks") \
        .delete() \
        .eq("document_id", document_id) \
        .execute()

    # --------------------------------------------------------
    # Delete document
    # --------------------------------------------------------

    supabase \
        .table("knowledge_documents") \
        .delete() \
        .eq("id", document_id) \
        .execute()


# ============================================================
# LOAD CURRENT KNOWLEDGE BASE
# ============================================================

try:

    documents = get_documents()

except Exception as e:

    st.error(
        f"❌ Failed to load knowledge base: {e}"
    )

    documents = []


# ============================================================
# STATISTICS
# ============================================================

total_documents = len(documents)

total_chunks = 0

for document in documents:

    try:

        chunk_response = (
            supabase
            .table("knowledge_chunks")
            .select(
                "id",
                count="exact"
            )
            .eq(
                "document_id",
                document["id"]
            )
            .execute()
        )

        total_chunks += (
            chunk_response.count or 0
        )

    except Exception:

        pass


st.markdown("### 📊 Knowledge Base Overview")

col1, col2, col3 = st.columns(3)

with col1:

    st.markdown(
        f"""
        <div class="stat-card">
            <div class="stat-number">
                {total_documents}
            </div>
            <div class="stat-label">
                Documents
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


with col2:

    st.markdown(
        f"""
        <div class="stat-card">
            <div class="stat-number">
                {total_chunks}
            </div>
            <div class="stat-label">
                Total Chunks
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


with col3:

    st.markdown(
        """
        <div class="stat-card">
            <div class="stat-number">
                768
            </div>
            <div class="stat-label">
                Embedding Dimensions
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


st.divider()


# ============================================================
# TABS
# ============================================================

tab_add, tab_existing = st.tabs(
    [
        "➕ Add Knowledge",
        "📚 Current Knowledge Base"
    ]
)


# ============================================================
# ADD KNOWLEDGE
# ============================================================

with tab_add:

    st.subheader("Add Knowledge")

    input_method = st.radio(
        "Choose Knowledge Source",
        [
            "✍️ Manual Text",
            "📁 Upload File"
        ],
        horizontal=True
    )


    # ========================================================
    # MANUAL TEXT
    # ========================================================

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

            if not title.strip():

                st.warning(
                    "Please enter a document title."
                )

            elif not content.strip():

                st.warning(
                    "Please enter knowledge content."
                )

            else:

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

                    st.rerun()

                except Exception as e:

                    st.error(
                        f"❌ Failed to add document: {e}"
                    )


    # ========================================================
    # FILE UPLOAD
    # ========================================================

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
                        "✅ File processed successfully!"
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

                    st.rerun()

                except Exception as e:

                    st.error(
                        f"❌ Failed to process file: {e}"
                    )


# ============================================================
# CURRENT KNOWLEDGE BASE
# ============================================================

with tab_existing:

    st.subheader("📚 Current Knowledge Base")

    if not documents:

        st.info(
            "📭 No knowledge documents have been added yet."
        )

    else:

        st.write(
            f"{len(documents)} document(s) currently indexed."
        )

        st.divider()


        # ====================================================
        # DOCUMENT LIST
        # ====================================================

        for document in documents:

            document_id = document.get("id")

            title = document.get(
                "title",
                "Untitled Document"
            )

            source_type = document.get(
                "source_type",
                "unknown"
            )

            source_url = document.get(
                "source_url"
            )

            created_at = document.get(
                "created_at",
                "Unknown"
            )

            updated_at = document.get(
                "updated_at",
                "Unknown"
            )


            # ------------------------------------------------
            # Get chunks
            # ------------------------------------------------

            chunks = get_chunks(
                document_id
            )

            chunk_count = len(chunks)


            # ------------------------------------------------
            # Document Card
            # ------------------------------------------------

            st.markdown(
                f"""
                <div class="kb-card">

                    <div class="kb-title">
                        📄 {title}
                    </div>

                    <div class="kb-meta">
                        Source: {source_type}
                        &nbsp; • &nbsp;
                        {chunk_count} chunks
                    </div>

                </div>
                """,
                unsafe_allow_html=True
            )


            col_info, col_view, col_delete = st.columns(
                [5, 1.5, 1.5]
            )


            # ------------------------------------------------
            # Information
            # ------------------------------------------------

            with col_info:

                st.caption(
                    f"Created: {created_at}"
                )

                if updated_at:

                    st.caption(
                        f"Updated: {updated_at}"
                    )

                if source_url:

                    st.caption(
                        f"Source URL: {source_url}"
                    )


            # ------------------------------------------------
            # View
            # ------------------------------------------------

            with col_view:

                view_key = (
                    f"view_{document_id}"
                )

                if st.button(
                    "👁️ View",
                    key=view_key,
                    use_container_width=True
                ):

                    st.session_state[
                        f"show_chunks_{document_id}"
                    ] = not st.session_state.get(
                        f"show_chunks_{document_id}",
                        False
                    )


            # ------------------------------------------------
            # Delete
            # ------------------------------------------------

            with col_delete:

                delete_key = (
                    f"delete_{document_id}"
                )

                if st.button(
                    "🗑️ Delete",
                    key=delete_key,
                    use_container_width=True
                ):

                    st.session_state[
                        f"confirm_delete_{document_id}"
                    ] = True


            # =================================================
            # DELETE CONFIRMATION
            # =================================================

            if st.session_state.get(
                f"confirm_delete_{document_id}",
                False
            ):

                st.warning(
                    f"⚠️ Are you sure you want to delete "
                    f"**{title}**?\n\n"
                    "This will permanently delete the document "
                    "and all of its chunks."
                )

                confirm_col, cancel_col = st.columns(2)

                with confirm_col:

                    if st.button(
                        "Yes, Delete Permanently",
                        key=f"confirm_{document_id}",
                        type="primary",
                        use_container_width=True
                    ):

                        try:

                            with st.spinner(
                                "Deleting document..."
                            ):

                                delete_document(
                                    document_id
                                )

                            st.success(
                                f"✅ '{title}' deleted successfully."
                            )

                            st.session_state[
                                f"confirm_delete_{document_id}"
                            ] = False

                            st.rerun()

                        except Exception as e:

                            st.error(
                                f"❌ Failed to delete "
                                f"'{title}': {e}"
                            )


                with cancel_col:

                    if st.button(
                        "Cancel",
                        key=f"cancel_{document_id}",
                        use_container_width=True
                    ):

                        st.session_state[
                            f"confirm_delete_{document_id}"
                        ] = False

                        st.rerun()


            # =================================================
            # VIEW CHUNKS
            # =================================================

            if st.session_state.get(
                f"show_chunks_{document_id}",
                False
            ):

                st.markdown(
                    "#### 🧩 Document Chunks"
                )

                if not chunks:

                    st.info(
                        "This document has no chunks."
                    )

                else:

                    st.caption(
                        f"{len(chunks)} chunks found."
                    )

                    for chunk in chunks:

                        chunk_index = chunk.get(
                            "chunk_index",
                            0
                        )

                        chunk_content = chunk.get(
                            "content",
                            ""
                        )

                        embedding = chunk.get(
                            "embedding"
                        )

                        created = chunk.get(
                            "created_at",
                            "Unknown"
                        )

                        with st.expander(
                            f"Chunk {chunk_index + 1}"
                        ):

                            st.markdown(
                                f"""
                                <div class="chunk-box">

                                    <div class="chunk-number">
                                        🧩 Chunk {chunk_index + 1}
                                    </div>

                                </div>
                                """,
                                unsafe_allow_html=True
                            )

                            st.text_area(
                                "Chunk Content",
                                value=chunk_content,
                                height=180,
                                disabled=True,
                                key=(
                                    f"chunk_content_"
                                    f"{document_id}_"
                                    f"{chunk_index}"
                                )
                            )

                            col_a, col_b = st.columns(2)

                            with col_a:

                                st.caption(
                                    f"Chunk Index: {chunk_index}"
                                )

                            with col_b:

                                st.caption(
                                    f"Created: {created}"
                                )

                            if embedding is not None:

                                st.caption(
                                    "🧠 Embedding: "
                                    "768-dimensional vector"
                                )

            st.divider()