#!/usr/bin/env python3
"""
Enhanced script to view the device monitor database with better formatting
"""

import sqlite3
from pathlib import Path
from datetime import datetime, timedelta

def format_uptime(seconds):
    """Convert seconds to readable format"""
    td = timedelta(seconds=int(seconds))
    days = td.days
    hours, remainder = divmod(td.seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    return f"{days}d {hours}h {minutes}m"

def main():
    # Database path
    db_path = Path(__file__).parent.parent / "agent_data.db"
    
    if not db_path.exists():
        print(f"❌ Database not found")
        return
    
    print(f"\n{'='*100}")
    print(f"📊 DEVICE MONITOR - DATABASE REPORT")
    print(f"{'='*100}\n")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Power Events
    print("🔋 POWER EVENTS:")
    print("-" * 100)
    cursor.execute("SELECT id, event_type, timestamp, details, synced FROM power_events ORDER BY timestamp")
    events = cursor.fetchall()
    
    if events:
        for event in events:
            event_id, event_type, timestamp, details, synced = event
            sync_status = "✅ Synced" if synced else "⏳ Not Synced"
            print(f"  [{event_id}] {event_type:12} | {timestamp} | {sync_status}")
            if details:
                print(f"       Details: {details}")
        print(f"\n  Total Power Events: {len(events)}\n")
    else:
        print("  No power events recorded.\n")
    
    # System Stats
    print("💻 SYSTEM STATISTICS:")
    print("-" * 100)
    cursor.execute("SELECT timestamp, cpu_percent, memory_percent, disk_percent, uptime FROM system_stats ORDER BY timestamp")
    stats = cursor.fetchall()
    
    if stats:
        print(f"  {'Timestamp':<22} | {'CPU %':<8} | {'Memory %':<10} | {'Disk %':<8} | {'Uptime'}")
        print("  " + "-" * 90)
        for stat in stats:
            timestamp, cpu, memory, disk, uptime = stat
            uptime_str = format_uptime(uptime)
            print(f"  {timestamp:<22} | {cpu:<8.1f} | {memory:<10.1f} | {disk:<8.1f} | {uptime_str}")
        print(f"\n  Total Statistics Collected: {len(stats)}")
        
        # Calculate averages
        avg_cpu = sum(s[1] for s in stats) / len(stats)
        avg_mem = sum(s[2] for s in stats) / len(stats)
        avg_disk = sum(s[3] for s in stats) / len(stats)
        
        print(f"\n  📊 Averages:")
        print(f"     CPU: {avg_cpu:.1f}% | Memory: {avg_mem:.1f}% | Disk: {avg_disk:.1f}%\n")
    else:
        print("  No system statistics recorded.\n")
    
    # Session Events
    print("👤 SESSION EVENTS:")
    print("-" * 100)
    cursor.execute("SELECT * FROM session_events")
    sessions = cursor.fetchall()
    
    if sessions:
        for session in sessions:
            print(f"  {session}")
        print(f"\n  Total Sessions: {len(sessions)}\n")
    else:
        print("  No session events recorded.\n")
    
    conn.close()
    
    print(f"{'='*100}")
    print(f"✅ Report Complete!")
    print(f"{'='*100}\n")

if __name__ == "__main__":
    main()
