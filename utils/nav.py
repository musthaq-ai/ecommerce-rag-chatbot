import streamlit as st

from utils.auth import sign_out


# ==========================================
# Hide Streamlit's default auto-generated
# multipage nav (it lists every page in
# pages/ for every user regardless of role).
# We render our own role-aware nav instead.
# ==========================================

_HIDE_DEFAULT_NAV_CSS = """
<style>
[data-testid="stSidebarNav"] {
    display: none;
}
</style>
"""


def render_sidebar(role):
    """
    Render a role-aware sidebar.

    NOTE: This is a UX convenience only — it hides links
    the current role shouldn't use. It is NOT the security
    boundary. Every page must still call require_user() or
    require_admin() at the top, since a user can always type
    a page URL directly regardless of what the sidebar shows.
    """

    st.markdown(_HIDE_DEFAULT_NAV_CSS, unsafe_allow_html=True)

    with st.sidebar:

        st.markdown("### 🛍️ ShopX")
        st.caption(f"Role: {role or 'unknown'}")

        st.divider()

        if role == "admin":

            st.page_link(
                "pages/admin.py",
                label="🛠️ Admin Dashboard"
            )

            st.page_link(
                "pages/knowledge.py",
                label="🧠 Knowledge Base"
            )

        else:

            st.page_link("app.py", label="🏠 Home")
            st.page_link("pages/products.py", label="🛍️ Products")
            st.page_link("pages/cart.py", label="🛒 Cart")
            st.page_link("pages/orders.py", label="📋 My Orders")
            st.page_link("pages/chatbot.py", label="🤖 Chatbot")

        st.divider()

        if st.button(
            "🚪 Logout",
            use_container_width=True,
            key="sidebar_logout_btn"
        ):
            sign_out()
            st.switch_page("pages/login.py")
