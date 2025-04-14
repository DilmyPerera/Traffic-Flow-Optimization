import numpy as np
import matplotlib.pyplot as plt
from pulp import LpProblem, LpVariable, LpMaximize, lpSum, LpStatus, value

# Get user inputs
n = int(input("Enter number of directions (e.g., 4): "))
directions = []
qi = []
si = []

print("\nEnter details for each direction:")
for i in range(n):
    name = input(f"  Name of direction {i+1} (e.g., North): ")
    directions.append(name)
    q = float(input(f"    Flow rate for {name} (vehicles/sec): "))
    s = float(input(f"    Saturation flow rate for {name} (vehicles/sec): "))
    qi.append(q)
    si.append(s)

print("\nEnter green time limits (in seconds):")
gmin = float(input("  Minimum green time: "))
gmax = float(input("  Maximum green time: "))

print("\nEnter cycle length limits (in seconds):")
cmin = float(input("  Minimum cycle length: "))
cmax = float(input("  Maximum cycle length: "))

y = float(input("\nEnter yellow time per direction (in seconds): "))

# Create LP Model
model = LpProblem("Traffic_Light_Optimization", LpMaximize)

# Decision Variables
g = [LpVariable(f"g_{i}", lowBound=gmin, upBound=gmax) for i in range(n)]
c = LpVariable("c", lowBound=cmin, upBound=cmax)

# Objective Function: maximize weighted green time
model += lpSum([qi[i] * g[i] for i in range(n)])

# Constraints
model += lpSum(g) + n * y == c  # total cycle length with yellow time

for i in range(n):
    model += (qi[i] / si[i]) * c <= g[i]  # capacity constraint

# Solve the problem
model.solve()

# Output results
print("\n===== Optimization Results =====")
print("Status:", LpStatus[model.status])
print(f"Optimal Cycle Length: {value(c):.2f} seconds")

for i in range(n):
    print(f"{directions[i]} Direction: Green time = {value(g[i]):.2f} seconds")

# Delay calculation using Webster formula
delays = []
print("\n===== Delay Analysis (Webster’s Formula) =====")
for i in range(n):
    delay = (qi[i] * (value(c) - value(g[i]))**2) / (2 * value(c) * (1 - qi[i] / si[i]))
    delays.append(delay)
    print(f"{directions[i]} Direction: Delay = {delay:.2f} seconds/vehicle")

print(f"\nOverall Average Delay: {np.mean(delays):.2f} seconds/vehicle")

# # Plot green times
# plt.bar(directions, [value(g[i]) for i in range(n)], color='green')
# plt.title('Optimal Green Time per Direction')
# plt.ylabel('Green Time (s)')
# plt.ylim(0, gmax + 10)
# plt.grid(True)
# plt.show()

# Define different colors for each bar
bar_colors = ['green', 'blue', 'orange', 'red', 'purple', 'brown', 'pink', 'gray', 'cyan', 'magenta'][:n]

# Plot green times with custom colors
plt.bar(directions, [value(g[i]) for i in range(n)], color=bar_colors)
plt.title('Optimal Green Time per Direction')
plt.ylabel('Green Time (s)')
plt.ylim(0, gmax + 10)
plt.grid(True)
plt.show()
