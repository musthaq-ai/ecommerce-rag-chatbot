import streamlit as st
from utils.supabase_client import supabase


# ==========================================
# Sign Up
# ==========================================

def sign_up(email, password, name):

    response = supabase.auth.sign_up({
        "email": email,
        "password": password,
        "options": {
            "data": {
                "name": name
            }
        }
    })

    return response


# ==========================================
# Sign In
# ==========================================

def sign_in(email, password):

    response = supabase.auth.sign_in_with_password({
        "email": email,
        "password": password
    })

    return response


# ==========================================
# Sign Out
# ==========================================

def sign_out():

    supabase.auth.sign_out()

    st.session_state.pop("user", None)
    st.session_state.pop("session", None)
    st.session_state.pop("user_profile", None)


# ==========================================
# Authentication Check
# ==========================================

def is_authenticated():

    return "user" in st.session_state


# ==========================================
# Get Current User
# ==========================================

def get_current_user():

    return st.session_state.get("user")


# ==========================================
# Get User Profile
# ==========================================

def get_user_profile(user_id):

    response = (
        supabase
        .table("profiles")
        .select("*")
        .eq("id", user_id)
        .single()
        .execute()
    )

    return response.data


# ==========================================
# Require Authentication
# ==========================================

def require_auth():

    if not is_authenticated():

        st.warning(
            "🔐 Please login to access this page."
        )

        if st.button(
            "Go to Login",
            key="require_auth_login"
        ):

            st.switch_page("pages/login.py")

        st.stop()


# ==========================================
# Get Current User Role
# ==========================================

def get_current_user_role():

    if not is_authenticated():
        return None

    user = get_current_user()

    try:

        profile = get_user_profile(user.id)

        if profile:

            st.session_state["user_profile"] = profile

            return profile["role"]

    except Exception:

        return None

    return None
def restore_supabase_session():
    """
    Restore the authenticated Supabase session from
    Streamlit session state.
    """

    session = st.session_state.get("session")

    if not session:
        return False

    try:
        supabase.auth.set_session(
            session.access_token,
            session.refresh_token
        )

        return True

    except Exception:
        return False
# ==========================================
# Admin Check
# ==========================================

def is_admin():

    role = get_current_user_role()

    return role == "admin"


# ==========================================
# Require Admin
# ==========================================

def require_admin():

    require_auth()

    if not is_admin():

        st.error(
            "⛔ You do not have permission to access this page."
        )

        st.stop()


# ==========================================
# Require Customer (Non-Admin) User
# ==========================================

def require_user():
    """
    Use this guard on customer-only pages/features
    (shopping, cart, checkout, orders, chatbot).

    Ensures the visitor is authenticated AND is not an
    admin account. Admin accounts are intentionally
    blocked from customer shopping workflows.
    """

    require_auth()

    if is_admin():

        st.error(
            "⛔ Admin accounts cannot access customer "
            "shopping features."
        )

        if st.button(
            "🛠️ Go to Admin Dashboard",
            key="require_user_admin_redirect"
        ):
            st.switch_page("pages/admin.py")

        st.stop()