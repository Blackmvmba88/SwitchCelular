package com.blackmamba.peripheral.motion

import com.blackmamba.peripheral.model.AndroidSensorEvent
import com.blackmamba.peripheral.model.MotionPacket
import com.blackmamba.peripheral.model.MotionProfile

interface MotionEngine {
    fun buildPacket(
        sensorEvents: List<AndroidSensorEvent>,
        profile: MotionProfile,
        sequence: Long,
        batteryPercent: Int,
    ): MotionPacket
}
