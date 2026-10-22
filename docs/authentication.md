# Accounts, dashboard and private prediction history

The app now includes a dashboard, email/password signup and login (sign in), logout, password recovery, and a history page. Public disease, yield and supply tools remain accessible without an account. Successful predictions made while signed in are saved as summaries in Supabase; guests' predictions are not persisted. Photos, passwords and tokens are never put in history. The latest 100 records can be reviewed or deleted individually. History queries and deletes include the current owner ID; database row-level security enforces ownership independently of the UI. Summaries are user-owned records, not tamper-proof diagnostic certificates.

## Render setup

1. In the intended AgriVision Supabase project, use the existing migrations `001_initial_schema.sql` and `002_user_auth_and_prediction_history.sql` if they have not already been applied. Do not rerun existing policy definitions blindly. Verify `public.user_prediction_history` has RLS enabled and the owner-only SELECT, INSERT and DELETE policies from migration 002.
2. Ensure the authenticated role has SELECT, INSERT and DELETE privileges on that table (and USAGE on public). If needed, run `GRANT SELECT, INSERT, DELETE ON public.user_prediction_history TO authenticated;`. Never disable RLS to fix permission errors.
3. In Supabase Authentication, enable email/password signups and set the Site URL to `https://agrivision-6o2f.onrender.com`. Allow `https://agrivision-6o2f.onrender.com/?panel=account` as a redirect for confirmation and password reset. Configure SMTP for real users and check email delivery/limits.
4. Render → Environment: set `SUPABASE_URL` to that project's HTTPS URL and `SUPABASE_PUBLISHABLE_KEY` to its publishable key (or legacy anon key). Do not use the service-role or secret key. Keep the existing `GEOAPIFY_API_KEY`.
5. Save and deploy the latest commit. No Vite build variables or Docker build arguments are needed: `/api/public-config` exposes only the explicitly configured public URL and browser-safe key at runtime. It never reads the service-role environment variable, rejects secret/service-role keys, and uses no-store caching.
6. Check signup and confirmation, login, reload, password recovery, a new disease/yield result, history review/deletion and logout. With two test accounts, verify one cannot read, insert or delete another's history through the Data API. These live checks require a working intended project and email configuration.

Session persistence/refresh uses the official pinned Supabase JS SDK. Session data remains in the SDK's browser storage; application history does not store authentication tokens. On logout or account switch, old history is hidden and stale fetches are ignored. Do not use a shared browser profile for private accounts.

## Verification and remaining configuration

Frontend tests exercise login, signup mismatch/confirmation, failed logout, signed-out history access, owner filtering/account-switch clearing and conditional product links using mocked SDK responses. Unit tests check history field allowlisting and public configuration secret rejection. These tests do not prove a remote project is configured. During implementation the connected Supabase project could not be inspected because the database connection timed out; no remote schema or accounts were changed. The intended AgriVision project URL/key, migrations, grants, RLS and SMTP must be confirmed before claiming live account/history availability.

## Detection-related supplies

Existing crop care now includes relevant external AgriBegri browsing links. Healthy results link routine supplies, virus results avoid chemical cure suggestions, and other conditions link crop protection only for adviser/label review. No exact product efficacy, dosage, live price, discount or stock is asserted. Current retailer prices and offers remain external. Shop search remains available. These supply links do not replace diagnosis or crop-specific approval.

English, Tamil, Hindi and Tanglish retain the existing translations. New account/dashboard/history and product text is English; additional translations remain to be added.
