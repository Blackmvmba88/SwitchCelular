# Gun Mode MVP

## Goal

Use an Android phone as a motion pistol controller for desktop games.

## Scope

This document describes the first playable implementation path for the "phone as pistol" mode.

The objective is to keep the core small, explicit, and testable while the implementation grows in layers.

## Runtime Layers

1. `sensor_core`
   - Read gyroscope, accelerometer, and magnetometer samples.
   - Normalize timestamps, units, and sensor status.

2. `fusion_core`
   - Convert raw sensor samples into stable orientation frames.
   - Emit quaternion plus `yaw`, `pitch`, and `roll`.

3. `calibration_core`
   - Recenter the current aim.
   - Apply dead zones and sensitivity.
   - Compensate for drift.

4. `pairing_core`
   - Bootstrap the LAN endpoint with a short-lived QR descriptor.
   - Carry transport, host, port, nonce, and expiry without polluting the motion packet contract.

5. `transport_core`
   - Send aim packets to the desktop host.
   - MVP transport is UDP.

6. `mapper_core`
   - Convert calibrated orientation into aim deltas.
   - Emit relative mouse movement on the host.

7. `trigger_core`
   - Map touch or physical inputs to fire, reload, zoom, and melee.

8. `profile_core`
   - Load and validate the pistol profile.
   - Keep game logic out of the core.

9. `diagnostics_core`
   - Track latency, jitter, packet loss, and drift score.

10. `regression_core`
    - Record traces.
    - Compare against goldens.
    - Detect trajectory drift.

## MVP Flow

```text
desktop pairing QR
  ↓
blackmamba://pair deep link
  ↓
phone sensors
  ↓
Android SensorManagerSource
  ↓
orientation fusion
  ↓
MOTION_PACKET_V1
  ↓
UDP transport
  ↓
desktop receiver
  ↓
AimFrame adapter
  ↓
mapper_core + pistol profile
  ↓
preview deltas
  ↓ (explicit --mouse opt-in on macOS)
relative mouse / left-click FIRE
```

## Required Features

- [x] Short-lived LAN QR pairing descriptor.
- [x] Android deep-link pairing parser.
- [x] Read motion sensors from Android `SensorManager`.
- [x] Produce normalized orientation quaternions.
- [ ] Recenter on demand with a real calibration transform.
- [x] Apply sensitivity, dead zones, and smoothing in the existing desktop mapper.
- [x] Send canonical motion packets over UDP.
- [x] Receive packets continuously on desktop.
- [x] Preview mapped aim deltas without moving the cursor.
- [x] Opt-in relative mouse movement on macOS.
- [x] Fire with a touch button and forward it as button bit `0x01`.
- [ ] Authenticate the post-QR session with a real handshake/ACK.
- [ ] Add live latency/jitter/loss diagnostics to the first playable UI.

## Safety / Trust Boundary

The QR is currently discovery/bootstrap only. UDP `connect()` configures a destination but does not prove a peer is reachable or authenticated. Use the current MVP only on a trusted LAN until the pairing nonce is consumed by an authenticated handshake.

## First Playable Test

```bash
# Generate QR
python -m pip install -r desktop/requirements-pairing.txt
python desktop/pairing_qr.py --port 41235

# Inspect raw packets
python desktop/motion_receiver.py --port 41235

# Or inspect mapped deltas
python desktop/aim_preview.py --port 41235

# Only after preview looks correct, opt into macOS cursor control
python desktop/aim_preview.py --port 41235 --mouse
```

## Non Goals

- No game-specific integration.
- No BLE in v1.
- No USB in v1.
- No advanced recoil model in v1.
- No multiplayer-specific logic.

## Next Execution Slice

1. Implement real recenter/calibration state on Android and desktop.
2. Add authenticated pairing ACK using the QR nonce.
3. Add latency/jitter/loss telemetry and packet sequence-gap detection.
4. Validate mouse scale/inversion on physical Android + macOS hardware.
5. Only then mark the first playable MVP as stable.
