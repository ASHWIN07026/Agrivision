# Account-free access

Login, logout, sign-in, sign-up, password recovery and account-only prediction history have been removed from the public frontend. Dashboard, disease detection/camera, automatic care, yield prediction and product/shop links open directly on desktop and mobile.

The Supabase frontend SDK, account screens, history persistence callbacks and `/api/public-config` endpoint are removed. Startup clears only default retired Supabase SDK session keys from browser storage, preserving other data such as language preferences. The frontend makes no authentication or private-history requests. Existing `?panel=account` and `?panel=history` links safely open the dashboard.

Existing Supabase users, records, migrations and owner-only RLS policies are not deleted or made public. Marketplace administrator authentication is unchanged; removing user account screens does not authorize anonymous publishing.

## Windows and Android apps

Both native clients load the deployed Render website. After deploying this change and selecting Home/Retry or reopening an app, the account-free interface appears in both. No new EXE/APK installation is required because no account UI or auth SDK is embedded in those binaries. Internet is still required. Existing CD screenshots/video showing account controls are historical captures and do not represent this updated interface.

## Deployment

Deploy the latest GitHub main commit on Render. `SUPABASE_URL` and `SUPABASE_PUBLISHABLE_KEY` are no longer required by the frontend, and the Render blueprint no longer asks for them. Existing Render variable values do not have to be changed to deploy. Keep `GEOAPIFY_API_KEY` for mapped shops. No database changes or credential rotations are performed by this update.

## Verification

Frontend tests cover all four public tabs, camera/analyze availability, absence of account controls and authentication requests, retired account/history links and selective browser session cleanup. Backend tests confirm the retired public account configuration endpoint returns 404. Models and inference validation are unchanged.
