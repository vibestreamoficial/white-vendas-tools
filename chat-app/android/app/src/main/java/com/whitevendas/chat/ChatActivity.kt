package com.whitevendas.chat

import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import java.net.URLEncoder

class ChatActivity : AppCompatActivity() {
    private var ultimo = 0
    private var rodando = true
    private val handler = Handler(Looper.getMainLooper())
    private lateinit var user: EditText
    private lateinit var room: EditText
    private lateinit var texto: EditText
    private lateinit var historico: TextView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_chat)

        user = findViewById(R.id.ch_user)
        room = findViewById(R.id.ch_room)
        texto = findViewById(R.id.ch_texto)
        historico = findViewById(R.id.ch_historico)

        findViewById<Button>(R.id.ch_enviar).setOnClickListener {
            val t = texto.text.toString().trim()
            if (t.isEmpty()) return@setOnClickListener
            thread {
                try {
                    Http.postJson("/send", org.json.JSONObject()
                        .put("room", room.text.toString().ifBlank { "geral" })
                        .put("user", user.text.toString().ifBlank { "Visitante" })
                        .put("text", t))
                } catch (_: Exception) {
                }
                ui { texto.setText("") }
            }
        }

        val loop = object : Runnable {
            override fun run() {
                thread { buscar() }
                handler.postDelayed(this, 1500)
            }
        }
        handler.postDelayed(loop, 1500)
    }

    private fun buscar() {
        try {
            val sala = room.text.toString().ifBlank { "geral" }
            val lista = Http.getArray("/messages?room=" + URLEncoder.encode(sala, "UTF-8") + "&after=$ultimo")
            for (i in 0 until lista.length()) {
                val m = lista.getJSONObject(i)
                ultimo = m.getInt("id")
                val linha = "${m.optString("user")} (${m.optString("ts")})\n${m.optString("text")}\n\n"
                ui { historico.append(linha) }
            }
        } catch (_: Exception) {
        }
    }

    private fun thread(b: () -> Unit) = Thread(b).start()
    private fun ui(b: () -> Unit) = runOnUiThread(b)
}
