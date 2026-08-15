package com.whitevendas.chat

import org.json.JSONArray
import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URL

object Http {
    var serverOverride: String? = null

    fun base(): String = serverOverride ?: Config.SERVER

    fun getArray(path: String): JSONArray {
        val conn = URL(base() + path).openConnection() as HttpURLConnection
        conn.connectTimeout = 10000
        conn.readTimeout = 20000
        try {
            val raw = conn.inputStream.bufferedReader().use { it.readText() }
            return JSONArray(raw)
        } finally {
            conn.disconnect()
        }
    }

    fun postJson(path: String, body: JSONObject): JSONObject {
        val conn = URL(base() + path).openConnection() as HttpURLConnection
        conn.requestMethod = "POST"
        conn.setRequestProperty("Content-Type", "application/json")
        conn.doOutput = true
        conn.connectTimeout = 10000
        conn.readTimeout = 10000
        try {
            conn.outputStream.write(body.toString().toByteArray())
            val raw = conn.inputStream.bufferedReader().use { it.readText() }
            return JSONObject(raw)
        } finally {
            conn.disconnect()
        }
    }
}
