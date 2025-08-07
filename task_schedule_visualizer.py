import matplotlib.pyplot as plt
import numpy as np
import rate_monotonic as rtm

def plot_rm_schedule(tasks, lcm_cycles=1, filename=None, algorithm='DM'):
    # Generate default filename based on task set characteristics if none provided
    if filename is None:
        periods = [task.period for task in tasks]
        periods_str = "_".join(map(str, sorted(periods)))
        filename = f"rm_schedule_tasks_{periods_str}.png"
    
    # Calculate LCM of all periods
    lcm = np.lcm.reduce([task.period for task in tasks])
    time_range = lcm * lcm_cycles
    
    # Sort tasks by priority based on algorithm
    if algorithm == 'DM':
        # Deadline Monotonic - shorter deadline = higher priority
        tasks = sorted(tasks, key=lambda x: x.deadline)
        title = 'Deadline Monotonic Preemptive Schedule'
        priority_key = 'deadline'
    else:
        # Rate Monotonic - shorter period = higher priority
        tasks = sorted(tasks, key=lambda x: x.period)
        title = 'Rate Monotonic Preemptive Schedule'
        priority_key = 'period'
    
    # Create execution timeline
    execution_timeline = [None] * time_range
    
    # Track active task instances
    active_tasks = []
    
    # Simulate schedule
    for t in range(time_range):
        # Add new task releases
        for task in tasks:
            if t % task.period == 0:
                active_tasks.append({
                    'task': task,
                    'remaining': task.execution_time,
                    'release_time': t
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
            executing_task['remaining'] -= 1
    
    # Plot schedule with timeline-based visualization
    fig, ax = plt.subplots(figsize=(16, 8))  # Increased height for better readability
    
    # Define colors similar to reference image
    task_colors = ['#4ECDC4', '#FF6B6B', '#FFD700']  # Teal, Red, Yellow to match reference order
    
    # Create timeline visualization
    y_positions = []
    task_labels = []
    
    # Collect all period and deadline releases for colored tick marks
    all_periods = set()
    all_deadlines = set()
    
    for task in tasks:
        # Collect period releases
        period_releases = np.arange(0, time_range + 1, task.period)
        all_periods.update(period_releases)
        
        # Collect deadline occurrences
        for release_time in period_releases:
            deadline_time = release_time + task.deadline
            if deadline_time <= time_range:
                all_deadlines.add(deadline_time)
    
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
        
        # Plot execution blocks
        start_time = None
        for t in range(time_range):
            if execution_timeline[t] == task:
                if start_time is None:
                    start_time = t
            elif start_time is not None:
                # Execution block
                ax.barh(y_pos, t - start_time, left=start_time,
                       height=0.6, color=task_colors[i % len(task_colors)], 
                       alpha=0.9, edgecolor='black', linewidth=0.5)
                start_time = None
        
        # Handle case where task runs until the end
        if start_time is not None:
            ax.barh(y_pos, time_range - start_time, left=start_time,
                   height=0.6, color=task_colors[i % len(task_colors)], 
                   alpha=0.9, edgecolor='black', linewidth=0.5)
    
    # Add processor timeline at bottom
    proc_y_pos = 0.5
    ax.barh(proc_y_pos, time_range, left=0, height=0.8, 
            color='lightgray', edgecolor='black', linewidth=1)
    
    # Create processor execution timeline
    for t in range(time_range):
        if execution_timeline[t] is not None:
            task_idx = tasks.index(execution_timeline[t])
            ax.barh(proc_y_pos, 1, left=t, height=0.6, 
                   color=task_colors[task_idx % len(task_colors)], 
                   alpha=0.9, edgecolor='black', linewidth=0.3)
    
    # Customize the plot
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.set_xlabel('Time', fontsize=12)
    ax.set_ylabel('')
    
    # Position y-axis labels at the top of the plot
    top_y_position = len(tasks) + 2.5  # Position at top of plot
    label_positions = [top_y_position + (i * 0.25) for i in range(len(task_labels))] + [top_y_position + (len(task_labels) * 0.25)]
    all_labels = task_labels + ["Processor: DEADLINE_MONOTONIC_PROTOCOL, PREEMPTIVE"]
    ax.set_yticks(label_positions)
    ax.set_yticklabels(all_labels, fontsize=9, ha='left', va='bottom')
    
    # Set axis limits with space for top labels
    ax.set_xlim(0, time_range)
    ax.set_ylim(0, len(tasks) + 3.5)
    
    # Create custom time ticks with better spacing to avoid overlap
    # Reduce the number of regular ticks based on time range
    tick_interval = max(2, time_range // 15)  # Ensure reasonable spacing
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
    
    # Filter out regular ticks that are too close to important ticks
    filtered_ticks = []
    for tick in all_ticks:
        if tick in important_ticks:
            filtered_ticks.append(tick)
        else:
            # Only add regular tick if it's not too close to important ticks
            min_distance = min([abs(tick - imp_tick) for imp_tick in important_ticks] + [float('inf')])
            if min_distance >= tick_interval * 0.8:
                filtered_ticks.append(tick)
    
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
    
    ax.set_xticklabels(tick_labels, fontsize=10)
    
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
    
    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    plt.close()

def plot_rm_schedule_inline(tasks, lcm_cycles=1, algorithm='DM'):
    """
    Generate and display a scheduling plot inline for Jupyter notebooks.
    Returns the plot without saving to file.
    """
    # Clear any existing plots
    plt.close('all')
    
    # Calculate LCM of all periods
    lcm = np.lcm.reduce([task.period for task in tasks])
    time_range = lcm * lcm_cycles
    
    # Sort tasks by priority based on algorithm
    if algorithm == 'DM':
        # Deadline Monotonic - shorter deadline = higher priority
        tasks = sorted(tasks, key=lambda x: x.deadline)
        title = 'Deadline Monotonic Preemptive Schedule'
    else:
        # Rate Monotonic - shorter period = higher priority
        tasks = sorted(tasks, key=lambda x: x.period)
        title = 'Rate Monotonic Preemptive Schedule'
    
    # Create execution timeline
    execution_timeline = [None] * time_range
    
    # Track active task instances
    active_tasks = []
    
    # Simulate schedule
    for t in range(time_range):
        # Add new task releases
        for task in tasks:
            if t % task.period == 0:
                active_tasks.append({
                    'task': task,
                    'remaining': task.execution_time,
                    'release_time': t
                })
        
        # Remove completed tasks
        active_tasks = [task_info for task_info in active_tasks if task_info['remaining'] > 0]
        
        # Sort by priority based on algorithm
        if algorithm == 'DM':
            active_tasks.sort(key=lambda x: x['task'].deadline)
        else:
            active_tasks.sort(key=lambda x: x['task'].period)
        
        # Execute highest priority task with remaining execution time
        if active_tasks:
            executing_task = active_tasks[0]
            execution_timeline[t] = executing_task['task']
            executing_task['remaining'] -= 1
    
    # Plot schedule with timeline-based visualization
    fig, ax = plt.subplots(figsize=(16, 8))
    
    # Define colors
    task_colors = ['#4ECDC4', '#FF6B6B', '#FFD700']
    
    # Create timeline visualization
    y_positions = []
    task_labels = []
    
    # Collect all period and deadline releases for colored tick marks
    all_periods = set()
    all_deadlines = set()
    
    for task in tasks:
        period_releases = np.arange(0, time_range + 1, task.period)
        all_periods.update(period_releases)
        
        for release_time in period_releases:
            deadline_time = release_time + task.deadline
            if deadline_time <= time_range:
                all_deadlines.add(deadline_time)
    
    # Plot each task on its own timeline
    for i, task in enumerate(tasks):
        y_pos = len(tasks) - i + 1.0
        y_positions.append(y_pos)
        
        # Task label
        actual_priority = i + 1
        if algorithm == 'DM':
            label = f"Task T{i+1}: Period={task.period}, Exec={task.execution_time}, Deadline={task.deadline}, Priority={actual_priority} (DM)"
        else:
            label = f"Task T{i+1}: Period={task.period}, Exec={task.execution_time}, Deadline={task.deadline}, Priority={actual_priority} (RM)"
        task_labels.append(label)
        
        # Plot timeline background
        ax.barh(y_pos, time_range, left=0, height=0.8, 
                color='white', edgecolor='black', linewidth=1)
        
        # Plot task releases and deadlines
        releases = np.arange(0, time_range + 1, task.period)
        for release in releases:
            if release <= time_range:
                if task.deadline == task.period:
                    ax.plot([release, release], [y_pos - 0.4, y_pos + 0.4], 
                           color='red', linewidth=2, solid_capstyle='butt')
                else:
                    ax.plot([release, release], [y_pos - 0.4, y_pos + 0.4], 
                           color='blue', linewidth=2, solid_capstyle='butt')
                    
                    deadline_time = release + task.deadline
                    if deadline_time <= time_range:
                        ax.plot([deadline_time, deadline_time], [y_pos - 0.4, y_pos + 0.4], 
                               color='red', linewidth=2, solid_capstyle='butt')
        
        # Plot execution blocks
        start_time = None
        for t in range(time_range):
            if execution_timeline[t] == task:
                if start_time is None:
                    start_time = t
            elif start_time is not None:
                ax.barh(y_pos, t - start_time, left=start_time,
                       height=0.6, color=task_colors[i % len(task_colors)], 
                       alpha=0.9, edgecolor='black', linewidth=0.5)
                start_time = None
        
        if start_time is not None:
            ax.barh(y_pos, time_range - start_time, left=start_time,
                   height=0.6, color=task_colors[i % len(task_colors)], 
                   alpha=0.9, edgecolor='black', linewidth=0.5)
    
    # Add processor timeline
    proc_y_pos = 0.5
    ax.barh(proc_y_pos, time_range, left=0, height=0.8, 
            color='lightgray', edgecolor='black', linewidth=1)
    
    for t in range(time_range):
        if execution_timeline[t] is not None:
            task_idx = tasks.index(execution_timeline[t])
            ax.barh(proc_y_pos, 1, left=t, height=0.6, 
                   color=task_colors[task_idx % len(task_colors)], 
                   alpha=0.9, edgecolor='black', linewidth=0.3)
    
    # Customize plot
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.set_xlabel('Time', fontsize=12)
    ax.set_ylabel('')
    
    # Position labels at top
    top_y_position = len(tasks) + 2.5
    label_positions = [top_y_position + (i * 0.25) for i in range(len(task_labels))] + [top_y_position + (len(task_labels) * 0.25)]
    all_labels = task_labels + [f"Processor: {algorithm}_PROTOCOL, PREEMPTIVE"]
    ax.set_yticks(label_positions)
    ax.set_yticklabels(all_labels, fontsize=9, ha='left', va='bottom')
    
    # Set limits and grid
    ax.set_xlim(0, time_range)
    ax.set_ylim(0, len(tasks) + 3.5)
    ax.grid(True, alpha=0.4, axis='x', which='major', linestyle='-', linewidth=0.5)
    
    # Style axes
    ax.spines['bottom'].set_position(('axes', 0.0))
    ax.spines['top'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.xaxis.set_ticks_position('bottom')
    
    plt.tight_layout()
    plt.show()
    return fig

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
    plot_rm_schedule(tasks=task_set_1,lcm_cycles=1,filename="task_set_1")  
    plot_rm_schedule(tasks=task_set_2,lcm_cycles=1,filename="task_set_2")  
    plot_rm_schedule(tasks=task_set_3,lcm_cycles=1,filename="task_set_3")  
    
    # Example of using custom filename
    # plot_rm_schedule(task_set_1, filename="custom_schedule.png")

if __name__ == "__main__":
    main()