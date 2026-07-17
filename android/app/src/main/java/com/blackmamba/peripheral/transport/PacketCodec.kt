package com.blackmamba.peripheral.transport

import com.blackmamba.peripheral.model.MotionPacket

interface PacketCodec {
    fun encode(packet: MotionPacket): ByteArray
    fun decode(payload: ByteArray): MotionPacket
}
