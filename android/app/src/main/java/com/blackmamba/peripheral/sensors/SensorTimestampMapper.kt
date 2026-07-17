package com.blackmamba.peripheral.sensors

interface SensorTimestampMapper {
    fun map(timestampNanos: Long): Long
}
