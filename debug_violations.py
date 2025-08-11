# Test script to debug deadline violation detection
import rate_monotonic as rtm
import task_schedule_visualizer as tsv

print("Starting debug script...")

# Create the same task set from the notebook
task_set_1 = [
    rtm.Task(period= 5,  deadline=5, execution_time=1),
    rtm.Task(period= 7, deadline= 7, execution_time=2),
    rtm.Task(period=10, deadline=10, execution_time=2),
    rtm.Task(period=14, deadline=14, execution_time=4) 
]

print("Task set created:", len(task_set_1), "tasks")

# Generate schedule data to examine violations
try:
    execution_timeline, tasks_sorted, time_range, title, all_periods, all_deadlines, task_colors, deadline_violations = tsv._generate_schedule_data(task_set_1, 1, 'RM')
    print("Schedule data generated successfully")
    print("Time range:", time_range)
    print("Number of violations:", sum(deadline_violations))
except Exception as e:
    print("Error generating schedule:", e)
    exit()

# Print execution timeline and violations for analysis
print("\nTime Analysis for Task 4 (Period=14, Deadline=14, Exec=4):")
print("=" * 60)

# Focus on time range around Task 4's executions
for t in range(70):
    current_task = execution_timeline[t]
    violation = deadline_violations[t]
    
    if current_task and current_task.period == 14:  # Task 4
        print(f"Time {t:2d}: Task 4 executing, Violation: {violation}")
        
        # Calculate which instance this is
        instance = t // 14
        release_time = instance * 14
        absolute_deadline = release_time + 14
        print(f"         Instance {instance}, Released at {release_time}, Deadline at {absolute_deadline}")
        print()

print("\nDeadline Violations Array (first 30 time units):")
for i in range(min(30, len(deadline_violations))):
    if deadline_violations[i]:
        task = execution_timeline[i]
        task_name = f"T{task_set_1.index(task)+1}" if task else "None"
        print(f"Time {i:2d}: VIOLATION - Task {task_name}")
