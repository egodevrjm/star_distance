#!/usr/bin/env python3

from astropy import units as u
from astropy.coordinates import SkyCoord
from astroquery.gaia import Gaia
import matplotlib.pyplot as plt
import numpy as np

def nearby_stars(max_distance):
	# Convert max_distance to parsecs
	max_distance_pc = max_distance.to(u.pc).value
	
	# Query Gaia DR2 for nearby stars within the specified distance range
	query = f"""
	SELECT source_id, ra, dec, parallax
	FROM gaiadr2.gaia_source
	WHERE parallax >= {1 / max_distance_pc} AND parallax IS NOT NULL
	"""
	job = Gaia.launch_job(query)
	result_table = job.get_results()
	
	if len(result_table) == 0:
		print("No nearby stars found within the specified distance.")
		return
	
	# Calculate distances in parsecs using parallax
	parallaxes = result_table['parallax'].data
	valid_parallaxes = parallaxes > 0
	distances = (1 / parallaxes[valid_parallaxes]) * u.pc
	
	# Convert right ascension and declination to radians
	ra_rad = np.radians(result_table['ra'][valid_parallaxes].data)
	dec_rad = np.radians(result_table['dec'][valid_parallaxes].data)
	
	# Convert distances and angles to Cartesian coordinates
	x = distances * np.cos(dec_rad) * np.cos(ra_rad)
	y = distances * np.cos(dec_rad) * np.sin(ra_rad)
	
	# Create a plot with a dark background
	fig, ax = plt.subplots(figsize=(10, 10), facecolor='black')
	ax.set_facecolor('black')
	
	# Plot the Sun at the center with a glowing effect
	sun_size = 200
	sun_glow = plt.Circle((0, 0), sun_size * 0.7, color='orange', alpha=0.3)
	ax.add_artist(sun_glow)
	sun_plot = ax.scatter(0, 0, c='yellow', s=sun_size, label='Sun', zorder=10)
	
	# Plot the nearby stars with varying sizes based on distance
	max_star_size = 100
	min_star_size = 10
	star_sizes = (1 - (distances - distances.min()) / (distances.max() - distances.min())) * (max_star_size - min_star_size) + min_star_size
	star_colors = plt.cm.coolwarm(1 - (distances - distances.min()) / (distances.max() - distances.min()))
	star_plot = ax.scatter(x, y, c=star_colors, s=star_sizes, alpha=0.8, zorder=5, label='Nearby Stars')
	
	# Set the limits and labels for the plot
	ax.set_xlim(-max_distance.to(u.pc).value, max_distance.to(u.pc).value)
	ax.set_ylim(-max_distance.to(u.pc).value, max_distance.to(u.pc).value)
	ax.set_xlabel('Distance (parsecs)', color='white')
	ax.set_ylabel('Distance (parsecs)', color='white')
	ax.set_title(f'Nearby Stars within {max_distance:.2f}', color='white', fontsize=16)
	
	# Create a legend
	legend = ax.legend(handles=[sun_plot, star_plot], fontsize=12, loc='upper right', facecolor='black', edgecolor='white')
	for text in legend.get_texts():
		text.set_color('white')
		
	# Add a colorbar to represent the distance scale
	cbar = plt.colorbar(star_plot, ax=ax, label='Distance (parsecs)')
	cbar.set_label('Distance (parsecs)', color='white', fontsize=12)
	cbar.ax.yaxis.set_tick_params(color='white', labelcolor='white')
	cbar.outline.set_edgecolor('white')
	plt.setp(plt.getp(cbar.ax.axes, 'yticklabels'), color='white')
	
	# Set the tick labels and grid color
	ax.tick_params(axis='both', which='major', labelsize=12, colors='white')
	ax.tick_params(axis='both', which='minor', labelsize=8, colors='white')
	ax.grid(color='gray', linestyle=':', linewidth=0.5, alpha=0.5)
	
	# Display the plot
	plt.tight_layout()
	plt.show()
	
# Get user input for the maximum distance
max_distance_input = float(input("Enter the maximum distance in light-years: "))
max_distance = max_distance_input * u.lyr

nearby_stars(max_distance)