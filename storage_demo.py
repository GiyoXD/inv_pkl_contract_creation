#!/usr/bin/env python3
"""
Storage Management Demo Script
Demonstrates the storage monitoring and cleanup features
"""

import sqlite3
import json
import os
from datetime import datetime, timedelta
from login import (
    get_storage_stats, cleanup_old_data, optimize_database,
    get_storage_recommendations, update_storage_config,
    STORAGE_CLEANUP_CONFIG
)

def demo_storage_features():
    """Demonstrate storage management features"""
    print("💾 Storage Management Demo")
    print("=" * 50)
    
    # 1. Get current storage statistics
    print("\n1. 📊 Current Storage Statistics:")
    stats = get_storage_stats()
    if stats:
        print(f"   Total Database Size: {stats.get('total_size_kb', 0):.1f} KB")
        print(f"   Total Database Size: {stats.get('total_size_kb', 0) / 1024:.2f} MB")
        
        tables = stats.get('tables', {})
        total_records = sum(table.get('count', 0) for table in tables.values())
        print(f"   Total Records: {total_records:,}")
        
        print("\n   Table Breakdown:")
        for table_name, table_info in tables.items():
            print(f"   - {table_name}: {table_info.get('count', 0):,} records, {table_info.get('estimated_size_kb', 0):.1f} KB")
    else:
        print("   Could not retrieve storage statistics.")
    
    # 2. Get storage recommendations
    print("\n2. 💡 Storage Recommendations:")
    recommendations = get_storage_recommendations()
    if recommendations:
        for i, rec in enumerate(recommendations, 1):
            print(f"   {i}. {rec['message']}")
            print(f"      Action: {rec['action']}")
    else:
        print("   No storage optimization recommendations at this time.")
    
    # 3. Show current configuration
    print("\n3. ⚙️ Current Storage Configuration:")
    for key, value in STORAGE_CLEANUP_CONFIG.items():
        print(f"   {key}: {value}")
    
    # 4. Demo cleanup (dry run)
    print("\n4. 🧹 Storage Cleanup Demo:")
    print("   Running cleanup with 30-day retention (demo mode)...")
    
    # Create some test data for demo
    create_test_data()
    
    # Run cleanup
    result = cleanup_old_data(days_back=30, force=True)
    if result['success']:
        print(f"   ✅ {result['message']}")
        if 'stats' in result:
            stats = result['stats']
            print(f"   Cleaned: {stats['business_activities_cleaned']} business activities")
            print(f"   Cleaned: {stats['security_audit_cleaned']} security logs")
            print(f"   Cleaned: {stats['sessions_cleaned']} sessions")
            if stats['archived_files']:
                print(f"   Archived: {len(stats['archived_files'])} files")
    else:
        print(f"   ❌ {result['message']}")
    
    # 5. Database optimization
    print("\n5. ⚡ Database Optimization:")
    result = optimize_database()
    if result['success']:
        print(f"   ✅ {result['message']}")
    else:
        print(f"   ❌ {result['message']}")
    
    # 6. Updated statistics
    print("\n6. 📊 Updated Storage Statistics:")
    stats = get_storage_stats()
    if stats:
        print(f"   Total Database Size: {stats.get('total_size_kb', 0):.1f} KB")
        print(f"   Total Database Size: {stats.get('total_size_kb', 0) / 1024:.2f} MB")
        
        tables = stats.get('tables', {})
        total_records = sum(table.get('count', 0) for table in tables.values())
        print(f"   Total Records: {total_records:,}")
    
    print("\n" + "=" * 50)
    print("✅ Storage Management Demo Complete!")

def create_test_data():
    """Create some test data for the demo"""
    try:
        from login import USER_DB_PATH, log_business_activity, log_security_event
        
        # Create some test business activities
        for i in range(5):
            log_business_activity(
                user_id=1,
                username="demo_user",
                activity_type="INVOICE_EDIT",
                target_invoice_ref=f"DEMO{i:03d}",
                target_invoice_no=f"INV{i:03d}",
                action_description=f"Demo activity {i}",
                old_values={"test": f"old_value_{i}"},
                new_values={"test": f"new_value_{i}"},
                success=True
            )
        
        # Create some test security events
        for i in range(3):
            log_security_event(
                user_id=1,
                username="demo_user",
                action="LOGIN_SUCCESS",
                success=True,
                details=f"Demo security event {i}"
            )
        
        print("   Created test data for demo...")
        
    except Exception as e:
        print(f"   Could not create test data: {e}")

if __name__ == "__main__":
    demo_storage_features() 