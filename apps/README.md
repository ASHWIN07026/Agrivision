# AgriVision Windows and Android apps

These are online app clients for `https://agrivision-6o2f.onrender.com`. They retain the deployed platform's design, models, camera/upload, care guidance, product links, dashboard and direct access without user accounts. They do not bundle or retrain models, implement an offline backend, or repair missing production credentials. The active Render deployment supplies the UI and APIs.

## Windows

`apps/desktop`: Electron 45.0.0, electron-builder 26.18.0, locked dependencies.

```
cd apps/desktop
npm ci
npm run build:windows
```

Output: `release/AgriVision-Windows-x64.exe`. Portable, Windows 10/11 64-bit; no separate Python or Node installation needed. Copy it from CD to a writable folder before running. The portable launcher extracts runtime files into the user's temporary folder. Internet is required. It is an unsigned student build; institutional security policy may require approval before running. Do not bypass an antivirus block. The offline screen provides a retry through the app menu.

Node integration is disabled, context isolation and sandboxing are enabled, insecure content is disabled. Only the expected HTTPS app origin stays inside the app. HTTPS product links, email and telephone links open through the operating system. Permissions are restricted to the app origin and media/geolocation; device OS permissions still apply. No API secrets are built into the executable.

## Android

`apps/android`: native Java Activity with Android System WebView; Android 6/API 23 or newer, target API 35. Current Android System WebView/Chrome is recommended. External camera capture and image picker are wired to the website's file input; approximate/precise location is requested only for the app's location search. The camera is optional. Product and maps links open externally. No JavaScript-to-native bridge is exposed. Cleartext traffic and backup are disabled, TLS errors are not ignored, and the non-exported photo provider only serves the one temporary camera file via URI grants.

A signed sideload/demo APK is built with platform 35, build-tools 35.0.0, Java 17 and Eclipse ECJ 3.40.0. Download Android tools from Google's official repository, verify the repository checksums, and download ECJ from Maven Central (verify its SHA-1). Example on Linux:

```
python apps/android/build.py --tools /path/to/build-tools/35.0.0 --android-jar /path/to/platforms/android-35/android.jar --ecj /path/to/ecj-3.40.0.jar --output /path/to/AgriVision-Android.apk
```

The build uses a temporary self-signed demo certificate; no signing key, password or service credential is included in the deliverables or source. Rebuilding generates a different signing identity, so uninstall this demo before installing a newly signed build. App data may be removed by uninstalling. This is not a Google Play release.

## Submission folder

`01_Report/`: add final approved report PDF.
`02_Presentation/`: add final approved PPT/PPTX.
`03_Demo/Windows/`: portable EXE.
`03_Demo/Android/`: signed APK.
`03_Demo/Screenshots/`: captured app/web interface images.
`03_Demo/Video/`: labelled screenshot walkthrough MP4 (not a recording of the Windows runtime).
`04_Source_Code/`: link and commit reference to the existing GitHub source, without duplicate source files or private credentials.

## Verification limits

Windows artifact: cross-built on Linux, PE/container inspection and packaged app security configuration reviewed. Android: Java compile, DEX/resources package, signature verification and zip alignment passed. Live dashboard and model readiness inspected through the browser. Screenshots demonstrate observed web-platform behavior. Physical Windows execution, Android installation, camera, location prompts must still be checked on the target devices. This source update removes login, logout, signup and account-only history from the web interface. Both clients receive this removal after the updated website is deployed and the client is reloaded. Do not describe this as an offline AI application or as fully device-tested.

## Account-free update

The clients load the current website, so a web deployment removes account screens from Windows and Android together. Existing installers remain usable; reopen the app or choose Home/Retry after deployment. See docs/authentication.md.
