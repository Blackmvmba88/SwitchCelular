package com.blackmamba.peripheral.runtime

import android.content.Context
import android.os.BatteryManager
import com.blackmamba.peripheral.model.ConnectionState
import com.blackmamba.peripheral.model.MotionProfile
import com.blackmamba.peripheral.motion.DefaultMotionEngine
import com.blackmamba.peripheral.pairing.PairingDescriptor
import com.blackmamba.peripheral.sensors.SensorAvailability
import com.blackmamba.peripheral.sensors.SensorManagerSource
import com.blackmamba.peripheral.transport.CanonicalJsonPacketCodec
import com.blackmamba.peripheral.transport.UdpMotionClient
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.cancel
import kotlinx.coroutines.delay
import kotlinx.coroutines.isActive
import kotlinx.coroutines.launch

/**
 * First playable runtime: Android sensors -> MOTION_PACKET_V1 -> UDP desktop endpoint.
 * No game-specific behavior lives here.
 */
class PhoneControllerRuntime(context: Context) {
    private val appContext = context.applicationContext
    private val sensorSource = SensorManagerSource(appContext)
    private val engine = DefaultMotionEngine()
    private val transport = UdpMotionClient(CanonicalJsonPacketCodec())
    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.Default)
    private val batteryManager = appContext.getSystemService(Context.BATTERY_SERVICE) as BatteryManager

    private var streamJob: Job? = null
    private var sensorsStarted = false
    private var sequence = 0L
    @Volatile private var buttons = 0

    var onPacketSent: ((Long) -> Unit)? = null
    var onError: ((String) -> Unit)? = null

    fun sensorAvailability(): SensorAvailability = sensorSource.availability()

    fun startSensors(profile: MotionProfile = MotionProfile(), periodMs: Long = 16L) {
        if (!sensorsStarted) {
            sensorSource.start()
            sensorsStarted = true
        }
        if (streamJob?.isActive == true) return

        streamJob = scope.launch {
            while (isActive) {
                if (transport.state.value is ConnectionState.Connected) {
                    val events = sensorSource.snapshot()
                    if (DefaultMotionEngine.isReady(events)) {
                        val packet = engine.buildPacket(
                            sensorEvents = events,
                            profile = profile,
                            sequence = sequence++,
                            batteryPercent = batteryPercent(),
                            buttons = buttons,
                        )
                        try {
                            transport.send(packet)
                            onPacketSent?.invoke(packet.sequence)
                        } catch (error: Exception) {
                            onError?.invoke(error.message ?: "UDP send failed")
                        }
                    }
                }
                delay(periodMs.coerceAtLeast(5L))
            }
        }
    }

    fun stopSensors() {
        streamJob?.cancel()
        streamJob = null
        if (sensorsStarted) {
            sensorSource.stop()
            sensorsStarted = false
        }
    }

    fun recenter(): Boolean = engine.recenter(sensorSource.snapshot())

    fun clearCalibration() {
        engine.clearCalibration()
    }

    suspend fun connect(descriptor: PairingDescriptor) {
        require(descriptor.transport == "udp") { "Only UDP pairing is supported by this runtime" }
        transport.connect(descriptor.host, descriptor.port)
    }

    suspend fun disconnect() {
        transport.disconnect()
    }

    fun setButtons(mask: Int) {
        buttons = mask
    }

    fun shutdown() {
        stopSensors()
        scope.launch {
            runCatching { transport.disconnect() }
            scope.cancel()
        }
    }

    private fun batteryPercent(): Int {
        val value = batteryManager.getIntProperty(BatteryManager.BATTERY_PROPERTY_CAPACITY)
        return if (value in 0..100) value else 0
    }
}
