import os
import time
from shapely.geometry import LineString, Point, Polygon, GeometryCollection
from shapely.ops import split
import math

import matplotlib.pyplot as plt

class PolygonDivision:
	def __init__(self, points):
		self.polygon = Polygon(points)
		self.centroid = self.polygon.centroid
		self.bounds = self.polygon.bounds
		self.diagonal = math.sqrt((self.bounds[2] - self.bounds[0])**2 + (self.bounds[3] - self.bounds[1])**2)
		
	def split(self, point_index=0):
		if point_index >= len(self.polygon.exterior.coords):
			raise ValueError('Invalid point index')
			
		self.p1 = Point(self.polygon.exterior.coords[point_index])

		dir_vector = (self.p1.x - self.centroid.x, self.p1.y - self.centroid.y)
		length = math.sqrt(dir_vector[0]**2 + dir_vector[1]**2)
		direction = (dir_vector[0] / length, dir_vector[1] / length)

		# get a second point that goes through the centroid and the opposite side of the polygon
		self.p2 = Point(self.p1.x - direction[0] * self.diagonal, self.p1.y - direction[1] * self.diagonal)

		self.split_line = LineString([self.p1, self.p2])

		# split the polygon
		self.split_polygons = split(self.polygon, self.split_line)

		return self.split_polygons.geoms

	def polygons(self):
		polygons = [list(polygon.exterior.coords) for polygon in self.split_polygons.geoms]
		return polygons
		
	def resize(self, scale):
		self.split_polygons = GeometryCollection([PolygonDivision.resize_polygon(polygon, scale) for polygon in self.split_polygons.geoms])

	def plot(self, show=True):
		# Plot the original polygon
		plt.figure(figsize=(10, 10))
		x, y = self.polygon.exterior.xy
		plt.plot(x, y, color='blue', linewidth=2, label='Original Polygon')

		# plot the centroid
		plt.plot(self.centroid.x, self.centroid.y, 'go', label='Centroid')
		
		# plot point and point2
		plt.plot(self.p1.x, self.p1.y, 'go', label='Point 1')
		plt.plot(self.p2.x, self.p2.y, 'go', label='Point 2')

		# plot the split line
		x, y = self.split_line.xy
		plt.plot(x, y, color='green', linewidth=2, label='Split Line')

		# plot the split polygons
		for polygon in self.split_polygons.geoms:
			x, y = polygon.exterior.xy
			plt.plot(x, y, color='red', linewidth=2, label='Split Polygon')

			# draw polygon vertices
			for coord in polygon.exterior.coords[:-1]:
				plt.plot(coord[0], coord[1], 'ro')

		# Configure the plot
		plt.xlabel('Longitude')
		plt.ylabel('Latitude')
		plt.legend()
		plt.title('Polygon Split by Line')

		if show:
			plt.show()
		

		# create plots directory if it doesn't exist
		if not os.path.exists('plots'):
			os.makedirs('plots')

		ms = int(round(time.time() * 1000))
		path = f'plots/polygon-{ms}.png'
		plt.savefig(path)

		return path

	def print(self):
		for polygon in self.split_polygons.geoms:
			print(f"Polygon ({len(polygon.exterior.coords)-1}):")
			for coord in polygon.exterior.coords[:-1]:
				print(f'({coord[0]}, {coord[1]})')
			print()

	@staticmethod
	def resize_polygon(polygon, scale):
		centroid = polygon.centroid
		resized_coords = []
		for coord in polygon.exterior.coords:
			x = centroid.x + scale * (coord[0] - centroid.x)
			y = centroid.y + scale * (coord[1] - centroid.y)
			resized_coords.append((x, y))

		return Polygon(resized_coords)