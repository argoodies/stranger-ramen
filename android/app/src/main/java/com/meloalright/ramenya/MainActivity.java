package com.meloalright.ramenya;

import android.app.Activity;
import android.graphics.Color;
import android.os.Build;
import android.os.Bundle;
import android.view.DisplayCutout;
import android.view.View;
import android.view.WindowManager;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;

/** Thin native shell: the whole game is the bundled assets/index.html, shown full screen in a WebView. */
public class MainActivity extends Activity {
    private WebView web;
    private int safeTop = 0;      // height of the camera cutout in CSS pixels, handed to the page as --sat

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        // Draw into the camera cutout too. Without this a full-screen window is kept out of the cutout strip,
        // which then shows as an empty bar above the game.
        if (Build.VERSION.SDK_INT >= 28) {
            WindowManager.LayoutParams lp = getWindow().getAttributes();
            lp.layoutInDisplayCutoutMode = WindowManager.LayoutParams.LAYOUT_IN_DISPLAY_CUTOUT_MODE_SHORT_EDGES;
            getWindow().setAttributes(lp);
        }
        web = new WebView(this);
        web.setBackgroundColor(Color.rgb(14, 12, 36));
        web.setOverScrollMode(View.OVER_SCROLL_NEVER);
        web.setVerticalScrollBarEnabled(false);
        web.setHorizontalScrollBarEnabled(false);
        web.setLongClickable(false);
        web.setHapticFeedbackEnabled(false);
        web.setOnLongClickListener(v -> true);
        WebSettings s = web.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);
        s.setMediaPlaybackRequiresUserGesture(false);
        s.setSupportZoom(false);
        s.setTextZoom(100);
        web.setWebViewClient(new WebViewClient() {
            @Override public void onPageFinished(WebView view, String url) { pushSafeTop(); }
        });
        setContentView(web);
        // The page keeps its buttons clear of the cutout with env(safe-area-inset-top); not every WebView reports it,
        // so the measured height is passed in as well.
        if (Build.VERSION.SDK_INT >= 28) {
            web.setOnApplyWindowInsetsListener((v, insets) -> {
                DisplayCutout c = insets.getDisplayCutout();
                safeTop = c == null ? 0 : Math.round(c.getSafeInsetTop() / getResources().getDisplayMetrics().density);
                pushSafeTop();
                return insets;
            });
        }
        immersive();
        web.loadUrl("file:///android_asset/index.html");
    }

    private void pushSafeTop() {
        web.evaluateJavascript("document.documentElement.style.setProperty('--sat','" + safeTop + "px')", null);
    }

    private void immersive() {
        getWindow().getDecorView().setSystemUiVisibility(
                View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY | View.SYSTEM_UI_FLAG_FULLSCREEN
                        | View.SYSTEM_UI_FLAG_HIDE_NAVIGATION | View.SYSTEM_UI_FLAG_LAYOUT_STABLE
                        | View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN | View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION);
    }

    @Override
    public void onWindowFocusChanged(boolean hasFocus) {
        super.onWindowFocusChanged(hasFocus);
        if (hasFocus) immersive();
    }

    @Override
    protected void onPause() {
        // fade the sound out and pause it before the page is frozen, so nothing crackles or hisses on the way out
        web.evaluateJavascript("window.__hush && window.__hush()", null);
        super.onPause();
        web.postDelayed(() -> { if (!hasWindowFocus()) web.onPause(); }, 150);
    }

    @Override
    protected void onResume() {
        super.onResume();
        web.onResume();
        // back from the background: let the game check that its sound still works (it restarts itself if not)
        web.evaluateJavascript("window.__wake && window.__wake()", null);
    }
}
