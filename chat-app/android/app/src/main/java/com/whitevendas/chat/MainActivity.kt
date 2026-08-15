package com.whitevendas.chat

import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import org.json.JSONArray
import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URL

class MainActivity : AppCompatActivity() {

    // Troque pelo IP da maquina que roda o server.py (mesma rede WiFi)
    private val base = "http://192.168.0.10:8000"
    private var ultimoId = 0
    private val handler = Handler(Looper.getMainLooper())

    private lateinit var nome: EditText
    private lateinit var sala: EditText
    private lateinit var texto: EditText
    private lateinit var historico: TextView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        nome = findViewById(R.id.nome)
        sala = findViewById(R.id.sala)
        texto = findViewById(R.id.texto)
        historico = findViewById(R.id.historico)
        val enviar = findViewById<Button>(R.id.enviar)

        enviar.setOnClickListener {
            thread {
                val t = texto.text.toString().trim()
                if (t.isEmpty()) return@thread
                enviarMensagem(t)
                runOnUiThread { texto.setText("") }
            }
        }

        val atualizar = object : Runnable {
            override fun run() {
                thread { buscarMensagens() }
                handler.postDelayed(this, 1500)
            }
        }
        handler.postDelayed(atualizar, 1500)
    }

    private fun thread(bloco: () -> Unit) = Thread(bloco).start()

    private fun enviarMensagem(t: String) {
        try {
            val body = JSONObject()
                .put("room", sala.text.toString().ifBlank { "geral" })
                .put("user", nome.text.toString().ifBlank { "Visitante" })
                .put("text", t).toString()
            val url = URL("$base/send")
            val conn = url.openConnection() as HttpURLConnection
            conn.requestMethod = "POST"
            conn.setRequestProperty("Content-Type", "application/json")
            conn.doOutput = true
            conn.outputStream.write(body.toByteArray())
            conn.responseCode
            conn.disconnect()
        } catch (_: Exception) {
        }
    }

    private fun buscarMensagens() {
        try {
            val url = URL("$base/messages?room=${sala.text.toString().ifBlank { "geral" }}&after=$ultimoId")
            val conn = url.openConnection() as HttpURLConnection
            val textoRaw = conn.inputStream.bufferedReader().use { it.readText() }
            conn.disconnect()
            val arr = JSONArray(textoRaw)
            for (i in 0 until arr.length()) {
                val m = arr.getJSONObject(i)
                val linha = "${m.getString("user")} (${m.getString("ts")})\n${m.getString("text")}\n\n"
                ultimoId = m.getInt("id")
                runOnUiThread { historico.append(linha) }
            }
        } catch (_: Exception) {
        }
    }
}
