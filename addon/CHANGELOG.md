# Changelog

## 1.0.2 - 2026-08-01

- First release-ready EnergyHub 1.0 build.
- Added persistent FTDI `/dev/serial/by-id` configuration with UART/udev access.
- Added executable release tests enforced during the Docker image build.
- Pinned `paho-mqtt` and `mppsolar` dependencies.
- Removed weak public MQTT credential defaults.
- Fixed the runtime publisher path and build-version startup banner.
- Removed obsolete raw inverter warning MQTT Discovery/state.
- Validated rebuild and full Home Assistant host restart on the real installation.

See the repository root `CHANGELOG.md` for complete details.
