package com.blackmamba.peripheral.sensors

data class SensorAvailability(
    val gyroscope: Boolean,
    val accelerometer: Boolean,
    val magnetometer: Boolean,
)
