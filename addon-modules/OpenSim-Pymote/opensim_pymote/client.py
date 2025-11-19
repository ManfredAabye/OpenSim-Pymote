"""
OpenSim-Pymote Client
TCP-based client with structured return values
"""

import socket
import json
from typing import Optional, List, Any
from dataclasses import dataclass


class ConnectionError(Exception):
    """Connection-related errors"""
    pass


class CommandError(Exception):
    """Command execution errors"""
    pass


@dataclass
class CommandResult:
    """
    Structured command result
    
    Attributes:
        success: Whether command succeeded
        output: Raw command output text
        data: Parsed structured data (if available)
        error: Error message (if failed)
    """
    success: bool
    output: str
    data: Optional[Any] = None
    error: Optional[str] = None
    
    def __bool__(self) -> bool:
        """Allow using result in if statements"""
        return self.success
    
    def __str__(self) -> str:
        """String representation"""
        if self.success:
            return self.output
        return f"Error: {self.error}"


class OpenSimClient:
    """
    OpenSimulator Client with structured return values
    
    Usage:
        with OpenSimClient(host='localhost', port=9500) as client:
            result = client.show_version()
            if result:
                print(result.output)
            
            regions = client.get_regions()
            for region in regions.data:
                print(f"Region: {region.name} at {region.location}")
    """
    
    def __init__(self, host: str = '127.0.0.1', port: int = 9500, timeout: float = 30.0):
        """
        Initialize OpenSim client
        
        Args:
            host: OpenSim server hostname
            port: Pymote server port
            timeout: Socket timeout in seconds
        """
        self.host = host
        self.port = port
        self.timeout = timeout
        self.socket: Optional[socket.socket] = None
    
    def connect(self) -> bool:
        """Connect to OpenSim Pymote server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(self.timeout)
            self.socket.connect((self.host, self.port))
            return True
        except socket.error as e:
            raise ConnectionError(f"Failed to connect to {self.host}:{self.port}: {e}")
    
    def disconnect(self):
        """Disconnect from server"""
        if self.socket:
            try:
                self.socket.close()
            except Exception:
                pass
            self.socket = None
    
    def is_connected(self) -> bool:
        """Check if connected"""
        return self.socket is not None
    
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()
    
    def _execute(self, command: str, parse_data: bool = False) -> CommandResult:
        """
        Execute command and return structured result
        
        Args:
            command: Console command to execute
            parse_data: Whether to parse output into structured data
            
        Returns:
            CommandResult with success status, output, and parsed data
        """
        if not self.socket:
            raise ConnectionError("Not connected to server")
        
        try:
            # Send command
            request = {
                "Command": command,
                "Parameters": {}
            }
            request_json = json.dumps(request) + "\n"
            self.socket.sendall(request_json.encode('utf-8'))
            
            # Receive response
            response_data = b""
            while True:
                chunk = self.socket.recv(4096)
                if not chunk:
                    break
                response_data += chunk
                if b"\n" in chunk:
                    break
            
            response_json = response_data.decode('utf-8').strip()
            response = json.loads(response_json)
            
            # Parse response
            success = response.get("Success", False)
            output = response.get("Result", "")
            error = response.get("Error")
            
            if not success:
                return CommandResult(success=False, output="", error=error)
            
            # Parse structured data if requested
            data = None
            if parse_data:
                data = self._parse_output(command, output)
            
            return CommandResult(success=True, output=output, data=data)
            
        except socket.timeout:
            raise ConnectionError("Command timeout")
        except json.JSONDecodeError as e:
            raise CommandError(f"Invalid JSON response: {e}")
        except Exception as e:
            raise CommandError(f"Command execution failed: {e}")
    
    def _parse_output(self, command: str, output: str) -> Any:
        """Parse command output into structured data"""
        # Import here to avoid circular dependency
        from .parsers import parse_regions, parse_users, parse_stats
        
        if "show regions" in command:
            return parse_regions(output)
        elif "show users" in command:
            return parse_users(output)
        elif "show stats" in command:
            return parse_stats(output)
        
        return None
    
    # ========== Alert Commands ==========
    
    def alert(self, message: str) -> CommandResult:
        """Send alert to all users"""
        return self._execute(f"alert {message}")
    
    def alert_user(self, first_name: str, last_name: str, message: str) -> CommandResult:
        """Send alert to specific user"""
        return self._execute(f"alert user {first_name} {last_name} {message}")
    
    # ========== User Management ==========
    
    def create_user(self, first_name: str, last_name: str, password: str, 
                   email: str, user_id: Optional[str] = None) -> CommandResult:
        """Create new user account"""
        cmd = f"create user {first_name} {last_name} {password} {email}"
        if user_id:
            cmd += f" {user_id}"
        return self._execute(cmd)
    
    def reset_user_password(self, first_name: str, last_name: str, 
                           new_password: str) -> CommandResult:
        """Reset user password"""
        return self._execute(f"reset user password {first_name} {last_name} {new_password}")
    
    def set_user_level(self, first_name: str, last_name: str, level: int) -> CommandResult:
        """Set user permission level (0=normal, 200+=god, 250=admin)"""
        return self._execute(f"set user level {first_name} {last_name} {level}")
    
    def kick_user(self, first_name: str, last_name: str, message: str = "") -> CommandResult:
        """Kick user from simulator"""
        return self._execute(f"kick user {first_name} {last_name} {message}")
    
    def show_users(self, full: bool = False) -> CommandResult:
        """Get online users with structured data"""
        cmd = "show users full" if full else "show users"
        return self._execute(cmd, parse_data=True)
    
    def get_users(self, full: bool = False) -> List:
        """Get online users as list of User objects"""
        result = self.show_users(full)
        return result.data if result.data else []
    
    # ========== Region Management ==========
    
    def create_region(self, region_name: str, region_file: str) -> CommandResult:
        """Create new region from file"""
        return self._execute(f"create region {region_name} {region_file}")
    
    def delete_region(self, region_name: str) -> CommandResult:
        """Delete region"""
        return self._execute(f"delete-region {region_name}")
    
    def change_region(self, region_name: str) -> CommandResult:
        """Change to different region"""
        return self._execute(f"change region {region_name}")
    
    def show_regions(self) -> CommandResult:
        """Get all regions with structured data"""
        return self._execute("show regions", parse_data=True)
    
    def get_regions(self) -> List:
        """Get all regions as list of Region objects"""
        result = self.show_regions()
        return result.data if result.data else []
    
    def region_restart(self) -> CommandResult:
        """Restart current region"""
        return self._execute("region restart")
    
    def region_restart_notice(self, message: str, *delays: int) -> CommandResult:
        """Schedule region restart with countdown notices"""
        delay_str = " ".join(str(d) for d in delays)
        return self._execute(f"region restart notice {delay_str} {message}")
    
    # ========== Object Management ==========
    
    def delete_object_id(self, uuid: str) -> CommandResult:
        """Delete object by UUID"""
        return self._execute(f"delete object id {uuid}")
    
    def delete_object_name(self, name: str, use_regex: bool = False) -> CommandResult:
        """Delete objects by name"""
        cmd = f"delete object name {name}"
        if use_regex:
            cmd += " regex"
        return self._execute(cmd)
    
    def delete_object_owner(self, uuid: str) -> CommandResult:
        """Delete all objects owned by user UUID"""
        return self._execute(f"delete object owner {uuid}")
    
    def delete_object_outside(self) -> CommandResult:
        """Delete objects outside region boundaries"""
        return self._execute("delete object outside")
    
    def show_object_id(self, uuid: str) -> CommandResult:
        """Show object details by UUID"""
        return self._execute(f"show object id {uuid}")
    
    def show_object_name(self, name: str) -> CommandResult:
        """Show objects by name"""
        return self._execute(f"show object name {name}")
    
    def edit_scale(self, prim_name: str, x: float, y: float, z: float) -> CommandResult:
        """Scale object"""
        return self._execute(f"edit scale {prim_name} {x} {y} {z}")
    
    # ========== Terrain Commands ==========
    
    def terrain_load(self, filename: str) -> CommandResult:
        """Load terrain from file"""
        return self._execute(f"terrain load {filename}")
    
    def terrain_save(self, filename: str) -> CommandResult:
        """Save terrain to file"""
        return self._execute(f"terrain save {filename}")
    
    def terrain_fill(self, value: float) -> CommandResult:
        """Fill terrain with height value"""
        return self._execute(f"terrain fill {value}")
    
    def terrain_elevate(self, amount: float) -> CommandResult:
        """Elevate terrain by amount"""
        return self._execute(f"terrain elevate {amount}")
    
    def terrain_lower(self, amount: float) -> CommandResult:
        """Lower terrain by amount"""
        return self._execute(f"terrain lower {amount}")
    
    def terrain_bake(self) -> CommandResult:
        """Bake terrain (save current state)"""
        return self._execute("terrain bake")
    
    def terrain_revert(self) -> CommandResult:
        """Revert terrain to baked state"""
        return self._execute("terrain revert")
    
    def terrain_stats(self) -> CommandResult:
        """Get terrain statistics"""
        return self._execute("terrain stats", parse_data=True)
    
    # ========== Archive Commands ==========
    
    def save_oar(self, filename: str, noassets: bool = False, 
                publish: bool = False) -> CommandResult:
        """Save region archive (OAR)"""
        cmd = f"save oar {filename}"
        if noassets:
            cmd += " --noassets"
        if publish:
            cmd += " --publish"
        return self._execute(cmd)
    
    def load_oar(self, filename: str, merge: bool = False, 
                skip_assets: bool = False) -> CommandResult:
        """Load region archive (OAR)"""
        cmd = f"load oar {filename}"
        if merge:
            cmd += " --merge"
        if skip_assets:
            cmd += " --skip-assets"
        return self._execute(cmd)
    
    def save_iar(self, first_name: str, last_name: str, inventory_path: str,
                password: str, filename: str, noassets: bool = False) -> CommandResult:
        """Save inventory archive (IAR)"""
        cmd = f"save iar {first_name} {last_name} {password} {inventory_path} {filename}"
        if noassets:
            cmd += " --noassets"
        return self._execute(cmd)
    
    def load_iar(self, first_name: str, last_name: str, inventory_path: str,
                password: str, filename: str) -> CommandResult:
        """Load inventory archive (IAR)"""
        return self._execute(f"load iar {first_name} {last_name} {password} {inventory_path} {filename}")
    
    # ========== Login Control ==========
    
    def login_enable(self) -> CommandResult:
        """Enable logins"""
        return self._execute("login enable")
    
    def login_disable(self) -> CommandResult:
        """Disable logins"""
        return self._execute("login disable")
    
    def login_status(self) -> CommandResult:
        """Show login status"""
        return self._execute("login status")
    
    def login_level(self, level: int) -> CommandResult:
        """Set minimum user level for login"""
        return self._execute(f"login level {level}")
    
    def login_text(self, message: str) -> CommandResult:
        """Set login message"""
        return self._execute(f"login text {message}")
    
    # ========== Statistics & Monitoring ==========
    
    def show_info(self) -> CommandResult:
        """Show server information"""
        return self._execute("show info")
    
    def show_version(self) -> CommandResult:
        """Show OpenSim version"""
        return self._execute("show version")
    
    def show_uptime(self) -> CommandResult:
        """Show server uptime"""
        return self._execute("show uptime")
    
    def show_stats(self, category: Optional[str] = None) -> CommandResult:
        """Show statistics with structured data"""
        cmd = "show stats"
        if category:
            cmd += f" {category}"
        return self._execute(cmd, parse_data=True)
    
    def get_stats(self, category: Optional[str] = None):
        """Get statistics as Stats object"""
        result = self.show_stats(category)
        return result.data if result.data else None
    
    def show_threads(self) -> CommandResult:
        """Show thread status"""
        return self._execute("show threads")
    
    def show_scene(self) -> CommandResult:
        """Show scene information"""
        return self._execute("show scene")
    
    def monitor_report(self) -> CommandResult:
        """Show monitoring report"""
        return self._execute("monitor report")
    
    # ========== System Commands ==========
    
    def backup(self) -> CommandResult:
        """Backup current region immediately"""
        return self._execute("backup")
    
    def shutdown(self) -> CommandResult:
        """Shutdown simulator"""
        return self._execute("shutdown")
    
    def force_gc(self) -> CommandResult:
        """Force garbage collection"""
        return self._execute("force gc")
    
    def set_log_level(self, level: str) -> CommandResult:
        """Set log level (DEBUG, INFO, WARN, ERROR, FATAL)"""
        return self._execute(f"set log level {level}")
    
    def get_log_level(self) -> CommandResult:
        """Get current log level"""
        return self._execute("get log level")
