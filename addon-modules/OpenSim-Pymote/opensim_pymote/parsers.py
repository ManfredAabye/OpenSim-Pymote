"""
Output parsers for structured data extraction
"""

import re
from typing import List, Optional
from .models import Region, User, Stats, TerrainInfo


def parse_regions(output: str) -> List[Region]:
    """
    Parse 'show regions' output into Region objects
    
    Example output:
        Region Name             Region UUID                          Location                 Size    Port   Flags
        DefaultRegion           1234-5678-90ab-cdef                  1000,1000                256x256 9000   DefaultRegion
    """
    regions = []
    lines = output.strip().split('\n')
    
    for line in lines:
        if not line.strip() or 'Region Name' in line or '---' in line:
            continue
        
        # Parse line (space-separated or tab-separated)
        parts = line.split()
        if len(parts) < 3:
            continue
        
        try:
            name = parts[0]
            uuid = parts[1] if len(parts) > 1 else ""
            
            # Parse location (format: "1000,1000")
            if len(parts) > 2:
                location_parts = parts[2].split(',')
                if len(location_parts) == 2:
                    loc_x = int(location_parts[0])
                    loc_y = int(location_parts[1])
                else:
                    loc_x, loc_y = 0, 0
            else:
                loc_x, loc_y = 0, 0
            
            # Parse size (format: "256x256")
            if len(parts) > 3:
                size_parts = parts[3].split('x')
                if len(size_parts) == 2:
                    size_x = int(size_parts[0])
                    size_y = int(size_parts[1])
                else:
                    size_x, size_y = 256, 256
            else:
                size_x, size_y = 256, 256
            
            # Parse port
            port = int(parts[4]) if len(parts) > 4 else None
            
            region = Region(
                name=name,
                uuid=uuid,
                location_x=loc_x,
                location_y=loc_y,
                size_x=size_x,
                size_y=size_y,
                port=port
            )
            regions.append(region)
            
        except (ValueError, IndexError):
            continue
    
    return regions


def parse_users(output: str) -> List[User]:
    """
    Parse 'show users' output into User objects
    
    Example output:
        Name                    Region                  Position
        John Doe                DefaultRegion           <128, 128, 25>
    """
    users = []
    lines = output.strip().split('\n')
    
    for line in lines:
        if not line.strip() or 'Name' in line or '---' in line:
            continue
        
        parts = line.split()
        if len(parts) < 2:
            continue
        
        try:
            # Parse name (first two parts usually)
            first_name = parts[0]
            last_name = parts[1] if len(parts) > 1 else ""
            
            # Parse region
            region = parts[2] if len(parts) > 2 else None
            
            # Parse position if available (format: <x, y, z>)
            position = None
            if len(parts) > 3:
                pos_match = re.search(r'<(\d+\.?\d*),\s*(\d+\.?\d*),\s*(\d+\.?\d*)>', line)
                if pos_match:
                    position = (
                        float(pos_match.group(1)),
                        float(pos_match.group(2)),
                        float(pos_match.group(3))
                    )
            
            user = User(
                first_name=first_name,
                last_name=last_name,
                region=region,
                position=position,
                online=True
            )
            users.append(user)
            
        except (ValueError, IndexError):
            continue
    
    return users


def parse_stats(output: str) -> Stats:
    """
    Parse 'show stats' output into Stats object
    
    Example output:
        FPS: 54.3
        Physics FPS: 54.2
        Agents: 5
        Child Agents: 0
        Objects: 1234
        Active Scripts: 56
    """
    stats = Stats()
    
    for line in output.strip().split('\n'):
        line = line.strip()
        
        # FPS
        if 'fps' in line.lower() and 'physics' not in line.lower():
            match = re.search(r'(\d+\.?\d*)', line)
            if match:
                stats.fps = float(match.group(1))
        
        # Physics FPS
        elif 'physics fps' in line.lower():
            match = re.search(r'(\d+\.?\d*)', line)
            if match:
                stats.physics_fps = float(match.group(1))
        
        # Agents
        elif 'agents' in line.lower() and 'child' not in line.lower():
            match = re.search(r'(\d+)', line)
            if match:
                stats.agents = int(match.group(1))
        
        # Objects
        elif 'objects' in line.lower():
            match = re.search(r'(\d+)', line)
            if match:
                stats.objects = int(match.group(1))
        
        # Scripts
        elif 'scripts' in line.lower():
            match = re.search(r'(\d+)', line)
            if match:
                stats.scripts = int(match.group(1))
        
        # Memory
        elif 'memory' in line.lower():
            match = re.search(r'(\d+\.?\d*)', line)
            if match:
                stats.memory_mb = float(match.group(1))
    
    return stats


def parse_terrain_stats(output: str) -> Optional[TerrainInfo]:
    """Parse terrain statistics"""
    try:
        lines = output.strip().split('\n')
        min_height = max_height = avg_height = 0.0
        
        for line in lines:
            if 'min' in line.lower():
                match = re.search(r'(\d+\.?\d*)', line)
                if match:
                    min_height = float(match.group(1))
            elif 'max' in line.lower():
                match = re.search(r'(\d+\.?\d*)', line)
                if match:
                    max_height = float(match.group(1))
            elif 'avg' in line.lower() or 'average' in line.lower():
                match = re.search(r'(\d+\.?\d*)', line)
                if match:
                    avg_height = float(match.group(1))
        
        return TerrainInfo(
            min_height=min_height,
            max_height=max_height,
            avg_height=avg_height
        )
    except Exception:
        return None
