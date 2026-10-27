# Android Motion Producer v0.1

This directory hosts the native Android producer for PeripheralOS.

## v0.1 Scope

- Read gyroscope, accelerometer, magnetometer, and Android rotation-vector sensors.
- Fuse orientation into a normalized quaternion.
- Recenter the current phone pose into a relative orientation zero.
- Build canonical `MOTION_PACKET_V1` packets compatible with the Python desktop receiver.
- Send packets over configurable UDP at roughly 60 Hz.
- Accept short-lived `blackmamba://pair` QR deep links.
- Provide a minimal status UI, `RECENTER`, and touch `FIRE` button.
- Track packet count and battery in the emitted packet stream.

## Non-Goals for v0.1

- Camera-based reference correction.
- BLE transport.
- USB transport.
- Game-specific logic.
- Treating UDP `connect()` as proof that the desktop peer is reachable. A future authenticated handshake will provide peer verification.

## Runtime Flow

```text
Android SensorManager
  ↓
SensorManagerSource
  ↓
DefaultOrientationFusion
  ↓
OrientationCalibration (optional RECENTER)
  ↓
DefaultMotionEngine
  ↓
CanonicalJsonPacketCodec
  ↓
UdpMotionClient
  ↓
Desktop Receiver
```

## First LAN Test

From the repository root on the desktop:

```bash
# Terminal 1: listen for phone packets
python desktop/motion_receiver.py --port 41235

# Terminal 2: render the short-lived QR for this desktop
python -m pip install -r desktop/requirements-pairing.txt
python desktop/pairing_qr.py --port 41235
```

Build/install the Android app with a JDK 17 + Android SDK environment:

```bash
gradle -p android :app:installDebug
```

Then:

1. Put phone and desktop on the same LAN/Wi-Fi.
2. Scan `pairing.svg` using the normal Android camera/QR scanner.
3. Open the `blackmamba://pair` deep link in PeripheralOS.
4. The phone UI should show `UDP: ARMED`, the endpoint, and sensor availability.
5. Hold the phone in the desired neutral aiming pose and press `RECENTER`; UI should show `Center: CALIBRATED`.
6. Move the phone: the desktop receiver should print increasing packet sequences and changing quaternions.
7. Hold `FIRE`: receiver output should show `buttons=0x01`; release it and the value returns to `0x00`.
8. For mapper validation, replace the raw receiver with `python desktop/aim_preview.py --port 41235`.
9. On macOS only, after preview looks correct, opt into cursor output with `python desktop/aim_preview.py --port 41235 --mouse`.

The QR is discovery/bootstrap only. Motion packets are not yet authenticated; keep this MVP on a trusted local network.
