import os

from shapely.coords import CoordinateSequence

class Missions:
	def __init__(self, drones, polygons, options=None):
		self.drones = drones
		self.polygons = polygons
		self.options = options or {}

		# handle defaults
		self.alt = self.options.get('alt', 3)
		self.speed = self.options.get('speed', 2)
		self.save_path = self.options.get('save_path', 'missions')
		self.close_loop = self.options.get('close_loop', True)

	# Generate groovy
	def generate(self):
		if len(self.drones) > len(self.polygons.geoms):
			raise ValueError('Not enough polygons to assign to drones')

		self.mission_files = []
		for i, drone in enumerate(self.drones):
			polygon = self.polygons.geoms[i]
			mission_file = f'{drone}_mission.groovy'
			
			coords = polygon.exterior.coords if self.close_loop else polygon.exterior.coords[:-1]

			file_content = (
				f'drone = assign {drone}' + '\n' 
				f'arm drone' + '\n'
				f'takeoff drone, {self.alt}.m'  + '\n'
				+ '\n'.join(
					[
						f'move drone,'
							f'lat: {coords[0]},'
							f'lon: {coords[1]},'
							f'alt: drone.position.alt,'
							f'speed: {self.speed}.m/s'
					for coords in coords]) + '\n'
				f'land drone'
			)

			self.mission_files.append({
				'drone': drone,
				'file': mission_file,
				'content': file_content,
			})

		return self.mission_files

	def save(self):
		# Create the save path
		if not os.path.exists(self.save_path):
			os.makedirs(self.save_path)

		for mission_file in self.mission_files:
			with open(os.path.join(self.save_path, mission_file['file']), 'w') as f:
				f.write(mission_file['content'])