package com.agrivision.app;

import android.Manifest;
import android.app.Activity;
import android.content.*;
import android.content.pm.PackageManager;
import android.net.Uri;
import android.os.Bundle;
import android.provider.MediaStore;
import android.webkit.*;
import android.widget.*;
import android.view.*;
import java.io.File;

public class MainActivity extends Activity {
    private static final String SITE = "https://agrivision-6o2f.onrender.com";
    private WebView web;
    private ValueCallback<Uri[]> upload;
    private GeolocationPermissions.Callback locationCallback;
    private String locationOrigin;
    private File cameraFile;
    private static boolean internal(String value) {
        try { Uri uri = Uri.parse(value); return "https".equals(uri.getScheme()) && "agrivision-6o2f.onrender.com".equals(uri.getHost()) && (uri.getPort() == -1 || uri.getPort() == 443); }
        catch (Exception ignored) { return false; }
    }
    private void external(String value) {
        Uri uri = Uri.parse(value);
        if (!("https".equals(uri.getScheme()) || "tel".equals(uri.getScheme()) || "mailto".equals(uri.getScheme()))) return;
        try { startActivity(new Intent(Intent.ACTION_VIEW, uri)); }
        catch (Exception ignored) { Toast.makeText(this, "No app is available to open this link.", Toast.LENGTH_LONG).show(); }
    }
    @Override public void onCreate(Bundle saved) {
        super.onCreate(saved);
        LinearLayout root = new LinearLayout(this); root.setOrientation(LinearLayout.VERTICAL);
        root.setOnApplyWindowInsetsListener((view, insets) -> { view.setPadding(insets.getSystemWindowInsetLeft(), insets.getSystemWindowInsetTop(), insets.getSystemWindowInsetRight(), insets.getSystemWindowInsetBottom()); return insets; });
        LinearLayout toolbar = new LinearLayout(this);
        String[] labels = {"Home", "Retry", "Browser"};
        for (int index = 0; index < labels.length; index++) {
            Button button = new Button(this); button.setText(labels[index]); final int action = index;
            button.setOnClickListener(view -> { if (action == 2) external(SITE); else web.loadUrl(SITE); });
            toolbar.addView(button, new LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1));
        }
        root.addView(toolbar); web = new WebView(this);
        root.addView(web, new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, 0, 1)); setContentView(root);
        WebSettings settings = web.getSettings(); settings.setJavaScriptEnabled(true); settings.setDomStorageEnabled(true);
        settings.setAllowFileAccess(false); settings.setAllowContentAccess(true);
        settings.setMixedContentMode(WebSettings.MIXED_CONTENT_NEVER_ALLOW);
        settings.setGeolocationEnabled(true); settings.setSupportMultipleWindows(true);
        CookieManager.getInstance().setAcceptCookie(true); CookieManager.getInstance().setAcceptThirdPartyCookies(web, false);
        web.setWebViewClient(new WebViewClient() {
            @Override public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
                String url = request.getUrl().toString();
                if (internal(url)) return false;
                if (request.isForMainFrame() && request.hasGesture()) external(url);
                return true;
            }
            @Override public void onReceivedError(WebView view, WebResourceRequest request, WebResourceError error) {
                if (request.isForMainFrame() && internal(request.getUrl().toString())) showOffline();
            }
        });
        web.setWebChromeClient(new WebChromeClient() {
            @Override public boolean onCreateWindow(WebView view, boolean dialog, boolean gesture, android.os.Message message) {
                if (!gesture) return false;
                final WebView temporary = new WebView(MainActivity.this);
                temporary.setWebViewClient(new WebViewClient() {
                    @Override public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) { external(request.getUrl().toString()); temporary.destroy(); return true; }
                });
                ((WebView.WebViewTransport)message.obj).setWebView(temporary); message.sendToTarget(); return true;
            }
            @Override public boolean onShowFileChooser(WebView view, ValueCallback<Uri[]> callback, FileChooserParams params) {
                if (!internal(view.getUrl())) return false;
                if (upload != null) upload.onReceiveValue(null); upload = callback;
                Intent gallery = new Intent(Intent.ACTION_GET_CONTENT); gallery.addCategory(Intent.CATEGORY_OPENABLE); gallery.setType("image/*");
                Intent camera = new Intent(MediaStore.ACTION_IMAGE_CAPTURE);
                try {
                    cameraFile = new File(getCacheDir(), "leaf-camera.jpg"); if (cameraFile.exists()) cameraFile.delete();
                    Uri output = Uri.parse("content://com.agrivision.app.photos/leaf-camera.jpg");
                    camera.putExtra(MediaStore.EXTRA_OUTPUT, output);
                    camera.setClipData(ClipData.newRawUri("Leaf photo", output));
                    camera.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION | Intent.FLAG_GRANT_WRITE_URI_PERMISSION);
                    if (params.isCaptureEnabled()) {
                        try { startActivityForResult(camera, 201); return true; } catch (ActivityNotFoundException ignored) {}
                    }
                    Intent chooser = Intent.createChooser(gallery, "Select a leaf photo");
                    chooser.putExtra(Intent.EXTRA_INITIAL_INTENTS, new Intent[]{camera}); startActivityForResult(chooser, 201);
                } catch (Exception ignored) { upload.onReceiveValue(null); upload = null; Toast.makeText(MainActivity.this, "Could not open camera or photo picker.", Toast.LENGTH_LONG).show(); }
                return true;
            }
            @Override public void onPermissionRequest(PermissionRequest request) { request.deny(); }
            @Override public void onGeolocationPermissionsShowPrompt(String origin, GeolocationPermissions.Callback callback) {
                if (!internal(origin)) { callback.invoke(origin, false, false); return; }
                if (hasLocation()) { callback.invoke(origin, true, false); return; }
                if (locationCallback != null) locationCallback.invoke(locationOrigin, false, false);
                locationCallback = callback; locationOrigin = origin;
                requestPermissions(new String[]{Manifest.permission.ACCESS_COARSE_LOCATION, Manifest.permission.ACCESS_FINE_LOCATION}, 202);
            }
        });
        if (saved == null || web.restoreState(saved) == null) web.loadUrl(SITE);
    }
    private boolean hasLocation() { return checkSelfPermission(Manifest.permission.ACCESS_FINE_LOCATION) == PackageManager.PERMISSION_GRANTED || checkSelfPermission(Manifest.permission.ACCESS_COARSE_LOCATION) == PackageManager.PERMISSION_GRANTED; }
    @Override public void onRequestPermissionsResult(int code, String[] permissions, int[] results) {
        super.onRequestPermissionsResult(code, permissions, results);
        if (code == 202 && locationCallback != null) { locationCallback.invoke(locationOrigin, hasLocation(), false); locationCallback = null; }
    }
    private void showOffline() {
        web.loadDataWithBaseURL(null, "<html><meta name='viewport' content='width=device-width, initial-scale=1'><body style='font:18px sans-serif;padding:25px;background:#eef5e9;color:#204c36'><h1>AgriVision</h1><h2>Internet connection needed</h2><p>This app connects to the live AgriVision server. Predictions, login and shops need internet. Render may need time to wake up.</p><p>Connect to the internet, then tap Retry above.</p></body></html>", "text/html", "UTF-8", null);
    }
    @Override protected void onActivityResult(int code, int result, Intent data) {
        super.onActivityResult(code, result, data);
        if (code != 201 || upload == null) return;
        Uri selected = result == RESULT_OK && data != null ? data.getData() : null;
        if (selected == null && result == RESULT_OK && cameraFile != null && cameraFile.length() > 0) selected = Uri.parse("content://com.agrivision.app.photos/leaf-camera.jpg");
        if (selected != null && !"content".equals(selected.getScheme())) selected = null;
        upload.onReceiveValue(selected == null ? null : new Uri[]{selected}); upload = null;
    }
    @Override public void onBackPressed() { if (web.canGoBack()) web.goBack(); else super.onBackPressed(); }
    @Override protected void onSaveInstanceState(Bundle out) { super.onSaveInstanceState(out); web.saveState(out); }
    @Override protected void onPause() { super.onPause(); web.onPause(); CookieManager.getInstance().flush(); }
    @Override protected void onResume() { super.onResume(); if (web != null) web.onResume(); }
    @Override protected void onDestroy() { if (upload != null) upload.onReceiveValue(null); if (locationCallback != null) locationCallback.invoke(locationOrigin, false, false); web.destroy(); super.onDestroy(); }
}
