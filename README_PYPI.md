# OpenSim-Pymote

Professional Python API for OpenSimulator with structured return values**

[![PyPI version](https://badge.fury.io/py/opensim-pymote.svg)](https://pypi.org/project/opensim-pymote/)
[![Python](https://img.shields.io/pypi/pyversions/opensim-pymote.svg)](https://pypi.org/project/opensim-pymote/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Control OpenSimulator programmatically from Python with a clean, typed API and structured return values.

## Features

✨ **Structured Return Values** - Get typed objects, not just text  
🎯 **Type Hints** - Full IDE autocomplete support  
📦 **Data Classes** - Region, User, Stats objects  
🔄 **Context Manager** - Automatic connection handling  
⚡ **TCP-Based** - Fast, reliable communication  
🐍 **Pure Python** - No external dependencies  

## Installation

```bash
pip install opensim-pymote
```

## Quick Start

```python
from opensim_pymote import OpenSimClient

# Connect to OpenSim
with OpenSimClient(host='localhost', port=9500) as client:
    # Get server version
    result = client.show_version()
    print(result.output)
    
    # Get structured data
    regions = client.get_regions()
    for region in regions:
        print(f"{region.name} at {region.location}")
    
    # User management
    result = client.create_user("John", "Doe", "pass", "john@example.com")
    if result.success:
        print("User created!")
```

## Return Values

All commands return a `CommandResult` object:

```python
result = client.show_version()

result.success   # bool: True if command succeeded
result.output    # str: Raw command output
result.data      # Any: Parsed structured data (if available)
result.error     # str: Error message (if failed)
```

## Structured Data

Get typed objects instead of parsing text:

```python
# Get regions as Region objects
regions = client.get_regions()
for region in regions:
    print(f"{region.name} - UUID: {region.uuid}")
    print(f"Location: {region.location_x}, {region.location_y}")
    print(f"Size: {region.size_x}x{region.size_y}")

# Get users as User objects
users = client.get_users()
for user in users:
    print(f"{user.full_name} in {user.region}")
    if user.online:
        print(f"  Position: {user.position}")

# Get stats as Stats object
stats = client.get_stats()
print(f"FPS: {stats.fps}")
print(f"Agents: {stats.agents}")
print(f"Objects: {stats.objects}")
```

## API Overview

### User Management

```python
client.create_user(first_name, last_name, password, email)
client.set_user_level(first_name, last_name, level)
client.kick_user(first_name, last_name, message="")
client.reset_user_password(first_name, last_name, new_password)
users = client.get_users(full=True)
```

### Region Management

```python
client.create_region(region_name, region_file)
client.delete_region(region_name)
client.change_region(region_name)
regions = client.get_regions()
client.region_restart()
client.region_restart_notice("Message", 300, 120, 60)
```

### Object Management

```python
client.delete_object_id(uuid)
client.delete_object_name(name, use_regex=False)
client.delete_object_owner(uuid)
client.delete_object_outside()
client.edit_scale(prim_name, x, y, z)
```

### Terrain

```python
client.terrain_load(filename)
client.terrain_save(filename)
client.terrain_fill(value)
client.terrain_elevate(amount)
client.terrain_lower(amount)
client.terrain_bake()
client.terrain_revert()
```

### Archives

```python
client.save_oar(filename, noassets=False, publish=False)
client.load_oar(filename, merge=False, skip_assets=False)
client.save_iar(first, last, path, password, filename)
client.load_iar(first, last, path, password, filename)
```

### Monitoring

```python
client.show_version()
client.show_uptime()
stats = client.get_stats()
client.show_threads()
client.monitor_report()
```

### System

```python
client.backup()
client.shutdown()
client.force_gc()
client.set_log_level("DEBUG")
```

## Complete Example

```python
from opensim_pymote import OpenSimClient, CommandError

try:
    with OpenSimClient() as client:
        # Check server status
        result = client.show_version()
        print(f"OpenSim Version: {result.output}")
        
        # Get all regions
        regions = client.get_regions()
        print(f"\nFound {len(regions)} regions:")
        for region in regions:
            print(f"  - {region.name} at ({region.location_x}, {region.location_y})")
        
        # Backup each region
        for region in regions:
            client.change_region(region.name)
            result = client.backup()
            if result.success:
                print(f"✓ Backed up {region.name}")
        
        # Get online users
        users = client.get_users()
        print(f"\n{len(users)} users online:")
        for user in users:
            print(f"  - {user.full_name} in {user.region}")
        
        # Send alert
        client.alert("Backup complete!")
        
except CommandError as e:
    print(f"Command failed: {e}")
except Exception as e:
    print(f"Error: {e}")
```

## Data Models

### Region

```python
@dataclass
class Region:
    name: str
    uuid: str
    location_x: int
    location_y: int
    size_x: int = 256
    size_y: int = 256
    external_hostname: Optional[str] = None
    port: Optional[int] = None
```

### User

```python
@dataclass
class User:
    first_name: str
    last_name: str
    uuid: Optional[str] = None
    region: Optional[str] = None
    position: Optional[tuple] = None
    online: bool = False
    level: int = 0
```

### Stats

```python
@dataclass
class Stats:
    fps: Optional[float] = None
    physics_fps: Optional[float] = None
    agents: Optional[int] = None
    objects: Optional[int] = None
    scripts: Optional[int] = None
    memory_mb: Optional[float] = None
    uptime: Optional[str] = None
```

## Requirements

- Python 3.7+
- OpenSimulator with Pymote server enabled
- Network access to OpenSim server (default port 9500)

## Server Setup

Enable Pymote in OpenSim's `OpenSim.ini`:

```ini
[Pymote]
    Enabled = true
    Port = 9500
    BindAddress = 127.0.0.1
```

## Error Handling

```python
from opensim_pymote import OpenSimClient, ConnectionError, CommandError

try:
    with OpenSimClient(timeout=10.0) as client:
        result = client.show_version()
        
except ConnectionError as e:
    print(f"Cannot connect: {e}")
    
except CommandError as e:
    print(f"Command failed: {e}")
```

## Type Hints

Full type hints for IDE support:

```python
from opensim_pymote import OpenSimClient, CommandResult
from typing import List

def backup_all_regions(client: OpenSimClient) -> None:
    regions: List[Region] = client.get_regions()
    for region in regions:
        result: CommandResult = client.backup()
        if result.success:
            print(f"Backed up: {region.name}")
```

## License

MIT License - see LICENSE file for details

## Version

1.0.0

## Links

- GitHub: <https://github.com/opensim/opensim-pymote>
- PyPI: <https://pypi.org/project/opensim-pymote/>
- Documentation: <https://github.com/opensim/opensim-pymote/blob/main/README.md>
