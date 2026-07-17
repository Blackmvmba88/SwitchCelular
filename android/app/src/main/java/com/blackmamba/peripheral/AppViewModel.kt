package com.blackmamba.peripheral

import androidx.lifecycle.ViewModel
import com.blackmamba.peripheral.model.UiState
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow

class AppViewModel : ViewModel() {
    private val _uiState = MutableStateFlow(UiState())
    val uiState: StateFlow<UiState> = _uiState

    fun startSensors() {
        _uiState.value = _uiState.value.copy(connected = true)
    }

    fun stopSensors() {
        _uiState.value = _uiState.value.copy(connected = false)
    }

    fun calibrate() {
        _uiState.value = _uiState.value.copy(calibrationReady = true)
    }
}
