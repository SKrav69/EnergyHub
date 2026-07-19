# Home Assistant Configuration

This directory contains the versioned Home Assistant part of EnergyHub.

For full behavior, see [`docs/12-HomeAssistant-Configuration.md`](../docs/12-HomeAssistant-Configuration.md).

## Directory structure

```text
homeassistant/
  live/
    config/
      configuration.yaml
      automations.yaml
      scripts.yaml
      scenes.yaml
    storage/
      input_boolean
      input_number
      timer
      lovelace.dashboard_powmr1
      lovelace_dashboards
      lovelace_resources
```

## What is versioned

- EnergyHub YAML automations and scripts;
- selected helpers;
- the EnergyHub dashboard;
- required dashboard resources.

## What is not versioned

- secrets;
- entity registry exports;
- recorder database;
- tokens;
- unrelated `.storage` state;
- temporary backups.

## Current HA-owned functions

- Autopilot helper;
- Hybrid schedule at 23:50 and Solar restoration at 07:00;
- live Solcast publication;
- atomic Daily Summary publication;
- manual Panic script;
- transition notifications;
- beacon;
- third-floor heat-pump auto-off;
- dashboard and floor controls.

## Current EnergyHub-owned functions

- telemetry and health;
- history and Grid Confidence;
- Hybrid/Panic decisions;
- inverter transitions and verification;
- Grid Import and Daily Summary persistence;
- restart reconstruction;
- MQTT state.

## Synchronize live HA to Git

```powershell
.\tools\dev\sync-from-ha.ps1
```

Review all changes before committing. Do not commit `core.entity_registry` or CSV exports created for audits.

## Synchronize Git to HA

```powershell
.\tools\dev\sync-to-ha.ps1
```

Reload the affected HA component or restart HA as directed.

## Deploy add-on code

```powershell
.\tools\dev\deploy-to-ha.ps1
```

Rebuild and restart the local EnergyHub add-on.

## Editing safety

- Edit dashboards/helpers through HA UI where possible.
- Do not overwrite live `.storage` files while HA is running.
- Replace YAML files as complete files, then reload automations/scripts.
- A conditional dashboard card displays all branches in edit mode; test the final view outside edit mode.

## Current dashboard dependencies

- ApexCharts Card custom resource;
- MQTT integration;
- Solcast entities;
- listed room sensors and smart plugs.

## Security

The repository must not contain real passwords or tokens. Published add-on defaults still require hardening before external release.
