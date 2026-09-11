import streamlit as st

from utils.auth import (
    sign_in,
    sign_up
)


st.set_page_config(
    page_title="Login - ShopX",
    page_icon="🔐",
    layout="centered"
)


st.title("🛍️ ShopX")

st.subheader("Account")


# ==========================================
# Login / Signup tabs
# ==========================================

login_tab, signup_tab = st.tabs(
    ["🔐 Login", "📝 Create Account"]
)


# ==========================================
# Login
# ==========================================

with login_tab:

    st.markdown("### Welcome back!")

    email = st.text_input(
        "Email",
        placeholder="you@example.com",
        key="login_email"
    )

    password = st.text_input(
        "Password",
        type="password",
        placeholder="Enter your password",
        key="login_password"
    )

    if st.button(
        "🔐 Login",
        use_container_width=True
    ):

        if not email.strip():
            st.error("Please enter your email.")
            st.stop()

        if not password:
            st.error("Please enter your password.")
            st.stop()

        try:

            response = sign_in(
                email.strip(),
                password
            )

            user = response.user
            session = response.session

            if user:

                st.session_state.user = user
                st.session_state.session = session

                st.success("Login successful!")

                st.switch_page("app.py")

        except Exception as e:

            st.error(
                f"Login failed: {str(e)}"
            )


# ==========================================
# Signup
# ==========================================

with signup_tab:

    st.markdown("### Create your ShopX account")

    name = st.text_input(
        "Full Name",
        placeholder="Enter your name",
        key="signup_name"
    )

    email = st.text_input(
        "Email",
        placeholder="you@example.com",
        key="signup_email"
    )

    password = st.text_input(
        "Password",
        type="password",
        placeholder="Create a password",
        key="signup_password"
    )

    confirm_password = st.text_input(
        "Confirm Password",
        type="password",
        placeholder="Re-enter your password",
        key="signup_confirm_password"
    )

    if st.button(
        "📝 Create Account",
        use_container_width=True
    ):

        if not name.strip():
            st.error("Please enter your name.")
            st.stop()

        if not email.strip():
            st.error("Please enter your email.")
            st.stop()

        if len(password) < 6:
            st.error(
                "Password must contain at least 6 characters."
            )
            st.stop()

        if password != confirm_password:
            st.error(
                "Passwords do not match."
            )
            st.stop()

        try:

            response = sign_up(
                email.strip(),
                password,
                name.strip()
            )

            if response.user:

                st.success(
                    "Account created successfully!"
                )

                if response.session is None:

                    st.info(
                        "Please check your email and "
                        "confirm your account before logging in."
                    )

                else:

                    st.session_state.user = response.user
                    st.session_state.session = response.session

                    st.switch_page("app.py")

        except Exception as e:

            st.error(
                f"Signup failed: {str(e)}"
            )