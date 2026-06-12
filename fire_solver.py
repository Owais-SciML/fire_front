import numpy as np

class LevelSetFireSolver:
    def __init__(self, Nx=100, Ny=100, X_max=50, Y_max=100, speed_model='australian'):
        self.x = np.linspace(-X_max, X_max, Nx)
        self.y = np.linspace(0, Y_max, Ny)
        self.X, self.Y = np.meshgrid(self.x, self.y)
        self.dx = self.x[1] - self.x[0]
        self.dy = self.y[1] - self.y[0]
        
        self.r0 = 0.165
        self.cf = 3.24
        self.Vx = 0.0
        self.Vy = 3.0
        self.V_mag = 3.0
        
        self.speed_model = speed_model 
        self.phi = None

    def set_initial_conditions(self, scenario):
        if scenario == 'fig2':
            self.phi = np.sqrt(self.X**2 + (self.Y - 50)**2) - 10.0
        elif scenario == 'fig3':
            line_fire = self.Y - 20
            spot_fire = np.sqrt(self.X**2 + (self.Y - 35)**2) - 4.0
            self.phi = np.minimum(line_fire, spot_fire)
        elif scenario == 'fig4':
            c1 = np.sqrt((self.X + 20)**2 + (self.Y - 50)**2) - 12.0
            c2 = np.sqrt((self.X - 20)**2 + (self.Y - 50)**2) - 12.0
            c3 = np.sqrt(self.X**2 + (self.Y - 30)**2) - 12.0
            self.phi = np.minimum(np.minimum(c1, c2), c3)
        elif scenario == 'fig5':
            c1 = np.sqrt((self.X + 25)**2 + (self.Y - 10)**2) - 8.0
            c2 = np.sqrt(self.X**2 + (self.Y - 10)**2) - 8.0
            c3 = np.sqrt((self.X - 25)**2 + (self.Y - 10)**2) - 8.0
            self.phi = np.minimum(np.minimum(c1, c2), c3)

    def _get_speed(self, nx, ny):
        if self.speed_model == 'australian':
            return self.r0 * (1 + self.cf * (self.Vx * nx + self.Vy * ny))
        elif self.speed_model == 'mallet':
            cos_theta = (self.Vx * nx + self.Vy * ny) / (self.V_mag + 1e-10)
            theta = np.arccos(np.clip(cos_theta, -1.0, 1.0))
            Un = np.zeros_like(nx)
            mask1 = np.abs(theta) <= np.pi/2
            Un[mask1] = self.r0 * (1 + self.cf * np.sqrt(self.V_mag) * (np.maximum(0, cos_theta[mask1])**1.5))
            Un[~mask1] = self.r0 * (0.5 + 0.5 * np.sin(theta[~mask1]))
            return Un

    def _superbee(self, r):
        return np.maximum(0, np.maximum(np.minimum(2*r, 1), np.minimum(r, 2)))

    def _limited_gradient(self, phi, U, ds, axis):
        phi_m1, phi_p1 = np.roll(phi, 1, axis=axis), np.roll(phi, -1, axis=axis)
        phi_m2, phi_p2 = np.roll(phi, 2, axis=axis), np.roll(phi, -2, axis=axis)
        
        D_bwd = (phi - phi_m1) / ds
        D_fwd = (phi_p1 - phi) / ds
        
        r_bwd = ((phi_m1 - phi_m2) / ds) / (D_bwd + 1e-10)
        r_fwd = ((phi_p2 - phi_p1) / ds) / (D_fwd + 1e-10)
        
        lim_bwd = self._superbee(r_bwd)
        lim_fwd = self._superbee(r_fwd)
        
        grad_pos = D_bwd + 0.5 * lim_bwd * (D_fwd - D_bwd)
        grad_neg = D_fwd + 0.5 * lim_fwd * (D_bwd - D_fwd)
        return np.where(U > 0, grad_pos, grad_neg)

    def run_simulation(self, target_times):
        t = 0.0
        saved_data = {}
        times_to_hit = sorted(target_times.copy())
        
        while len(times_to_hit) > 0:
            phi_x = np.gradient(self.phi, self.dx, axis=1)
            phi_y = np.gradient(self.phi, self.dy, axis=0)
            mag = np.sqrt(phi_x**2 + phi_y**2) + 1e-10
            
            Un = self._get_speed(phi_x/mag, phi_y/mag)
            Ux, Uy = Un * (phi_x/mag), Un * (phi_y/mag)
            
            F_phi = Ux * self._limited_gradient(self.phi, Ux, self.dx, axis=1) + Uy * self._limited_gradient(self.phi, Uy, self.dy, axis=0)
            
            # Calculate maximum safe dt
            dt = 0.4 * min(self.dx / (np.max(np.abs(Ux)) + 1e-10), self.dy / (np.max(np.abs(Uy)) + 1e-10))
            
            # THE FIX: Temporal Clipping
            # If the next step overshoots our target time, shrink dt to land exactly on it.
            save_after_step = False
            if t + dt >= times_to_hit[0]:
                dt = times_to_hit[0] - t
                save_after_step = True
            
            # RK2 Time steps (Predictor)
            phi_star = self.phi - dt * F_phi
            
            # Re-calculate F for star step (Corrector)
            phi_x_s = np.gradient(phi_star, self.dx, axis=1)
            phi_y_s = np.gradient(phi_star, self.dy, axis=0)
            mag_s = np.sqrt(phi_x_s**2 + phi_y_s**2) + 1e-10
            Un_s = self._get_speed(phi_x_s/mag_s, phi_y_s/mag_s)
            Ux_s, Uy_s = Un_s * (phi_x_s/mag_s), Un_s * (phi_y_s/mag_s)
            F_phi_star = Ux_s * self._limited_gradient(phi_star, Ux_s, self.dx, axis=1) + Uy_s * self._limited_gradient(phi_star, Uy_s, self.dy, axis=0)
            
            self.phi = 0.5 * self.phi + 0.5 * (phi_star - dt * F_phi_star)
            t += dt
            
            # Save exactly on the target time
            if save_after_step:
                saved_data[times_to_hit[0]] = np.copy(self.phi)
                times_to_hit.pop(0)
            
        return saved_data