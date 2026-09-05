package com.blackmamba.peripheral.motion

import com.blackmamba.peripheral.model.AndroidSensorEvent
import com.blackmamba.peripheral.model.MotionPacket
import com.blackmamba.peripheral.model.MotionProfile
import com.blackmamba.peripheral.model.SensorType
import com.blackmamba.peripheral.model.Vector3

class DefaultMotionEngine(
    private val fusion: OrientationFusion = DefaultOrientationFusion(),
) : MotionEngine {
    override fun buildPacket(
        sensorEvents: List<AndroidSensorEvent>,
        profile: MotionProfile,
        sequence: Long,
        batteryPercent: Int,
        buttons: Int,
    ): MotionPacket {
        require(isReady(sensorEvents)) { "Motion sensors are not ready" }

        val gyroscope = sensorEvents.last { it.sensor == SensorType.GYROSCOPE }
        val acceleration = sensorEvents.last { it.sensor == SensorType.ACCELEROMETER }
        val timestampNs = sensorEvents.maxOf { it.timestampNs }

        return MotionPacket(
            version = 1,
            sequence = sequence,
            timestampNs = timestampNs,
            orientation = fusion.fuse(sensorEvents),
            angularVelocity = vector3(gyroscope.values),
            acceleration = vector3(acceleration.values),
            buttons = buttons,
            battery = batteryPercent.coerceIn(0, 100),
            flags = 0,
            capabilities = CAPABILITIES,
            reserved = emptyList(),
            extensionLength = 0,
        )
    }

    companion object {
        private val CAPABILITIES = listOf(
            "CAPABILITY_ORIENTATION",
            "CAPABILITY_GYROSCOPE",
            "CAPABILITY_ACCELERATION",
        )

        fun isReady(events: List<AndroidSensorEvent>): Boolean {
            val types = events.mapTo(mutableSetOf()) { it.sensor }
            val hasOrientation = SensorType.ROTATION_VECTOR in types ||
                (SensorType.ACCELEROMETER in types && SensorType.MAGNETOMETER in types)
            return hasOrientation &&
                SensorType.GYROSCOPE in types &&
                SensorType.ACCELEROMETER in types
        }

        private fun vector3(values: FloatArray): Vector3 = Vector3(
            x = values.getOrElse(0) { 0f },
            y = values.getOrElse(1) { 0f },
            z = values.getOrElse(2) { 0f },
        )
    }
}
