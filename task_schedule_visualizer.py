import matplotlib.pyplot as plt
import numpy as np
import rate_monotonic as rtm
import os

def _generate_schedule_data(tasks, lcm_cycles=1, algorithm='DM'):
    """
    Generate scheduling data and plot elements for both inline and file output functions.
    
    Returns:
        tuple: (execution_timeline, tasks_sorted, time_range, title, all_periods, all_deadlines, task_colors, deadline_violations)
    """
    # Calculate LCM of all periods
    lcm = np.lcm.reduce([task.period for task in tasks])
    time_range = lcm * lcm_cycles
    
    # Sort tasks by priority based on algorithm
    if algorithm == 'DM':
        # Deadline Monotonic - shorter deadline = higher priority
        tasks_sorted = sorted(tasks, key=lambda x: x.deadline)
        title = 'Deadline Monotonic Preemptive Schedule'
    else:
        # Rate Monotonic - shorter period = higher priority
        tasks_sorted = sorted(tasks, key=lambda x: x.period)
        title = 'Rate Monotonic Preemptive Schedule'
    
    # Create execution timeline
    execution_timeline = [None] * time_range
    
    # Track deadline violations for each time unit
    deadline_violations = [False] * time_range
    
    # Track active task instances with their deadlines
    active_tasks = []
    
    # Simulate schedule
    for t in range(time_range):
        # Add new task releases
        for task in tasks_sorted:
            if t % task.period == 0:
                active_tasks.append({
                    'task': task,
                    'remaining': task.execution_time,
                    'release_time': t,
                    'absolute_deadline': t + task.deadline  # Absolute deadline for this instance
                })
        
        # Remove completed tasks
        active_tasks = [task_info for task_info in active_tasks if task_info['remaining'] > 0]
        
        # Sort by priority based on algorithm
        if algorithm == 'DM':
            # Deadline Monotonic - shortest deadline first
            active_tasks.sort(key=lambda x: x['task'].deadline)
        else:
            # Rate Monotonic - shortest period first
            active_tasks.sort(key=lambda x: x['task'].period)
        
        # Execute highest priority task with remaining execution time
        if active_tasks:
            executing_task = active_tasks[0]
            execution_timeline[t] = executing_task['task']
            
            # Check if current execution is past the deadline
            if t >= executing_task['absolute_deadline']:
                deadline_violations[t] = True
            
            executing_task['remaining'] -= 1
    
    # Define an extended color palette for many tasks
    task_colors = [
        '#4ECDC4',  # Teal
        '#FF6B6B',  # Red
        '#FFD700',  # Yellow
        '#95E1D3',  # Mint
        '#F38BA8',  # Pink
        '#A8DADC',  # Light Blue
        '#457B9D',  # Steel Blue
        '#1D3557',  # Navy
        '#F1FAEE',  # Off White
        '#E63946',  # Red variant
        '#2A9D8F',  # Teal variant
        '#E9C46A',  # Yellow variant
        '#F4A261',  # Orange
        '#E76F51',  # Orange Red
        '#264653',  # Dark Green
        '#287271',  # Dark Teal
        '#F77F00',  # Orange variant
        '#FCBF49',  # Light Orange
        '#003049',  # Dark Blue
        '#669BBC'   # Blue variant
    ]
    
    # Collect all period and deadline releases for colored tick marks
    all_periods = set()
    all_deadlines = set()
    
    for task in tasks_sorted:
        # Collect period releases
        period_releases = np.arange(0, time_range + 1, task.period)
        all_periods.update(period_releases)
        
        # Collect deadline occurrences
        for release_time in period_releases:
            deadline_time = release_time + task.deadline
            if deadline_time <= time_range:
                all_deadlines.add(deadline_time)
    
    return execution_timeline, tasks_sorted, time_range, title, all_periods, all_deadlines, task_colors, deadline_violations

def _create_plot(execution_timeline, tasks, time_range, title, all_periods, all_deadlines, task_colors, deadline_violations, algorithm='DM'):
    """
    Create the actual matplotlib plot with all the visualization elements.
    
    Returns:
        tuple: (fig, ax) - matplotlib figure and axes objects
    """
    # Plot schedule with timeline-based visualization
    fig, ax = plt.subplots(figsize=(16, 8))  # Increased height for better readability
    
    # Create timeline visualization
    y_positions = []
    task_labels = []
    
    # Plot each task on its own timeline
    for i, task in enumerate(tasks):
        y_pos = len(tasks) - i + 1.0  # Increased spacing and positioning
        y_positions.append(y_pos)
        
        # Task label with more details (positioned at the top)
        actual_priority = i + 1  # Priority 1 = highest (shortest deadline for DM, shortest period for RM)
        if algorithm == 'DM':
            label = f"Task T{i+1}: Period={task.period}, Exec={task.execution_time}, Deadline={task.deadline}, Priority={actual_priority} (DM)"
        else:
            label = f"Task T{i+1}: Period={task.period}, Exec={task.execution_time}, Deadline={task.deadline}, Priority={actual_priority} (RM)"
        task_labels.append(label)
        
        # Plot the timeline background (thinner bars) - positioned higher
        ax.barh(y_pos, time_range, left=0, height=0.8, 
                color='white', edgecolor='black', linewidth=1)
        
        # Plot task releases and deadlines with colored vertical lines on this task's timeline
        releases = np.arange(0, time_range + 1, task.period)
        for release in releases:
            if release <= time_range:
                # Period release - draw in blue (unless deadline equals period)
                if task.deadline == task.period:
                    # If deadline equals period, draw only red line spanning this task's timeline
                    ax.plot([release, release], [y_pos - 0.4, y_pos + 0.4], 
                           color='red', linewidth=2, solid_capstyle='butt')
                else:
                    # Draw blue line for period spanning this task's timeline
                    ax.plot([release, release], [y_pos - 0.4, y_pos + 0.4], 
                           color='blue', linewidth=2, solid_capstyle='butt')
                    
                    # Draw red line for deadline on this task's timeline if within time range
                    deadline_time = release + task.deadline
                    if deadline_time <= time_range:
                        ax.plot([deadline_time, deadline_time], [y_pos - 0.4, y_pos + 0.4], 
                               color='red', linewidth=2, solid_capstyle='butt')
        
        # Plot execution blocks with color cycling and pattern support
        start_time = None
        for t in range(time_range):
            if execution_timeline[t] == task:
                if start_time is None:
                    start_time = t
            elif start_time is not None:
                # Get color for this task (cycle through available colors)
                color = task_colors[i % len(task_colors)]
                # Add hatching pattern for tasks beyond the base color set to improve distinction
                hatch_pattern = None
                if i >= len(task_colors):
                    # Use different hatch patterns for tasks that repeat colors
                    hatch_patterns = ['///', '\\\\\\', '|||', '---', '+++', 'xxx', 'ooo', '...']
                    hatch_pattern = hatch_patterns[(i // len(task_colors)) % len(hatch_patterns)]
                
                # Check if any execution in this block violates deadline
                has_deadline_violation = any(deadline_violations[time_slot] for time_slot in range(start_time, t))
                
                # Multiple highlighting methods for deadline violations
                if has_deadline_violation:
                    # Method 1: Thick black border with white inner border for high contrast
                    edge_color = 'black'
                    line_width = 3.0
                    
                    # Method 2: Add diagonal cross-hatch pattern specifically for violations
                    if hatch_pattern is None:
                        hatch_pattern = 'xxx'  # Cross-hatch for violations
                    else:
                        hatch_pattern = hatch_pattern + 'xxx'  # Combine existing pattern with violation marker
                    
                    # Method 3: Reduce alpha slightly to make violation blocks more distinct
                    alpha_value = 0.8
                else:
                    edge_color = 'black'
                    line_width = 0.5
                    alpha_value = 0.9
                
                # Execution block
                ax.barh(y_pos, t - start_time, left=start_time,
                       height=0.6, color=color, hatch=hatch_pattern,
                       alpha=alpha_value, edgecolor=edge_color, linewidth=line_width)
                
                # Method 4: Add a red warning stripe overlay for deadline violations
                if has_deadline_violation:
                    # Add thin red stripe at the top of the execution block
                    ax.barh(y_pos + 0.25, t - start_time, left=start_time,
                           height=0.1, color='red', alpha=0.9, edgecolor='darkred', linewidth=1)
                start_time = None
        
        # Handle case where task runs until the end
        if start_time is not None:
            color = task_colors[i % len(task_colors)]
            hatch_pattern = None
            if i >= len(task_colors):
                hatch_patterns = ['///', '\\\\\\', '|||', '---', '+++', 'xxx', 'ooo', '...']
                hatch_pattern = hatch_patterns[(i // len(task_colors)) % len(hatch_patterns)]
            
            # Check if any execution in this final block violates deadline
            has_deadline_violation = any(deadline_violations[time_slot] for time_slot in range(start_time, time_range))
            
            # Multiple highlighting methods for deadline violations
            if has_deadline_violation:
                # Method 1: Thick black border with white inner border for high contrast
                edge_color = 'black'
                line_width = 3.0
                
                # Method 2: Add diagonal cross-hatch pattern specifically for violations
                if hatch_pattern is None:
                    hatch_pattern = 'xxx'  # Cross-hatch for violations
                else:
                    hatch_pattern = hatch_pattern + 'xxx'  # Combine existing pattern with violation marker
                
                # Method 3: Reduce alpha slightly to make violation blocks more distinct
                alpha_value = 0.8
            else:
                edge_color = 'black'
                line_width = 0.5
                alpha_value = 0.9
            
            ax.barh(y_pos, time_range - start_time, left=start_time,
                   height=0.6, color=color, hatch=hatch_pattern,
                   alpha=alpha_value, edgecolor=edge_color, linewidth=line_width)
            
            # Method 4: Add a red warning stripe overlay for deadline violations
            if has_deadline_violation:
                # Add thin red stripe at the top of the execution block
                ax.barh(y_pos + 0.25, time_range - start_time, left=start_time,
                       height=0.1, color='red', alpha=0.9, edgecolor='darkred', linewidth=1)
    
    # Add processor timeline at bottom
    proc_y_pos = 0.5
    ax.barh(proc_y_pos, time_range, left=0, height=0.8, 
            color='lightgray', edgecolor='black', linewidth=1)
    
    # Create processor execution timeline with improved color distinction
    for t in range(time_range):
        if execution_timeline[t] is not None:
            task_idx = tasks.index(execution_timeline[t])
            color = task_colors[task_idx % len(task_colors)]
            hatch_pattern = None
            if task_idx >= len(task_colors):
                hatch_patterns = ['///', '\\\\\\', '|||', '---', '+++', 'xxx', 'ooo', '...']
                hatch_pattern = hatch_patterns[(task_idx // len(task_colors)) % len(hatch_patterns)]
            
            ax.barh(proc_y_pos, 1, left=t, height=0.6, 
                   color=color, hatch=hatch_pattern,
                   alpha=0.9, edgecolor='black', linewidth=0.3)
    
    # Customize the plot
    has_violations = any(deadline_violations)
    violation_note = " (Cross-hatch pattern + red stripe + thick border = deadline violations)" if has_violations else ""
    ax.set_title(title + violation_note, fontsize=14, fontweight='bold')
    ax.set_xlabel('Time', fontsize=12)
    ax.set_ylabel('')
    
    # Position y-axis labels at the top of the plot
    top_y_position = len(tasks) + 2.5  # Position at top of plot
    label_positions = [top_y_position + (i * 0.25) for i in range(len(task_labels))] + [top_y_position + (len(task_labels) * 0.25)]
    all_labels = task_labels + [f"Processor: {algorithm}_PROTOCOL, PREEMPTIVE"]
    ax.set_yticks(label_positions)
    ax.set_yticklabels(all_labels, fontsize=9, ha='left', va='bottom')
    
    # Set axis limits with space for top labels
    ax.set_xlim(0, time_range)
    ax.set_ylim(0, len(tasks) + 3.5)
    
    # Create custom time ticks with better spacing to avoid overlap
    # Adaptive tick interval based on time range and figure width
    if time_range <= 30:
        tick_interval = 2
    elif time_range <= 60:
        tick_interval = 4
    elif time_range <= 120:
        tick_interval = 6
    elif time_range <= 240:
        tick_interval = 10
    else:
        tick_interval = max(10, time_range // 20)  # Ensure reasonable spacing for very long ranges
    
    regular_ticks = np.arange(0, time_range + 1, tick_interval)
    period_ticks = sorted(list(all_periods))
    deadline_ticks = sorted(list(all_deadlines))
    
    # Determine which periods have deadlines equal to periods
    period_equals_deadline = set()
    for task in tasks:
        if task.deadline == task.period:
            period_releases = np.arange(0, time_range + 1, task.period)
            period_equals_deadline.update(period_releases)
    
    # Set all ticks with smart filtering to avoid overcrowding
    important_ticks = set(period_ticks) | set(deadline_ticks)
    all_ticks = sorted(list(set(regular_ticks) | important_ticks))
    
    # Intelligent filtering to prevent overlapping labels
    filtered_ticks = []
    min_spacing = max(3, time_range // 30)  # Minimum spacing between ticks
    
    for tick in all_ticks:
        if tick in important_ticks:
            # Always include important ticks (periods/deadlines) but check spacing
            if not filtered_ticks or abs(tick - filtered_ticks[-1]) >= min_spacing:
                filtered_ticks.append(tick)
            elif tick == 0 or tick == time_range:
                # Always include start and end points
                filtered_ticks.append(tick)
        else:
            # For regular ticks, ensure minimum spacing from any existing tick
            if not filtered_ticks or min([abs(tick - existing) for existing in filtered_ticks]) >= min_spacing:
                filtered_ticks.append(tick)
    
    # Ensure we don't have too many ticks (max 25 ticks for readability)
    if len(filtered_ticks) > 25:
        # Keep every nth tick, but always keep important ones
        step = len(filtered_ticks) // 20
        final_ticks = []
        for i, tick in enumerate(filtered_ticks):
            if i % step == 0 or tick in important_ticks or tick == 0 or tick == time_range:
                final_ticks.append(tick)
        filtered_ticks = sorted(list(set(final_ticks)))
    
    ax.set_xticks(filtered_ticks)
    
    # Color the tick labels - red for deadlines, blue for periods, red if they're equal, black for others
    tick_labels = []
    tick_colors = []
    for tick in filtered_ticks:
        tick_labels.append(f"{int(tick)}")  # Use integer labels for cleaner appearance
        
        if tick in period_equals_deadline:
            # If any task has deadline == period at this time, use red
            tick_colors.append('red')
        elif tick in deadline_ticks and tick in period_ticks:
            # If both deadline and period occur at same time (but not equal), prioritize red for deadline
            tick_colors.append('red')
        elif tick in deadline_ticks:
            # Deadline only - red
            tick_colors.append('red')
        elif tick in period_ticks:
            # Period only - blue
            tick_colors.append('blue')
        else:
            # Regular tick - black
            tick_colors.append('black')
    
    ax.set_xticklabels(tick_labels, fontsize=9, rotation=45 if len(filtered_ticks) > 15 else 0)  # Rotate labels if many ticks
    
    # Color individual tick labels
    for tick_label, color in zip(ax.get_xticklabels(), tick_colors):
        tick_label.set_color(color)
        if color in ['red', 'blue']:
            tick_label.set_fontweight('bold')
    
    # Add slightly more visible grid
    ax.grid(True, alpha=0.4, axis='x', which='major', linestyle='-', linewidth=0.5)
    
    # Position x-axis at the bottom like in reference images
    ax.spines['bottom'].set_position(('axes', 0.0))
    ax.spines['top'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.xaxis.set_ticks_position('bottom')
    
    return fig, ax

def plot_rm_schedule(tasks, lcm_cycles=1, filename=None, algorithm='DM', output_dir='output'):
    """
    Generate and save a scheduling plot to file.
    
    Args:
        tasks: List of Task objects
        lcm_cycles: Number of LCM cycles to simulate
        filename: Custom filename (without path). If None, auto-generates based on task periods
        algorithm: 'DM' for Deadline Monotonic or 'RM' for Rate Monotonic
        output_dir: Directory to save output files (default: 'output')
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate default filename based on task set characteristics if none provided
    if filename is None:
        periods = [task.period for task in tasks]
        periods_str = "_".join(map(str, sorted(periods)))
        filename = f"rm_schedule_tasks_{periods_str}.png"
    
    # Ensure filename has .png extension
    if not filename.endswith('.png'):
        filename += '.png'
    
    # Combine output directory with filename
    full_path = os.path.join(output_dir, filename)
    
    # Generate scheduling data
    execution_timeline, tasks_sorted, time_range, title, all_periods, all_deadlines, task_colors, deadline_violations = _generate_schedule_data(tasks, lcm_cycles, algorithm)
    
    # Create the plot
    fig, ax = _create_plot(execution_timeline, tasks_sorted, time_range, title, all_periods, all_deadlines, task_colors, deadline_violations, algorithm)
    
    plt.tight_layout()
    plt.savefig(full_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"Plot saved to: {full_path}")
    return full_path
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    plt.close()

def plot_rm_schedule_inline(tasks, lcm_cycles=1, algorithm='DM'):
    """
    Generate and display a scheduling plot inline for Jupyter notebooks.
    Returns the plot without saving to file.
    """
    # Clear any existing plots
    plt.close('all')
    
    # Generate scheduling data
    execution_timeline, tasks_sorted, time_range, title, all_periods, all_deadlines, task_colors, deadline_violations = _generate_schedule_data(tasks, lcm_cycles, algorithm)
    
    # Create the plot
    fig, ax = _create_plot(execution_timeline, tasks_sorted, time_range, title, all_periods, all_deadlines, task_colors, deadline_violations, algorithm)
    
    plt.tight_layout()
    plt.show()
    return fig

def create_test_task_set(num_tasks, base_period=6):
    """
    Create a test task set with the specified number of tasks.
    
    Args:
        num_tasks: Number of tasks to create
        base_period: Base period for the first task (others will be multiples)
    
    Returns:
        List of Task objects
    """
    tasks = []
    for i in range(num_tasks):
        period = base_period + (i * 4)  # Periods: 6, 10, 14, 18, 22, ...
        deadline = period - 1           # Deadline is one less than period
        execution_time = max(1, period // 6)  # Execution time scales with period
        
        task = rtm.Task(period=period, deadline=deadline, execution_time=execution_time)
        tasks.append(task)
    
    return tasks

def main():
    # Define Task Sets with Progressive Difficulty (D ≠ T)
    # Task Set 1: Easy case - schedulable with all methods
    task_set_1 = [
        rtm.Task(period=8,  deadline=6,  execution_time=2),   # D < T, Utilization: 0.25
        rtm.Task(period=12, deadline=10, execution_time=3),   # D < T, Utilization: 0.25
        rtm.Task(period=20, deadline=18, execution_time=4)    # D < T, Utilization: 0.20
    ]
    # Total utilization: 0.70 (moderate utilization, tight deadlines)
    
    # Task Set 2: Medium case - fails sufficient condition 1, passes 2 and 3
    task_set_2 = [
        rtm.Task(period=6,  deadline=4,  execution_time=1),   # D < T, High priority
        rtm.Task(period=10, deadline=8,  execution_time=3),   # D < T, Medium priority
        rtm.Task(period=15, deadline=12, execution_time=4)    # D < T, Low priority
    ]
    # Total utilization: 0.73 (reasonable utilization but tight deadlines)
    
    # Task Set 3: Hard case - only schedulable with exact response time analysis
    task_set_3 = [
        rtm.Task(period=7,  deadline=5,  execution_time=2),   # D < T, Very tight deadline
        rtm.Task(period=14, deadline=10, execution_time=4),   # D < T, Tight deadline
        rtm.Task(period=21, deadline=15, execution_time=6)    # D < T, Tight deadline
    ]
    
    # Task Set 4: Extended case with 6 tasks to test color cycling and patterns
    task_set_extended = [
        rtm.Task(period=6,  deadline=5,  execution_time=1),   # Task 1
        rtm.Task(period=8,  deadline=7,  execution_time=1),   # Task 2
        rtm.Task(period=12, deadline=10, execution_time=2),   # Task 3
        rtm.Task(period=16, deadline=14, execution_time=2),   # Task 4
        rtm.Task(period=20, deadline=18, execution_time=3),   # Task 5
        rtm.Task(period=24, deadline=22, execution_time=3)    # Task 6
    ]
    
    # Task Set 5: Deadline violation case - intentionally unschedulable to test red borders
    task_set_deadline_violations = [
        rtm.Task(period=6,  deadline=3,  execution_time=2),   # Very tight deadline
        rtm.Task(period=8,  deadline=4,  execution_time=3),   # Very tight deadline  
        rtm.Task(period=12, deadline=6,  execution_time=4)    # Very tight deadline
    ]
    # This set has high utilization with very tight deadlines that will cause violations
    
    plot_rm_schedule(tasks=task_set_1, lcm_cycles=1, filename="task_set_1")  
    plot_rm_schedule(tasks=task_set_2, lcm_cycles=1, filename="task_set_2")  
    plot_rm_schedule(tasks=task_set_3, lcm_cycles=1, filename="task_set_3")
    plot_rm_schedule(tasks=task_set_extended, lcm_cycles=1, filename="task_set_extended")
    plot_rm_schedule(tasks=task_set_deadline_violations, lcm_cycles=1, filename="task_set_deadline_violations")
    
    # Example of using custom output directory and filename
    # plot_rm_schedule(task_set_1, filename="custom_schedule.png", output_dir="custom_output")

def demo_output_directories():
    """
    Demonstrate using different output directories for organized file management.
    """
    # Create a simple test task set
    test_tasks = [
        rtm.Task(period=6, deadline=5, execution_time=1),
        rtm.Task(period=10, deadline=9, execution_time=2)
    ]
    
    # Save to default output directory
    plot_rm_schedule(test_tasks, filename="demo_default")
    
    # Save to custom output directory
    plot_rm_schedule(test_tasks, filename="demo_custom", output_dir="results")
    
    # Save with algorithm-specific directory
    plot_rm_schedule(test_tasks, filename="demo_dm", output_dir="output/deadline_monotonic", algorithm='DM')
    plot_rm_schedule(test_tasks, filename="demo_rm", output_dir="output/rate_monotonic", algorithm='RM')
    
    print("Demo files created in various output directories!")

if __name__ == "__main__":
    main()
    # Uncomment to run demo
    # demo_output_directories()