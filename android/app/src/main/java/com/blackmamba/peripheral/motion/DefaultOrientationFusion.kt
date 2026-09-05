package com.blackmamba.peripheral.motion

import android.hardware.SensorManager
import com.blackmamba.peripheral.model.AndroidSensorEvent
import com.blackmamba.peripheral.model.Quaternion
import com.blackmamba.peripheral.model.SensorType
import kotlin.math.cos
import kotlin.math.sin
import kotlin.math.sqrt

/**
 * Prefers Android's rotation-vector fusion and falls back to accel + magnetometer.
 * The output quaternion is normalized before it reaches MOTION_PACKET_V1.
 */
class DefaultOrientationFusion : OrientationFusion {
    override fun fuse(sensorEvents: List<AndroidSensorEvent>): Quaternion {
        val rotationVector = sensorEvents.lastOrNull { it.sensor == SensorType.ROTATION_VECTOR }
        if (rotationVector != null) {
            val q = FloatArray(4)
            SensorManager.getQuaternionFromVector(q, rotationVector.values)
            return normalize(Quaternion(w = q[0], x = q[1], y = q[2], z = q[3]))
        }

        val acceleration = sensorEvents.lastOrNull { it.sensor == SensorType.ACCELEROMETER }
        val magnetic = sensorEvents.lastOrNull { it.sensor == SensorType.MAGNETOMETER }
        if (acceleration != null && magnetic != null) {
            val rotationMatrix = FloatArray(9)
            if (SensorManager.getRotationMatrix(rotationMatrix, null, acceleration.values, magnetic.values)) {
                val angles = FloatArray(3)
                SensorManager.getOrientation(rotationMatrix, angles)
                return normalize(fromEuler(angles[0], angles[1], angles[2]))
            }
        }

        return Quaternion(w = 1f, x = 0f, y = 0f, z = 0f)
    }

    private fun fromEuler(yaw: Float, pitch: Float, roll: Float): Quaternion {
        val halfYaw = yaw.toDouble() * 0.5
        val halfPitch = pitch.toDouble() * 0.5
        val halfRoll = roll.toDouble() * 0.5
        val cy = cos(halfYaw)
        val sy = sin(halfYaw)
        val cp = cos(halfPitch)
        val sp = sin(halfPitch)
        val cr = cos(halfRoll)
        val sr = sin(halfRoll)
        return Quaternion(
            w = (cr * cp * cy + sr * sp * sy).toFloat(),
            x = (sr * cp * cy - cr * sp * sy).toFloat(),
            y = (cr * sp * cy + sr * cp * sy).toFloat(),
            z = (cr * cp * sy - sr * sp * cy).toFloat(),
        )
    }

    private fun normalize(q: Quaternion): Quaternion {
        val squaredMagnitude =
            q.w.toDouble() * q.w + q.x.toDouble() * q.x + q.y.toDouble() * q.y + q.z.toDouble() * q.z
        val magnitude = sqrt(squaredMagnitude).toFloat()
        if (magnitude <= 1e-6f) return Quaternion(1f, 0f, 0f, 0f)
        return Quaternion(q.w / magnitude, q.x / magnitude, q.y / magnitude, q.z / magnitude)
    }
}
