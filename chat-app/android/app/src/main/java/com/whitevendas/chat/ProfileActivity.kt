package com.whitevendas.chat

import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import org.json.JSONObject

class ProfileActivity : AppCompatActivity() {
    private lateinit var user: EditText
    private lateinit var name: EditText
    private lateinit var bio: EditText
    private lateinit var resultado: TextView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_profile)

        user = findViewById(R.id.pf_user)
        name = findViewById(R.id.pf_name)
        bio = findViewById(R.id.pf_bio)
        resultado = findViewById(R.id.pf_resultado)

        findViewById<Button>(R.id.pf_salvar).setOnClickListener {
            thread {
                try {
                    val body = JSONObject()
                        .put("username", user.text.toString().trim())
                        .put("name", name.text.toString().trim())
                        .put("bio", bio.text.toString().trim())
                    val r = Http.postJson("/api/profile", body)
                    ui { resultado.append(if (r.optBoolean("ok")) "✅ Perfil salvo.\n\n" else "❌ ${r.optString("erro")}\n\n") }
                } catch (e: Exception) {
                    ui { resultado.append("❌ Sem conexão com o servidor.\n\n") }
                }
            }
        }

        findViewById<Button>(R.id.pf_listar).setOnClickListener {
            thread {
                try {
                    val lista = Http.getArray("/api/profiles")
                    val sb = StringBuilder("Perfis:\n")
                    for (i in 0 until lista.length()) {
                        val p = lista.getJSONObject(i)
                        sb.append("• ").append(p.optString("name")).append(" (@")
                            .append(p.optString("username")).append(") — ")
                            .append(p.optString("bio")).append("\n")
                    }
                    ui { resultado.text = sb.toString() }
                } catch (e: Exception) {
                    ui { resultado.append("❌ Sem conexão.\n") }
                }
            }
        }
    }

    private fun thread(b: () -> Unit) = Thread(b).start()
    private fun ui(b: () -> Unit) = runOnUiThread(b)
}
