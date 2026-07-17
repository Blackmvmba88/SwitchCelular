package com.blackmamba.peripheral.transport

import com.blackmamba.peripheral.model.ConnectionState
import com.blackmamba.peripheral.model.MotionPacket
import kotlinx.coroutines.CoroutineDispatcher
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.withContext
import java.net.DatagramPacket
import java.net.DatagramSocket
import java.net.InetSocketAddress

class UdpMotionClient(
    private val codec: PacketCodec,
    private val dispatcher: CoroutineDispatcher = Dispatchers.IO,
) : MotionTransport {
    private var socket: DatagramSocket? = null
    private var destination: InetSocketAddress? = null
    private val _state = MutableStateFlow<ConnectionState>(ConnectionState.Disconnected)
    override val state: StateFlow<ConnectionState> = _state

    override suspend fun connect(host: String, port: Int) = withContext(dispatcher) {
        disconnect()
        destination = InetSocketAddress(host, port)
        socket = DatagramSocket().apply { connect(destination) }
        _state.value = ConnectionState.Connected
    }

    override suspend fun send(packet: MotionPacket) = withContext(dispatcher) {
        val activeSocket = checkNotNull(socket) { "UDP transport is not connected" }
        val target = checkNotNull(destination)
        val bytes = codec.encode(packet)
        activeSocket.send(DatagramPacket(bytes, bytes.size, target))
    }

    override suspend fun disconnect() = withContext(dispatcher) {
        socket?.close()
        socket = null
        destination = null
        _state.value = ConnectionState.Disconnected
    }
}
