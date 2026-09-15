import streamlit as st

from utils.auth import (
    require_user,
    get_current_user,
    get_current_user_role,
    restore_supabase_session,
)
from utils.nav import render_sidebar

from utils.chat_history import (
    create_conversation,
    get_user_conversations,
    get_conversation_messages,
    save_message,
    save_feedback,
    get_message_feedback,
)

from utils.rag.generator import generate_rag_answer


# =========================================================
# Authentication (customer-only)
# =========================================================

require_user()

if not restore_supabase_session():
    st.error(
        "Your login session could not be restored. "
        "Please login again."
    )
    st.stop()


# =========================================================
# Page Configuration
# =========================================================

st.set_page_config(
    page_title="ShopX AI Assistant",
    page_icon="🤖",
    layout="wide",
)

render_sidebar(get_current_user_role())


# =========================================================
# Current User
# =========================================================

user = get_current_user()

if not user:
    st.error("Unable to identify the logged-in user.")
    st.stop()

user_id = user.id


# =========================================================
# Initialize Conversation
# =========================================================

if "conversation_id" not in st.session_state:

    conversation = create_conversation(user_id)

    if not conversation:
        st.error(
            "Unable to create a chat conversation."
        )
        st.stop()

    st.session_state.conversation_id = conversation["id"]

    st.session_state.chat_messages = []

    st.session_state.chat_messages_loaded = False


# =========================================================
# Load Conversation
# =========================================================

if (
    "chat_messages_loaded" not in st.session_state
    or not st.session_state.chat_messages_loaded
):

    messages = get_conversation_messages(
        st.session_state.conversation_id
    )

    st.session_state.chat_messages = messages

    st.session_state.chat_messages_loaded = True


# =========================================================
# Header
# =========================================================

st.title("🤖 ShopX AI Assistant")

st.write(
    "Ask me anything about ShopX products, "
    "orders, shipping, returns, payments, "
    "and store policies."
)

st.divider()


# =========================================================
# Sidebar
# =========================================================

with st.sidebar:

    st.header("💬 Conversations")

    # -----------------------------------------------------
    # New Chat
    # -----------------------------------------------------

    if st.button(
        "➕ New Chat",
        use_container_width=True,
    ):

        conversation = create_conversation(user_id)

        if conversation:

            st.session_state.conversation_id = (
                conversation["id"]
            )

            st.session_state.chat_messages = []

            st.session_state.chat_messages_loaded = True

            st.rerun()

        else:

            st.error(
                "Unable to create a new conversation."
            )


    st.divider()


    # -----------------------------------------------------
    # Previous Conversations
    # -----------------------------------------------------

    conversations = get_user_conversations(
        user_id
    )

    if conversations:

        st.subheader("Previous Chats")

        for conversation in conversations:

            conversation_id = conversation["id"]

            created_at = conversation.get(
                "created_at",
                ""
            )

            label = f"Chat {conversation_id}"

            if created_at:

                label = (
                    f"Chat {conversation_id} "
                    f"• {created_at[:10]}"
                )

            if conversation_id == (
                st.session_state.conversation_id
            ):

                label = f"🟢 {label}"

            else:

                label = f"💬 {label}"


            if st.button(
                label,
                key=f"conversation_{conversation_id}",
                use_container_width=True,
            ):

                st.session_state.conversation_id = (
                    conversation_id
                )

                messages = get_conversation_messages(
                    conversation_id
                )

                st.session_state.chat_messages = messages

                st.session_state.chat_messages_loaded = True

                st.rerun()

    else:

        st.caption(
            "No previous conversations."
        )


# =========================================================
# Display Chat History
# =========================================================

for message in st.session_state.chat_messages:

    role = message["role"]

    with st.chat_message(role):

        st.markdown(
            message["content"]
        )

        # -------------------------------------------------
        # Feedback for assistant messages
        # -------------------------------------------------

        if role == "assistant":

            message_id = message.get("id")

            if message_id:

                existing_feedback = (
                    get_message_feedback(
                        message_id,
                        user_id
                    )
                )

                if existing_feedback:

                    if existing_feedback["rating"] == 1:

                        st.caption(
                            "👍 You liked this response."
                        )

                    elif existing_feedback["rating"] == -1:

                        st.caption(
                            "👎 You didn't like this response."
                        )

                else:

                    col1, col2 = st.columns(2)

                    with col1:

                        if st.button(
                            "👍 Helpful",
                            key=f"like_{message_id}",
                        ):

                            try:

                                save_feedback(
                                    message_id,
                                    user_id,
                                    1,
                                )

                                st.success(
                                    "Thanks for your feedback!"
                                )

                                st.rerun()

                            except Exception as e:

                                st.error(
                                    f"Unable to save feedback: {e}"
                                )


                    with col2:

                        if st.button(
                            "👎 Not Helpful",
                            key=f"dislike_{message_id}",
                        ):

                            try:

                                save_feedback(
                                    message_id,
                                    user_id,
                                    -1,
                                )

                                st.success(
                                    "Thanks for your feedback!"
                                )

                                st.rerun()

                            except Exception as e:

                                st.error(
                                    f"Unable to save feedback: {e}"
                                )


# =========================================================
# User Input
# =========================================================

question = st.chat_input(
    "Ask ShopX AI..."
)


# =========================================================
# Process Question
# =========================================================

if question:

    # -----------------------------------------------------
    # Display User Message
    # -----------------------------------------------------

    with st.chat_message("user"):

        st.markdown(question)


    # -----------------------------------------------------
    # Save User Message
    # -----------------------------------------------------

    try:

        user_message = save_message(
            st.session_state.conversation_id,
            "user",
            question,
        )

        st.session_state.chat_messages.append(
            user_message
        )

    except Exception as e:

        st.error(
            f"Unable to save your message: {e}"
        )

        st.stop()


    # -----------------------------------------------------
    # Generate AI Response
    # -----------------------------------------------------

    with st.chat_message("assistant"):

        with st.spinner(
            "Thinking..."
        ):

            try:

                result = generate_rag_answer(
                    question,
                    match_count=5,
                    user_id=user_id,
                )

                answer = result["answer"]

                st.markdown(answer)


                # -----------------------------------------
                # Sources
                # -----------------------------------------

                if result.get("sources"):

                    with st.expander(
                        "📚 Sources used"
                    ):

                        for source in result["sources"]:

                            similarity = source.get(
                                "similarity"
                            )

                            if similarity is not None:

                                st.write(
                                    f"Similarity: "
                                    f"{similarity:.3f}"
                                )

                            st.write(
                                source["content"]
                            )

                            st.divider()


                # -----------------------------------------
                # Save Assistant Message
                # -----------------------------------------

                assistant_message = save_message(
                    st.session_state.conversation_id,
                    "assistant",
                    answer,
                )


                st.session_state.chat_messages.append(
                    assistant_message
                )


                # -----------------------------------------
                # Feedback buttons for new answer
                # -----------------------------------------

                message_id = assistant_message["id"]

                col1, col2 = st.columns(2)

                with col1:

                    if st.button(
                        "👍 Helpful",
                        key=f"new_like_{message_id}",
                    ):

                        try:

                            save_feedback(
                                message_id,
                                user_id,
                                1,
                            )

                            st.success(
                                "Thanks for your feedback!"
                            )

                            st.rerun()

                        except Exception as e:

                            st.error(
                                f"Unable to save feedback: {e}"
                            )


                with col2:

                    if st.button(
                        "👎 Not Helpful",
                        key=f"new_dislike_{message_id}",
                    ):

                        try:

                            save_feedback(
                                message_id,
                                user_id,
                                -1,
                            )

                            st.success(
                                "Thanks for your feedback!"
                            )

                            st.rerun()

                        except Exception as e:

                            st.error(
                                f"Unable to save feedback: {e}"
                            )


            except Exception as e:

                error_message = (
                    f"❌ Failed to generate answer: {e}"
                )

                st.error(error_message)