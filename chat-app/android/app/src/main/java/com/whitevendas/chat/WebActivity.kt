package com.whitevendas.chat

import android.annotation.SuppressLint
import android.graphics.Bitmap
import android.os.Bundle
import android.webkit.WebChromeClient
import android.webkit.WebResourceRequest
import android.webkit.WebSettings
import android.webkit.WebView
import android.webkit.WebViewClient
import android.widget.ProgressBar
import androidx.appcompat.app.AppCompatActivity

class WebActivity : AppCompatActivity() {

    private lateinit var web: WebView
    private lateinit var progresso: ProgressBar

    @SuppressLint("SetJavaScriptEnabled")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_web)

        web = findViewById(R.id.wv_app)
        progresso = findViewById(R.id.wv_progress)

        val settings: WebSettings = web.settings
        settings.javaScriptEnabled = true
        settings.domStorageEnabled = true
        settings.mediaPlaybackRequiresUserGesture = false
        settings.loadWithOverviewMode = true
        settings.useWideViewPort = true

        web.webViewClient = object : WebViewClient() {
            override fun shouldOverrideUrlLoading(view: WebView, request: WebResourceRequest): Boolean {
                view.loadUrl(request.url.toString())
                return true
            }
            override fun onPageStarted(view: WebView, url: String, favicon: Bitmap?) {
                progresso.visibility = ProgressBar.VISIBLE
            }
            override fun onPageFinished(view: WebView, url: String) {
                progresso.visibility = ProgressBar.GONE
            }
        }
        web.webChromeClient = WebChromeClient()

        val url = Http.base().trimEnd('/') + "/"
        web.loadUrl(url)
    }

    @Deprecated("Deprecated in Java")
    override fun onBackPressed() {
        if (web.canGoBack()) web.goBack() else super.onBackPressed()
    }
}
