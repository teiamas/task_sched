import numpy as np
import pandas as pd
from   IPython.display import display, Markdown


class Task:
    def __init__(self, period, execution_time, deadline=None, priority=None):
        self.period = period
        self.execution_time = execution_time
        self.deadline = deadline if deadline else period
        self.priority = priority



def rate_monotonic_check(task_set, verbose=False):
    """
    Check if a set of periodic tasks is schedulable using Rate Monotonic Scheduling
    """
    n = len(task_set)
    utilization = sum(task.execution_time / task.deadline for task in task_set)
    # Utilization bound for RM scheduling
    bound = n * (2 ** (1/n) - 1)
    # Summary information
    schedulable = utilization <= bound
    
    if verbose:
        # Prepare data for the table
        table_data = []
        for idx, task in enumerate(task_set):
            task_utilization = task.execution_time / task.deadline
            table_data.append({
                'Task': f'T{idx+1}',
                'Execution Time (C)': task.execution_time,
                'Period (T)': task.period,
                'Deadline (D)': task.deadline,
                'Utilization (C/T)': f'{task_utilization:.3f}'
            })
        
        # Create DataFrame
        df = pd.DataFrame(table_data)
        
        # Display the table
        print("Rate Monotonic Schedulability Analysis")
        print("=" * 50)
        display(df)
        
        
        summary_data = {
            'Metric': ['Number of Tasks', 'Total Utilization', 'RM Bound', 'Schedulable'],
            'Value': [n, f'{utilization:.3f}', f'{bound:.3f}', '✓ Yes' if schedulable else '✗ No']
        }
        
        summary_df = pd.DataFrame(summary_data)
        print("\nSummary:")
        display(summary_df)
           
    return schedulable

def response_time_analysis(tasks):
    """
    Perform response time analysis for a set of periodic tasks
    tasks should be ordered by priority (highest first)
    """
    n = len(tasks)
    response_times = []
    
    for i in range(n):
        # Initial response time is task's execution time
        r_new = tasks[i].execution_time
        
        while True:
            r_old = r_new
            interference = 0
            
            # Calculate interference from higher priority tasks
            for j in range(i):
                interference += np.ceil(r_old / tasks[j].period) * tasks[j].execution_time
            
            r_new = tasks[i].execution_time + interference
            
            # Check for convergence or unschedulability
            if r_new > tasks[i].deadline:
                return False, response_times + [float('inf')]
            if r_new == r_old:
                response_times.append(r_new)
                break
                
    return True, response_times

def display_response_time_table(tasks, response_times, schedulable):
    """Display response time analysis in a formatted table using pandas"""
    
    # Prepare data for the table
    table_data = []
    for i, (task, resp_time) in enumerate(zip(tasks, response_times)):
        utilization = task.execution_time / task.deadline
        schedulable_status = "✓" if resp_time <= task.deadline else "✗"
        
        table_data.append({
            'Task': f'T{i+1}',
            'Period (T)': task.period,
            'Execution (C)': task.execution_time,
            'Deadline (D)': task.deadline,
            'Utilization': f'{utilization:.3f}',
            'Response Time (R)': f'{resp_time:.1f}' if resp_time != float('inf') else '∞',
            'R ≤ D': schedulable_status,
            'Status': 'Schedulable' if resp_time <= task.deadline else 'Miss Deadline'
        })
    
    # Create DataFrame
    df = pd.DataFrame(table_data)
    
    # Display table
    print("\n" + "="*80)
    print("RESPONSE TIME ANALYSIS RESULTS")
    print("="*80)
    print(df.to_string(index=False))
    print("="*80)
    
    # Summary
    total_utilization = sum(task.execution_time / task.period for task in tasks)
    # Fix the problematic line - use separate loop instead of generator comprehension
    schedulable_count = 0
    for idx, rt in enumerate(response_times):
        if rt <= tasks[idx].deadline:
            schedulable_count += 1
    
    print(f"\nSUMMARY:")
    print(f"Total Utilization: {total_utilization:.3f}")
    print(f"Schedulable Tasks: {schedulable_count}/{len(tasks)}")
    print(f"Overall Status: {'SCHEDULABLE' if schedulable else 'NOT SCHEDULABLE'}")
    print("="*80)

def rate_monotonic_check_1(task_set, verbose=False):
    """
    Check schedulability using response time analysis with deadline-based interference
    Formula: R_i = C_i + sum(h=1 to i-1) ceil(D_i/T_h) * C_h <= D_i
    
    Args:
        task_set: List of Task objects
        verbose: If True, display detailed analysis table
    
    Returns:
        bool: True if schedulable, False otherwise
    """
    # Sort tasks by period (Rate Monotonic priority assignment)
    sorted_tasks = sorted(task_set, key=lambda x: x.period)
    n = len(sorted_tasks)
    
    response_times = []
    all_schedulable = True
    
    # Calculate response time for each task
    for i in range(n):
        task = sorted_tasks[i]
        
        # Start with execution time
        response_time = task.execution_time
        
        # Add interference from higher priority tasks (h = 1 to i-1)
        interference = 0
        for h in range(i):
            higher_priority_task = sorted_tasks[h]
            # Calculate interference: ceil(D_i/T_h) * C_h
            interference += np.ceil(task.deadline / higher_priority_task.period) * higher_priority_task.execution_time
        
        response_time += interference
        response_times.append(response_time)
        
        # Check if this task meets its deadline
        if response_time > task.deadline:
            all_schedulable = False
    
    if verbose:
        # Display detailed analysis table
        _display_deadline_based_analysis(sorted_tasks, response_times, all_schedulable)
    
    return all_schedulable

def _display_deadline_based_analysis(tasks, response_times, schedulable):
    """Display deadline-based response time analysis in a formatted table"""
    
    # Prepare data for the table
    table_data = []
    for i, (task, resp_time) in enumerate(zip(tasks, response_times)):
        utilization = task.execution_time / task.period
        schedulable_status = "✓" if resp_time <= task.deadline else "✗"
        
        # Calculate interference details
        interference = 0
        interference_details = []
        for h in range(i):
            higher_task = tasks[h]
            task_interference = np.ceil(task.deadline / higher_task.period) * higher_task.execution_time
            interference += task_interference
            interference_details.append(f"⌈{task.deadline}/{higher_task.period}⌉×{higher_task.execution_time}={task_interference}")
        
        interference_str = " + ".join(interference_details) if interference_details else "0"
        
        table_data.append({
            'Task': f'T{i+1}',
            'Period (T)': task.period,
            'Execution (C)': task.execution_time,
            'Deadline (D)': task.deadline,
            'Utilization': f'{utilization:.3f}',
            'Interference (I)': f'{interference:.1f}',
            'Response Time (R)': f'{resp_time:.1f}',
            'R ≤ D': schedulable_status,
            'Interference Formula': interference_str if interference_str != "0" else "No interference"
        })
    
    # Create DataFrame
    df = pd.DataFrame(table_data)
    
    # Display table
    print("\n" + "="*120)
    print("DEADLINE-BASED RESPONSE TIME ANALYSIS")
    print("="*120)
    
    # Display main table without interference formula for cleaner view
    main_df = df.drop('Interference Formula', axis=1)
    display(main_df)
    
    # Display interference details separately
    if any(tasks[idx].execution_time < response_times[idx] for idx in range(len(tasks))):
        print("\nInterference Calculation Details:")
        print("-" * 60)
        for idx, (task, formula) in enumerate(zip(tasks, df['Interference Formula'])):
            if formula != "No interference":
                print(f"Task T{idx+1}: I = {formula}")
    
    # Summary
    total_utilization = sum(task.execution_time / task.period for task in tasks)
    # Fix the problematic line - use separate loop instead of generator comprehension
    schedulable_count = 0
    for idx, rt in enumerate(response_times):
        if rt <= tasks[idx].deadline:
            schedulable_count += 1
    
    print(f"\nSUMMARY:")
    print(f"Total Utilization: {total_utilization:.3f}")
    print(f"Schedulable Tasks: {schedulable_count}/{len(tasks)}")
    print(f"Overall Status: {'SCHEDULABLE' if schedulable else 'NOT SCHEDULABLE'}")
    print("="*120)

def compare_rm_methods(task_set, verbose=False):
    """
    Compare different Rate Monotonic schedulability tests
    """
    print("COMPARISON OF RATE MONOTONIC SCHEDULABILITY TESTS")
    print("="*80)
    
    # Method 1: Utilization bound test
    schedulable_bound = rate_monotonic_check(task_set, verbose=False)
    
    # Method 2: Iterative response time analysis
    sorted_tasks = sorted(task_set, key=lambda x: x.period)
    schedulable_rta, _ = response_time_analysis(sorted_tasks)
    
    # Method 3: Deadline-based response time analysis
    schedulable_deadline = rate_monotonic_check_1(task_set, verbose=False)
    
    # Create comparison table
    comparison_data = {
        'Method': [
            'Utilization Bound Test',
            'Iterative Response Time Analysis', 
            'Deadline-based Response Time Analysis'
        ],
        'Formula': [
            'Σ(C_i/T_i) ≤ n(2^(1/n) - 1)',
            'R_i = C_i + Σ⌈R_i/T_h⌉C_h ≤ D_i',
            'R_i = C_i + Σ⌈D_i/T_h⌉C_h ≤ D_i'
        ],
        'Result': [
            '✓ Schedulable' if schedulable_bound else '✗ Not Schedulable',
            '✓ Schedulable' if schedulable_rta else '✗ Not Schedulable',
            '✓ Schedulable' if schedulable_deadline else '✗ Not Schedulable'
        ],
        'Accuracy': [
            'Sufficient (may be pessimistic)',
            'Exact (necessary & sufficient)',
            'May be pessimistic for D_i < T_i'
        ]
    }
    
    comparison_df = pd.DataFrame(comparison_data)
    display(comparison_df)
    
    if verbose:
        print("\nDetailed Analysis:")
        print("-" * 40)
        print("1. Utilization Bound Test:")
        rate_monotonic_check(task_set, verbose=True)
        
        print("\n2. Deadline-based Response Time Analysis:")
        rate_monotonic_check_1(task_set, verbose=True)

# Update the main function to include the new method
def main():
    # Example task set
    task_set = [
        Task(period=8,  deadline=6,  execution_time=2),
        Task(period=14, deadline=12, execution_time=5),
        Task(period=24, deadline=20, execution_time=6)
    ]
    
    print("Task Set Definition:")
    task_matrix = [[f"T{i+1}", row.period, row.deadline, row.execution_time] 
                   for i, row in enumerate(task_set)]
    task_df = pd.DataFrame(task_matrix, columns=['Task', 'Period', 'Deadline', 'Execution Time'])
    display(task_df)
    
    # Compare different methods
    compare_rm_methods(task_set, verbose=True)
    
    # Sort tasks by period for response time analysis
    sorted_tasks = sorted(task_set, key=lambda x: x.period)
    schedulable, response_times = response_time_analysis(sorted_tasks)
    display_response_time_table(sorted_tasks, response_times, schedulable)

if __name__ == "__main__":
    main()