package com.blackmamba.peripheral

import android.content.Context
import android.net.Uri
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.blackmamba.peripheral.model.UiState
import com.blackmamba.peripheral.pairing.PairingDescriptor
import com.blackmamba.peripheral.pairing.PairingDescriptorException
import com.blackmamba.peripheral.pairing.PairingUriParser
import com.blackmamba.peripheral.runtime.PhoneControllerRuntime
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch

class AppViewModel(context: Context) : ViewModel() {
    private val _uiState = MutableStateFlow(UiState())
    val uiState: StateFlow<UiState> = _uiState

    private val runtime = PhoneControllerRuntime(context.applicationContext)
    private var pairingDescriptor: PairingDescriptor? = null

    init {
        runtime.onPacketSent = { sequence ->
            _uiState.value = _uiState.value.copy(packetsSent = sequence + 1L)
        }
        runtime.onError = { message ->
            _uiState.value = _uiState.value.copy(pairingError = message)
        }
    }

    fun startSensors() {
        val availability = runtime.sensorAvailability()
        _uiState.value = _uiState.value.copy(
            sensorGyroscope = availability.gyroscope,
            sensorAccelerometer = availability.accelerometer,
            sensorMagnetometer = availability.magnetometer,
        )
        runtime.startSensors(profile = _uiState.value.profile)
    }

    fun stopSensors() {
        runtime.stopSensors()
    }

    fun calibrate() {
        val calibrated = runtime.recenter()
        _uiState.value = _uiState.value.copy(
            calibrationReady = calibrated,
            pairingError = if (calibrated) null else "Motion sensors are not ready for recenter",
        )
    }

    fun setTriggerPressed(pressed: Boolean) {
        runtime.setButtons(if (pressed) 1 else 0)
    }

    fun acceptPairingUri(uri: Uri) {
        val descriptor = try {
            PairingUriParser.parse(uri)
        } catch (error: PairingDescriptorException) {
            pairingDescriptor = null
            _uiState.value = _uiState.value.copy(
                pairingReady = false,
                connected = false,
                pairingHost = null,
                pairingPort = null,
                pairingError = error.message ?: "Invalid pairing QR",
            )
            return
        }

        pairingDescriptor = descriptor
        _uiState.value = _uiState.value.copy(
            pairingReady = true,
            connected = false,
            pairingHost = descriptor.host,
            pairingPort = descriptor.port,
            pairingError = null,
        )

        viewModelScope.launch {
            try {
                runtime.connect(descriptor)
                _uiState.value = _uiState.value.copy(connected = true, pairingError = null)
            } catch (error: Exception) {
                _uiState.value = _uiState.value.copy(
                    connected = false,
                    pairingError = error.message ?: "Unable to connect UDP endpoint",
                )
            }
        }
    }

    fun currentPairing(): PairingDescriptor? = pairingDescriptor

    override fun onCleared() {
        runtime.shutdown()
        super.onCleared()
    }
}
