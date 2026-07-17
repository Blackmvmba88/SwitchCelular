package com.blackmamba.peripheral.model

data class MotionPacket(
    val protocolVersion: Int,
    val sequence: Long,
    val deviceTimestampNs: Long,
    val orientation: Quaternion,
    val angularVelocity: Vector3,
    val linearAcceleration: Vector3,
    val calibrationState: CalibrationState,
    val batteryPercent: Int,
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
