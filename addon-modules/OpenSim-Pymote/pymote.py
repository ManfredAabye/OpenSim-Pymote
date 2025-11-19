"""
Pymote - Python Client for OpenSimulator Console Commands
Copyright (c) Pymote Team. All rights reserved.

This module provides a high-level Python interface to OpenSimulator's console commands.
"""

import json
import socket
from typing import Optional, Dict, Any, List
from enum import Enum


class PymoteException(Exception):
    """Base exception for Pymote errors"""
    pass


class ConnectionError(PymoteException):
    """Raised when connection to OpenSim fails"""
    pass


class CommandError(PymoteException):
    """Raised when command execution fails"""
    pass


class PymoteClient:
    """
    Python client for OpenSimulator console commands via TCP bridge.
    
    Example:
        client = PymoteClient()
        client.connect()
        result = client.alert("Server will restart in 5 minutes!")
        print(result)
        client.disconnect()
    """
    
    def __init__(self, host: str = "127.0.0.1", port: int = 9500, timeout: float = 30.0):
        """
        Initialize Pymote client.
        
        Args:
            host: OpenSim server address
            port: Pymote server port
            timeout: Socket timeout in seconds
        """
        self.host = host
        self.port = port
        self.timeout = timeout
        self._socket: Optional[socket.socket] = None
        self._connected = False
    
    def connect(self) -> bool:
        """
        Connect to Pymote server.
        
        Returns:
            True if connection successful
            
        Raises:
            ConnectionError: If connection fails
        """
        try:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket.settimeout(self.timeout)
            self._socket.connect((self.host, self.port))
            self._connected = True
            return True
        except Exception as e:
            raise ConnectionError(f"Failed to connect to {self.host}:{self.port}: {e}")
    
    def disconnect(self):
        """Disconnect from Pymote server."""
        if self._socket:
            try:
                self._socket.close()
            except:
                pass
            finally:
                self._socket = None
                self._connected = False
    
    def is_connected(self) -> bool:
        """Check if connected to server."""
        return self._connected
    
    def _execute_command(self, command: str, parameters: Optional[Dict[str, str]] = None) -> str:
        """
        Execute a console command on OpenSim server.
        
        Args:
            command: Console command string
            parameters: Optional command parameters
            
        Returns:
            Command output as string
            
        Raises:
            ConnectionError: If not connected
            CommandError: If command execution fails
        """
        if not self._connected or not self._socket:
            raise ConnectionError("Not connected to server")
        
        request = {
            "Command": command,
            "Parameters": parameters or {}
        }
        
        try:
            # Send request
            request_json = json.dumps(request) + "\n"
            self._socket.sendall(request_json.encode('utf-8'))
            
            # Receive response
            response_data = b""
            while True:
                chunk = self._socket.recv(4096)
                if not chunk:
                    raise ConnectionError("Connection closed by server")
                response_data += chunk
                if b"\n" in chunk:
                    break
            
            response = json.loads(response_data.decode('utf-8'))
            
            if not response.get("Success", False):
                error = response.get("Error", "Unknown error")
                raise CommandError(f"Command failed: {error}")
            
            return response.get("Result", "")
            
        except json.JSONDecodeError as e:
            raise CommandError(f"Invalid response from server: {e}")
        except socket.timeout:
            raise ConnectionError("Command timeout")
        except Exception as e:
            if isinstance(e, (ConnectionError, CommandError)):
                raise
            raise CommandError(f"Command execution error: {e}")
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()
    
    # =========================================================================
    # ALERT COMMANDS
    # =========================================================================
    
    def alert(self, message: str) -> str:
        """Send an alert to everyone."""
        return self._execute_command(f"alert {message}")
    
    def alert_user(self, first_name: str, last_name: str, message: str) -> str:
        """Send an alert to a specific user."""
        return self._execute_command(f"alert-user {first_name} {last_name} {message}")
    
    # =========================================================================
    # APPEARANCE COMMANDS
    # =========================================================================
    
    def appearance_find(self, uuid: str) -> str:
        """Find out which avatar uses the given asset as a baked texture."""
        return self._execute_command(f"appearance find {uuid}")
    
    def appearance_rebake(self, first_name: str, last_name: str) -> str:
        """Request the user's viewer to rebake and reupload appearance textures."""
        return self._execute_command(f"appearance rebake {first_name} {last_name}")
    
    def appearance_send(self, first_name: Optional[str] = None, last_name: Optional[str] = None) -> str:
        """Send appearance data for avatars to other viewers."""
        if first_name and last_name:
            return self._execute_command(f"appearance send {first_name} {last_name}")
        return self._execute_command("appearance send")
    
    def appearance_show(self, first_name: Optional[str] = None, last_name: Optional[str] = None) -> str:
        """Show appearance information for avatars."""
        if first_name and last_name:
            return self._execute_command(f"appearance show {first_name} {last_name}")
        return self._execute_command("appearance show")
    
    # =========================================================================
    # ATTACHMENTS COMMANDS
    # =========================================================================
    
    def attachments_show(self, first_name: Optional[str] = None, last_name: Optional[str] = None) -> str:
        """Show attachment information for avatars."""
        if first_name and last_name:
            return self._execute_command(f"attachments show {first_name} {last_name}")
        return self._execute_command("attachments show")
    
    # =========================================================================
    # BACKUP & PERSISTENCE
    # =========================================================================
    
    def backup(self) -> str:
        """Persist currently unsaved object changes immediately."""
        return self._execute_command("backup")
    
    # =========================================================================
    # PERMISSIONS
    # =========================================================================
    
    def bypass_permissions(self, enabled: bool) -> str:
        """Bypass permission checks."""
        value = "true" if enabled else "false"
        return self._execute_command(f"bypass permissions {value}")
    
    def force_permissions(self, enabled: bool) -> str:
        """Force permissions on or off."""
        value = "true" if enabled else "false"
        return self._execute_command(f"force permissions {value}")
    
    def debug_permissions(self, enabled: bool) -> str:
        """Turn on permissions debugging."""
        value = "true" if enabled else "false"
        return self._execute_command(f"debug permissions {value}")
    
    # =========================================================================
    # REGION MANAGEMENT
    # =========================================================================
    
    def change_region(self, region_name: str) -> str:
        """Change current console region."""
        return self._execute_command(f"change region {region_name}")
    
    def create_region(self, region_name: str, region_file: str) -> str:
        """Create a new region."""
        return self._execute_command(f'create region "{region_name}" {region_file}')
    
    def delete_region(self, region_name: str) -> str:
        """Delete a region from disk."""
        return self._execute_command(f"delete-region {region_name}")
    
    def remove_region(self, region_name: str) -> str:
        """Remove a region from this simulator."""
        return self._execute_command(f"remove-region {region_name}")
    
    def deregister_region_id(self, *region_ids: str) -> str:
        """Deregister regions manually."""
        ids = " ".join(region_ids)
        return self._execute_command(f"deregister region id {ids}")
    
    def show_regions(self) -> str:
        """Show region data."""
        return self._execute_command("show regions")
    
    def show_region(self) -> str:
        """Show control information for the currently selected region."""
        return self._execute_command("show region")
    
    def show_region_at(self, x: int, y: int) -> str:
        """Show details on a region at the given coordinate."""
        return self._execute_command(f"show region at {x} {y}")
    
    def show_region_name(self, region_name: str) -> str:
        """Show details on a region by name."""
        return self._execute_command(f"show region name {region_name}")
    
    def region_restart(self) -> str:
        """Restart the currently selected region(s)."""
        return self._execute_command("restart")
    
    def region_restart_notice(self, message: str, *delta_seconds: int) -> str:
        """Schedule a region restart with notice."""
        deltas = " ".join(str(d) for d in delta_seconds)
        return self._execute_command(f"region restart notice {message} {deltas}")
    
    def region_restart_bluebox(self, message: str, *delta_seconds: int) -> str:
        """Schedule a region restart with bluebox message."""
        deltas = " ".join(str(d) for d in delta_seconds)
        return self._execute_command(f"region restart bluebox {message} {deltas}")
    
    def region_restart_abort(self, message: Optional[str] = None) -> str:
        """Abort a region restart."""
        if message:
            return self._execute_command(f"region restart abort {message}")
        return self._execute_command("region restart abort")
    
    def region_get(self) -> str:
        """Show control information for the currently selected region."""
        return self._execute_command("region get")
    
    def region_set(self, parameter: str, value: str) -> str:
        """Set control information for the currently selected region."""
        return self._execute_command(f"region set {parameter} {value}")
    
    # =========================================================================
    # USER MANAGEMENT
    # =========================================================================
    
    def create_user(self, first_name: str, last_name: str, password: str, 
                   email: str = "", user_id: str = "", model: str = "") -> str:
        """Create a new user."""
        cmd = f"create user {first_name} {last_name} {password}"
        if email:
            cmd += f" {email}"
        if user_id:
            cmd += f" {user_id}"
        if model:
            cmd += f" {model}"
        return self._execute_command(cmd)
    
    def kick_user(self, first_name: str, last_name: str, force: bool = False, 
                 message: str = "") -> str:
        """Kick a user off the simulator."""
        cmd = f"kick user {first_name} {last_name}"
        if force:
            cmd += " --force"
        if message:
            cmd += f" {message}"
        return self._execute_command(cmd)
    
    def show_users(self, full: bool = False) -> str:
        """Show user data for users currently on the region."""
        cmd = "show users"
        if full:
            cmd += " full"
        return self._execute_command(cmd)
    
    def show_account(self, first_name: str, last_name: str) -> str:
        """Show account details for the given user."""
        return self._execute_command(f"show account {first_name} {last_name}")
    
    def set_user_level(self, first_name: str, last_name: str, level: int) -> str:
        """Set user level (>= 200 for god mode if configured)."""
        return self._execute_command(f"set user level {first_name} {last_name} {level}")
    
    def reset_user_email(self, first_name: str, last_name: str, email: str) -> str:
        """Reset a user email address."""
        return self._execute_command(f"reset user email {first_name} {last_name} {email}")
    
    def reset_user_password(self, first_name: str, last_name: str, password: str) -> str:
        """Reset a user password."""
        return self._execute_command(f"reset user password {first_name} {last_name} {password}")
    
    # =========================================================================
    # OBJECT MANAGEMENT
    # =========================================================================
    
    def delete_object_id(self, uuid_or_local_id: str) -> str:
        """Delete a scene object by uuid or localID."""
        return self._execute_command(f"delete object id {uuid_or_local_id}")
    
    def delete_object_name(self, name: str, use_regex: bool = False) -> str:
        """Delete a scene object by name."""
        cmd = "delete object name"
        if use_regex:
            cmd += " --regex"
        cmd += f" {name}"
        return self._execute_command(cmd)
    
    def delete_object_owner(self, owner_uuid: str) -> str:
        """Delete scene objects by owner."""
        return self._execute_command(f"delete object owner {owner_uuid}")
    
    def delete_object_creator(self, creator_uuid: str) -> str:
        """Delete scene objects by creator."""
        return self._execute_command(f"delete object creator {creator_uuid}")
    
    def delete_object_outside(self) -> str:
        """Delete all scene objects outside region boundaries."""
        return self._execute_command("delete object outside")
    
    def delete_object_pos(self, start_x: float, start_y: float, start_z: float,
                         end_x: float, end_y: float, end_z: float) -> str:
        """Delete scene objects within the given volume."""
        return self._execute_command(
            f"delete object pos {start_x}, {start_y}, {start_z} {end_x}, {end_y}, {end_z}"
        )
    
    def show_object_id(self, uuid_or_local_id: str, full: bool = False) -> str:
        """Show details of a scene object."""
        cmd = "show object id"
        if full:
            cmd += " --full"
        cmd += f" {uuid_or_local_id}"
        return self._execute_command(cmd)
    
    def show_object_name(self, name: str, full: bool = False, use_regex: bool = False) -> str:
        """Show details of scene objects with the given name."""
        cmd = "show object name"
        if full:
            cmd += " --full"
        if use_regex:
            cmd += " --regex"
        cmd += f" {name}"
        return self._execute_command(cmd)
    
    def show_object_owner(self, owner_id: str, full: bool = False) -> str:
        """Show details of scene objects with given owner."""
        cmd = "show object owner"
        if full:
            cmd += " --full"
        cmd += f" {owner_id}"
        return self._execute_command(cmd)
    
    def dump_object_id(self, uuid_or_local_id: str) -> str:
        """Dump the formatted serialization of the given object."""
        return self._execute_command(f"dump object id {uuid_or_local_id}")
    
    def edit_scale(self, name: str, x: float, y: float, z: float) -> str:
        """Change the scale of a named prim."""
        return self._execute_command(f"edit scale {name} {x} {y} {z}")
    
    def force_update(self) -> str:
        """Force the update of all objects on clients."""
        return self._execute_command("force update")
    
    # =========================================================================
    # TERRAIN COMMANDS
    # =========================================================================
    
    def terrain_load(self, filename: str) -> str:
        """Load terrain from file."""
        return self._execute_command(f"terrain load {filename}")
    
    def terrain_save(self, filename: str) -> str:
        """Save terrain to file."""
        return self._execute_command(f"terrain save {filename}")
    
    def terrain_fill(self, value: float) -> str:
        """Fill terrain with value."""
        return self._execute_command(f"terrain fill {value}")
    
    def terrain_elevate(self, amount: float) -> str:
        """Elevate terrain."""
        return self._execute_command(f"terrain elevate {amount}")
    
    def terrain_lower(self, amount: float) -> str:
        """Lower terrain."""
        return self._execute_command(f"terrain lower {amount}")
    
    def terrain_multiply(self, value: float) -> str:
        """Multiply terrain heights."""
        return self._execute_command(f"terrain multiply {value}")
    
    def terrain_bake(self) -> str:
        """Bake terrain."""
        return self._execute_command("terrain bake")
    
    def terrain_revert(self) -> str:
        """Revert terrain to baked state."""
        return self._execute_command("terrain revert")
    
    def terrain_stats(self) -> str:
        """Show terrain statistics."""
        return self._execute_command("terrain stats")
    
    def set_water_height(self, height: float, x: int = -1, y: int = -1) -> str:
        """Set water height in meters."""
        cmd = f"set water height {height}"
        if x >= 0 or y >= 0:
            cmd += f" {x} {y}"
        return self._execute_command(cmd)
    
    def set_terrain_texture(self, number: int, uuid: str, x: int = -1, y: int = -1) -> str:
        """Set terrain texture."""
        cmd = f"set terrain texture {number} {uuid}"
        if x >= 0 or y >= 0:
            cmd += f" {x} {y}"
        return self._execute_command(cmd)
    
    # =========================================================================
    # ARCHIVE COMMANDS (OAR/IAR)
    # =========================================================================
    
    def save_oar(self, oar_path: str = "", noassets: bool = False, 
                publish: bool = False, home_url: str = "") -> str:
        """Save a region's data to an OAR archive."""
        cmd = "save oar"
        if home_url:
            cmd += f" -h={home_url}"
        if noassets:
            cmd += " --noassets"
        if publish:
            cmd += " --publish"
        if oar_path:
            cmd += f" {oar_path}"
        return self._execute_command(cmd)
    
    def load_oar(self, oar_path: str = "", merge: bool = False, 
                skip_assets: bool = False, default_user: str = "") -> str:
        """Load a region's data from an OAR archive."""
        cmd = "load oar"
        if merge:
            cmd += " --merge"
        if skip_assets:
            cmd += " --skip-assets"
        if default_user:
            cmd += f' --default-user "{default_user}"'
        if oar_path:
            cmd += f" {oar_path}"
        return self._execute_command(cmd)
    
    def save_iar(self, first_name: str, last_name: str, inventory_path: str,
                password: str, iar_path: str = "", noassets: bool = False) -> str:
        """Save user inventory archive (IAR)."""
        cmd = f"save iar"
        if noassets:
            cmd += " --noassets"
        cmd += f" {first_name} {last_name} {inventory_path} {password}"
        if iar_path:
            cmd += f" {iar_path}"
        return self._execute_command(cmd)
    
    def load_iar(self, first_name: str, last_name: str, inventory_path: str,
                password: str, iar_path: str = "", merge: bool = False) -> str:
        """Load user inventory archive (IAR)."""
        cmd = "load iar"
        if merge:
            cmd += " --merge"
        cmd += f" {first_name} {last_name} {inventory_path} {password}"
        if iar_path:
            cmd += f" {iar_path}"
        return self._execute_command(cmd)
    
    # =========================================================================
    # LOGIN CONTROL
    # =========================================================================
    
    def login_enable(self) -> str:
        """Enable simulator logins."""
        return self._execute_command("login enable")
    
    def login_disable(self) -> str:
        """Disable simulator logins."""
        return self._execute_command("login disable")
    
    def login_status(self) -> str:
        """Show login status."""
        return self._execute_command("login status")
    
    def login_level(self, level: int) -> str:
        """Set the minimum user level to log in."""
        return self._execute_command(f"login level {level}")
    
    def login_reset(self) -> str:
        """Reset the login level to allow all users."""
        return self._execute_command("login reset")
    
    def login_text(self, text: str) -> str:
        """Set the text users will see on login."""
        return self._execute_command(f"login text {text}")
    
    # =========================================================================
    # STATISTICS & MONITORING
    # =========================================================================
    
    def show_info(self) -> str:
        """Show general information about the server."""
        return self._execute_command("show info")
    
    def show_version(self) -> str:
        """Show server version."""
        return self._execute_command("show version")
    
    def show_uptime(self) -> str:
        """Show server uptime."""
        return self._execute_command("show uptime")
    
    def show_stats(self, category: str = "") -> str:
        """Show statistical information."""
        cmd = "show stats"
        if category:
            cmd += f" {category}"
        return self._execute_command(cmd)
    
    def show_threads(self) -> str:
        """Show thread status."""
        return self._execute_command("show threads")
    
    def show_scene(self) -> str:
        """Show live information for the currently selected scene."""
        return self._execute_command("show scene")
    
    def show_queues(self, full: bool = False) -> str:
        """Show queue data for each client."""
        cmd = "show queues"
        if full:
            cmd += " full"
        return self._execute_command(cmd)
    
    def monitor_report(self) -> str:
        """Returns variety of statistics about the current region."""
        return self._execute_command("monitor report")
    
    def stats_record_start(self) -> str:
        """Start recording stats to file."""
        return self._execute_command("stats record start")
    
    def stats_record_stop(self) -> str:
        """Stop recording stats to file."""
        return self._execute_command("stats record stop")
    
    def stats_save(self, path: str) -> str:
        """Save stats snapshot to a file."""
        return self._execute_command(f"stats save {path}")
    
    # =========================================================================
    # DEBUG COMMANDS
    # =========================================================================
    
    def debug_scene_get(self) -> str:
        """List current scene options."""
        return self._execute_command("debug scene get")
    
    def debug_scene_set(self, param: str, value: str) -> str:
        """Turn on scene debugging options."""
        return self._execute_command(f"debug scene set {param} {value}")
    
    def debug_http(self, direction: str, level: int = 0) -> str:
        """Turn on http request logging (in/out/all)."""
        cmd = f"debug http {direction}"
        if level > 0:
            cmd += f" {level}"
        return self._execute_command(cmd)
    
    def force_gc(self) -> str:
        """Manually invoke runtime garbage collection."""
        return self._execute_command("force gc")
    
    # =========================================================================
    # CONFIG COMMANDS
    # =========================================================================
    
    def config_get(self, section: str = "", key: str = "") -> str:
        """Get config information."""
        cmd = "config get"
        if section:
            cmd += f" {section}"
        if key:
            cmd += f" {key}"
        return self._execute_command(cmd)
    
    def config_set(self, section: str, key: str, value: str) -> str:
        """Set a config option."""
        return self._execute_command(f"config set {section} {key} {value}")
    
    def config_save(self, path: str) -> str:
        """Save current configuration to a file."""
        return self._execute_command(f"config save {path}")
    
    # =========================================================================
    # ESTATE COMMANDS
    # =========================================================================
    
    def estate_create(self, owner_uuid: str, estate_name: str) -> str:
        """Create a new estate."""
        return self._execute_command(f"estate create {owner_uuid} {estate_name}")
    
    def estate_link_region(self, estate_id: int, region_id: str) -> str:
        """Attach region to estate."""
        return self._execute_command(f"estate link region {estate_id} {region_id}")
    
    def estate_set_name(self, estate_id: int, new_name: str) -> str:
        """Set estate name."""
        return self._execute_command(f"estate set name {estate_id} {new_name}")
    
    def estate_set_owner(self, estate_id: int, owner: str) -> str:
        """Set estate owner (UUID or First Last)."""
        return self._execute_command(f"estate set owner {estate_id} {owner}")
    
    def estate_show(self) -> str:
        """Show all estates on the simulator."""
        return self._execute_command("estate show")
    
    # =========================================================================
    # TELEPORT & AVATAR COMMANDS
    # =========================================================================
    
    def teleport_user(self, first_name: str, last_name: str, destination: str) -> str:
        """Teleport a user to the given destination."""
        return self._execute_command(f"teleport user {first_name} {last_name} {destination}")
    
    def sit_user_name(self, first_name: str, last_name: str, use_regex: bool = False) -> str:
        """Sit the named user on an unoccupied object with a sit target."""
        cmd = "sit user name"
        if use_regex:
            cmd += " --regex"
        cmd += f" {first_name} {last_name}"
        return self._execute_command(cmd)
    
    def stand_user_name(self, first_name: str, last_name: str, use_regex: bool = False) -> str:
        """Stand the named user."""
        cmd = "stand user name"
        if use_regex:
            cmd += " --regex"
        cmd += f" {first_name} {last_name}"
        return self._execute_command(cmd)
    
    # =========================================================================
    # PARCEL/LAND COMMANDS
    # =========================================================================
    
    def land_clear(self) -> str:
        """Clear all the parcels from the region."""
        return self._execute_command("land clear")
    
    def land_show(self, local_land_id: Optional[int] = None) -> str:
        """Show information about the parcels on the region."""
        cmd = "land show"
        if local_land_id is not None:
            cmd += f" {local_land_id}"
        return self._execute_command(cmd)
    
    # =========================================================================
    # ASSET COMMANDS
    # =========================================================================
    
    def show_asset(self, asset_id: str) -> str:
        """Show asset information."""
        return self._execute_command(f"show asset {asset_id}")
    
    def dump_asset(self, asset_id: str) -> str:
        """Dump an asset."""
        return self._execute_command(f"dump asset {asset_id}")
    
    def fcache_status(self) -> str:
        """Display cache status."""
        return self._execute_command("fcache status")
    
    def fcache_clear(self, cache_type: str = "") -> str:
        """Remove all assets in the cache (file/memory)."""
        cmd = "fcache clear"
        if cache_type:
            cmd += f" {cache_type}"
        return self._execute_command(cmd)
    
    def fcache_assets(self) -> str:
        """Deep scan and cache of all assets in all scenes."""
        return self._execute_command("fcache assets")
    
    # =========================================================================
    # SCRIPT COMMANDS
    # =========================================================================
    
    def command_script(self, script_path: str) -> str:
        """Run a command script from file."""
        return self._execute_command(f"command-script {script_path}")
    
    # =========================================================================
    # SYSTEM COMMANDS
    # =========================================================================
    
    def shutdown(self) -> str:
        """Quit the application."""
        return self._execute_command("shutdown")
    
    def quit(self) -> str:
        """Quit the application (alias for shutdown)."""
        return self._execute_command("quit")
    
    def help_command(self, command: str = "") -> str:
        """Display help on a particular command."""
        cmd = "help"
        if command:
            cmd += f" {command}"
        return self._execute_command(cmd)
    
    def set_log_level(self, level: str) -> str:
        """Set the console logging level for this session."""
        return self._execute_command(f"set log level {level}")
    
    def get_log_level(self) -> str:
        """Get the current console logging level."""
        return self._execute_command("get log level")


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def quick_command(command: str, host: str = "127.0.0.1", port: int = 9500) -> str:
    """
    Execute a single command without managing connection.
    
    Example:
        result = quick_command("show regions")
        print(result)
    """
    with PymoteClient(host, port) as client:
        return client._execute_command(command)


if __name__ == "__main__":
    # Example usage
    print("Pymote - Python Client for OpenSimulator")
    print("=" * 50)
    
    try:
        with PymoteClient() as client:
            print("Connected to OpenSim")
            
            # Show version
            version = client.show_version()
            print(f"\nServer Version:\n{version}")
            
            # Show regions
            regions = client.show_regions()
            print(f"\nRegions:\n{regions}")
            
            # Show uptime
            uptime = client.show_uptime()
            print(f"\nUptime:\n{uptime}")
            
    except Exception as e:
        print(f"Error: {e}")
