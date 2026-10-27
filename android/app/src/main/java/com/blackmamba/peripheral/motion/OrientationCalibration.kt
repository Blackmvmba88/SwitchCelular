package com.blackmamba.peripheral.motion

import com.blackmamba.peripheral.model.Quaternion
import kotlin.math.sqrt

/**
 * Re-centers orientation by treating the current phone quaternion as identity.
 * Output is q_relative = inverse(q_center) * q_current.
 */
class OrientationCalibration {
    @Volatile private var center: Quaternion? = null

    fun recenter(current: Quaternion) {
        center = normalize(current)
    }

    fun clear() {
        center = null
    }

    fun isCalibrated(): Boolean = center != null

    fun apply(current: Quaternion): Quaternion {
        val normalizedCurrent = normalize(current)
        val reference = center ?: return normalizedCurrent
        return normalize(multiply(conjugate(reference), normalizedCurrent))
    }

    private fun conjugate(q: Quaternion): Quaternion = Quaternion(
        w = q.w,
        x = -q.x,
        y = -q.y,
        z = -q.z,
    )

    private fun multiply(a: Quaternion, b: Quaternion): Quaternion = Quaternion(
        w = a.w * b.w - a.x * b.x - a.y * b.y - a.z * b.z,
        x = a.w * b.x + a.x * b.w + a.y * b.z - a.z * b.y,
        y = a.w * b.y - a.x * b.z + a.y * b.w + a.z * b.x,
        z = a.w * b.z + a.x * b.y - a.y * b.x + a.z * b.w,
    )

    private fun normalize(q: Quaternion): Quaternion {
        val magnitude = sqrt(
            q.w.toDouble() * q.w +
                q.x.toDouble() * q.x +
                q.y.toDouble() * q.y +
                q.z.toDouble() * q.z
        ).toFloat()
        if (magnitude <= 1e-6f) return Quaternion(1f, 0f, 0f, 0f)
        return Quaternion(q.w / magnitude, q.x / magnitude, q.y / magnitude, q.z / magnitude)
    }
}
