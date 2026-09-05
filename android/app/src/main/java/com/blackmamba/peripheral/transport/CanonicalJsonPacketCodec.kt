package com.blackmamba.peripheral.transport

import com.blackmamba.peripheral.model.MotionPacket
import com.blackmamba.peripheral.model.Quaternion
import com.blackmamba.peripheral.model.Vector3
import org.json.JSONArray
import org.json.JSONObject

/** JSON binding compatible with core.protocol_core.serializer on desktop. */
class CanonicalJsonPacketCodec : PacketCodec {
    override fun encode(packet: MotionPacket): ByteArray {
        val json = JSONObject()
        json.put("version", packet.version)
        json.put("sequence", packet.sequence)
        json.put("timestamp_ns", packet.timestampNs)
        json.put("orientation", quaternion(packet.orientation))
        json.put("angular_velocity", vector(packet.angularVelocity))
        json.put("acceleration", vector(packet.acceleration))
        json.put("buttons", packet.buttons)
        json.put("battery", packet.battery)
        json.put("flags", packet.flags)
        json.put("capabilities", JSONArray(packet.capabilities))
        json.put("reserved", JSONArray(packet.reserved))
        json.put("extension_length", packet.extensionLength)
        return json.toString().toByteArray(Charsets.UTF_8)
    }

    override fun decode(payload: ByteArray): MotionPacket {
        val json = JSONObject(payload.toString(Charsets.UTF_8))
        val orientation = json.getJSONObject("orientation")
        return MotionPacket(
            version = json.getInt("version"),
            sequence = json.getLong("sequence"),
            timestampNs = json.getLong("timestamp_ns"),
            orientation = Quaternion(
                w = orientation.getDouble("w").toFloat(),
                x = orientation.getDouble("x").toFloat(),
                y = orientation.getDouble("y").toFloat(),
                z = orientation.getDouble("z").toFloat(),
            ),
            angularVelocity = decodeVector(json.getJSONObject("angular_velocity")),
            acceleration = decodeVector(json.getJSONObject("acceleration")),
            buttons = json.optInt("buttons", 0),
            battery = json.optInt("battery", 0),
            flags = json.optInt("flags", 0),
            capabilities = decodeStrings(json.optJSONArray("capabilities")),
            reserved = decodeStrings(json.optJSONArray("reserved")),
            extensionLength = json.optInt("extension_length", 0),
        )
    }

    private fun quaternion(q: Quaternion): JSONObject = JSONObject()
        .put("w", q.w)
        .put("x", q.x)
        .put("y", q.y)
        .put("z", q.z)

    private fun vector(v: Vector3): JSONObject = JSONObject()
        .put("x", v.x)
        .put("y", v.y)
        .put("z", v.z)

    private fun decodeVector(json: JSONObject): Vector3 = Vector3(
        x = json.getDouble("x").toFloat(),
        y = json.getDouble("y").toFloat(),
        z = json.getDouble("z").toFloat(),
    )

    private fun decodeStrings(array: JSONArray?): List<String> {
        if (array == null) return emptyList()
        return List(array.length()) { index -> array.getString(index) }
    }
}
