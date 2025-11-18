"""
OpenSim-Pymote Type Stubs
Provides type hints and code completion for Python scripts running in OpenSim-Pymote

This is a stub-only package - the actual implementation is provided by
the C# PymoteAPI when scripts run inside OpenSim.

Install for development (code completion in IDE):
    pip install opensim-pymote-stubs

Usage in your Python script:
    # Type hints for IDE
    from opensim_pymote import opensim, scene, console
    
    # Now you get autocomplete!
    opensim.Alert('message')
    scene.Name
    console.Output('text')
"""

from typing import Optional

class PymoteAPI:
    """
    OpenSim API - available as 'opensim' in Pymote scripts
    Provides convenient methods for common OpenSim operations
    """
    
    def GetPythonVersion(self) -> str:
        """Get the Python version being used"""
        ...
    
    def RunCommand(self, command: str) -> None:
        """Execute any OpenSim console command"""
        ...
    
    def Alert(self, message: str) -> None:
        """Send alert message to all users"""
        ...
    
    def AlertUser(self, firstName: str, lastName: str, message: str) -> None:
        """Send alert message to specific user"""
        ...
    
    def CreateUser(self, firstName: str, lastName: str, password: str, email: str) -> None:
        """Create a new user account"""
        ...
    
    def KickUser(self, firstName: str, lastName: str, message: str = "") -> None:
        """Kick a user from the simulator"""
        ...
    
    def ChangeRegion(self, regionName: str) -> None:
        """Change to a different region"""
        ...
    
    def RestartRegion(self) -> None:
        """Restart the current region"""
        ...
    
    def Backup(self) -> None:
        """Backup the current region"""
        ...
    
    def SaveOar(self, filename: str) -> None:
        """Save region archive (OAR) to file"""
        ...
    
    def LoadOar(self, filename: str) -> None:
        """Load region archive (OAR) from file"""
        ...
    
    def ShowRegions(self) -> None:
        """Display all regions"""
        ...
    
    def ShowUsers(self) -> None:
        """Display online users"""
        ...
    
    def ShowVersion(self) -> None:
        """Display OpenSim version"""
        ...
    
    def ShowStats(self) -> None:
        """Display server statistics"""
        ...
    
    def TerrainLoad(self, filename: str) -> None:
        """Load terrain from file"""
        ...
    
    def TerrainSave(self, filename: str) -> None:
        """Save terrain to file"""
        ...
    
    def GetScene(self) -> 'Scene':
        """Get the current Scene object"""
        ...


class Scene:
    """
    OpenSim Scene object - available as 'scene' in Pymote scripts
    Full C# OpenSim.Region.Framework.Scenes.Scene object
    """
    
    @property
    def Name(self) -> str:
        """Region name"""
        ...
    
    @property
    def RegionInfo(self) -> 'RegionInfo':
        """Region information"""
        ...
    
    @property
    def Entities(self) -> 'EntityManager':
        """Scene entities"""
        ...


class RegionInfo:
    """OpenSim RegionInfo object"""
    
    @property
    def RegionID(self) -> str:
        """Region UUID"""
        ...
    
    @property
    def RegionName(self) -> str:
        """Region name"""
        ...
    
    @property
    def RegionLocX(self) -> int:
        """Region X coordinate"""
        ...
    
    @property
    def RegionLocY(self) -> int:
        """Region Y coordinate"""
        ...


class EntityManager:
    """OpenSim EntityManager"""
    
    @property
    def Count(self) -> int:
        """Number of entities"""
        ...


class MainConsole:
    """
    OpenSim MainConsole - available as 'console' in Pymote scripts
    """
    
    def Output(self, text: str) -> None:
        """Output text to console"""
        ...
    
    def RunCommand(self, command: str) -> None:
        """Run a console command"""
        ...


# Global instances (available in Pymote scripts)
opensim: PymoteAPI = PymoteAPI()
scene: Optional[Scene] = None
console: MainConsole = MainConsole()


__all__ = [
    'opensim',
    'scene', 
    'console',
    'PymoteAPI',
    'Scene',
    'RegionInfo',
    'EntityManager',
    'MainConsole',
]
