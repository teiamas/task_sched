# Test script to create a more precise visualization
import matplotlib.pyplot as plt
import rate_monotonic as rtm
import task_schedule_visualizer as tsv

# Create task set
task_set_1 = [
    rtm.Task(period= 5,  deadline=5, execution_time=1),
    rtm.Task(period= 7, deadline= 7, execution_time=2),
    rtm.Task(period=10, deadline=10, execution_time=2),
    rtm.Task(period=14, deadline=14, execution_time=4) 
]

# Generate schedule data
execution_timeline, tasks_sorted, time_range, title, all_periods, all_deadlines, task_colors, deadline_violations = tsv._generate_schedule_data(task_set_1, 1, 'RM')

# Create a custom plot focusing on the violation area
fig, ax = plt.subplots(figsize=(12, 3))

# Focus on Task 4 (index 3) and time range 14-20
task_4 = task_set_1[3]
y_pos = 1

# Draw individual time units for Task 4 around the violation
for t in range(14, 21):
    if execution_timeline[t] == task_4:
        is_violation = deadline_violations[t]
        
        if is_violation:
            # Violation: red with cross-hatch
            color = 'red'
            hatch = 'xxx'
            alpha = 0.8
        else:
            # Normal: light green
            color = 'lightgreen'
            hatch = None
            alpha = 0.9
            
        # Draw individual time unit
        ax.barh(y_pos, 1, left=t, height=0.6, 
               color=color, hatch=hatch, alpha=alpha, 
               edgecolor='black', linewidth=1)
        
        # Add time label
        ax.text(t+0.5, y_pos, str(t), ha='center', va='center', fontsize=8)

ax.set_xlim(13, 21)
ax.set_ylim(0.5, 1.5)
ax.set_xlabel('Time')
ax.set_title('Task 4 Execution Detail (Individual Time Units)')
ax.set_yticks([y_pos])
ax.set_yticklabels(['Task 4'])
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('task4_violation_detail.png', dpi=150, bbox_inches='tight')
plt.show()

print("Detailed Task 4 execution visualization saved as 'task4_violation_detail.png'")
print("\nViolation analysis:")
for t in range(14, 21):
    if execution_timeline[t] == task_4:
        print(f"Time {t}: Task 4 executing, Violation = {deadline_violations[t]}")
