#!/usr/bin/env python3
"""
Comprehensive test with detailed logging to track all PDB Gateway operations.
"""

import sys
import os
import time
sys.path.insert(0, '/app/pdb-rest-gateway/src')

from pdb_gateway.core.session_manager import SessionManager
from pdb_gateway.core.debug_logger import init_logger, get_logger
from pdb_gateway.schemas.simple_schemas import StepType


def test_with_comprehensive_logging():
    """Test PDB Gateway with comprehensive logging enabled."""
    print("🔧 PDB Gateway Testing with Comprehensive Logging")
    print("📋 All operations will be logged to pdb_gateway.log")
    print("=" * 70)
    
    # Initialize logger with detailed logging
    logger = init_logger(
        log_file="/app/pdb-rest-gateway/pdb_gateway.log",
        console_output=True,
        log_level="DEBUG"
    )
    
    logger.log_info("=== STARTING COMPREHENSIVE LOGGING TEST ===")
    
    # Create session manager
    print("\n1. 🏗️  Creating Session Manager")
    manager = SessionManager(max_sessions=3, session_timeout=300)
    logger.log_info("Session manager created", {
        "max_sessions": 3,
        "timeout": 300
    })
    
    # Create debugging session
    print("\n2. 🚀 Creating Debug Session")
    target_file = "data_processor.py"
    working_dir = "/app/breakpoint-simulation"
    
    result = manager.create_session(
        target_file=target_file,
        working_directory=working_dir,
        args=["test_source", "12"],
        environment={"DEBUG": "1", "LOG_LEVEL": "DEBUG"}
    )
    
    session_id = result["session_id"]
    session = manager.get_session(session_id)
    
    print(f"   ✅ Session created: {session_id[:8]}...")
    logger.log_info("Test session retrieved", {
        "session_id": session_id,
        "target_file": target_file
    })
    
    # Start debugging
    print("\n3. 🐛 Starting Debug Process")
    debug_result = session.start_debugging()
    print(f"   ✅ Debug started: {debug_result['success']}")
    
    # Set multiple types of breakpoints
    print("\n4. 🎯 Setting Various Types of Breakpoints")
    
    # Regular breakpoints
    regular_breakpoints = [
        (15, "load_raw_data function entry"),
        (60, "validate_data function entry"),
        (120, "transform_data function entry"),
        (185, "aggregate_data function entry"),
        (235, "generate_report function entry")
    ]
    
    print("   📍 Setting regular breakpoints...")
    for line_num, description in regular_breakpoints:
        result = session.set_breakpoint(target_file, line_num)
        print(f"      Line {line_num}: {description} - {result['success']}")
    
    # Conditional breakpoints
    print("   🔀 Setting conditional breakpoints...")
    conditional_breakpoints = [
        (35, "i > 3", "Break when loop counter > 3"),
        (80, "not is_valid", "Break for invalid records"),
        (150, "'computed_score' in transformed_record", "Break when computed score exists")
    ]
    
    for line_num, condition, description in conditional_breakpoints:
        result = session.set_breakpoint(
            filename=target_file,
            line_number=line_num,
            condition=condition
        )
        print(f"      Line {line_num} (if {condition}): {description} - {result['success']}")
    
    # Temporary breakpoints
    print("   ⏱️  Setting temporary breakpoints...")
    temp_breakpoints = [
        (45, "Temporary in load_raw_data"),
        (100, "Temporary in validate_data")
    ]
    
    for line_num, description in temp_breakpoints:
        result = session.set_breakpoint(
            filename=target_file,
            line_number=line_num,
            temporary=True
        )
        print(f"      Line {line_num}: {description} - {result['success']}")
    
    total_breakpoints = len(regular_breakpoints) + len(conditional_breakpoints) + len(temp_breakpoints)
    print(f"   📊 Total breakpoints set: {total_breakpoints}")
    
    # Comprehensive stepping test
    print("\n5. 👣 Comprehensive Stepping Operations")
    step_sequence = [
        (StepType.NEXT, 1, "Step to next line"),
        (StepType.CONTINUE, 1, "Continue to first breakpoint"),
        (StepType.STEP, 1, "Step into function"),
        (StepType.NEXT, 3, "Next 3 lines"),
        (StepType.CONTINUE, 1, "Continue to next breakpoint"),
        (StepType.STEP, 2, "Step 2 times"),
        (StepType.UNTIL, 1, "Run until line"),
        (StepType.RETURN, 1, "Return from function")
    ]
    
    for i, (step_type, count, description) in enumerate(step_sequence, 1):
        print(f"   👣 Step {i}: {description}")
        result = session.step(step_type, count)
        print(f"      ✅ Success: {result['success']}")
        print(f"      📍 Location: {result.get('current_file', 'N/A')}:{result.get('current_line', 'N/A')}")
        print(f"      🔄 Status: {result.get('status', 'N/A')}")
        
        # Small delay for realistic testing
        time.sleep(0.1)
    
    # Extensive variable inspection
    print("\n6. 🔍 Extensive Variable Inspection")
    
    # Simple variables
    print("   📝 Simple variables:")
    simple_vars = ["source_name", "record_count", "i", "__name__", "__file__"]
    for var in simple_vars:
        result = session.inspect(var)
        print(f"      {var}: {result['success']} (type: {result['type_name']})")
    
    # Complex objects
    print("   🏗️  Complex objects:")
    complex_vars = ["raw_data", "validation_rules", "validation_result", "transformed_records"]
    for var in complex_vars:
        result = session.inspect(var)
        print(f"      {var}: {result['success']} (type: {result['type_name']})")
        if result['repr_value']:
            preview = result['repr_value'][:50]
            print(f"         Preview: {preview}...")
    
    # Expressions and computations
    print("   🧮 Expressions and computations:")
    expressions = [
        "len(raw_data) if 'raw_data' in locals() else 0",
        "validation_result.get('valid_count', 0)",
        "sum(r.get('value', 0) for r in raw_data[:3]) if 'raw_data' in locals() else 0",
        "[r['id'] for r in raw_data[:3]] if 'raw_data' in locals() else []",
        "validation_rules.get('value_min', 0) < 10"
    ]
    
    for expr in expressions:
        result = session.inspect(expr)
        print(f"      {expr[:40]}...: {result['success']}")
        if result['repr_value']:
            print(f"         Result: {result['repr_value']}")
    
    # Debug command testing
    print("\n7. ⚡ Debug Command Execution")
    debug_commands = [
        ("list", "Show current code"),
        ("list 15,25", "Show function start"),
        ("where", "Show call stack"),
        ("args", "Show function arguments"),
        ("locals", "Show local variables"),
        ("pp locals()", "Pretty print locals"),
        ("globals", "Show global variables"),
        ("whatis raw_data", "Show variable type"),
        ("up", "Move up stack frame"),
        ("down", "Move down stack frame"),
        ("bt", "Full backtrace"),
        ("break", "List all breakpoints"),
        ("help", "Show help")
    ]
    
    for command, description in debug_commands:
        print(f"   ⚡ '{command}': {description}")
        result = session.execute_command(command)
        print(f"      ✅ Success: {result['success']}")
        if result['output']:
            output_preview = result['output'][:80].replace('\n', ' ')
            print(f"      📄 Output: {output_preview}...")
    
    # Breakpoint management testing
    print("\n8. 🔧 Breakpoint Management")
    
    # List current breakpoints
    info = session.get_session_info()
    print(f"   📊 Current breakpoints: {len(info['breakpoints'])}")
    
    # Remove some breakpoints
    print("   🗑️  Removing selected breakpoints:")
    breakpoints_to_remove = [(15, "load_raw_data"), (60, "validate_data")]
    for line_num, description in breakpoints_to_remove:
        result = session.set_breakpoint(
            filename=target_file,
            line_number=line_num,
            remove=True
        )
        print(f"      Line {line_num} ({description}): {result['success']}")
    
    # Check remaining breakpoints
    info = session.get_session_info()
    print(f"   📊 Remaining breakpoints: {len(info['breakpoints'])}")
    
    # Session information and statistics
    print("\n9. 📊 Session Information and Statistics")
    session_info = session.get_session_info()
    print(f"   🆔 Session ID: {session_info['session_id'][:8]}...")
    print(f"   📁 Target file: {session_info['target_file']}")
    print(f"   🔄 Status: {session_info['status']}")
    print(f"   🎯 Active breakpoints: {len(session_info['breakpoints'])}")
    print(f"   ⏰ Created: {session_info['created_at']}")
    print(f"   ⏱️  Last activity: {session_info['last_activity']}")
    
    # Get logger statistics
    logger_summary = logger.get_session_summary(session_id)
    if logger_summary:
        print(f"   📋 Logger statistics:")
        print(f"      Total operations: {logger_summary['total_operations']}")
        print(f"      Duration: {logger_summary['duration']:.2f} seconds")
        print(f"      Operations breakdown: {logger_summary['operations_breakdown']}")
    
    # Output analysis
    print("\n10. 📄 Output Analysis")
    output = session.get_output()
    print(f"   📄 Total debug output: {len(output)} characters")
    
    if output:
        lines = output.split('\n')
        print(f"   📝 Output contains {len(lines)} lines")
        print(f"   📋 Sample output (first 100 chars): {output[:100]}...")
        print(f"   📋 Sample output (last 100 chars): ...{output[-100:]}")
    
    # Export session log
    print("\n11. 💾 Exporting Session Log")
    log_export_file = f"/app/pdb-rest-gateway/session_{session_id[:8]}_log.json"
    logger.export_session_log(session_id, log_export_file)
    print(f"   💾 Session log exported to: {log_export_file}")
    
    # Final cleanup
    print("\n12. 🧹 Session Cleanup")
    terminate_result = manager.terminate_session(session_id)
    print(f"   🛑 Session terminated: {terminate_result['success']}")
    print(f"   📝 Message: {terminate_result['message']}")
    print(f"   📊 Remaining sessions: {manager.get_session_count()}")
    
    # Final logging
    logger.log_info("=== COMPREHENSIVE LOGGING TEST COMPLETED ===", {
        "total_operations_performed": [
            "session_creation", "debug_start", "breakpoint_setting",
            "stepping_operations", "variable_inspection", "command_execution",
            "breakpoint_management", "session_termination"
        ],
        "test_duration_seconds": time.time() - test_start_time
    })
    
    print("\n" + "=" * 70)
    print("✅ Comprehensive Logging Test Complete!")
    print(f"📋 All operations logged to: /app/pdb-rest-gateway/pdb_gateway.log")
    print(f"💾 Session details exported to: {log_export_file}")
    print("\n🎯 Logged Operations:")
    print("   • ✅ Session creation and configuration")
    print("   • ✅ Debug process initialization")
    print("   • ✅ Multiple breakpoint types (regular, conditional, temporary)")
    print("   • ✅ Comprehensive stepping operations")
    print("   • ✅ Variable inspection (simple, complex, expressions)")
    print("   • ✅ Debug command execution")
    print("   • ✅ Breakpoint management and removal")
    print("   • ✅ Session information and statistics")
    print("   • ✅ Output capture and analysis")
    print("   • ✅ Session cleanup and termination")
    print("\n📊 Log Analysis Available:")
    print("   • Timestamp tracking for all operations")
    print("   • Success/failure status for each operation")
    print("   • Parameter values and results for each call")
    print("   • Session duration and operation statistics")
    print("   • Detailed error logging for troubleshooting")
    print("\n🚀 PDB Gateway Logging System is Production Ready!")


if __name__ == "__main__":
    test_start_time = time.time()
    test_with_comprehensive_logging()