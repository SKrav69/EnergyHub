# Home Assistant Configuration

This directory stores the Home Assistant configuration used by EnergyHub.

## Directory Structure

```text
homeassistant/
├── live/
│   ├── config/
│   └── storage/
└── legacy/
```

## `live/`

The `live/` directory contains the current Home Assistant configuration synchronized directly from the Home Assistant instance.

It is the source of truth for:

- automations;
- scripts;
- scenes;
- selected helpers;
- selected timers;
- the Solar / EnergyHub dashboard;
- Lovelace dashboard registration and resources.

### `live/config/`

Contains selected YAML configuration files copied from:

```text
/config/
```

Current files:

- `automations.yaml`
- `scripts.yaml`
- `scenes.yaml`
- `configuration.yaml`

### `live/storage/`

Contains explicitly approved Home Assistant storage files copied from:

```text
/config/.storage/
```

Current files:

- `input_boolean`
- `input_number`
- `timer`
- `lovelace.dashboard_powmr1`
- `lovelace_dashboards`
- `lovelace_resources`

Only reviewed files are synchronized. The complete `.storage` directory must never be copied into the repository.

## `legacy/`

The `legacy/` directory contains older manually exported YAML files.

These files are kept for reference only and may not match the current Home Assistant configuration.

Do not update `legacy/` after every Home Assistant change.

## Synchronizing from Home Assistant

After changing dashboards, charts, automations, scripts, helpers, or timers in Home Assistant, run:

```powershell
.\tools\dev\sync-from-ha.ps1
```

The script copies the approved Home Assistant files into `homeassistant/live/`.

Then:

1. Review changes in GitHub Desktop or with `git diff`.
2. Check that no secrets or private data were added.
3. Commit the reviewed changes.

The script does not commit or push automatically.

## Add-on Deployment

EnergyHub add-on code is edited in the Windows repository and deployed in the opposite direction:

```text
Windows repository
→ Home Assistant add-on directory
```

Use:

```powershell
.\tools\dev\deploy-to-ha.ps1
```

The add-on deployment script does not copy Home Assistant dashboards or automations.

## Security

Never commit:

- `secrets.yaml`;
- authentication files;
- API tokens;
- passwords;
- private URLs;
- `home-assistant_v2.db`;
- log files;
- unrestricted `.storage` contents;
- mobile-app registration data;
- device and entity registries unless explicitly reviewed.

The repository is public, so every synchronized file must be reviewed before committing.

## Current Workflow

### EnergyHub Python code

```text
Edit in VS Code
→ deploy to Home Assistant
→ test
→ commit
```

### Home Assistant configuration

```text
Edit in Home Assistant
→ run sync-from-ha.ps1
→ review Git changes
→ commit
```