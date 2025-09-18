#!/usr/bin/env python3
"""
VFL Virtual Soccer MVP - Database Setup Script
Creates the MySQL database and initializes it with sample data
"""

import pymysql
import sys
from database import init_database, seed_database
from flask import Flask

def create_database():
    """Create the MySQL database if it doesn't exist"""
    try:
        # Connect to MySQL server (without specifying database)
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='Admin!2025',
            charset='utf8mb4'
        )
        
        with connection.cursor() as cursor:
            # Create database if it doesn't exist
            cursor.execute("CREATE DATABASE IF NOT EXISTS vfl_soccer CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            print("✅ Database 'vfl_soccer' created successfully")
            
            # Use the database
            cursor.execute("USE vfl_soccer")
            print("✅ Connected to vfl_soccer database")
        
        connection.close()
        return True
        
    except Exception as e:
        print(f"❌ Failed to create database: {e}")
        return False

def setup_database():
    """Complete database setup process"""
    print("🚀 VFL Virtual Soccer MVP - Database Setup")
    print("=" * 50)
    
    # Step 1: Create database
    print("\n📊 Step 1: Creating MySQL database...")
    if not create_database():
        print("❌ Database creation failed. Exiting.")
        return False
    
    # Step 2: Initialize Flask app and database
    print("\n🔧 Step 2: Initializing Flask app and database...")
    app = Flask(__name__)
    
    if not init_database(app):
        print("❌ Database initialization failed. Exiting.")
        return False
    
    # Step 3: Seed database with sample data
    print("\n🌱 Step 3: Seeding database with sample data...")
    with app.app_context():
        if not seed_database():
            print("❌ Database seeding failed. Exiting.")
            return False
    
    print("\n✅ Database setup completed successfully!")
    print("\n📋 Summary:")
    print("   - Database: vfl_soccer")
    print("   - Companies: 3 (eBet Europe, eBet Spain, eBet Germany)")
    print("   - Clients: 8 (various betting shops)")
    print("   - Leagues: 8 (Premier League, La Liga, Bundesliga, etc.)")
    print("   - Client-League assignments: Configured")
    
    return True

if __name__ == "__main__":
    if setup_database():
        print("\n🎉 You can now start the simulation engine!")
        print("   Run: python simulation_engine.py")
    else:
        print("\n💥 Database setup failed!")
        sys.exit(1)
