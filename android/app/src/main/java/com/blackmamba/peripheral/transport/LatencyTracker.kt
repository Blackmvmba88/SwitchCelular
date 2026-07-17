package com.blackmamba.peripheral.transport

data class LatencyTracker(
    val lastLatencyMs: Float = 0f,
    val averageLatencyMs: Float = 0f,
    val sampleCount: Long = 0L,
)
