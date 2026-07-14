# Home Assistant Configuration

This directory stores the Home Assistant configuration used by EnergyHub.

## Directory Structure

```text
homeassistant/
└── live/
    ├── config/
    └── storage/
```

## `live/`

The `live/` directory contains the current Home Assistant configuration synchronized directly from the Home Assistant instance.

It is the source of truth for:

- automations
- scripts
- scenes
- selected helpers
- selected timers
- the Solar / EnergyHub dashboard
- Lovelace dashboard registration and resources

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

Only reviewed files are synchronized.

The complete `.storage` directory must never be copied into the repository.

## Synchronizing from Home Assistant

After changing dashboards, charts, automations, scripts, helpers, or timers in Home Assistant, run:

```powershell
.\tools\dev\sync-from-ha.ps1
```

The script copies the approved Home Assistant files into `homeassistant/live/`.

Then:

1. Review the synchronized changes in GitHub Desktop.
2. Check that no secrets or private data were added.
3. Commit the reviewed changes.
4. Push the commit to GitHub.

The synchronization script does not commit or push automatically.

## Add-on Deployment

Use:

```powershell
.\tools\dev\deploy-to-ha.ps1
```

This script deploys the EnergyHub add-on code from the Windows repository to Home Assistant. It does not copy Home Assistant dashboards, automations, scripts, or helpers.

## Development Workflow

### EnergyHub Python code

```text
Edit in VS Code
→ deploy to Home Assistant
→ rebuild & restart add-on
→ test
→ review in GitHub Desktop
→ commit
→ push
```

### Home Assistant configuration

```text
Edit in Home Assistant
→ run sync-from-ha.ps1
→ review in GitHub Desktop
→ commit
→ push
```

## Security

Never commit secrets, authentication files, tokens, passwords, private URLs, Home Assistant databases, logs, or unreviewed `.storage` files.

Review every synchronized file before committing because this repository is public.

## Source of Truth

- Windows Git repository → EnergyHub add-on source code
- Running Home Assistant → Home Assistant configuration

The synchronization scripts keep both represented in Git for version control, review, backup, and documentation.