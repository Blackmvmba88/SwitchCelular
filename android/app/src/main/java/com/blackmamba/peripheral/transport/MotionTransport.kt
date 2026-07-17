package com.blackmamba.peripheral.transport

import com.blackmamba.peripheral.model.ConnectionState
import com.blackmamba.peripheral.model.MotionPacket
import kotlinx.coroutines.flow.StateFlow

interface MotionTransport {
    suspend fun connect(host: String, port: Int)
    suspend fun send(packet: MotionPacket)
    suspend fun disconnect()
    val state: StateFlow<ConnectionState>
}
