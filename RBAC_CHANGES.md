# RBAC Implementation — What Changed

This implements the pending task from the project brief (section 55):
complete role-based access control so admins can't shop and users can't
reach admin tooling — at the UI, direct-page, and database levels.

## New files

- **`utils/nav.py`** — `render_sidebar(role)`. Hides Streamlit's default
  auto-generated page list (`[data-testid="stSidebarNav"]`) and renders a
  role-aware sidebar instead: admins see Admin Dashboard + Knowledge Base;
  everyone else sees Home/Products/Cart/My Orders/Chatbot. This is a UX
  convenience only, **not** the security boundary — see below.
- **`migrations/002_rbac_orders.sql`** — SQL to run in the Supabase SQL
  editor. Rebuilds the `orders` INSERT policy so `auth.uid() = user_id AND
  NOT is_admin()`, so an admin's order insert is rejected by Postgres even
  if every app-layer check were somehow bypassed.

## Changed files

- **`utils/auth.py`** — added `require_user()`. Like `require_admin()`,
  but blocks *admins* instead of unauthenticated visitors, with a button
  that routes them to the Admin Dashboard.
- **`app.py`** — after login, admins are shown a short notice and a
  button to the Admin Dashboard instead of the storefront; the storefront
  (featured products, Shop Now, cart) only renders for non-admin roles.
- **`pages/products.py`, `product_details.py`, `cart.py`, `checkout.py`,
  `order_confirmation.py`, `orders.py`, `chatbot.py`** — swapped
  `require_auth()` → `require_user()` and added `render_sidebar(role)`.
  These are exactly the customer-shopping pages called out in the spec;
  an admin hitting any of these URLs directly now gets redirected, not
  just hidden from the sidebar.
- **`pages/admin.py`, `pages/knowledge.py`** — unchanged auth
  (`require_admin()` was already correct and is left as-is), just added
  `render_sidebar("admin")` for the matching nav.

## What was intentionally left alone

- RAG chatbot, tool calling, Phoenix tracing, chat history, and the
  embeddings/retrieval pipeline — none of that was touched.
- `data/products.py` backup data used by `cart.py`/`product_details.py` —
  left in place per the brief; unifying everything onto Supabase products
  is a separate follow-up, not part of RBAC.
- Supabase session restoration (`restore_supabase_session()`) — untouched.

## To finish the rollout

1. Run `migrations/002_rbac_orders.sql` in the Supabase SQL editor.
2. Verify the two duplicate policy names dropped in step 2 of that file
   actually match what exists in your project — if your policy has a
   different name, list them first with:
   `select policyname from pg_policies where tablename = 'orders';`
3. Manually walk the checklist in section 68 of the project brief
   (log in as a normal user, confirm shopping + chatbot work and admin
   pages are unreachable by URL; log in as admin, confirm the reverse).
