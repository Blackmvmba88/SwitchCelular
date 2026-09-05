package com.blackmamba.peripheral

import android.net.Uri
import androidx.lifecycle.ViewModel
import com.blackmamba.peripheral.model.UiState
import com.blackmamba.peripheral.pairing.PairingDescriptor
import com.blackmamba.peripheral.pairing.PairingDescriptorException
import com.blackmamba.peripheral.pairing.PairingUriParser
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow

class AppViewModel : ViewModel() {
    private val _uiState = MutableStateFlow(UiState())
    val uiState: StateFlow<UiState> = _uiState

    private var pairingDescriptor: PairingDescriptor? = null

    fun startSensors() {
        _uiState.value = _uiState.value.copy(connected = true)
    }

    fun stopSensors() {
        _uiState.value = _uiState.value.copy(connected = false)
    }

    fun calibrate() {
        _uiState.value = _uiState.value.copy(calibrationReady = true)
    }

    fun acceptPairingUri(uri: Uri) {
        try {
            val descriptor = PairingUriParser.parse(uri)
            pairingDescriptor = descriptor
            _uiState.value = _uiState.value.copy(
                pairingReady = true,
                pairingHost = descriptor.host,
                pairingPort = descriptor.port,
                pairingError = null,
            )
        } catch (error: PairingDescriptorException) {
            pairingDescriptor = null
            _uiState.value = _uiState.value.copy(
                pairingReady = false,
                pairingHost = null,
                pairingPort = null,
                pairingError = error.message ?: "Invalid pairing QR",
            )
        }
    }

    fun currentPairing(): PairingDescriptor? = pairingDescriptor
}
