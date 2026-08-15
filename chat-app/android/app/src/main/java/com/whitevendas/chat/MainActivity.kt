package com.whitevendas.chat

import android.content.Intent
import android.os.Bundle
import android.widget.EditText
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity

class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val prefs = getSharedPreferences("whitechat", MODE_PRIVATE)
        Http.serverOverride = prefs.getString("servidor", null)
        val edtServidor = findViewById<EditText>(R.id.edt_servidor)
        edtServidor.setText(Http.base())
        findViewById<android.widget.Button>(R.id.btn_salvar_servidor).setOnClickListener {
            val novo = edtServidor.text.toString().trim().trimEnd('/')
            if (novo.isNotEmpty()) {
                prefs.edit().putString("servidor", novo).apply()
                Http.serverOverride = novo
                Toast.makeText(this, "Servidor salvo: $novo", Toast.LENGTH_LONG).show()
            }
        }

        findViewById<android.widget.Button>(R.id.btn_perfil).setOnClickListener {
            startActivity(Intent(this, ProfileActivity::class.java))
        }
        findViewById<android.widget.Button>(R.id.btn_chat).setOnClickListener {
            startActivity(Intent(this, ChatActivity::class.java))
        }
        findViewById<android.widget.Button>(R.id.btn_live).setOnClickListener {
            startActivity(Intent(this, LiveActivity::class.java))
        }
    }
}
