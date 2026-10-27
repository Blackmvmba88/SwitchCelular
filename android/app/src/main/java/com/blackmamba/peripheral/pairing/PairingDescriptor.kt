package com.blackmamba.peripheral.pairing

import android.net.Uri

data class PairingDescriptor(
    val version: Int,
    val transport: String,
    val host: String,
    val port: Int,
    val nonce: String,
    val expiresAtEpochSeconds: Long?,
)

class PairingDescriptorException(message: String) : IllegalArgumentException(message)

object PairingUriParser {
    private val noncePattern = Regex("^[A-Za-z0-9_-]{16,}$")

    fun parse(
        uri: Uri,
        nowEpochSeconds: Long = System.currentTimeMillis() / 1000L,
    ): PairingDescriptor {
        if (!uri.scheme.equals("blackmamba", ignoreCase = true) || !uri.host.equals("pair", ignoreCase = true)) {
            throw PairingDescriptorException("Pairing URI must use blackmamba://pair")
        }

        fun required(name: String): String = uri.getQueryParameter(name)
            ?.takeIf { it.isNotBlank() }
            ?: throw PairingDescriptorException("Missing pairing field: $name")

        val version = required("v").toIntOrNull()
            ?: throw PairingDescriptorException("Invalid pairing version")
        if (version != 1) {
            throw PairingDescriptorException("Unsupported pairing version: $version")
        }

        val transport = required("transport").lowercase()
        if (transport != "udp") {
            throw PairingDescriptorException("Unsupported pairing transport: $transport")
        }

        val endpointHost = required("host")
        if (endpointHost.length > 253 || endpointHost.any { it.isWhitespace() }) {
            throw PairingDescriptorException("Invalid pairing host")
        }

        val port = required("port").toIntOrNull()
            ?: throw PairingDescriptorException("Invalid pairing port")
        if (port !in 1..65535) {
            throw PairingDescriptorException("Pairing port must be between 1 and 65535")
        }

        val nonce = required("nonce")
        if (!noncePattern.matches(nonce)) {
            throw PairingDescriptorException("Pairing nonce must be URL-safe and at least 16 characters")
        }

        val expiresAt = uri.getQueryParameter("exp")?.let {
            it.toLongOrNull() ?: throw PairingDescriptorException("Invalid pairing expiry")
        }
        if (expiresAt != null && expiresAt <= nowEpochSeconds) {
            throw PairingDescriptorException("Pairing descriptor has expired")
        }

        return PairingDescriptor(
            version = version,
            transport = transport,
            host = endpointHost,
            port = port,
            nonce = nonce,
            expiresAtEpochSeconds = expiresAt,
        )
    }
}
