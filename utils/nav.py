import streamlit as st

from utils.auth import sign_out


# =========================================================
# HIDE STREAMLIT DEFAULT NAVIGATION
# =========================================================

_HIDE_DEFAULT_NAV_CSS = """
<style>

[data-testid="stSidebarNav"] {
    display: none;
}

/* Sidebar container */
section[data-testid="stSidebar"] {
    border-right: 1px solid rgba(128, 128, 128, 0.15);
}

/* Sidebar content */
section[data-testid="stSidebar"] > div {
    padding-top: 1.5rem;
    padding-left: 1rem;
    padding-right: 1rem;
}


/* =====================================================
   SHOPX BRAND
   ===================================================== */

.shopx-sidebar-brand {
    font-size: 1.55rem;
    font-weight: 800;
    letter-spacing: -0.5px;
    margin-bottom: 0.15rem;
}

.shopx-sidebar-subtitle {
    font-size: 0.78rem;
    color: #6b7280;
    margin-bottom: 1rem;
}


/* =====================================================
   ROLE BADGE
   ===================================================== */

.shopx-role-user {
    display: inline-block;
    padding: 0.25rem 0.65rem;
    border-radius: 999px;
    font-size: 0.72rem;
    font-weight: 600;
    background: #eef2ff;
    color: #4338ca;
}

.shopx-role-admin {
    display: inline-block;
    padding: 0.25rem 0.65rem;
    border-radius: 999px;
    font-size: 0.72rem;
    font-weight: 600;
    background: #fff7ed;
    color: #c2410c;
}


/* =====================================================
   NAVIGATION LABEL
   ===================================================== */

.shopx-nav-label {
    font-size: 0.72rem;
    font-weight: 700;
    color: #9ca3af;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin-top: 1rem;
    margin-bottom: 0.5rem;
}


/* =====================================================
   SIDEBAR BUTTONS
   ===================================================== */

section[data-testid="stSidebar"] .stButton > button {
    border-radius: 10px;
    border: 1px solid transparent;
    min-height: 42px;
    font-weight: 500;
    text-align: left;
    padding-left: 0.85rem;
}

section[data-testid="stSidebar"] .stButton > button:hover {
    border-color: rgba(128, 128, 128, 0.2);
}


/* =====================================================
   LOGOUT BUTTON
   ===================================================== */

.shopx-logout {
    margin-top: 1rem;
}

</style>
"""


# =========================================================
# SIDEBAR
# =========================================================

def render_sidebar(role):

    st.markdown(
        _HIDE_DEFAULT_NAV_CSS,
        unsafe_allow_html=True
    )

    with st.sidebar:

        # -------------------------------------------------
        # BRAND
        # -------------------------------------------------

        if role == "admin":

            st.markdown(
                '<div class="shopx-sidebar-brand">'
                '🛠️ ShopX Admin'
                '</div>',
                unsafe_allow_html=True
            )

            st.markdown(
                '<div class="shopx-sidebar-subtitle">'
                'Store management & AI knowledge'
                '</div>',
                unsafe_allow_html=True
            )

            st.markdown(
                '<span class="shopx-role-admin">'
                'ADMIN'
                '</span>',
                unsafe_allow_html=True
            )

        else:

            st.markdown(
                '<div class="shopx-sidebar-brand">'
                '🛍️ ShopX'
                '</div>',
                unsafe_allow_html=True
            )

            st.markdown(
                '<div class="shopx-sidebar-subtitle">'
                'Smart shopping powered by AI'
                '</div>',
                unsafe_allow_html=True
            )

            st.markdown(
                '<span class="shopx-role-user">'
                'CUSTOMER'
                '</span>',
                unsafe_allow_html=True
            )


        st.divider()


        # =================================================
        # ADMIN NAVIGATION
        # =================================================

        if role == "admin":

            st.markdown(
                '<div class="shopx-nav-label">'
                'Administration'
                '</div>',
                unsafe_allow_html=True
            )

            st.page_link(
                "pages/admin.py",
                label="🛠️  Admin Dashboard"
            )

            st.page_link(
                "pages/knowledge.py",
                label="🧠  Knowledge Base"
            )


        # =================================================
        # USER NAVIGATION
        # =================================================

        else:

            st.markdown(
                '<div class="shopx-nav-label">'
                'Shopping'
                '</div>',
                unsafe_allow_html=True
            )

            st.page_link(
                "app.py",
                label="🏠  Home"
            )

            st.page_link(
                "pages/products.py",
                label="🛍️  Products"
            )

            st.page_link(
                "pages/cart.py",
                label="🛒  Cart"
            )

            st.page_link(
                "pages/orders.py",
                label="📋  My Orders"
            )

            st.markdown(
                '<div class="shopx-nav-label">'
                'AI Assistant'
                '</div>',
                unsafe_allow_html=True
            )

            st.page_link(
                "pages/chatbot.py",
                label="🤖  Chatbot"
            )


        # =================================================
        # LOGOUT
        # =================================================

        st.divider()

        if st.button(
            "🚪  Logout",
            use_container_width=True,
            key="sidebar_logout_btn"
        ):

            sign_out()

            st.switch_page(
                "pages/login.py"
            )