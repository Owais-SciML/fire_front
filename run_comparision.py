# run_comparison.py
import numpy as np
import os
import pandas as pd
import matplotlib.pyplot as plt
from fire_solver import LevelSetFireSolver

# 1. Setup Solver and target times for Figure 2
times = [0, 6, 12, 18, 24, 30]

base_path = r'C:\programming\fire_front'
csv_files = ["1dataset.csv", "2dataset.csv", "3dataset.csv", "4dataset.csv", "5dataset.csv", "6dataset.csv"]
csv_files = [os.path.join(base_path, f"{i}dataset.csv") for i in range(1, 7)]

print("Simulating Eulerian baseline...")
solver = LevelSetFireSolver(Nx=101, Ny=101, speed_model='mallet')
solver.set_initial_conditions('fig2')
results = solver.run_simulation(times)

# Lists to store the quantitative head data
eulerian_heads = []
lagrangian_heads = []

# 2. Setup Plot 1: The Visual Overlay
fig1, axs = plt.subplots(3, 2, figsize=(10, 15))
axs = axs.flatten()

print("\n--- Numerical Comparison ---")
print(f"{'Time(s)':<10} | {'Eulerian Head (y)':<20} | {'Lagrangian Head (y)':<20} | {'Difference (m)'}")

for i, t in enumerate(times):
    phi_t = results[t]
    
    # Plot Eulerian
    axs[i].contour(solver.X, solver.Y, phi_t, levels=[0], colors='red', linewidths=2)
    e_head = np.max(solver.Y[phi_t <= 0])
    eulerian_heads.append(e_head)

    # Plot Lagrangian and extract data
    try:
        df = pd.read_csv(csv_files[i], header=None)
        axs[i].plot(df[0], df[1], color='blue', linewidth=1.5, label='Lagrangian MOL')
        l_head = df[1].max()
        lagrangian_heads.append(l_head)
    except FileNotFoundError:
        lagrangian_heads.append(np.nan)
        l_head = np.nan

    # Format subplot
    axs[i].set_xlim(-50, 50)
    axs[i].set_ylim(0, 100)
    axs[i].set_title(f"Time = {t} s")
    axs[i].grid(True, linestyle='--', alpha=0.5)
    if i == 0:
        axs[i].legend(["Eulerian", "Lagrangian MOL"])
        
    # Print numerical output to terminal
    diff = abs(e_head - l_head) if not np.isnan(l_head) else np.nan
    print(f"{t:<10} | {e_head:<20.2f} | {l_head:<20.2f} | {diff:.2f}")

fig1.suptitle("Visual Comparison: Eulerian Level-Set vs Lagrangian MOL", fontsize=16)
plt.tight_layout()
plt.show()

# 3. Setup Plot 2: Quantitative Difference Plot
lagrangian_heads = np.array(lagrangian_heads)
eulerian_heads = np.array(eulerian_heads)

# Only plot if CSVs were successfully loaded
if not np.isnan(lagrangian_heads).all():
    difference = np.abs(eulerian_heads - lagrangian_heads)
    
    fig2 = plt.figure(figsize=(8, 5))
    plt.plot(times, difference, marker='o', color='black', linestyle='dashed', linewidth=2)
    plt.title("Absolute Error in Head Position vs Time")
    plt.xlabel("Simulation Time (Seconds)")
    plt.ylabel("Difference (meters)")
    plt.grid(True)
    plt.show()
else:
    print("\nWarning: CSV files not found. Ensure 1dataset.csv through 6dataset.csv are in the folder to generate the difference plot.")