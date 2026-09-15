from utils.supabase_client import supabase


# =========================================================
# Create Conversation
# =========================================================

def create_conversation(user_id):
    """
    Create a new conversation for the logged-in user.
    """

    if not user_id:
        return None

    response = (
        supabase
        .table("conversations")
        .insert({
            "user_id": user_id
        })
        .execute()
    )

    if response.data:
        return response.data[0]

    return None


# =========================================================
# Get User Conversations
# =========================================================

def get_user_conversations(user_id, limit=20):
    """
    Get conversations belonging only to the logged-in user.
    """

    if not user_id:
        return []

    response = (
        supabase
        .table("conversations")
        .select("*")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )

    return response.data or []


# =========================================================
# Get Conversation Messages
# =========================================================

def get_conversation_messages(conversation_id):
    """
    Get all messages from a conversation.
    """

    if not conversation_id:
        return []

    response = (
        supabase
        .table("messages")
        .select("*")
        .eq("conversation_id", conversation_id)
        .order("created_at", desc=False)
        .execute()
    )

    return response.data or []


# =========================================================
# Save Message
# =========================================================

def save_message(conversation_id, role, content):
    """
    Save a user or assistant message.
    """

    if not conversation_id or not content:
        return None

    response = (
        supabase
        .table("messages")
        .insert({
            "conversation_id": conversation_id,
            "role": role,
            "content": content
        })
        .execute()
    )

    if response.data:
        return response.data[0]

    return None


# =========================================================
# Save Feedback
# =========================================================

def save_feedback(
    message_id,
    user_id,
    rating,
    reason=None
):
    """
    Save feedback for an assistant message.

    rating:
        1  = Helpful
       -1  = Not Helpful
    """

    if not message_id or not user_id:
        return None

    response = (
        supabase
        .table("feedback")
        .insert({
            "message_id": message_id,
            "user_id": user_id,
            "rating": rating,
            "reason": reason
        })
        .execute()
    )

    if response.data:
        return response.data[0]

    return None


# =========================================================
# Get Message Feedback
# =========================================================

def get_message_feedback(
    message_id,
    user_id
):
    """
    Get feedback submitted by the current user
    for a specific message.
    """

    if not message_id or not user_id:
        return None

    response = (
        supabase
        .table("feedback")
        .select("*")
        .eq("message_id", message_id)
        .eq("user_id", user_id)
        .limit(1)
        .execute()
    )

    if response.data:
        return response.data[0]

    return None