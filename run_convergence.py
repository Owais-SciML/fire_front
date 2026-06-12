# run_convergence.py
import numpy as np
import matplotlib.pyplot as plt
from fire_solver import LevelSetFireSolver

def get_exact_contour_head(solver, phi):
    """
    Foolproof sub-grid extraction: Uses Matplotlib's marching squares algorithm 
    to find the exact mathematical boundary of the phi=0 contour, bypassing grid snapping.
    """
    fig_temp, ax_temp = plt.subplots()
    cs = ax_temp.contour(solver.X, solver.Y, phi, levels=[0])
    
    y_max = 0
    # Iterate through the generated contour lines to find the absolute highest Y point
    for path in cs.collections[0].get_paths():
        vertices = path.vertices
        if len(vertices) > 0:
            y_max = max(y_max, np.max(vertices[:, 1]))
            
    plt.close(fig_temp) # Close hidden figure to save memory
    return y_max

def run_convergence_analysis():
    print("Starting Professional Grid Convergence Analysis...")
    print("Extracting exact sub-grid contours. Please wait...")

    dx_values = [2.0, 1.25, 1.0, 0.8, 0.625, 0.5, 0.4]
    errors = []
    
    # Analytical baseline from paper
    analytical_head_y = 92.7 
    target_time = 30

    print(f"\n{'Grid (Nx x Ny)':<15} | {'dx (m)':<8} | {'Exact Head (m)':<15} | {'Absolute Error (m)'}")
    print("-" * 65)

    for dx in dx_values:
        Nx = int(100 / dx) + 1
        Ny = int(150 / dx) + 1
        
        solver = LevelSetFireSolver(Nx=Nx, Ny=Ny, X_max=50, Y_max=150, speed_model='mallet')
        solver.set_initial_conditions('fig2')
        
        results = solver.run_simulation([target_time])
        phi_final = results[target_time]
        
        # Get exact head using the contour extraction method
        eulerian_head = get_exact_contour_head(solver, phi_final)
        
        error = np.abs(eulerian_head - analytical_head_y)
        errors.append(error)
        
        print(f"{Nx}x{Ny:<12} | {solver.dx:<8.2f} | {eulerian_head:<15.4f} | {error:.4f}")

    # ==========================================
    # PLOTTING THE CONVERGENCE CURVE
    # ==========================================
    plt.figure(figsize=(10, 6))
    
    plt.plot(dx_values, errors, marker='o', markersize=8, color='black', linewidth=2, linestyle='-')
    
    plt.title('Grid Convergence Analysis ($t = 30$ s)', fontsize=14, fontweight='bold')
    plt.xlabel('Grid Spacing $\Delta x$ (meters)', fontsize=12)
    plt.ylabel('Absolute Error vs Reference 92.7m (meters)', fontsize=12)
    
    # Standard CFD practice: read left to right (Coarse to Fine)
    plt.gca().invert_xaxis() 
    
    plt.grid(True, which="both", ls="--", alpha=0.7)
    
    for i, txt in enumerate(dx_values):
        grid_label = f"{int(100/txt)+1}x{int(150/txt)+1}"
        plt.annotate(grid_label, 
                     (dx_values[i], errors[i]), 
                     textcoords="offset points", 
                     xytext=(0,10), 
                     ha='center',
                     fontsize=9)

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    run_convergence_analysis()