"""
OpenSim-Pymote Examples
Demonstrates structured return values and typed data
"""

from opensim_pymote import OpenSimClient, CommandError, ConnectionError


def example_structured_returns():
    """Demonstrate structured return values"""
    print("=== Structured Return Values ===\n")
    
    with OpenSimClient() as client:
        # CommandResult object
        result = client.show_version()
        
        print(f"Success: {result.success}")
        print(f"Output: {result.output}")
        print(f"Error: {result.error}")
        
        # Use result in if statement
        if result:
            print("✓ Command succeeded!")


def example_regions():
    """Get regions as Region objects"""
    print("=== Regions (Structured Data) ===\n")
    
    with OpenSimClient() as client:
        # Get regions as list of Region objects
        regions = client.get_regions()
        
        print(f"Found {len(regions)} regions:\n")
        
        for region in regions:
            print(f"Region: {region.name}")
            print(f"  UUID: {region.uuid}")
            print(f"  Location: ({region.location_x}, {region.location_y})")
            print(f"  Size: {region.size_x}x{region.size_y}")
            if region.port:
                print(f"  Port: {region.port}")
            print()


def example_users():
    """Get users as User objects"""
    print("=== Users (Structured Data) ===\n")
    
    with OpenSimClient() as client:
        # Get users as list of User objects
        users = client.get_users(full=True)
        
        print(f"Found {len(users)} online users:\n")
        
        for user in users:
            print(f"User: {user.full_name}")
            print(f"  UUID: {user.uuid}")
            print(f"  Region: {user.region}")
            if user.position:
                x, y, z = user.position
                print(f"  Position: ({x:.1f}, {y:.1f}, {z:.1f})")
            print(f"  Level: {user.level}")
            print()


def example_stats():
    """Get stats as Stats object"""
    print("=== Stats (Structured Data) ===\n")
    
    with OpenSimClient() as client:
        # Get stats as Stats object
        stats = client.get_stats()
        
        if stats:
            print(f"FPS: {stats.fps}")
            print(f"Physics FPS: {stats.physics_fps}")
            print(f"Agents: {stats.agents}")
            print(f"Objects: {stats.objects}")
            print(f"Scripts: {stats.scripts}")
            print(f"Memory: {stats.memory_mb} MB")


def example_user_management():
    """User management with return values"""
    print("=== User Management ===\n")
    
    with OpenSimClient() as client:
        # Create user - check result
        result = client.create_user("Test", "User", "pass123", "test@example.com")
        
        if result.success:
            print("✓ User created successfully")
            print(f"Output: {result.output}")
        else:
            print(f"✗ Failed: {result.error}")
        
        # Set user level
        result = client.set_user_level("Test", "User", 250)
        if result:
            print("✓ User promoted to god mode")
        
        # Send alert with result check
        result = client.alert_user("Test", "User", "Welcome!")
        if result:
            print("✓ Alert sent")


def example_region_operations():
    """Region operations with return values"""
    print("=== Region Operations ===\n")
    
    with OpenSimClient() as client:
        # Get all regions
        regions = client.get_regions()
        
        for region in regions:
            print(f"Processing region: {region.name}")
            
            # Change region
            result = client.change_region(region.name)
            if not result:
                print(f"  ✗ Failed to change region: {result.error}")
                continue
            
            # Backup region
            result = client.backup()
            if result:
                print(f"  ✓ Backed up {region.name}")
            
            # Save OAR
            oar_file = f"{region.name}.oar"
            result = client.save_oar(oar_file, noassets=False)
            if result:
                print(f"  ✓ Saved OAR: {oar_file}")
            
            print()


def example_batch_operations():
    """Batch operations with structured results"""
    print("=== Batch Operations ===\n")
    
    with OpenSimClient() as client:
        users_to_create = [
            ("Alice", "Smith", "pass1", "alice@example.com"),
            ("Bob", "Jones", "pass2", "bob@example.com"),
            ("Charlie", "Brown", "pass3", "charlie@example.com"),
        ]
        
        success_count = 0
        fail_count = 0
        
        for first, last, password, email in users_to_create:
            result = client.create_user(first, last, password, email)
            
            if result.success:
                print(f"✓ Created: {first} {last}")
                success_count += 1
            else:
                print(f"✗ Failed: {first} {last} - {result.error}")
                fail_count += 1
        
        print(f"\nResults: {success_count} succeeded, {fail_count} failed")


def example_error_handling():
    """Comprehensive error handling"""
    print("=== Error Handling ===\n")
    
    try:
        with OpenSimClient(host='localhost', port=9500, timeout=5.0) as client:
            # Valid command
            result = client.show_version()
            if result:
                print(f"✓ Success: {result.output[:50]}...")
            
            # Command that might fail
            result = client.delete_object_id("invalid-uuid")
            if not result:
                print(f"✗ Expected failure: {result.error}")
            
    except ConnectionError as e:
        print(f"Connection error: {e}")
    except CommandError as e:
        print(f"Command error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


def example_monitoring_loop():
    """Continuous monitoring with structured data"""
    print("=== Monitoring Loop ===\n")
    
    import time
    
    with OpenSimClient() as client:
        for i in range(3):  # Just 3 iterations for demo
            print(f"Check #{i+1}")
            
            # Get stats
            stats = client.get_stats()
            if stats:
                print(f"  FPS: {stats.fps}")
                print(f"  Agents: {stats.agents}")
                print(f"  Objects: {stats.objects}")
            
            # Get users
            users = client.get_users()
            print(f"  Online users: {len(users)}")
            for user in users:
                print(f"    - {user.full_name} in {user.region}")
            
            print()
            if i < 2:
                time.sleep(2)


def example_typed_functions():
    """Use type hints with structured data"""
    print("=== Typed Functions ===\n")
    
    from typing import List
    from opensim_pymote import Region
    
    def get_active_regions(client: OpenSimClient) -> List[Region]:
        """Get list of active regions"""
        return client.get_regions()
    
    def count_users_in_region(client: OpenSimClient, region_name: str) -> int:
        """Count users in specific region"""
        users = client.get_users()
        return len([u for u in users if u.region == region_name])
    
    with OpenSimClient() as client:
        # Use typed functions
        regions: List[Region] = get_active_regions(client)
        print(f"Found {len(regions)} regions")
        
        for region in regions:
            count = count_users_in_region(client, region.name)
            print(f"  {region.name}: {count} users")


if __name__ == "__main__":
    import sys
    
    examples = {
        "1": ("Structured Return Values", example_structured_returns),
        "2": ("Regions (Structured Data)", example_regions),
        "3": ("Users (Structured Data)", example_users),
        "4": ("Stats (Structured Data)", example_stats),
        "5": ("User Management", example_user_management),
        "6": ("Region Operations", example_region_operations),
        "7": ("Batch Operations", example_batch_operations),
        "8": ("Error Handling", example_error_handling),
        "9": ("Monitoring Loop", example_monitoring_loop),
        "10": ("Typed Functions", example_typed_functions),
    }
    
    print("OpenSim-Pymote Examples (Structured Data)\n")
    print("Choose example:")
    for key, (name, _) in examples.items():
        print(f"  {key}. {name}")
    print("  0. Exit\n")
    
    if len(sys.argv) > 1:
        choice = sys.argv[1]
    else:
        choice = input("Enter choice: ").strip()
    
    print()
    
    if choice in examples:
        name, func = examples[choice]
        print(f"Running: {name}\n")
        print("=" * 60)
        print()
        try:
            func()
        except Exception as e:
            print(f"\nError: {e}")
    elif choice == "0":
        print("Goodbye!")
    else:
        print("Invalid choice!")
