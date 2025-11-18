# ⚠️This is a feasibility study and has no practical use yet

# OpenSim-Pymote
Python Remote Control for OpenSimulator

**OpenSim-Pymote** provides TCP-based remote control of OpenSimulator from Python.

---

## 🎯 Features

- ✅ **Remote Control** - Control OpenSim from anywhere via TCP
- ✅ **Structured Data** - Returns typed objects (Region, User, Stats)
- ✅ **70+ API Methods** - Pre-defined methods for all commands
- ✅ **Command Whitelist** - Security via Pymote.ini (like osslEnable.ini)
- ✅ **Rate Limiting** - Commands per minute/hour limits
- ✅ **IP Whitelist** - Restrict access by IP address
- ✅ **Type Hints** - Full IDE autocomplete support
- ✅ **Context Manager** - Automatic connection cleanup
- ✅ **No Dependencies** - Pure Python 3.7+ standard library

---

## 📦 Installation

### 1. C# TCP Server (OpenSim Addon)

**Enable in `bin/config-include/Pymote.ini`:**

```ini
[Pymote]
    ; Enable TCP server
    Enabled = true
    
    ; TCP configuration
    Port = 9500
    BindAddress = "127.0.0.1"
    Timeout = 30
    MaxConnections = 10
    
    ; Security
    LogCommands = false

[PymoteCommands]
    ; Allow read-only commands (safe)
    Allow_show_info = true
    Allow_show_version = true
    Allow_show_regions = true
    Allow_show_users = true
    Allow_show_stats = true
    
    ; Deny destructive commands (default)
    Allow_delete_object_id = false
    Allow_shutdown = false
```

**Compile:**

```bash
runprebuild.bat
# Then rebuild OpenSim solution
```

### 2. Python Client Package

**Install from PyPI** (when published):

```bash
pip install opensim-pymote
```

**Or install from source:**

```bash
cd addon-modules/OpenSim-Pymote
pip install -e .
```

---

## 🚀 Usage

### Python TCP Client

```python
from opensim_pymote import OpenSimClient

# Connect to OpenSim
with OpenSimClient() as client:
    # Structured return values
    result = client.show_version()
    print(f"Success: {result.success}")
    print(f"Output: {result.output}")
    
    # Get typed data objects
    regions = client.get_regions()  # Returns List[Region]
    for region in regions:
        print(f"{region.name} at ({region.location_x}, {region.location_y})")
    
    # User management
    users = client.get_users()  # Returns List[User]
    for user in users:
        print(f"{user.full_name} - {user.region}")
    
    # Statistics
    stats = client.get_stats()  # Returns Stats object
    print(f"FPS: {stats.fps}, Agents: {stats.agents}")
```

---

## 🔒 Security Configuration (Pymote.ini)

### Command Whitelist

Similar to `osslEnable.ini`, control which commands can be executed:

```ini
[PymoteCommands]
    ; SAFE - Read-only commands
    Allow_show_regions = true
    Allow_show_users = true
    Allow_show_stats = true
    
    ; MODERATE - User management
    Allow_create_user = false
    Allow_kick_user = false
    Allow_alert = false
    
    ; DANGER - Destructive operations
    Allow_delete_object_id = false
    Allow_shutdown = false
    Allow_terrain_fill = false
    
    ; Wildcards supported
    Allow_show_* = true  ; Allow all "show" commands
```

### IP Whitelist

```ini
[PymoteIPWhitelist]
    AllowedIP1 = "127.0.0.1"
    AllowedIP2 = "192.168.1.100"
    AllowedIP3 = "10.0.0.0/24"
```

### User Level Requirements

```ini
[PymoteUserLevels]
    ; Require admin level (250) for dangerous commands
    RequireLevel_delete_object_id = 250
    RequireLevel_shutdown = 250
    RequireLevel_create_user = 250
```

### Rate Limiting

```ini
[PymoteRateLimit]
    Enabled = true
    MaxCommandsPerMinute = 60
    MaxCommandsPerHour = 1000
```

---

## 📚 API Reference

### Python.NET API (opensim object)

Available in embedded scripts as `opensim`:

```python
opensim.RunCommand(command)              # Execute any console command
opensim.Alert(message)                   # Broadcast alert
opensim.AlertUser(first, last, msg)      # Alert specific user
opensim.CreateUser(first, last, pw, email)
opensim.KickUser(first, last, message)
opensim.ChangeRegion(name)
opensim.RestartRegion()
---

## 📚 API Reference

### Python Client API

See [README_PYPI.md](README_PYPI.md) for complete API documentation.

**Quick Reference:**

```python
# Connection
client = OpenSimClient(host='127.0.0.1', port=9500, timeout=30.0)
client.connect()
client.disconnect()

# Alert commands
client.alert(message)
client.alert_user(first, last, message)

# User management
client.create_user(first, last, password, email)
client.kick_user(first, last, message)
client.set_user_level(first, last, level)
client.get_users()  # Returns List[User]

# Region management
client.change_region(name)
client.region_restart()
client.get_regions()  # Returns List[Region]

# System commands
client.backup()
client.save_oar(filename)
client.load_oar(filename)
client.show_version()
client.get_stats()  # Returns Stats object

# Terrain commands
client.terrain_load(filename)
client.terrain_save(filename)
client.terrain_fill(value)
```

**Complete API documentation:** See [README_PYPI.md](README_PYPI.md)

---

## 📊 Examples

### Remote Monitoring

```python
from opensim_pymote import OpenSimClient
import time

with OpenSimClient() as client:
    while True:
        stats = client.get_stats()
        users = client.get_users()
        
        print(f"\n=== OpenSim Status ===")
        print(f"FPS: {stats.fps}")
        print(f"Agents: {stats.agents}")
        print(f"Online Users: {len(users)}")
        
        for user in users:
            print(f"  - {user.full_name} in {user.region}")
        
        time.sleep(60)
```

### Batch User Creation

```python
from opensim_pymote import OpenSimClient

users_to_create = [
    ("Alice", "Smith", "pass1", "alice@example.com"),
    ("Bob", "Jones", "pass2", "bob@example.com"),
    ("Charlie", "Brown", "pass3", "charlie@example.com"),
]

with OpenSimClient() as client:
    for first, last, password, email in users_to_create:
        result = client.create_user(first, last, password, email)
        
        if result.success:
            print(f"✓ Created: {first} {last}")
        else:
            print(f"✗ Failed: {first} {last} - {result.error}")
```

---

## 🛡️ Security Best Practices

### 1. Production Configuration

```ini
[Pymote]
    ; Only enable when needed
    Enabled = false
    
    ; Bind to localhost only
    BindAddress = "127.0.0.1"
    
    ; Enable command logging
    LogCommands = true

[PymoteCommands]
    ; Default deny - only allow safe commands
    Allow_show_* = true
    Allow_monitor_report = true
    
    ; Explicitly deny dangerous commands
    Allow_delete_* = false
    Allow_shutdown = false
    Allow_terrain_fill = false

[PymoteIPWhitelist]
    ; Only allow from localhost
    AllowedIP1 = "127.0.0.1"

[PymoteRateLimit]
    ; Enable rate limiting
    Enabled = true
    MaxCommandsPerMinute = 60
```

### 2. SSH Tunneling for Remote Access

```bash
# On client machine
ssh -L 9500:localhost:9500 user@opensim-server

# Then connect Python client to localhost:9500
```

### 3. Firewall Rules

```bash
# Block external access to Pymote port
sudo ufw deny 9500
sudo ufw allow from 127.0.0.1 to any port 9500
```

---

## 🐛 Troubleshooting

### Python.NET Issues

**Error: `Failed to initialize Python engine`**

```ini
[Pymote]
    ; Set correct Python paths
    PythonHome = "C:\Python310"          # Windows
    PythonDLL = "python310.dll"
    
    ; Or on Linux
    PythonHome = "/usr"
    PythonDLL = "libpython3.10.so"
```

**Solution:**

- Install Python.NET: `pip install pythonnet`
- Verify Python version matches DLL
- Check Python installation path

### Command Not Allowed

**Error: `Command not allowed: delete object`**

**Solution:** Enable command in `Pymote.ini`:

```ini
[PymoteCommands]
---

## 🐛 Troubleshooting

### Command Not Allowed

**Error: `Command not allowed: delete object`**

**Solution:** Enable command in `Pymote.ini`:

```ini
[PymoteCommands]
    Allow_delete_object_id = true
```

### Connection Refused

**Error: `ConnectionError: Failed to connect`**

**Solutions:**

- Verify OpenSim is running
- Check `Enabled = true` in Pymote.ini
- Verify port is correct (default: 9500)
- Check firewall rules

### Rate Limit Exceeded

**Error: `Rate limit exceeded for IP`**

**Solution:** Adjust limits in `Pymote.ini`:

```ini
[PymoteRateLimit]
    MaxCommandsPerMinute = 120
    MaxCommandsPerHour = 5000
```

---

## 📚 Documentation Files

- [README_PYPI.md](README_PYPI.md) - Complete PyPI package API reference
- [BUILD_GUIDE.md](BUILD_GUIDE.md) - Build and publish instructions
- [examples_package.py](examples_package.py) - 10 comprehensive examples
- [bin/config-include/Pymote.ini](../../bin/config-include/Pymote.ini) - Configuration reference

---

## 🔄 Version History

**Version 2.0.0** - November 2025

- ✅ TCP-based remote control
- ✅ Command whitelist security (Pymote.ini)
- ✅ IP whitelist and rate limiting
- ✅ User level requirements
- ✅ PyPI package with structured return values
- ✅ Typed data models (Region, User, Stats)
- ✅ 70+ API methods

**Version 1.0.0** - November 2025

- Initial TCP-based implementation

---

## 📝 License

Copyright © OpenSim-Pymote Team 2025. All rights reserved.

---

## 🤝 Support

For issues, questions, or contributions:

- OpenSim Forums
- GitHub Issues
- OpenSim Discord

---

## 🎓 Quick Start Guide

1. **Enable Pymote** in `bin/config-include/Pymote.ini`:

   ```ini
   [Pymote]
       Enabled = true
       Port = 9500
       BindAddress = "127.0.0.1"
   ```

2. **Restart OpenSim**

3. **Install Python client**:

   ```bash
   pip install opensim-pymote
   ```

4. **Use from Python**:

   ```python
   from opensim_pymote import OpenSimClient

   with OpenSimClient() as client:
       regions = client.get_regions()
       for region in regions:
           print(region.name)
   ```

Done! 🎉

