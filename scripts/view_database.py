#!/usr/bin/env python3
"""
Script to view the contents of the device monitor database
"""

import sqlite3
import sys
from pathlib import Path
from datetime import datetime

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

def print_table(cursor, table_name):
    """Print all records from a table"""
    print(f"\n{'='*80}")
    print(f"TABLE: {table_name}")
    print(f"{'='*80}")
    
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()
    
    if not rows:
        print("No data found in this table.")
        return
    
    # Get column names
    columns = [description[0] for description in cursor.description]
    
    # Print header
    header = " | ".join(f"{col:15}" for col in columns)
    print(header)
    print("-" * len(header))
    
    # Print rows
    for row in rows:
        row_str = " | ".join(f"{str(val)[:15]:15}" for val in row)
        print(row_str)
    
    print(f"\nTotal records: {len(rows)}")

def main():
    # Database path
    db_path = project_root / "agent_data.db"
    
    if not db_path.exists():
        print(f"❌ Database not found at: {db_path}")
        return
    
    print(f"📊 Reading database from: {db_path}")
    print(f"Database size: {db_path.stat().st_size} bytes")
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        print(f"\n✅ Found {len(tables)} tables in the database")
        
        # Print data from each table
        for table in tables:
            table_name = table[0]
            print_table(cursor, table_name)
        
        conn.close()
        
        print(f"\n{'='*80}")
        print("✅ Database inspection complete!")
        print(f"{'='*80}")
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
