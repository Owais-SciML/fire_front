# Level-Set Wildfire Propagation Solver

A high-fidelity computational fluid dynamics (CFD) and multi-physics simulation engine written in Python. This solver leverages the **Level-Set Method (LSM)** to track non-linear interface propagation across complex 2D domains, modeling wildland firefront dynamics under variable wind vectors and directional rate-of-spread empirical formulations.

## 🚀 Key Numerical Features

* **High-Order Flux Limiting:** Implements the **Superbee Flux Limiter** to dynamically interpolate upwinded spatial derivatives, mitigating numerical diffusion and non-physical oscillations across steep gradient fronts.
* **Temporal Discretization:** Utilizes an explicit **2nd-Order Runge-Kutta (RK2 / Heun's Method)** predictor-corrector time-stepping sequence to ensure numerical stability and temporal accuracy.
* **Adaptive Time-Stepping (CFL Enforcement):** Automatically calculates maximum allowable time steps ($\Delta t$) at each iteration by continuously computing the Courant-Friedrichs-Lewy (CFL) constraint condition based on instantaneous advection velocities.
* **Precise Temporal Clipping:** Features an exact target-time matching algorithm that temporarily shrinks the step size to land squarely on pre-defined observation milestones without overshooting.

## 🧠 Core Physics & Mathematical Framework

The solver implicitizes the propagating firefront as the zero-level set of a higher-dimensional scalar function, $\phi(x, y, t) = 0$. The evolution of the interface is governed by the classic Level-Set Hamilton-Jacobi equation:

$$\frac{\partial \phi}{\partial t} + U_n |\nabla \phi| = 0$$

Where the normal velocity field, $U_n$, is derived via localized unit normal vectors $\vec{n} = \frac{\nabla \phi}{|\nabla \phi|}$ mapped against two empirical wind models:
1. **Australian Rate-of-Spread Model:** A linear wind-velocity vector field mapping.
2. **Mallet Model:** A non-linear, angular-dependent model applying a clipped-cosine thresholding parameter to govern forward heading vs. backing fire dynamics.

---

## 🛠️ Software Stack & Architecture

* **Language:** Python 3.x
* **Core Libraries:** `NumPy` (Vectorized array calculations, matrix rolling, and analytical spatial gradients).
* **Structural Design:** Encapsulated inside a clean, object-oriented `LevelSetFireSolver` class to allow modular initial condition configurations and multi-scenario executions.

### Pre-configured Initial Conditions (Scenarios)
* `fig2`: Simple Expanding Circular Core.
* `fig3`: Intersecting Line Firefront and Discrete Spot Fire Core (Coalescence tracking).
* `fig4`: Multi-core Interaction Array (Tri-point thermal merging).
* `fig5`: Linear Triple-Core Multi-point Ignition Array.

---

## 💻 Quick Start & Usage

```python
import numpy as np
from firefront_solver import LevelSetFireSolver

# Initialize solver over a 100x100 spatial grid domain
solver = LevelSetFireSolver(Nx=100, Ny=100, X_max=50, Y_max=100, speed_model='mallet')

# Set initial conditions for complex firefront intersection tracking
solver.set_initial_conditions(scenario='fig3')

# Run tracking sequence and capture continuous matrix states at exact timesteps
target_intervals = [10.0, 25.0, 50.0, 100.0]
simulation_history = solver.run_simulation(target_times=target_intervals)

# Extract zero-level contours from the simulation_history dictionary for visualization
