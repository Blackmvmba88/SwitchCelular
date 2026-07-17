package com.blackmamba.peripheral.model

data class MotionProfile(
    val id: String = "pointer",
    val sensitivityYaw: Float = 1f,
    val sensitivityPitch: Float = 1f,
    val smoothingAlpha: Float = 0.75f,
    val deadzoneYaw: Float = 0.1f,
    val deadzonePitch: Float = 0.1f,
)
