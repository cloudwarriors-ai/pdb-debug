#!/usr/bin/env python3
"""
Log viewer and analyzer for PDB Gateway operations.
"""

import json
import os
from datetime import datetime


def analyze_main_log():
    """Analyze the main PDB Gateway log file."""
    log_file = "/app/pdb-rest-gateway/pdb_gateway.log"
    
    if not os.path.exists(log_file):
        print("❌ Log file not found!")
        return
    
    print("📋 PDB Gateway Log Analysis")
    print("=" * 50)
    
    with open(log_file, 'r') as f:
        content = f.read()
    
    lines = content.split('\n')
    print(f"📄 Total log lines: {len(lines)}")
    
    # Count operation types
    operations = {}
    sessions = set()
    
    for line in lines:
        if '|' in line and 'INFO' in line:
            try:
                # Extract the message part
                parts = line.split(' | ')
                if len(parts) >= 3:
                    message = parts[2].strip()
                    
                    # Count different operation types
                    if "BREAKPOINT SET" in message:
                        operations["breakpoint_set"] = operations.get("breakpoint_set", 0) + 1
                    elif "BREAKPOINT REMOVED" in message:
                        operations["breakpoint_removed"] = operations.get("breakpoint_removed", 0) + 1
                    elif "STEP OPERATION" in message:
                        operations["step_operation"] = operations.get("step_operation", 0) + 1
                    elif "VARIABLE INSPECTION" in message:
                        operations["variable_inspection"] = operations.get("variable_inspection", 0) + 1
                    elif "COMMAND EXECUTION" in message:
                        operations["command_execution"] = operations.get("command_execution", 0) + 1
                    elif "DEBUG SESSION CREATED" in message:
                        operations["session_created"] = operations.get("session_created", 0) + 1
                    elif "DEBUG SESSION TERMINATED" in message:
                        operations["session_terminated"] = operations.get("session_terminated", 0) + 1
                    
                    # Try to extract session IDs
                    next_line_idx = lines.index(line) + 1
                    if next_line_idx < len(lines) and lines[next_line_idx].strip().startswith('{'):
                        try:
                            data = json.loads(lines[next_line_idx])
                            if "session_id" in data:
                                sessions.add(data["session_id"][:8])
                        except:
                            pass
            except:
                continue
    
    print(f"🎯 Operations Summary:")
    for op_type, count in operations.items():
        print(f"   {op_type}: {count}")
    
    print(f"\n🔧 Unique sessions: {len(sessions)}")
    for session in sessions:
        print(f"   Session: {session}...")
    
    # Show recent log entries
    print(f"\n📝 Recent Log Entries (last 10):")
    recent_entries = []
    for line in lines[-20:]:
        if '|' in line and ('INFO' in line or 'ERROR' in line or 'WARNING' in line):
            recent_entries.append(line)
    
    for entry in recent_entries[-10:]:
        timestamp = entry.split(' | ')[0] if ' | ' in entry else "Unknown"
        level = entry.split(' | ')[1] if ' | ' in entry and len(entry.split(' | ')) > 1 else "Unknown"
        message = entry.split(' | ')[2] if ' | ' in entry and len(entry.split(' | ')) > 2 else entry
        print(f"   {timestamp} [{level}] {message[:60]}...")


def analyze_session_log():
    """Analyze exported session log."""
    # Find the most recent session log
    log_dir = "/app/pdb-rest-gateway"
    session_files = [f for f in os.listdir(log_dir) if f.startswith("session_") and f.endswith("_log.json")]
    
    if not session_files:
        print("❌ No session log files found!")
        return
    
    # Get the most recent one
    latest_session_file = sorted(session_files)[-1]
    session_file_path = os.path.join(log_dir, latest_session_file)
    
    print(f"\n📊 Session Log Analysis: {latest_session_file}")
    print("=" * 50)
    
    with open(session_file_path, 'r') as f:
        session_data = json.load(f)
    
    print(f"🆔 Session ID: {session_data['session_id'][:8]}...")
    print(f"📁 Target file: {session_data['target_file']}")
    print(f"⏰ Created: {datetime.fromtimestamp(session_data['created_at']).strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📤 Exported: {session_data['export_timestamp']}")
    print(f"📊 Total operations: {len(session_data['operations'])}")
    
    # Analyze operations
    operation_types = {}
    timeline = []
    
    for op in session_data['operations']:
        op_type = op['operation_type']
        operation_types[op_type] = operation_types.get(op_type, 0) + 1
        
        timestamp = datetime.fromtimestamp(op['timestamp'])
        timeline.append({
            'time': timestamp.strftime('%H:%M:%S.%f')[:-3],
            'type': op_type,
            'data': op['data']
        })
    
    print(f"\n🎯 Operation Breakdown:")
    for op_type, count in operation_types.items():
        print(f"   {op_type}: {count}")
    
    # Show timeline of operations
    print(f"\n⏰ Operation Timeline (first 15):")
    for i, op in enumerate(timeline[:15], 1):
        print(f"   {i:2d}. {op['time']} | {op['type']:<15} | ", end="")
        
        if op['type'] == 'breakpoint_set':
            line = op['data'].get('line_number', 'N/A')
            condition = op['data'].get('condition')
            temp = op['data'].get('temporary', False)
            suffix = " (conditional)" if condition else " (temporary)" if temp else ""
            print(f"Line {line}{suffix}")
        elif op['type'] == 'step':
            step_type = op['data'].get('step_type', 'unknown')
            count = op['data'].get('count', 1)
            print(f"{step_type} (count: {count})")
        elif op['type'] == 'inspect':
            expr = op['data'].get('expression', 'unknown')
            success = op['data'].get('success', False)
            status = "✅" if success else "❌"
            print(f"{status} {expr[:30]}...")
        elif op['type'] == 'command':
            cmd = op['data'].get('command', 'unknown')
            success = op['data'].get('success', False)
            status = "✅" if success else "❌"
            print(f"{status} '{cmd}'")
        else:
            print(f"{op['data']}")
    
    if len(timeline) > 15:
        print(f"   ... and {len(timeline) - 15} more operations")
    
    # Calculate session duration
    if len(timeline) > 1:
        start_time = datetime.fromtimestamp(session_data['operations'][0]['timestamp'])
        end_time = datetime.fromtimestamp(session_data['operations'][-1]['timestamp'])
        duration = (end_time - start_time).total_seconds()
        print(f"\n⏱️  Session duration: {duration:.3f} seconds")
        print(f"📈 Operations per second: {len(timeline) / duration:.2f}")


def show_log_statistics():
    """Show comprehensive log statistics."""
    print(f"\n📈 Comprehensive Log Statistics")
    print("=" * 50)
    
    # File sizes
    log_file = "/app/pdb-rest-gateway/pdb_gateway.log"
    if os.path.exists(log_file):
        size = os.path.getsize(log_file)
        print(f"📄 Main log file size: {size:,} bytes")
    
    # Session log files
    log_dir = "/app/pdb-rest-gateway"
    session_files = [f for f in os.listdir(log_dir) if f.startswith("session_") and f.endswith("_log.json")]
    print(f"📊 Session log files: {len(session_files)}")
    
    total_session_size = 0
    for session_file in session_files:
        session_path = os.path.join(log_dir, session_file)
        size = os.path.getsize(session_path)
        total_session_size += size
        print(f"   {session_file}: {size:,} bytes")
    
    print(f"💾 Total session logs size: {total_session_size:,} bytes")
    print(f"📁 Total logging data: {os.path.getsize(log_file) + total_session_size:,} bytes")


if __name__ == "__main__":
    print("🔍 PDB Gateway Log Analysis Tool")
    print("=" * 60)
    
    analyze_main_log()
    analyze_session_log()
    show_log_statistics()
    
    print("\n" + "=" * 60)
    print("✅ Log Analysis Complete!")
    print("\n💡 What the logs show:")
    print("   • Detailed timestamp tracking for all operations")
    print("   • Success/failure status for each operation")
    print("   • Complete parameter values and results")
    print("   • Session duration and performance metrics")
    print("   • Operation sequencing and timing")
    print("   • Error tracking and debugging information")
    print("\n🎯 This provides complete debugging audit trail!")
    print("📋 Perfect for troubleshooting and performance analysis!")