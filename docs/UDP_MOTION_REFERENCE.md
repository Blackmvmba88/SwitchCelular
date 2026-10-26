# Experimental UDP motion reference

This branch adds a **non-normative** Python reference for exercising a minimal
orientation datagram and desktop UDP reception. It does **not** claim compliance
with the frozen PeripheralOS MOTION_PACKET_V1 specification.

The temporary JSON envelope is:
`version` (integer 1), `seq` (uint32), `timestamp_ms` (nonnegative integer),
and finite numeric `yaw`, `pitch`, `roll` (degrees by convention).

Run from the repository root:

```sh
python -m unittest discover -s runtime -p 'test_udp_motion_reference.py'
python runtime/udp_motion_reference.py
```

Receiver binds to loopback `127.0.0.1:8765` by default. It deliberately
does not inject mouse or game input, does not authenticate remote senders,
and must not be exposed to untrusted networks. To send a loopback test:

```sh
python -c "import socket; from runtime.udp_motion_reference import encode_packet; socket.socket(socket.AF_INET,socket.SOCK_DGRAM).sendto(encode_packet(1,0,0,0),('127.0.0.1',8765))"
```

Next: compare the envelope with canonical MOTION_PACKET_V1, add replay
protection and a configurable authenticated desktop receiver before
supporting remote phone connections.
