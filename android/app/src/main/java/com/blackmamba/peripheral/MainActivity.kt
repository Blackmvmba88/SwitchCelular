package com.blackmamba.peripheral

import android.content.Intent
import android.os.Bundle
import android.view.Gravity
import android.view.MotionEvent
import android.view.ViewGroup
import android.widget.Button
import android.widget.LinearLayout
import android.widget.TextView
import androidx.activity.ComponentActivity
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.lifecycleScope
import androidx.lifecycle.repeatOnLifecycle
import kotlinx.coroutines.launch

class MainActivity : ComponentActivity() {
    private lateinit var viewModel: AppViewModel
    private lateinit var statusText: TextView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        viewModel = AppViewModel(applicationContext)
        setContentView(buildControllerView())
        handlePairingIntent(intent)

        lifecycleScope.launch {
            repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.uiState.collect { state ->
                    statusText.text = buildString {
                        appendLine("BlackMamba PeripheralOS")
                        appendLine()
                        appendLine(if (state.connected) "UDP: CONNECTED" else "UDP: WAITING FOR QR")
                        val endpoint = state.pairingHost?.let { host ->
                            state.pairingPort?.let { port -> "$host:$port" }
                        }
                        if (endpoint != null) appendLine("Endpoint: $endpoint")
                        appendLine("Gyro: ${if (state.sensorGyroscope) "OK" else "NO"}")
                        appendLine("Accel: ${if (state.sensorAccelerometer) "OK" else "NO"}")
                        appendLine("Mag: ${if (state.sensorMagnetometer) "OK" else "NO"}")
                        appendLine("Packets: ${state.packetsSent}")
                        state.pairingError?.let { appendLine("Error: $it") }
                    }
                }
            }
        }
    }

    override fun onNewIntent(intent: Intent) {
        super.onNewIntent(intent)
        setIntent(intent)
        handlePairingIntent(intent)
    }

    override fun onResume() {
        super.onResume()
        viewModel.startSensors()
    }

    override fun onPause() {
        viewModel.setTriggerPressed(false)
        viewModel.stopSensors()
        super.onPause()
    }

    private fun handlePairingIntent(intent: Intent?) {
        if (intent?.action != Intent.ACTION_VIEW) return
        intent.data?.let(viewModel::acceptPairingUri)
    }

    private fun buildControllerView(): LinearLayout {
        statusText = TextView(this).apply {
            textSize = 18f
            gravity = Gravity.CENTER
            text = "BlackMamba PeripheralOS\n\nScan the desktop QR to pair"
        }

        val fireButton = Button(this).apply {
            text = "FIRE"
            textSize = 24f
            minHeight = 140
            setOnTouchListener { _, event ->
                when (event.actionMasked) {
                    MotionEvent.ACTION_DOWN -> viewModel.setTriggerPressed(true)
                    MotionEvent.ACTION_UP, MotionEvent.ACTION_CANCEL -> viewModel.setTriggerPressed(false)
                }
                true
            }
        }

        return LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            gravity = Gravity.CENTER
            setPadding(32, 32, 32, 32)
            addView(
                statusText,
                LinearLayout.LayoutParams(
                    ViewGroup.LayoutParams.MATCH_PARENT,
                    0,
                    1f,
                ),
            )
            addView(
                fireButton,
                LinearLayout.LayoutParams(
                    ViewGroup.LayoutParams.MATCH_PARENT,
                    ViewGroup.LayoutParams.WRAP_CONTENT,
                ),
            )
        }
    }
}
