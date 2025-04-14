import pulp as pl
import numpy as np
import matplotlib.pyplot as plt

# Problem parameters
n = 4  # Number of directions (North, East, South, West)
q = [0.15, 0.25, 0.2, 0.1]  # Flow rates (vehicles/second)
s = [0.5, 0.5, 0.5, 0.5]  # Saturation flow rates (vehicles/second)
g_min = 15  # Minimum green time (seconds)
g_max = 60  # Maximum green time (seconds)
c_min = 60  # Minimum cycle length (seconds)
c_max = 180  # Maximum cycle length (seconds)
y = 3  # Yellow time (seconds)

# Create the optimization problem
problem = pl.LpProblem("Traffic_Light_Optimization", pl.LpMinimize)

# Define the decision variables
g = [pl.LpVariable(f"g_{i}", lowBound=g_min, upBound=g_max) for i in range(n)]
c = pl.LpVariable("c", lowBound=c_min, upBound=c_max)

# Objective: maximize weighted green time (converted to minimization)
problem += -pl.lpSum([q[i] * g[i] for i in range(n)])

# Add constraints
# Total cycle time constraint: sum of green + total yellow = cycle
problem += pl.lpSum(g) + n * y == c

# Capacity constraints (avoid dividing variables)
for i in range(n):
    problem += g[i] >= (q[i] / s[i]) * c

# Solve the problem
problem.solve(pl.PULP_CBC_CMD(msg=False))

# Extract the solution
green_times = [g[i].value() for i in range(n)]
cycle_length = c.value()

print("Optimization Results:")
print(f"Cycle Length: {cycle_length:.2f} seconds")
for i in range(n):
    direction = ["North", "East", "South", "West"][i]
    print(f"{direction}: Green time = {green_times[i]:.2f} seconds")

# Calculate delay using Webster's formula
delays = []
for i in range(n):
    delay = (q[i] * (cycle_length - green_times[i])**2) / (2 * cycle_length * (1 - q[i]/s[i]))
    delays.append(delay)
    print(f"Average delay for {['North', 'East', 'South', 'West'][i]}: {delay:.2f} seconds/vehicle")

# Create a visual representation of the timing plan
fig, ax = plt.subplots(figsize=(10, 6))

colors = ['green', 'yellow', 'red']
y_positions = np.arange(n)
labels = ['North', 'East', 'South', 'West']

# Starting positions for each direction
start_positions = [0]
current_pos = 0
for i in range(n - 1):
    current_pos += green_times[i] + y
    start_positions.append(current_pos)

# Plot green, yellow, and red bars
for i in range(n):
    ax.barh(y_positions[i], green_times[i], left=start_positions[i], color='green', alpha=0.7)
    ax.barh(y_positions[i], y, left=start_positions[i] + green_times[i], color='yellow', alpha=0.7)
    red_time = cycle_length - green_times[i] - y
    red_start = (start_positions[i] + green_times[i] + y) % cycle_length
    ax.barh(y_positions[i], red_time, left=red_start, color='red', alpha=0.7)

ax.set_yticks(y_positions)
ax.set_yticklabels(labels)
ax.set_xlabel('Time (seconds)')
ax.set_title('Traffic Light Timing Plan')
plt.xlim(0, cycle_length)
plt.grid(axis='x', linestyle='--', alpha=0.7)

plt.savefig('traffic_light_plan.png')
plt.close()

# Create a pie chart for green time allocation
labels = [f'{direction}\n{green_times[i]:.1f}s' for i, direction in enumerate(['North', 'East', 'South', 'West'])]
plt.figure(figsize=(8, 8))
plt.pie(green_times, labels=labels, autopct='%1.1f%%', startangle=90,
        colors=['lightgreen', 'lightblue', 'lightcoral', 'lightyellow'])
plt.title('Green Time Allocation')
plt.savefig('green_time_allocation.png')
