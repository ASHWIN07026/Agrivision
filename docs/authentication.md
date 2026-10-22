# Authentication status

The frontend currently opens directly to the dashboard. Sign-up, login, password recovery, logout, and user prediction history are not included in the frontend.

The existing Supabase migrations and database policies are intentionally left unchanged. The `user_prediction_history` table remains owner-scoped by row-level security; the frontend does not read or write it while account authentication is removed.

## Language coverage

English, Tamil, Hindi, and Tanglish have complete local dictionaries for the interface. Telugu, Kannada, Malayalam, and Bengali include common navigation and form labels; untranslated entries intentionally fall back to English. No external translation service or paid API is used.
