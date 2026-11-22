package com.farida.adventures;
import android.app.Activity;
import android.os.Bundle;
import android.graphics.Color;
import android.view.View;
import android.view.Window;
import android.webkit.WebChromeClient;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
public class MainActivity extends Activity {
  private WebView web;
  @Override public void onCreate(Bundle state) {
    super.onCreate(state);
    Window w=getWindow(); w.setStatusBarColor(Color.rgb(5,92,133)); w.setNavigationBarColor(Color.rgb(5,55,88));
    getWindow().getDecorView().setSystemUiVisibility(5894|1024|512|4096);
    web=new WebView(this); web.setBackgroundColor(Color.rgb(102,210,242));
    WebSettings s=web.getSettings(); s.setJavaScriptEnabled(true); s.setDomStorageEnabled(true);
    s.setAllowFileAccess(true); s.setAllowContentAccess(false); s.setMediaPlaybackRequiresUserGesture(true);
    s.setSupportZoom(false); s.setBuiltInZoomControls(false); s.setDisplayZoomControls(false);
    web.setWebChromeClient(new WebChromeClient()); web.setWebViewClient(new WebViewClient());
    setContentView(web); web.loadUrl("file:///android_asset/index.html");
  }
  @Override public void onBackPressed() {
    if(web!=null) web.evaluateJavascript("window.backToHome&&window.backToHome()",v->{if(!"true".equals(v)) super.onBackPressed();});
    else super.onBackPressed();
  }
  @Override protected void onPause(){if(web!=null)web.onPause();super.onPause();}
  @Override protected void onResume(){super.onResume();if(web!=null)web.onResume();}
}
