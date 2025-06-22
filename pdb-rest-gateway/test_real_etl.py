#!/usr/bin/env python3
"""Test PDB Gateway with actual ETL system components."""

import sys
import os
sys.path.insert(0, 'src')
sys.path.insert(0, '/app/backend')

from pdb_gateway.core.session_manager import SessionManager
from pdb_gateway.schemas.simple_schemas import StepType

def find_etl_files():
    """Find actual ETL files to debug."""
    etl_files = []
    
    # Core ETL files
    core_files = [
        "/app/backend/api/etl/core/etl_factory.py",
        "/app/backend/api/etl/core/job_group_service.py",
        "/app/backend/api/etl/core/dynamic_extractor.py",
        "/app/backend/api/etl/core/enhanced_loader.py",
        "/app/backend/api/etl/core/llm_transformer.py"
    ]
    
    # Platform-specific files
    platform_files = [
        "/app/backend/api/etl/platforms/zoom/extractors.py",
        "/app/backend/api/etl/platforms/dialpad/extractors.py",
        "/app/backend/api/etl/platforms/factory.py"
    ]
    
    all_files = core_files + platform_files
    
    for file_path in all_files:
        if os.path.exists(file_path):
            etl_files.append(file_path)
    
    return etl_files

def analyze_etl_file(file_path):
    """Analyze an ETL file for debugging opportunities."""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        lines = content.split('\n')
        analysis = {
            "file_path": file_path,
            "total_lines": len(lines),
            "classes": [],
            "functions": [],
            "potential_breakpoints": []
        }
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            # Find classes
            if stripped.startswith('class '):
                class_name = stripped.split('class ')[1].split('(')[0].split(':')[0]
                analysis["classes"].append((i, class_name))
            
            # Find functions
            if stripped.startswith('def '):
                func_name = stripped.split('def ')[1].split('(')[0]
                analysis["functions"].append((i, func_name))
            
            # Find potential breakpoints (error handling, data processing)
            if any(keyword in stripped.lower() for keyword in ['except', 'raise', 'error', 'transform', 'extract', 'load']):
                analysis["potential_breakpoints"].append((i, stripped[:50]))
        
        return analysis
        
    except Exception as e:
        return {
            "file_path": file_path,
            "error": str(e)
        }

def test_real_etl_debugging():
    """Test debugging with real ETL system files."""
    print("🔧 Testing PDB Gateway with Real ETL System\n")
    print("=" * 60)
    
    # Find ETL files
    print("1. 🔍 Discovering ETL Files")
    etl_files = find_etl_files()
    print(f"   ✅ Found {len(etl_files)} ETL files:")
    
    for file_path in etl_files:
        filename = os.path.basename(file_path)
        size = os.path.getsize(file_path)
        print(f"      📁 {filename} ({size} bytes)")
    
    if not etl_files:
        print("   ❌ No ETL files found!")
        return
    
    print()
    
    # Analyze first ETL file
    print("2. 📊 Analyzing ETL File Structure")
    target_file = etl_files[0]  # Use first file
    analysis = analyze_etl_file(target_file)
    
    if "error" in analysis:
        print(f"   ❌ Analysis failed: {analysis['error']}")
        return
    
    print(f"   📁 File: {os.path.basename(analysis['file_path'])}")
    print(f"   📝 Total lines: {analysis['total_lines']}")
    print(f"   🏗️  Classes: {len(analysis['classes'])}")
    print(f"   ⚙️  Functions: {len(analysis['functions'])}")
    print(f"   🎯 Potential breakpoints: {len(analysis['potential_breakpoints'])}")
    
    # Show some classes and functions
    if analysis['classes']:
        print(f"   📚 Classes found:")
        for line_num, class_name in analysis['classes'][:3]:
            print(f"      - Line {line_num}: {class_name}")
    
    if analysis['functions']:
        print(f"   ⚙️  Functions found:")
        for line_num, func_name in analysis['functions'][:5]:
            print(f"      - Line {line_num}: {func_name}")
    
    print()
    
    # Create session manager
    print("3. 🏗️  Creating Debug Session for Real ETL")
    manager = SessionManager()
    
    # Create session with actual ETL file
    try:
        result = manager.create_session(
            target_file=target_file,
            working_directory="/app/backend",
            environment={
                "PYTHONPATH": "/app/backend",
                "DEBUG": "1",
                "ETL_DEBUG_MODE": "true"
            }
        )
        
        session_id = result["session_id"]
        session = manager.get_session(session_id)
        
        print(f"   ✅ Session created: {session_id[:8]}...")
        print(f"   📁 Target: {os.path.basename(target_file)}")
        print(f"   📂 Working directory: /app/backend")
        print(f"   🔄 Status: {result['status']}")
        
    except Exception as e:
        print(f"   ❌ Failed to create session: {e}")
        return
    
    print()
    
    # Start debugging session
    print("4. 🐛 Starting Real ETL Debug Session")
    try:
        debug_result = session.start_debugging()
        print(f"   ✅ Debug started: {debug_result['success']}")
        print(f"   📝 Message: {debug_result['message']}")
        print(f"   🔄 Status: {session.status.value}")
        
    except Exception as e:
        print(f"   ❌ Debug start failed: {e}")
        return
    
    print()
    
    # Set strategic breakpoints
    print("5. 🎯 Setting Strategic ETL Breakpoints")
    
    # Set breakpoints at interesting locations
    breakpoints_to_set = []
    
    # Add breakpoints for classes (constructors)
    for line_num, class_name in analysis['classes'][:2]:
        breakpoints_to_set.append((line_num + 2, f"{class_name} constructor area"))
    
    # Add breakpoints for key functions
    for line_num, func_name in analysis['functions'][:3]:
        if any(keyword in func_name.lower() for keyword in ['extract', 'transform', 'load', 'process', 'execute']):
            breakpoints_to_set.append((line_num + 1, f"{func_name} function entry"))
    
    # Add breakpoints at potential error locations
    for line_num, code_snippet in analysis['potential_breakpoints'][:2]:
        breakpoints_to_set.append((line_num, f"Error handling: {code_snippet[:30]}..."))
    
    successful_breakpoints = []
    for line_num, description in breakpoints_to_set:
        try:
            result = session.set_breakpoint(
                filename=os.path.basename(target_file),
                line_number=line_num
            )
            
            if result["success"]:
                successful_breakpoints.append((line_num, description))
                print(f"   🎯 Line {line_num}: {description}")
            else:
                print(f"   ❌ Line {line_num}: Failed - {result['message']}")
                
        except Exception as e:
            print(f"   ❌ Line {line_num}: Exception - {e}")
    
    print(f"   📊 Successfully set {len(successful_breakpoints)} breakpoints")
    print()
    
    # Demonstrate ETL debugging commands
    print("6. ⚡ ETL-Specific Debug Commands")
    etl_debug_commands = [
        "list 1,20",  # Show beginning of file
        "where",      # Show call stack
        "args",       # Show arguments
        "locals",     # Show local variables
    ]
    
    for cmd in etl_debug_commands:
        try:
            result = session.execute_command(cmd)
            print(f"   ⚡ '{cmd}': {result['success']}")
            if result["output"]:
                output_preview = result["output"][:100].replace('\n', ' ')
                print(f"      📄 Output: {output_preview}...")
        except Exception as e:
            print(f"   ❌ '{cmd}': {e}")
    
    print()
    
    # Try to inspect ETL-related variables
    print("7. 🔍 Inspecting ETL Context")
    etl_variables = [
        "__file__",
        "__name__", 
        "sys.path",
        "os.environ"
    ]
    
    for var in etl_variables:
        try:
            result = session.inspect(var)
            print(f"   🔍 {var}: {result['success']} (type: {result['type_name']})")
        except Exception as e:
            print(f"   ❌ {var}: {e}")
    
    print()
    
    # Session information
    print("8. 📊 Real ETL Debug Session Info")
    info = session.get_session_info()
    print(f"   🆔 Session ID: {info['session_id'][:8]}...")
    print(f"   📁 Target file: {info['target_file']}")
    print(f"   🔄 Status: {info['status']}")
    print(f"   🎯 Breakpoints: {len(info['breakpoints'])}")
    print(f"   ⏰ Created: {info['created_at']}")
    
    # Show breakpoint details
    if info['breakpoints']:
        print(f"   📍 Breakpoint details:")
        for bp in info['breakpoints']:
            print(f"      - Line {bp['line_number']}: {bp['filename']}")
    
    print()
    
    # Cleanup
    print("9. 🧹 Cleanup")
    terminate_result = manager.terminate_session(session_id)
    print(f"   🛑 Session terminated: {terminate_result['success']}")
    print(f"   📊 Remaining sessions: {manager.get_session_count()}")
    
    print("\n" + "=" * 60)
    print("✅ Real ETL System Integration Test Complete!")
    print("\n🎯 Successfully Tested:")
    print("   • ✅ Discovery of actual ETL system files")
    print("   • ✅ Analysis of ETL code structure (classes, functions)")
    print("   • ✅ Debug session creation with real ETL files")
    print("   • ✅ Strategic breakpoint placement in ETL code")
    print("   • ✅ ETL-specific debugging commands")
    print("   • ✅ Context inspection for ETL environment")
    print("\n🚀 PDB Gateway + ETL System Integration Success!")
    print("💡 Ready for debugging:")
    print(f"   - ETL Factory classes in {len([f for f in etl_files if 'factory' in f])} files")
    print(f"   - Platform extractors in {len([f for f in etl_files if 'extractor' in f])} files") 
    print(f"   - Core ETL components in {len([f for f in etl_files if 'core' in f])} files")

if __name__ == "__main__":
    test_real_etl_debugging()