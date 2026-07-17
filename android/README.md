# Android Motion Producer v0.1

This directory hosts the native Android producer for PeripheralOS.

## v0.1 Scope

- Read gyroscope, accelerometer, and magnetometer sensors.
- Build motion packets compatible with the desktop receiver.
- Send packets over configurable UDP.
- Provide a minimal calibration and connection UI.
- Track packet count, battery, and latency.

## Non-Goals for v0.1

- Camera-based reference correction.
- BLE transport.
- USB transport.
- Game-specific logic.

## Suggested Runtime Flow

```text
SensorManager
  ↓
AndroidSensorSource
  ↓
OrientationFusion
  ↓
CalibrationEngine
  ↓
MotionPacketFactory
  ↓
PacketCodec
  ↓
UdpMotionClient
  ↓
Desktop Receiver
```
