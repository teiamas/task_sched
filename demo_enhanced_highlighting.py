#!/usr/bin/env python3
"""
Demonstration script showing the enhanced deadline violation visualization.
Creates a clear example of how the new multi-method highlighting works.
"""

import rate_monotonic as rtm
from task_schedule_visualizer import plot_rm_schedule, plot_rm_schedule_inline

def main():
    print("=== Enhanced Deadline Violation Visualization Demo ===")
    print()
    
    # Create a task set that will use red colors and have violations
    print("Creating task set with red task colors and deadline violations...")
    
    # This task set is carefully designed to:
    # 1. Use the red color from the palette (task index 1 = #FF6B6B) 
    # 2. Have clear deadline violations
    # 3. Be simple enough to understand
    demo_tasks = [
        rtm.Task(period=4, deadline=4, execution_time=1),   # Task 1: No violations (teal color)
        rtm.Task(period=6, deadline=2, execution_time=3),   # Task 2: VIOLATIONS (red color - problematic!)
        rtm.Task(period=10, deadline=8, execution_time=2),  # Task 3: No violations (yellow color)
    ]
    
    print()
    print("Task Details:")
    for i, task in enumerate(demo_tasks, 1):
        color_info = "🔴 RED" if i == 2 else "⚫ Other"
        violation_info = "⚠️  WILL VIOLATE" if i == 2 else "✅ Schedulable"
        print(f"  Task {i}: Period={task.period}, Deadline={task.deadline}, Exec={task.execution_time} | {color_info} | {violation_info}")
    
    print()
    print("🎯 Focus on Task 2 (red background) - violations should be clearly visible despite red color!")
    print()
    print("ENHANCED VIOLATION INDICATORS:")
    print("  1. ⬛ THICK BLACK BORDER (3px instead of 0.5px)")
    print("  2. ❌ CROSS-HATCH PATTERN ('xxx' overlay)")  
    print("  3. 🔴 RED WARNING STRIPE (thin red bar on top)")
    print("  4. 🌫️  REDUCED TRANSPARENCY (more opaque)")
    print()
    
    # Generate the visualization
    plot_rm_schedule(demo_tasks, filename="demo_enhanced_violations", output_dir="enhanced_test")
    
    print("✅ Visualization saved to: enhanced_test/demo_enhanced_violations.png")
    print()
    print("💡 The combination of these 4 indicators ensures deadline violations")
    print("   are visible even when the task color is red or any other color!")

if __name__ == "__main__":
    main()
