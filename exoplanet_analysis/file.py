import numpy as np
import matplotlib.pyplot as plt
import lightkurve as lk

# Download Kepler-10 light curve data
search_result = lk.search_targetpixelfile('Kepler-10', quarter=3)
tpf = search_result.download()
lc = tpf.to_lightcurve(aperture_mask=tpf.pipeline_mask)

# Clean and normalize the light curve
lc = lc.remove_outliers()
lc = lc.normalize()  # Normalize flux to 1, making it dimensionless

# Fold the light curve with Kepler-10b's period and epoch
period = 0.837495  # days
epoch = 131.56575  # BJD - 2454833
folded_lc = lc.fold(period=period, epoch_time=epoch)

# Plot the folded light curve
plt.figure(figsize=(10, 6))
ax = folded_lc.scatter()
folded_lc.bin(bins=50).plot(ax=ax, color='red', lw=2, label='Binned Light Curve')
plt.axvline(0, color='gray', ls='--', label='Transit Center')
plt.xlabel('Time from Transit Center (days)')
plt.ylabel('Normalized Flux')
plt.title('Kepler-10b Transit Light Curve')
plt.legend()

# Calculate and print transit depth and approximate duration
transit_depth = 1 - folded_lc.flux.min()  # Depth calculation for normalized flux
transit_duration = period * 0.05  # Rough estimate (5% of period)
print(f"Approximate Transit Depth: {transit_depth:.4f}")
print(f"Approximate Transit Duration: {transit_duration:.3f} days")

# Save the plot
plt.savefig('kepler_10b_transit.png')
plt.show()