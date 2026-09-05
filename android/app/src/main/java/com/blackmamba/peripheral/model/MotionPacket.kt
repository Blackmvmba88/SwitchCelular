package com.blackmamba.peripheral.model

/**
 * Android binding for the canonical MOTION_PACKET_V1 contract.
 *
 * Property names are Kotlin-friendly; PacketCodec is responsible for emitting
 * the normative snake_case wire names used by the Python desktop receiver.
 */
data class MotionPacket(
    val version: Int = 1,
    val sequence: Long,
    val timestampNs: Long,
    val orientation: Quaternion,
    val angularVelocity: Vector3,
    val acceleration: Vector3,
    val buttons: Int = 0,
    val battery: Int = 0,
    val flags: Int = 0,
    val capabilities: List<String> = emptyList(),
    val reserved: List<String> = emptyList(),
    val extensionLength: Int = 0,
)

data class Quaternion(val w: Float, val x: Float, val y: Float, val z: Float)

data class Vector3(val x: Float, val y: Float, val z: Float)

data class CalibrationState(
    val centerYaw: Float = 0f,
    val centerPitch: Float = 0f,
    val centerRoll: Float = 0f,
    val sensitivityYaw: Float = 1f,
    val sensitivityPitch: Float = 1f,
    val deadzoneYaw: Float = 0f,
    val deadzonePitch: Float = 0f,
)
