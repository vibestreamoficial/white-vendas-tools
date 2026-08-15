package com.whitevendas.chat

import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import org.json.JSONObject
import org.webrtc.*
import java.net.URLEncoder
import java.util.UUID

class LiveActivity : AppCompatActivity() {

    private var meuId = UUID.randomUUID().toString().substring(0, 8)
    private var canal = ""
    private var ultimoSinal = 0
    private var souStreamer = false
    private var rodando = true
    private var offerPendente = ""

    private var pcFactory: PeerConnectionFactory? = null
    private var pc: PeerConnection? = null
    private var capturer: CameraVideoCapturer? = null
    private var surfaceHelper: SurfaceTextureHelper? = null
    private var trackVideo: VideoTrack? = null
    private var trackAudio: AudioTrack? = null

    private lateinit var campoCanal: EditText
    private lateinit var campoNome: EditText
    private lateinit var status: TextView
    private lateinit var local: SurfaceViewRenderer
    private lateinit var remoto: SurfaceViewRenderer

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_live)

        campoCanal = findViewById(R.id.lv_canal)
        campoNome = findViewById(R.id.lv_nome)
        status = findViewById(R.id.lv_status)
        local = findViewById(R.id.lv_local)
        remoto = findViewById(R.id.lv_remoto)
        local.init(EglBase.create().eglBaseContext, null)
        remoto.init(EglBase.create().eglBaseContext, null)
        local.setMirror(true)

        findViewById<Button>(R.id.lv_transmitir).setOnClickListener { transmitir() }
        findViewById<Button>(R.id.lv_assistir).setOnClickListener { assistir() }
        findViewById<Button>(R.id.lv_parar).setOnClickListener { parar() }

        Thread {
            while (rodando) {
                try {
                    if (canal.isNotEmpty()) {
                        val lista = Http.getArray("/api/signal?room=" + URLEncoder.encode("live:$canal", "UTF-8") + "&after=$ultimoSinal")
                        for (i in 0 until lista.length()) {
                            val s = lista.getJSONObject(i)
                            ultimoSinal = s.getInt("id")
                            tratarSinal(s)
                        }
                    }
                } catch (_: Exception) {
                }
                Thread.sleep(1200)
            }
        }.start()
    }

    // ---------- infra ----------

    private fun factory(): PeerConnectionFactory {
        if (pcFactory == null) {
            PeerConnectionFactory.initialize(PeerConnectionFactory.InitializationOptions.builder(this).createInitializationOptions())
            pcFactory = PeerConnectionFactory.builder().createPeerConnectionFactory()
        }
        return pcFactory!!
    }

    private fun observer(): PeerConnection.Observer = object : PeerConnection.Observer {
        override fun onIceCandidate(c: IceCandidate?) {
            try {
                post("candidate", JSONObject().put("v", if (souStreamer) "S" else meuId)
                    .put("c", JSONObject().put("mid", c?.sdpMid).put("mline", c?.sdpMLineIndex).put("sdp", c?.sdp)))
            } catch (_: Exception) {
            }
        }
        override fun onSignalingChange(s: PeerConnection.SignalingState) {}
        override fun onIceConnectionReceivingChange(receiving: Boolean) {}
        override fun onIceCandidatesRemoved(candidates: Array<IceCandidate>) {}
        override fun onAddStream(s: MediaStream?) {}
        override fun onRemoveStream(s: MediaStream?) {}
        override fun onRenegotiationNeeded() {}
        override fun onIceConnectionChange(s: PeerConnection.IceConnectionState?) {}
        override fun onIceGatheringChange(s: PeerConnection.IceGatheringState?) {}
        override fun onDataChannel(d: DataChannel?) {}
        override fun onAddTrack(r: RtpReceiver?, streams: Array<out MediaStream>?) {
            r?.track()?.let { t ->
                if (t is VideoTrack) ui { t.addSink(remoto) }
            }
        }
    }

    private fun novoPc(): PeerConnection {
        val config = PeerConnection.RTCConfiguration(listOf(PeerConnection.IceServer("stun:stun.l.google.com:19302")))
        return factory().createPeerConnection(config, observer())!!
    }

    private fun post(tipo: String, payload: JSONObject) {
        Thread {
            try {
                Http.postJson("/api/signal", JSONObject()
                    .put("room", "live:$canal")
                    .put("from", campoNome.text.toString().ifBlank { "anonimo" })
                    .put("type", tipo)
                    .put("payload", payload))
            } catch (_: Exception) {
            }
        }.start()
    }

    // ---------- acoes ----------

    private fun transmitir() {
        canal = campoCanal.text.toString().trim().ifEmpty { "canal1" }
        souStreamer = true
        try {
            pc = novoPc()
            val enums = Camera2Enumerator(this)
            val nomeCam = enums.deviceNames.firstOrNull { enums.isFrontFacing(it) } ?: enums.deviceNames.firstOrNull()
            if (nomeCam == null) { setStatus("Sem câmera disponível."); return }
            capturer = enums.createCapturer(nomeCam, null)
            surfaceHelper = SurfaceTextureHelper.create("Cam", EglBase.create().eglBaseContext)
            val videoSource = factory().createVideoSource(false)
            capturer?.initialize(surfaceHelper, this, videoSource.capturerObserver)
            capturer?.startCapture(640, 480, 30)
            trackVideo = factory().createVideoTrack("v0", videoSource)
            val audioSource = factory().createAudioSource(MediaConstraints())
            trackAudio = factory().createAudioTrack("a0", audioSource)
            pc?.addTrack(trackVideo!!, listOf("v0"))
            pc?.addTrack(trackAudio!!, listOf("a0"))
            ui { trackVideo?.addSink(local) }
            setStatus("📡 Transmitindo no canal $canal")
            post("live", JSONObject().put("on", true).put("u", campoNome.text.toString()))
        } catch (e: Exception) {
            setStatus("❌ Erro ao transmitir: ${e.message}")
        }
    }

    private fun assistir() {
        canal = campoCanal.text.toString().trim().ifEmpty { "canal1" }
        souStreamer = false
        try {
            pc = novoPc()
            val videoSource = factory().createVideoSource(false)
            trackVideo = factory().createVideoTrack("v0", videoSource)
            pc?.addTrack(trackVideo!!, listOf("v0"))
            setStatus("Procurando live no canal $canal...")
            post("join", JSONObject().put("v", meuId).put("u", campoNome.text.toString()))
        } catch (e: Exception) {
            setStatus("❌ Erro ao entrar: ${e.message}")
        }
    }

    private fun parar() {
        souStreamer = false
        capturer?.stopCapture()
        capturer?.dispose()
        capturer = null
        surfaceHelper?.dispose()
        surfaceHelper = null
        pc?.close()
        pc = null
        ui {
            local.clearImage()
            remoto.clearImage()
            setStatus("Live encerrada.")
        }
    }

    // ---------- sinalizacao ----------

    private fun tratarSinal(s: JSONObject) {
        val tipo = s.optString("tipo")
        val p = s.optJSONObject("payload") ?: JSONObject()
        when (tipo) {
            "live" -> if (!souStreamer) ui { setStatus("📺 Live encontrada no canal! Conectando...") }
            "join" -> if (souStreamer) thread { criarOferta(p.optString("v")) }
            "offer" -> if (!souStreamer && p.optString("v") == meuId) thread { responderOferta(p) }
            "answer" -> if (souStreamer && p.optString("i") == offerPendente) thread { aceitarResposta(p) }
            "candidate" -> thread { aplicarCandidato(p) }
            "stop" -> parar()
        }
    }

    private fun criarOferta(viewer: String) {
        try {
            val p = pc ?: return
            p.createOffer(object : SdpObserver {
                override fun onCreateSuccess(desc: SessionDescription?) {
                    offerPendente = UUID.randomUUID().toString().substring(0, 8)
                    post("offer", JSONObject().put("v", viewer).put("i", offerPendente).put("o", desc?.description))
                }
                override fun onSetSuccess() {}
                override fun onSetFailure(reason: String?) {}
                override fun onCreateFailure(reason: String?) {}
            }, MediaConstraints())
        } catch (e: Exception) {
            ui { setStatus("❌ Erro na oferta: ${e.message}") }
        }
    }

    private fun responderOferta(p: JSONObject) {
        try {
            val pc2 = pc ?: return
            pc2.setRemoteDescription(object : SdpObserver {
                override fun onCreateSuccess(desc: SessionDescription?) {}
                override fun onSetSuccess() {
                    try {
                        pc2.createAnswer(object : SdpObserver {
                            override fun onCreateSuccess(desc: SessionDescription?) {
                                pc2.setLocalDescription(SdpObserverImpl(), desc)
                                post("answer", JSONObject().put("i", p.optString("i")).put("o", desc?.description))
                            }
                            override fun onSetSuccess() {}
                            override fun onSetFailure(reason: String?) {}
                            override fun onCreateFailure(reason: String?) {}
                        }, MediaConstraints())
                    } catch (e: Exception) {
                        setStatus("Erro ao responder: ${e.message}")
                    }
                }
                override fun onSetFailure(reason: String?) { setStatus("Falha: $reason") }
                override fun onCreateFailure(reason: String?) {}
            }, SessionDescription(SessionDescription.Type.OFFER, p.optString("o")))
        } catch (e: Exception) {
            setStatus("Erro na resposta: ${e.message}")
        }
    }

    private fun aceitarResposta(p: JSONObject) {
        try {
            pc?.setRemoteDescription(SdpObserverImpl(), SessionDescription(SessionDescription.Type.ANSWER, p.optString("o")))
            ui { setStatus("📺 Conectado à live!") }
        } catch (e: Exception) {
            ui { setStatus("❌ Erro ao conectar: ${e.message}") }
        }
    }

    private fun aplicarCandidato(p: JSONObject) {
        try {
            val c = p.optJSONObject("c") ?: return
            val alvo = p.optString("v")
            if (souStreamer && alvo == "S") pc?.addIceCandidate(IceCandidate(c.optString("mid"), c.optInt("mline"), c.optString("sdp")))
            if (!souStreamer && alvo == meuId) pc?.addIceCandidate(IceCandidate(c.optString("mid"), c.optInt("mline"), c.optString("sdp")))
        } catch (_: Exception) {
        }
    }

    private class SdpObserverImpl : SdpObserver {
        override fun onCreateSuccess(desc: SessionDescription?) {}
        override fun onSetSuccess() {}
        override fun onSetFailure(reason: String?) {}
        override fun onCreateFailure(reason: String?) {}
    }

    override fun onDestroy() {
        super.onDestroy()
        rodando = false
        parar()
    }

    private fun thread(b: () -> Unit) = Thread(b).start()
    private fun ui(b: () -> Unit) = runOnUiThread(b)
    private fun setStatus(t: String) = ui { status.text = t }
}
