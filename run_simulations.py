import matplotlib.pyplot as plt
from fire_solver import LevelSetFireSolver

def plot_normal_merger(scenario, title):
    # Standard grid for short times
    solver = LevelSetFireSolver(Nx=100, Ny=150, X_max=50, Y_max=150, speed_model='australian')
    solver.set_initial_conditions(scenario)
    
    # Times 5, 10, 15... up to 60 (Exactly 12 frames)
    times = list(range(5, 65, 5)) 
    print(f"Simulating {scenario} from 5 to 60s in grid format...")
    results = solver.run_simulation(times)
    
    # 3 rows, 4 columns = 12 spots.
    fig, axs = plt.subplots(3, 4, figsize=(15, 10))
    axs = axs.flatten()
    
    for i, t in enumerate(times):
        axs[i].contour(solver.X, solver.Y, results[t], levels=[0], colors='red', linewidths=2)
        axs[i].set_xlim(-50, 50)
        axs[i].set_ylim(0, 150)
        axs[i].set_title(f"Time = {t}s")
        
    plt.suptitle(title, fontsize=16)
    plt.tight_layout()
    plt.show()

def plot_overlaid_figure5(scenario):
    """
    Recreates the exact aesthetic of Figure 5 from the paper by overlaying 
    multiple time steps on a single plot and adding a wind vector arrow.
    """
    solver = LevelSetFireSolver(Nx=100, Ny=150, X_max=50, Y_max=150, speed_model='australian')
    solver.set_initial_conditions(scenario)
    
    # Select specific times to overlay to match the density of the paper's graph
    times = [5, 20, 40, 60]
    print(f"\nSimulating {scenario} OVERLAID for times {times}...")
    results = solver.run_simulation(times)
    
    plt.figure(figsize=(8, 10))
    
    # Plot each time step on the same axis
    for t in times:
        plt.contour(solver.X, solver.Y, results[t], levels=[0], colors='#c82323', linewidths=2.5)
        
    # Add the blue wind vector arrow (matching the reference image)
    # Starts at x=-20, y=40, points upward in the +y direction
    plt.arrow(-18, 40, 0, 15, head_width=3, head_length=4, fc='#2f5597', ec='#2f5597', linewidth=2.5)
    
    plt.xlim(-50, 50)
    plt.ylim(0, 150)
    plt.title("Figure 5: Overlaid Scalloped Merger (5s to 60s)", fontsize=14, fontweight='bold')
    plt.xlabel("X-coordinate (meters)", fontsize=12)
    plt.ylabel("Y-coordinate (meters)", fontsize=12)
    
    # Format tick marks to match the paper's style
    plt.minorticks_on()
    plt.tick_params(direction='in', length=6, width=1)
    plt.tick_params(which='minor', direction='in', length=3, width=1)
    
    plt.tight_layout()
    plt.show()

def plot_10000_jump(scenario):
    # MASSIVE 15-kilometer grid, low resolution so it calculates fast
    solver = LevelSetFireSolver(Nx=200, Ny=200, X_max=5000, Y_max=15000, speed_model='australian')
    solver.set_initial_conditions(scenario)
    
    print(f"\nSimulating {scenario} MASSIVE JUMP to t = 10000s... (Wait ~15 seconds)")
    results = solver.run_simulation([10000])
    
    plt.figure(figsize=(6, 8))
    plt.contour(solver.X, solver.Y, results[10000], levels=[0], colors='red', linewidths=2)
    plt.xlim(-5000, 5000)
    plt.ylim(0, 15000)
    plt.title(f"Time = 10000s\nNotice it is one perfectly smooth giant fire.")
    plt.grid(True)
    plt.show()


if __name__ == "__main__":
    
    # 1. Figure 3: Line and Spot Fire Merger
    plot_normal_merger('fig3', 'Figure 3: Line and Spot Fire Merger (5-60s)')
    
    # 2. Figure 4: Unburned Fuel Pocket
    plot_normal_merger('fig4', 'Figure 4: Unburned Fuel Pocket (5-60s)')
    
    # 3. Figure 5: Three Front Scalloped Merger (Grid View)
    plot_normal_merger('fig5', 'Figure 5: Three Front Scalloped Merger (5-60s)')

    # 4. Figure 5: Exact Overlay Match for the Report
    plot_overlaid_figure5('fig5')

    # 5. The MASSIVE 10,000s Stabilization Jump
    plot_10000_jump('fig5')