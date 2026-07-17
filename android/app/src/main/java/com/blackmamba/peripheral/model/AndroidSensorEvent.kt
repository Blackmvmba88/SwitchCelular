package com.blackmamba.peripheral.model

enum class SensorType {
    ACCELEROMETER,
    GYROSCOPE,
    MAGNETOMETER,
    ROTATION_VECTOR,
}

data class AndroidSensorEvent(
    val sensor: SensorType,
    val timestampNs: Long,
    val values: FloatArray,
    val accuracy: Int,
)
