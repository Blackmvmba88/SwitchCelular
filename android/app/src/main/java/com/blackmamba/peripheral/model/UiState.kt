package com.blackmamba.peripheral.model

data class UiState(
    val connected: Boolean = false,
    val sensorGyroscope: Boolean = false,
    val sensorAccelerometer: Boolean = false,
    val sensorMagnetometer: Boolean = false,
    val profile: MotionProfile = MotionProfile(),
    val calibrationReady: Boolean = false,
    val rateHz: Float = 0f,
    val latencyMs: Float = 0f,
    val batteryPercent: Int = 0,
    val packetsSent: Long = 0L,
)
