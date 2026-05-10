# shadowtagai-antigravity (Arch Linux Package)

Arch Linux / Manjaro package for SHADOWTAGAI Kernel Chain service.

## Overview

This package provides:

- SHADOWTAGAI FastAPI service installation

- systemd service integration

- Automatic daily updates via GitHub Actions

## Quick Install

```bash
git clone https://github.com/ShadowTag-v2/shadowtag_v4-fastapi-services.git
cd shadowtag_v4-fastapi-services/antigravity-arch
makepkg -si

```

## Post-Install

### Configure

Edit the configuration file:

```bash
sudo nano /etc/shadowtagai/config.env

```

Required settings:

```bash
GOOGLE_API_KEY=your-gemini-api-key
SECRET_KEY=your-secret-key

```

### Start Service

```bash

# Enable and start

sudo systemctl enable --now shadowtagai

# Check status

sudo systemctl status shadowtagai

# View logs

journalctl -u shadowtagai -f

```

### Verify

```bash
curl http://localhost:8000/health

```

Expected response:

```json
{ "status": "healthy", "service": "shadowtagai-kernel-chain", "version": "0.1.0" }
```

## Directory Structure

| Path                                          | Purpose                         |
| --------------------------------------------- | ------------------------------- |
| `/opt/shadowtagai/`                           | Application code and virtualenv |
| `/etc/shadowtagai/`                           | Configuration files             |
| `/var/log/shadowtagai/`                       | Log files                       |
| `/usr/lib/systemd/system/shadowtagai.service` | systemd unit                    |

## Auto-Updates

A GitHub Actions workflow runs daily to:

1. Check `pyproject.toml` for version changes

2. Update `PKGBUILD` if needed

3. Run validation tests

4. Commit and push changes

To get updates:

```bash
cd shadowtag_v4-fastapi-services/antigravity-arch
git pull
makepkg -si

```

## Manual Build

```bash

# Build package

makepkg -s

# Install built package

sudo pacman -U shadowtagai-antigravity-*.pkg.tar.zst

# Or build and install in one step

makepkg -si

```

## Uninstall

```bash
sudo systemctl stop shadowtagai
sudo systemctl disable shadowtagai
sudo pacman -R shadowtagai-antigravity

```

## Development

### Run Tests

```bash
pip install pytest
pytest tests/ -v

```

### Check PKGBUILD Syntax

```bash
bash -n PKGBUILD

```

### Validate with namcap

```bash
namcap PKGBUILD

```

## API Endpoints

| Endpoint      | Method | Description                 |
| ------------- | ------ | --------------------------- |
| `/`           | GET    | Service info                |
| `/health`     | GET    | Health check                |
| `/decision`   | POST   | Execute kernel chain        |
| `/validation` | GET    | JR Engine validation report |
| `/metrics`    | GET    | Prometheus metrics          |

## Troubleshooting

### Service won't start

```bash

# Check logs

journalctl -u shadowtagai -e

# Verify config

sudo cat /etc/shadowtagai/config.env

# Test manually

sudo -u shadowtagai /opt/shadowtagai/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000

```

### Permission errors

```bash

# Fix ownership

sudo chown -R shadowtagai:shadowtagai /opt/shadowtagai
sudo chown -R shadowtagai:shadowtagai /var/log/shadowtagai

```

### Python version mismatch

```bash

# Check Python version

python --version  # Needs 3.11+

# If using pyenv

pyenv install 3.11.0
pyenv global 3.11.0

```

## License

Proprietary - SHADOWTAGAI Core Stack Team
