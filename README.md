# redfish-wrapper

Simple python wrapper for RedFish HTTP API.

## Features - intel:
- IPMI module reboot
- server power actions - `"PushPowerButton", "On", "GracefulShutdown", "ForceOn", "ForceOff"`
- get system power consumption
- get proprietary metrics - `"ProcessorPowerWatt", "MemoryPowerWatt", "ProcessorBandwidthPercent", "MemoryBandwidthPercent","IOBandwidthGBps"`
- get Thermals stats
- get server power state

## Features - supermicro
- server power actions - `"On", "ForceOff", "GracefulShutdown", "GracefulRestart", "ForceRestart", "Nmi", "ForceOn"`
- get system power consumption
- get Thermals stats
- get server power state

## example

```
from redfishwrapper.intelRedfish import *
intel_ipmi = IntelRedfish(ipmi_host = 'https://1.2.3.4',ipmi_pass='your_pass',ipmi_user='your_user',verifySSL=False)
print(intel_ipmi.getAllMetrics())
```

gives:

```
{'ProcessorPowerWatt': 133.486328125, 'MemoryPowerWatt': 88.114013671875, 'BB Lft Rear Temp': 40, 'BB P1 VR Temp': 42, 'Front Panel Temp': 25, 'SSB Temp': 45, 'BB P2 VR Temp': 39, 'BB BMC Temp': 40, 'BB Rt Rear Temp': 38, 'Riser 1 Temp': 32, 'HSBP 1 Temp': 32, 'Riser 2 Temp': 35, 'Exit Air Temp': 40, 'LAN NIC Temp': 45, 'PS1 Temperature': 30, 'P1 DTS Therm Mgn': -34, 'P2 DTS Therm Mgn': -32, 'P1 Temperature': 52, 'P2 Temperature': 54, 'NVMe 1 Therm Mgn': -33, 'DIMM Thrm Mrgn 1': -55, 'DIMM Thrm Mrgn 2': -57, 'DIMM Thrm Mrgn 3': -53, 'DIMM Thrm Mrgn 4': -58, 'Agg Therm Mgn 1': -25, 'Agg Therm Mgn 2': -35, 'NodeTotalPower': 273}
```
