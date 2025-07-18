import warnings

import matplotlib.pyplot as plt
import numpy as np
from astropy import units as u
from astropy.coordinates import get_body, solar_system_ephemeris
from astropy.time import Time

warnings.filterwarnings("ignore")

# Set high precision ephemeris
solar_system_ephemeris.set("jpl")


def calculate_planet_positions(planet_name, start_date, end_date, num_points=200):
    """Calculate planet positions over time as seen from Earth."""
    # Create time array
    start_time = Time(start_date)
    end_time = Time(end_date)
    times = start_time + np.linspace(0, (end_time - start_time).jd, num_points) * u.day

    # Get planet positions relative to Earth
    planet_coords = get_body(planet_name, times, location=None)

    # Convert to RA and Dec (apparent sky coordinates)
    ra = planet_coords.ra.degree
    dec = planet_coords.dec.degree

    return times, ra, dec


RETROGRADE_RA_WRAP_DEGREES = 180


def detect_retrograde_periods(times, ra):
    """Detect retrograde motion periods by finding where RA decreases."""
    # Calculate RA velocity (change in RA over time)
    dt = np.diff(times.jd)
    dra = np.diff(ra)

    # Handle RA wrap-around at 0/360 degrees
    dra[dra > RETROGRADE_RA_WRAP_DEGREES] -= 360
    dra[dra < -RETROGRADE_RA_WRAP_DEGREES] += 360

    ra_velocity = dra / dt

    # Retrograde when RA velocity is negative (moving backwards)
    retrograde_mask = ra_velocity < 0

    return retrograde_mask


def plot_retrograde_motion():
    """Plot retrograde motion for Mars and Jupiter."""
    # Time period covering retrograde motion
    # Mars has retrograde motion approximately every 26 months
    start_date = "2022-01-01"
    end_date = "2024-12-31"

    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle("Planetary Retrograde Motion Analysis", fontsize=16, fontweight="bold")

    planets = ["mars", "jupiter"]
    colors = ["red", "orange"]

    for i, (planet, color) in enumerate(zip(planets, colors, strict=False)):
        print(f"Calculating {planet.title()} positions...")

        # Calculate positions
        times, ra, dec = calculate_planet_positions(planet, start_date, end_date, 300)

        # Detect retrograde periods
        retrograde_mask = detect_retrograde_periods(times, ra)

        # Plot RA vs time
        ax1 = axes[i, 0]
        ax1.plot(
            times.datetime,
            ra,
            color=color,
            linewidth=2,
            alpha=0.7,
            label=f"{planet.title()} RA",
        )

        # Highlight retrograde periods
        retrograde_times = times[1:][retrograde_mask]
        retrograde_ra = ra[1:][retrograde_mask]
        ax1.scatter(
            retrograde_times.datetime,
            retrograde_ra,
            color="darkred",
            s=20,
            alpha=0.8,
            zorder=5,
            label="Retrograde Motion",
        )

        ax1.set_xlabel("Date")
        ax1.set_ylabel("Right Ascension (degrees)")
        ax1.set_title(f"{planet.title()} - Right Ascension vs Time")
        ax1.grid(True, alpha=0.3)
        ax1.legend()

        # Plot sky path (RA vs Dec)
        ax2 = axes[i, 1]
        ax2.plot(
            ra,
            dec,
            color=color,
            linewidth=2,
            alpha=0.7,
            label=f"{planet.title()} Path",
        )

        # Highlight retrograde portions in sky path
        retrograde_ra_path = ra[1:][retrograde_mask]
        retrograde_dec_path = dec[1:][retrograde_mask]
        ax2.plot(
            retrograde_ra_path,
            retrograde_dec_path,
            color="darkred",
            linewidth=3,
            alpha=0.9,
            label="Retrograde Loops",
        )

        # Mark start and end points
        ax2.scatter(
            ra[0],
            dec[0],
            color="green",
            s=100,
            marker="o",
            zorder=5,
            label="Start",
            edgecolor="black",
        )
        ax2.scatter(
            ra[-1],
            dec[-1],
            color="blue",
            s=100,
            marker="s",
            zorder=5,
            label="End",
            edgecolor="black",
        )

        ax2.set_xlabel("Right Ascension (degrees)")
        ax2.set_ylabel("Declination (degrees)")
        ax2.set_title(f"{planet.title()} - Sky Path with Retrograde Loops")
        ax2.grid(True, alpha=0.3)
        ax2.legend()
        ax2.invert_xaxis()  # RA increases to the left in sky coordinates

        # Calculate and print retrograde statistics
        total_retrograde_days = np.sum(retrograde_mask) * (times[1] - times[0]).jd
        print(
            f"{planet.title()} retrograde motion: {total_retrograde_days:.1f} days total",
        )

    plt.tight_layout()
    plt.show()


def plot_mars_detailed_retrograde():
    """Detailed plot of Mars retrograde motion for a specific period."""
    # Focus on a specific Mars retrograde period
    start_date = "2022-08-01"
    end_date = "2023-02-28"

    times, ra, dec = calculate_planet_positions("mars", start_date, end_date, 150)
    retrograde_mask = detect_retrograde_periods(times, ra)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    fig.suptitle(
        "Mars Retrograde Motion - Detailed View (Aug 2022 - Feb 2023)",
        fontsize=14,
        fontweight="bold",
    )

    # Time series plot
    ax1.plot(times.datetime, ra, "r-", linewidth=2, alpha=0.7, label="Mars RA")
    retrograde_times = times[1:][retrograde_mask]
    retrograde_ra = ra[1:][retrograde_mask]
    ax1.plot(
        retrograde_times.datetime,
        retrograde_ra,
        "darkred",
        linewidth=3,
        alpha=0.9,
        label="Retrograde Period",
    )

    ax1.set_xlabel("Date")
    ax1.set_ylabel("Right Ascension (degrees)")
    ax1.set_title("Mars Right Ascension vs Time")
    ax1.grid(True, alpha=0.3)
    ax1.legend()

    # Sky path with retrograde loop
    ax2.plot(ra, dec, "r-", linewidth=2, alpha=0.7, label="Mars Path")
    retrograde_ra_path = ra[1:][retrograde_mask]
    retrograde_dec_path = dec[1:][retrograde_mask]
    ax2.plot(
        retrograde_ra_path,
        retrograde_dec_path,
        "darkred",
        linewidth=4,
        alpha=0.9,
        label="Retrograde Loop",
    )

    # Add arrows to show direction
    for j in range(0, len(ra) - 10, 20):
        dx = ra[j + 5] - ra[j]
        dy = dec[j + 5] - dec[j]
        ax2.arrow(
            ra[j],
            dec[j],
            dx * 0.3,
            dy * 0.3,
            head_width=0.3,
            head_length=0.2,
            fc="red",
            ec="red",
            alpha=0.6,
        )

    ax2.scatter(
        ra[0],
        dec[0],
        color="green",
        s=100,
        marker="o",
        zorder=5,
        label="Start",
        edgecolor="black",
    )
    ax2.scatter(
        ra[-1],
        dec[-1],
        color="blue",
        s=100,
        marker="s",
        zorder=5,
        label="End",
        edgecolor="black",
    )

    ax2.set_xlabel("Right Ascension (degrees)")
    ax2.set_ylabel("Declination (degrees)")
    ax2.set_title("Mars Sky Path - Retrograde Loop Detail")
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    ax2.invert_xaxis()

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    print("Plotting planetary retrograde motion...")
    print("This may take a moment to calculate positions...")

    # Plot overview for multiple planets
    plot_retrograde_motion()

    # Detailed Mars retrograde plot
    plot_mars_detailed_retrograde()

    print("\nRetrograde motion explanation:")
    print("- Retrograde motion occurs when Earth overtakes outer planets in orbit")
    print("- The planet appears to move backwards against the star background")
    print("- Mars shows retrograde motion approximately every 26 months")
    print("- Jupiter shows retrograde motion approximately every 13 months")
    print(
        "- The loops in the sky path show the characteristic retrograde motion pattern",
    )
