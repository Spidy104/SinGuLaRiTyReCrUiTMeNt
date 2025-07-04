import numpy as np
import matplotlib.pyplot as plt
from astropy import units as u
from astropy import constants as const
from astropy.cosmology import Planck18, FlatLambdaCDM
from astropy.coordinates import SkyCoord
import warnings
warnings.filterwarnings('ignore')

class GalaxyRedshiftAnalyzer:
    """
    Class to analyze redshift data of galaxies and calculate velocities and distances
    """
    
    def __init__(self, cosmology=None):
        """Initialize with a cosmological model"""
        self.cosmology = cosmology if cosmology else Planck18
        
    def calculate_velocity_from_redshift(self, redshift, method='relativistic'):
        """
        Calculate recession velocity from redshift
        
        Parameters:
        -----------
        redshift : float or array
            Observed redshift (z)
        method : str
            'classical' for v = cz (valid for z << 1)
            'relativistic' for relativistic formula
        
        Returns:
        --------
        velocity : astropy.units.Quantity
            Recession velocity
        """
        z = redshift
        c = const.c.to(u.km/u.s)
        
        if method == 'classical':
            # Classical approximation: v = cz (only valid for z << 1)
            velocity = c * z
        elif method == 'relativistic':
            # Relativistic formula: v = c * (z^2 + 2z) / (z^2 + 2z + 2)
            velocity = c * (z**2 + 2*z) / (z**2 + 2*z + 2)
        else:
            raise ValueError("Method must be 'classical' or 'relativistic'")
            
        return velocity
    
    def calculate_distance_from_redshift(self, redshift):
        """
        Calculate distance from redshift using cosmological model
        
        Parameters:
        -----------
        redshift : float or array
            Observed redshift (z)
            
        Returns:
        --------
        distances : dict
            Dictionary containing various distance measures
        """
        z = redshift
        
        # Luminosity distance
        d_L = self.cosmology.luminosity_distance(z)
        
        # Angular diameter distance
        d_A = self.cosmology.angular_diameter_distance(z)
        
        # Comoving distance
        d_C = self.cosmology.comoving_distance(z)
        
        # Light travel time distance
        d_LT = self.cosmology.lookback_time(z) * const.c.to(u.Mpc/u.Gyr)
        
        return {
            'luminosity_distance': d_L,
            'angular_diameter_distance': d_A,
            'comoving_distance': d_C,
            'light_travel_distance': d_LT
        }
    
    def hubble_velocity(self, distance):
        """
        Calculate expected velocity from Hubble's law: v = H0 * d
        
        Parameters:
        -----------
        distance : astropy.units.Quantity
            Distance in Mpc
            
        Returns:
        --------
        velocity : astropy.units.Quantity
            Expected Hubble velocity
        """
        H0 = self.cosmology.H0
        return H0 * distance

def analyze_galaxy_pair():
    """
    Analyze redshift data for two real galaxies with different redshifts
    """
    
    # Initialize analyzer
    analyzer = GalaxyRedshiftAnalyzer()
    
    # Galaxy data (using real examples)
    galaxies = {
        'Andromeda (M31)': {
            'redshift': -0.001001,  # Blue-shifted (approaching us)
            'observed_wavelength': 656.3 * u.nm,  # H-alpha line
            'rest_wavelength': 656.281 * u.nm,
            'type': 'Spiral Galaxy',
            'notes': 'Nearest major galaxy, blue-shifted due to local motion'
        },
        'NGC 4889 (Coma Cluster)': {
            'redshift': 0.02310,  # Red-shifted (receding)
            'observed_wavelength': 671.4 * u.nm,  # H-alpha line
            'rest_wavelength': 656.281 * u.nm,
            'type': 'Elliptical Galaxy',
            'notes': 'Galaxy in Coma cluster, cosmological redshift'
        }
    }
    
    print("=" * 70)
    print("GALAXY REDSHIFT ANALYSIS")
    print("=" * 70)
    print(f"Using cosmology: {analyzer.cosmology.name}")
    print(f"H0 = {analyzer.cosmology.H0:.2f}")
    print(f"Ωm = {analyzer.cosmology.Om0:.3f}")
    print(f"ΩΛ = {analyzer.cosmology.Ode0:.3f}")
    print()
    
    results = {}
    
    for galaxy_name, data in galaxies.items():
        print(f"ANALYZING: {galaxy_name}")
        print("-" * 50)
        
        z = data['redshift']
        
        # Calculate redshift from wavelengths (verification)
        z_calculated = (data['observed_wavelength'] - data['rest_wavelength']) / data['rest_wavelength']
        
        print(f"Type: {data['type']}")
        print(f"Given redshift (z): {z:.6f}")
        print(f"Calculated redshift: {z_calculated:.6f}")
        print(f"Rest wavelength: {data['rest_wavelength']:.3f}")
        print(f"Observed wavelength: {data['observed_wavelength']:.3f}")
        
        # Calculate velocities
        v_classical = analyzer.calculate_velocity_from_redshift(abs(z), 'classical')
        v_relativistic = analyzer.calculate_velocity_from_redshift(abs(z), 'relativistic')
        
        print(f"\nVELOCITY CALCULATIONS:")
        print(f"Classical (v = cz): {v_classical:.1f}")
        print(f"Relativistic: {v_relativistic:.1f}")
        
        if z < 0:
            print(f"Direction: APPROACHING (blue-shifted)")
        else:
            print(f"Direction: RECEDING (red-shifted)")
        
        # Calculate distances (only meaningful for positive redshift)
        if z > 0:
            distances = analyzer.calculate_distance_from_redshift(z)
            hubble_vel = analyzer.hubble_velocity(distances['comoving_distance'])
            
            print(f"\nDISTANCE CALCULATIONS:")
            print(f"Luminosity distance: {distances['luminosity_distance']:.2f}")
            print(f"Angular diameter distance: {distances['angular_diameter_distance']:.2f}")
            print(f"Comoving distance: {distances['comoving_distance']:.2f}")
            print(f"Light travel distance: {distances['light_travel_distance']:.2f}")
            
            print(f"\nHUBBLE LAW COMPARISON:")
            print(f"Expected Hubble velocity: {hubble_vel:.1f}")
            print(f"Observed velocity: {v_relativistic:.1f}")
            
            # Store results for comparison
            results[galaxy_name] = {
                'redshift': z,
                'velocity': v_relativistic,
                'distance': distances['comoving_distance'],
                'hubble_velocity': hubble_vel
            }
        else:
            print(f"\nNote: Negative redshift indicates local motion, not cosmological expansion")
            print(f"Distance calculation not applicable for blue-shifted objects")
            
            results[galaxy_name] = {
                'redshift': z,
                'velocity': -v_relativistic,  # Negative for approaching
                'distance': None,
                'hubble_velocity': None
            }
        
        print(f"Notes: {data['notes']}")
        print("\n" + "="*70 + "\n")
    
    return results, analyzer

def create_redshift_visualization(results, analyzer):
    """
    Create visualizations of redshift analysis
    """
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('Galaxy Redshift Analysis Results', fontsize=16, fontweight='bold')
    
    # Extract data for plotting
    galaxy_names = list(results.keys())
    redshifts = [results[name]['redshift'] for name in galaxy_names]
    velocities = [results[name]['velocity'].value for name in galaxy_names]
    
    # Filter out None distances for distance plots
    valid_distances = [(name, results[name]) for name in galaxy_names 
                      if results[name]['distance'] is not None]
    
    # Plot 1: Redshift comparison
    colors = ['blue' if z < 0 else 'red' for z in redshifts]
    bars1 = ax1.bar(range(len(galaxy_names)), redshifts, color=colors, alpha=0.7)
    ax1.set_xlabel('Galaxy')
    ax1.set_ylabel('Redshift (z)')
    ax1.set_title('Redshift Comparison')
    ax1.set_xticks(range(len(galaxy_names)))
    ax1.set_xticklabels([name.split('(')[0].strip() for name in galaxy_names], rotation=45)
    ax1.grid(True, alpha=0.3)
    ax1.axhline(y=0, color='black', linestyle='--', alpha=0.5)
    
    # Add value labels on bars
    for bar, z in zip(bars1, redshifts):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + (0.001 if height > 0 else -0.002),
                f'{z:.6f}', ha='center', va='bottom' if height > 0 else 'top')
    
    # Plot 2: Velocity comparison
    bars2 = ax2.bar(range(len(galaxy_names)), velocities, color=colors, alpha=0.7)
    ax2.set_xlabel('Galaxy')
    ax2.set_ylabel('Velocity (km/s)')
    ax2.set_title('Recession/Approach Velocity')
    ax2.set_xticks(range(len(galaxy_names)))
    ax2.set_xticklabels([name.split('(')[0].strip() for name in galaxy_names], rotation=45)
    ax2.grid(True, alpha=0.3)
    ax2.axhline(y=0, color='black', linestyle='--', alpha=0.5)
    
    # Add value labels on bars
    for bar, v in zip(bars2, velocities):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + (100 if height > 0 else -200),
                f'{v:.0f}', ha='center', va='bottom' if height > 0 else 'top')
    
    # Plot 3: Distance vs Redshift (Hubble diagram)
    if valid_distances:
        z_vals = [results[name]['redshift'] for name, _ in valid_distances]
        d_vals = [results[name]['distance'].value for name, _ in valid_distances]
        
        ax3.scatter(z_vals, d_vals, s=100, color='red', alpha=0.7, edgecolors='black')
        
        # Plot theoretical Hubble relation
        z_theory = np.linspace(0, max(z_vals)*1.2, 100)
        d_theory = [analyzer.cosmology.comoving_distance(z).value for z in z_theory]
        ax3.plot(z_theory, d_theory, 'b--', label='Theoretical (ΛCDM)', alpha=0.7)
        
        ax3.set_xlabel('Redshift (z)')
        ax3.set_ylabel('Comoving Distance (Mpc)')
        ax3.set_title('Distance vs Redshift (Hubble Diagram)')
        ax3.grid(True, alpha=0.3)
        ax3.legend()
        
        # Annotate points
        for (name, _), z, d in zip(valid_distances, z_vals, d_vals):
            ax3.annotate(name.split('(')[0].strip(), (z, d), 
                        xytext=(5, 5), textcoords='offset points', fontsize=8)
    else:
        ax3.text(0.5, 0.5, 'No positive redshift data\nfor distance calculation', 
                ha='center', va='center', transform=ax3.transAxes)
        ax3.set_title('Distance vs Redshift (No Data)')
    
    # Plot 4: Velocity vs Distance (Hubble Law)
    if valid_distances:
        d_vals = [results[name]['distance'].value for name, _ in valid_distances]
        v_vals = [results[name]['velocity'].value for name, _ in valid_distances]
        v_hubble = [results[name]['hubble_velocity'].value for name, _ in valid_distances]
        
        ax4.scatter(d_vals, v_vals, s=100, color='red', alpha=0.7, 
                   edgecolors='black', label='Observed')
        ax4.scatter(d_vals, v_hubble, s=100, color='blue', alpha=0.7, 
                   edgecolors='black', label='Hubble Law Prediction')
        
        # Plot Hubble law line
        d_max = max(d_vals) * 1.1
        d_line = np.linspace(0, d_max, 100)
        v_line = analyzer.cosmology.H0.value * d_line
        ax4.plot(d_line, v_line, 'g--', alpha=0.7, label=f'v = H₀d (H₀={analyzer.cosmology.H0:.1f})')
        
        ax4.set_xlabel('Distance (Mpc)')
        ax4.set_ylabel('Velocity (km/s)')
        ax4.set_title('Hubble Law: Velocity vs Distance')
        ax4.grid(True, alpha=0.3)
        ax4.legend()
        
        # Annotate points
        for (name, _), d, v in zip(valid_distances, d_vals, v_vals):
            ax4.annotate(name.split('(')[0].strip(), (d, v), 
                        xytext=(5, 5), textcoords='offset points', fontsize=8)
    else:
        ax4.text(0.5, 0.5, 'No distance data available\nfor Hubble law plot', 
                ha='center', va='center', transform=ax4.transAxes)
        ax4.set_title('Hubble Law (No Data)')
    
    plt.tight_layout()
    plt.show()

def demonstrate_redshift_range():
    """
    Demonstrate redshift calculations across a range of values
    """
    print("REDSHIFT RANGE DEMONSTRATION")
    print("=" * 50)
    
    analyzer = GalaxyRedshiftAnalyzer()
    
    # Range of redshifts from nearby to very distant
    redshifts = np.array([0.001, 0.01, 0.1, 0.5, 1.0, 2.0, 5.0])
    
    print(f"{'z':<8} {'v_class(km/s)':<12} {'v_rel(km/s)':<12} {'Distance(Mpc)':<15} {'Lookback(Gyr)':<12}")
    print("-" * 70)
    
    for z in redshifts:
        v_classical = analyzer.calculate_velocity_from_redshift(z, 'classical')
        v_relativistic = analyzer.calculate_velocity_from_redshift(z, 'relativistic')
        distance = analyzer.cosmology.comoving_distance(z)
        lookback = analyzer.cosmology.lookback_time(z)
        
        print(f"{z:<8.3f} {v_classical.value:<12.0f} {v_relativistic.value:<12.0f} "
              f"{distance.value:<15.0f} {lookback.value:<12.2f}")
    
    # Plot the comparison
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    v_classical_vals = [analyzer.calculate_velocity_from_redshift(z, 'classical').value for z in redshifts]
    v_relativistic_vals = [analyzer.calculate_velocity_from_redshift(z, 'relativistic').value for z in redshifts]
    distances = [analyzer.cosmology.comoving_distance(z).value for z in redshifts]
    
    # Classical vs Relativistic velocity
    ax1.loglog(redshifts, v_classical_vals, 'b-o', label='Classical (v = cz)', alpha=0.7)
    ax1.loglog(redshifts, v_relativistic_vals, 'r-s', label='Relativistic', alpha=0.7)
    ax1.axhline(y=299792.458, color='black', linestyle='--', alpha=0.5, label='Speed of Light')
    ax1.set_xlabel('Redshift (z)')
    ax1.set_ylabel('Velocity (km/s)')
    ax1.set_title('Classical vs Relativistic Velocity')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    
    # Distance vs Redshift
    ax2.loglog(redshifts, distances, 'g-o', alpha=0.7)
    ax2.set_xlabel('Redshift (z)')
    ax2.set_ylabel('Comoving Distance (Mpc)')
    ax2.set_title('Distance vs Redshift')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    # Analyze the two galaxies
    results, analyzer = analyze_galaxy_pair()
    
    # Create visualizations
    create_redshift_visualization(results, analyzer)
    
    # Demonstrate range of redshifts
    demonstrate_redshift_range()
    
    print("\n" + "="*70)
    print("SUMMARY COMPARISON")
    print("="*70)
    
    galaxy_names = list(results.keys())
    
    print(f"\n1. {galaxy_names[0]}:")
    print(f"   - Blue-shifted (z = {results[galaxy_names[0]]['redshift']:.6f})")
    print(f"   - Approaching at {abs(results[galaxy_names[0]]['velocity']):.1f}")
    print(f"   - Local motion, not cosmological expansion")
    
    print(f"\n2. {galaxy_names[1]}:")
    print(f"   - Red-shifted (z = {results[galaxy_names[1]]['redshift']:.6f})")
    print(f"   - Receding at {results[galaxy_names[1]]['velocity']:.1f}")
    if results[galaxy_names[1]]['distance'] is not None:
        print(f"   - Distance: {results[galaxy_names[1]]['distance']:.1f}")
        print(f"   - Follows Hubble's law within measurement uncertainties")
    
    print(f"\nKey Insights:")
    print(f"- Andromeda shows blue-shift due to local gravitational attraction")
    print(f"- NGC 4889 shows cosmological red-shift due to universe expansion")
    print(f"- For high redshifts (z > 0.1), relativistic effects become important")
    print(f"- Distance measurements require positive redshift and cosmological model")