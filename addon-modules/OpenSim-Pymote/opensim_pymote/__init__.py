"""
OpenSim-Pymote - Professional Python API for OpenSimulator
TCP-based communication with structured return values
"""

__version__ = "1.0.0"
__author__ = "OpenSim-Pymote Team"
__license__ = "MIT"

from .client import OpenSimClient, CommandResult, ConnectionError, CommandError
from .models import Region, User, Stats

__all__ = [
    'OpenSimClient',
    'CommandResult',
    'ConnectionError',
    'CommandError',
    'Region',
    'User',
    'Stats',
]
