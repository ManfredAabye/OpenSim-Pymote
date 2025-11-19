"""
Data models for OpenSim entities
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Region:
    """OpenSim Region information"""
    name: str
    uuid: str
    location_x: int
    location_y: int
    size_x: int = 256
    size_y: int = 256
    external_hostname: Optional[str] = None
    port: Optional[int] = None
    
    @property
    def location(self) -> tuple:
        """Get (x, y) location tuple"""
        return (self.location_x, self.location_y)
    
    def __repr__(self) -> str:
        return f"Region(name='{self.name}', location=({self.location_x}, {self.location_y}))"


@dataclass
class User:
    """OpenSim User information"""
    first_name: str
    last_name: str
    uuid: Optional[str] = None
    region: Optional[str] = None
    position: Optional[tuple] = None
    online: bool = False
    level: int = 0
    
    @property
    def full_name(self) -> str:
        """Get full name"""
        return f"{self.first_name} {self.last_name}"
    
    def __repr__(self) -> str:
        status = "online" if self.online else "offline"
        return f"User(name='{self.full_name}', {status})"


@dataclass
class Stats:
    """OpenSim Server Statistics"""
    fps: Optional[float] = None
    physics_fps: Optional[float] = None
    agents: Optional[int] = None
    objects: Optional[int] = None
    scripts: Optional[int] = None
    memory_mb: Optional[float] = None
    uptime: Optional[str] = None
    
    def __repr__(self) -> str:
        return f"Stats(fps={self.fps}, agents={self.agents}, objects={self.objects})"


@dataclass
class ObjectInfo:
    """OpenSim Object/Prim information"""
    name: str
    uuid: str
    owner: Optional[str] = None
    position: Optional[tuple] = None
    size: Optional[tuple] = None
    
    def __repr__(self) -> str:
        return f"ObjectInfo(name='{self.name}', uuid='{self.uuid}')"


@dataclass
class TerrainInfo:
    """Terrain information"""
    min_height: float
    max_height: float
    avg_height: float
    
    def __repr__(self) -> str:
        return f"TerrainInfo(min={self.min_height:.2f}, max={self.max_height:.2f}, avg={self.avg_height:.2f})"
