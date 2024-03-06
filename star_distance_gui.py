#!/usr/bin/env python3

import sys
from astropy import units as u
from astroquery.gaia import Gaia
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget

class NearbyStarsApp(QMainWindow):
	def __init__(self):
		super().__init__()
		self.setWindowTitle('Nearby Stars')
		self.setGeometry(100, 100, 800, 600)
		
		# Create a figure and canvas for the plot
		self.fig, self.ax = plt.subplots(figsize=(8, 8), facecolor='black')
		self.canvas = FigureCanvas(self.fig)
		
		# Create GUI components
		self.label = QLabel('Enter the maximum distance in light-years:')
		self.input_field = QLineEdit()
		self.plot_button = QPushButton('Plot Nearby Stars')
		self.plot_button.clicked.connect(self.plot_nearby_stars)
		
		# Create layout and add components
		layout = QVBoxLayout()
		layout.addWidget(self.canvas)
		layout.addWidget(self.label)
		layout.addWidget(self.input_field)
		layout.addWidget(self.plot_button)
		
		# Create a central widget and set the layout
		central_widget = QWidget()
		central_widget.setLayout(layout)
		self.setCentralWidget(central_widget)
		
	def plot_nearby_stars(self):
		max_distance_input = float(self.input_field.text())
		max_distance = max_distance_input * u.lyr
		
		# Query Gaia DR2 for nearby stars within the specified distance range
		max_distance_pc = max_distance.to(u.pc).value
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
		
		# Recreate the figure and axes to ensure it's cleared
		self.fig.clf()  # Clear the figure completely
		self.ax = self.fig.add_subplot(111, facecolor='black')  # Recreate the axes on the cleared figure
		
		
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
		
		# Clear the previous plot
		self.ax.clear()
		
		# Plot the Sun at the center with a glowing effect
		sun_size = 200
		sun_glow = plt.Circle((0, 0), sun_size * 0.7, color='orange', alpha=0.3)
		self.ax.add_artist(sun_glow)
		sun_plot = self.ax.scatter(0, 0, c='yellow', s=sun_size, label='Sun', zorder=10)
		
		# Plot the nearby stars with varying sizes based on distance
		max_star_size = 100
		min_star_size = 10
		star_sizes = (1 - (distances - distances.min()) / (distances.max() - distances.min())) * (max_star_size - min_star_size) + min_star_size
		star_colors = plt.cm.coolwarm(1 - (distances - distances.min()) / (distances.max() - distances.min()))
		star_plot = self.ax.scatter(x, y, c=star_colors, s=star_sizes, alpha=0.8, zorder=5, label='Nearby Stars')
		
		# Set the limits and labels for the plot
		self.ax.set_xlim(-max_distance.to(u.pc).value, max_distance.to(u.pc).value)
		self.ax.set_ylim(-max_distance.to(u.pc).value, max_distance.to(u.pc).value)
		self.ax.set_xlabel('Distance (parsecs)', color='white')
		self.ax.set_ylabel('Distance (parsecs)', color='white')
		self.ax.set_title(f'Nearby Stars within {max_distance:.2f}', color='white', fontsize=16)
		
		# Create a legend
		legend = self.ax.legend(handles=[sun_plot, star_plot], fontsize=12, loc='upper right', facecolor='black', edgecolor='white')
		for text in legend.get_texts():
			text.set_color('white')
			
		# Add a colorbar to represent the distance scale
		cbar = plt.colorbar(star_plot, ax=self.ax, label='Distance (parsecs)')
		cbar.set_label('Distance (parsecs)', color='white', fontsize=12)
		cbar.ax.yaxis.set_tick_params(color='white', labelcolor='white')
		cbar.outline.set_edgecolor('white')
		plt.setp(plt.getp(cbar.ax.axes, 'yticklabels'), color='white')
		
		# Set the tick labels and grid color
		self.ax.tick_params(axis='both', which='major', labelsize=12, colors='white')
		self.ax.tick_params(axis='both', which='minor', labelsize=8, colors='white')
		self.ax.grid(color='gray', linestyle=':', linewidth=0.5, alpha=0.5)
		
		# Redraw the canvas
		self.canvas.draw()
		
if __name__ == '__main__':
	app = QApplication(sys.argv)
	nearby_stars_app = NearbyStarsApp()
	nearby_stars_app.show()
	sys.exit(app.exec_())