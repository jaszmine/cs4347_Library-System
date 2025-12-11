#!/usr/bin/env python3
"""
Easy start script for the Library Management System
"""

import subprocess
import sys
import os

def check_dependencies():
    """Check if required packages are installed"""
    try:
        import flask
        import mysql.connector
        print("✓ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"✗ Missing dependency: {e}")
        print("\nInstalling dependencies...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            print("✓ Dependencies installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("✗ Failed to install dependencies")
            return False

def check_mysql():
    """Check if MySQL is running"""
    try:
        import mysql.connector
        conn = mysql.connector.connect(
            host='127.0.0.1',
            user='root',
            password='password'
        )
        conn.close()
        print("✓ MySQL is running")
        return True
    except Exception as e:
        print(f"✗ MySQL connection failed: {e}")
        print("\nPlease make sure:")
        print("  1. MySQL is running (sudo service mysql start)")
        print("  2. Database 'Library' exists")
        print("  3. Username: root, Password: password")
        return False

def setup_database():
    """Run your existing setup scripts"""
    print("\nSetting up database...")
    
    # You'll need to run your existing scripts here
    # For example:
    # import create_tables
    # create_tables.createTables(...)
    
    print("Note: Please run your existing setup scripts manually")
    print("      e.g., python create_tables.py")

def main():
    print("=" * 50)
    print("LIBRARY MANAGEMENT SYSTEM - SETUP")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        return
    
    # Check MySQL
    if not check_mysql():
        return
    
    # Setup database
    setup_database()
    
    # Start Flask server
    print("\n" + "=" * 50)
    print("STARTING FLASK SERVER...")
    print("=" * 50)
    print("\nFrontend URL: http://localhost:3000 (or your HTML file)")
    print("API URL:      http://localhost:5001")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 50)
    
    # Import and run the app
    from app import app
    app.run(debug=True, host='0.0.0.0', port=5000)

if __name__ == '__main__':
    main()