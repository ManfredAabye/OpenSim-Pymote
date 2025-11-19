"""
Pymote Examples - Practical usage scenarios
"""

from pymote import PymoteClient, CommandError
import time


def example_basic_usage():
    """Basic connection and command execution"""
    print("=== Basic Usage Example ===\n")
    
    with PymoteClient() as client:
        # Get server info
        version = client.show_version()
        print(f"Server Version:\n{version}\n")
        
        # Show regions
        regions = client.show_regions()
        print(f"Regions:\n{regions}\n")
        
        # Show online users
        users = client.show_users()
        print(f"Online Users:\n{users}\n")


def example_region_backup():
    """Backup all regions automatically"""
    print("=== Region Backup Example ===\n")
    
    with PymoteClient() as client:
        # Get list of regions
        regions_output = client.show_regions()
        
        # Parse region names (simplified)
        region_lines = regions_output.split('\n')
        regions = []
        for line in region_lines:
            if 'Region Name' in line or '---' in line or not line.strip():
                continue
            if line.strip():
                # Extract first column (region name)
                parts = line.split()
                if parts:
                    regions.append(parts[0])
        
        print(f"Found {len(regions)} regions to backup\n")
        
        # Backup each region
        for region_name in regions:
            try:
                print(f"Backing up {region_name}...")
                client.change_region(region_name)
                client.backup()
                print(f"  ✓ {region_name} backed up successfully")
                time.sleep(0.5)  # Small delay between backups
            except CommandError as e:
                print(f"  ✗ Failed to backup {region_name}: {e}")
        
        print("\nBackup complete!")


def example_user_creation():
    """Create multiple users from a list"""
    print("=== Batch User Creation Example ===\n")
    
    users_to_create = [
        ("Alice", "Smith", "password123", "alice@example.com"),
        ("Bob", "Jones", "password456", "bob@example.com"),
        ("Charlie", "Brown", "password789", "charlie@example.com"),
    ]
    
    with PymoteClient() as client:
        for first, last, password, email in users_to_create:
            try:
                result = client.create_user(first, last, password, email)
                print(f"✓ Created user: {first} {last}")
                print(f"  {result}\n")
            except CommandError as e:
                print(f"✗ Failed to create {first} {last}: {e}\n")


def example_server_maintenance():
    """Schedule server restart with warnings"""
    print("=== Server Maintenance Example ===\n")
    
    with PymoteClient() as client:
        # Warn users 5 minutes, 2 minutes, and 1 minute before restart
        restart_delays = [300, 120, 60]  # seconds
        
        print("Scheduling restart with warnings...")
        result = client.region_restart_notice(
            "Server maintenance - please save your work!",
            *restart_delays
        )
        print(result)
        
        # You could also disable logins before restart
        client.login_disable()
        print("\nLogins disabled")


def example_terrain_modification():
    """Load, modify, and save terrain"""
    print("=== Terrain Modification Example ===\n")
    
    with PymoteClient() as client:
        try:
            # Load terrain from file
            print("Loading terrain from myterrain.raw...")
            client.terrain_load("myterrain.raw")
            
            # Show current stats
            stats = client.terrain_stats()
            print(f"\nOriginal terrain stats:\n{stats}")
            
            # Elevate terrain by 10 meters
            print("\nElevating terrain by 10 meters...")
            client.terrain_elevate(10.0)
            
            # Bake the changes
            print("Baking terrain...")
            client.terrain_bake()
            
            # Save modified terrain
            print("Saving to myterrain_elevated.raw...")
            client.terrain_save("myterrain_elevated.raw")
            
            print("\n✓ Terrain modification complete!")
            
        except CommandError as e:
            print(f"✗ Terrain modification failed: {e}")


def example_object_cleanup():
    """Clean up objects in region"""
    print("=== Object Cleanup Example ===\n")
    
    with PymoteClient() as client:
        # Delete objects outside region boundaries
        print("Deleting objects outside region...")
        result = client.delete_object_outside()
        print(result)
        
        # Delete temporary objects by name pattern
        print("\nDeleting temporary objects...")
        try:
            result = client.delete_object_name("temp_*", use_regex=True)
            print(result)
        except CommandError as e:
            print(f"No temporary objects found: {e}")
        
        # Force update all clients
        print("\nForcing client updates...")
        client.force_update()
        
        print("\n✓ Cleanup complete!")


def example_monitoring_loop():
    """Continuous monitoring of server status"""
    print("=== Server Monitoring Example ===")
    print("(Press Ctrl+C to stop)\n")
    
    client = PymoteClient()
    
    try:
        client.connect()
        
        iteration = 0
        while True:
            iteration += 1
            
            print(f"\n{'='*60}")
            print(f"Monitoring Check #{iteration} - {time.strftime('%Y-%m-%d %H:%M:%S')}")
            print('='*60)
            
            # Get uptime
            uptime = client.show_uptime()
            print(f"\nUptime:\n{uptime}")
            
            # Get online users count
            users = client.show_users()
            user_count = len([l for l in users.split('\n') if l.strip() and 'Name' not in l])
            print(f"\nOnline Users: {user_count}")
            
            # Get scene stats
            scene = client.show_scene()
            print(f"\nScene Stats:\n{scene}")
            
            # Wait 30 seconds before next check
            print(f"\nNext check in 30 seconds...")
            time.sleep(30)
            
    except KeyboardInterrupt:
        print("\n\nMonitoring stopped by user")
    except Exception as e:
        print(f"\nError: {e}")
    finally:
        client.disconnect()
        print("Disconnected from server")


def example_archive_operations():
    """OAR and IAR operations"""
    print("=== Archive Operations Example ===\n")
    
    with PymoteClient() as client:
        # Save region OAR
        print("Saving region to OAR...")
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        oar_filename = f"region_backup_{timestamp}.oar"
        
        result = client.save_oar(oar_filename, noassets=False, publish=False)
        print(f"✓ OAR saved: {oar_filename}")
        print(result)
        
        # Save user inventory
        print("\nSaving user inventory to IAR...")
        iar_filename = f"user_backup_{timestamp}.iar"
        
        try:
            result = client.save_iar(
                "Test", "User",
                "/",  # Root inventory folder
                "password123",
                iar_filename,
                noassets=False
            )
            print(f"✓ IAR saved: {iar_filename}")
            print(result)
        except CommandError as e:
            print(f"✗ IAR save failed: {e}")


def example_permission_management():
    """Manage permissions and god mode"""
    print("=== Permission Management Example ===\n")
    
    with PymoteClient() as client:
        # Temporarily bypass permissions for admin tasks
        print("Bypassing permissions...")
        client.bypass_permissions(True)
        
        # Do admin work here
        print("Performing admin tasks...")
        
        # Set a user to god level
        client.set_user_level("Admin", "User", 250)
        print("✓ Admin User elevated to god mode (level 250)")
        
        # Re-enable permissions
        print("\nRe-enabling permissions...")
        client.bypass_permissions(False)
        
        print("\n✓ Permission management complete!")


def example_estate_management():
    """Manage estates"""
    print("=== Estate Management Example ===\n")
    
    with PymoteClient() as client:
        # Show all estates
        print("Current estates:")
        estates = client.estate_show()
        print(estates)
        
        # Create new estate (example - adjust UUID to valid owner)
        # estate_name = "My New Estate"
        # owner_uuid = "00000000-0000-0000-0000-000000000000"
        # result = client.estate_create(owner_uuid, estate_name)
        # print(f"\n✓ Estate created: {estate_name}")


def example_error_handling():
    """Demonstrate error handling"""
    print("=== Error Handling Example ===\n")
    
    try:
        with PymoteClient(timeout=5.0) as client:
            # Valid command
            print("Executing valid command...")
            result = client.show_version()
            print(f"✓ Success:\n{result}\n")
            
            # Invalid command (will raise CommandError)
            print("Executing invalid command...")
            result = client._execute_command("invalid command xyz")
            print(result)
            
    except CommandError as e:
        print(f"✗ Command Error: {e}")
    except Exception as e:
        print(f"✗ Unexpected Error: {e}")


if __name__ == "__main__":
    print("Pymote Examples\n")
    print("Choose an example to run:")
    print("1. Basic Usage")
    print("2. Region Backup")
    print("3. Batch User Creation")
    print("4. Server Maintenance")
    print("5. Terrain Modification")
    print("6. Object Cleanup")
    print("7. Server Monitoring (continuous)")
    print("8. Archive Operations")
    print("9. Permission Management")
    print("10. Estate Management")
    print("11. Error Handling")
    print("0. Exit")
    
    choice = input("\nEnter choice (1-11): ").strip()
    print()
    
    examples = {
        "1": example_basic_usage,
        "2": example_region_backup,
        "3": example_user_creation,
        "4": example_server_maintenance,
        "5": example_terrain_modification,
        "6": example_object_cleanup,
        "7": example_monitoring_loop,
        "8": example_archive_operations,
        "9": example_permission_management,
        "10": example_estate_management,
        "11": example_error_handling,
    }
    
    if choice in examples:
        examples[choice]()
    elif choice == "0":
        print("Goodbye!")
    else:
        print("Invalid choice!")
