package com.blackmamba.peripheral.motion

import com.blackmamba.peripheral.model.AndroidSensorEvent
import com.blackmamba.peripheral.model.Quaternion

interface OrientationFusion {
    fun fuse(sensorEvents: List<AndroidSensorEvent>): Quaternion
}
