package com.blackmamba.peripheral.sensors

import android.content.Context
import android.hardware.Sensor
import android.hardware.SensorEvent
import android.hardware.SensorEventListener
import android.hardware.SensorManager
import com.blackmamba.peripheral.model.AndroidSensorEvent
import com.blackmamba.peripheral.model.SensorType
import java.util.EnumMap

/** Native Android sensor source used by the first playable phone-controller path. */
class SensorManagerSource(
    context: Context,
    private val samplingPeriodUs: Int = 10_000,
) : AndroidSensorSource, SensorEventListener {
    private val manager = context.applicationContext
        .getSystemService(Context.SENSOR_SERVICE) as SensorManager
    private val latest = EnumMap<SensorType, AndroidSensorEvent>(SensorType::class.java)
    private val lock = Any()

    private val bindings: Map<SensorType, Sensor?> = mapOf(
        SensorType.GYROSCOPE to manager.getDefaultSensor(Sensor.TYPE_GYROSCOPE),
        SensorType.ACCELEROMETER to manager.getDefaultSensor(Sensor.TYPE_ACCELEROMETER),
        SensorType.MAGNETOMETER to manager.getDefaultSensor(Sensor.TYPE_MAGNETIC_FIELD),
        SensorType.ROTATION_VECTOR to manager.getDefaultSensor(Sensor.TYPE_ROTATION_VECTOR),
    )

    fun availability(): SensorAvailability = SensorAvailability(
        gyroscope = bindings[SensorType.GYROSCOPE] != null,
        accelerometer = bindings[SensorType.ACCELEROMETER] != null,
        magnetometer = bindings[SensorType.MAGNETOMETER] != null,
    )

    fun hasRotationVector(): Boolean = bindings[SensorType.ROTATION_VECTOR] != null

    override fun start() {
        synchronized(lock) { latest.clear() }
        bindings.values.filterNotNull().forEach { sensor ->
            manager.registerListener(this, sensor, samplingPeriodUs)
        }
    }

    override fun stop() {
        manager.unregisterListener(this)
    }

    override fun snapshot(): List<AndroidSensorEvent> = synchronized(lock) {
        latest.values.sortedBy { it.timestampNs }.toList()
    }

    override fun onSensorChanged(event: SensorEvent) {
        val type = when (event.sensor.type) {
            Sensor.TYPE_GYROSCOPE -> SensorType.GYROSCOPE
            Sensor.TYPE_ACCELEROMETER -> SensorType.ACCELEROMETER
            Sensor.TYPE_MAGNETIC_FIELD -> SensorType.MAGNETOMETER
            Sensor.TYPE_ROTATION_VECTOR -> SensorType.ROTATION_VECTOR
            else -> return
        }
        val sample = AndroidSensorEvent(
            sensor = type,
            timestampNs = event.timestamp,
            values = event.values.copyOf(),
            accuracy = event.accuracy,
        )
        synchronized(lock) { latest[type] = sample }
    }

    override fun onAccuracyChanged(sensor: Sensor?, accuracy: Int) = Unit
}
