package com.blackmamba.peripheral.sensors

import com.blackmamba.peripheral.model.AndroidSensorEvent

interface AndroidSensorSource {
    fun start()
    fun stop()
    fun snapshot(): List<AndroidSensorEvent>
}
