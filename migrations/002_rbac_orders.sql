-- ============================================================
-- RBAC migration: prevent admin accounts from creating orders
-- ============================================================
-- Run this in the Supabase SQL editor for the ShopX project.
--
-- Context: role-based access control is now enforced in the
-- Streamlit app (require_user() blocks admins from reaching
-- cart/checkout/orders/chatbot pages), but the UI layer alone
-- is never sufficient — a direct API call could still bypass
-- it. This migration adds the same rule at the database layer
-- via Row Level Security, per section 28 of the project spec.
--
-- Safe to run multiple times (uses IF EXISTS / OR REPLACE).
-- ============================================================

-- 1. Ensure the is_admin() helper exists (idempotent).
create or replace function public.is_admin()
returns boolean
language sql
security definer
set search_path = public
as $$
  select exists (
    select 1
    from public.profiles
    where id = auth.uid()
    and role = 'admin'
  );
$$;

-- 2. Drop any duplicate/older INSERT policies on orders so we
--    don't end up with conflicting permissive policies. Adjust
--    the names below if your project used different policy
--    names — check with:
--      select policyname from pg_policies where tablename = 'orders';
drop policy if exists "Users can create their own orders" on public.orders;
drop policy if exists "Users can insert own orders" on public.orders;

-- 3. Recreate a single INSERT policy that requires the row's
--    user_id to match the caller AND that the caller is NOT
--    an admin.
create policy "Users can create their own orders"
on public.orders
for insert
to authenticated
with check (
    auth.uid() = user_id
    and not public.is_admin()
);

-- ============================================================
-- Optional verification queries (run manually, not part of
-- the migration):
--
--   select policyname, cmd, qual, with_check
--   from pg_policies
--   where tablename = 'orders';
--
--   -- as an admin user, this insert should now be rejected:
--   -- insert into public.orders (user_id, total_amount, status, ...)
--   -- values (auth.uid(), 100, 'pending', ...);
-- ============================================================
