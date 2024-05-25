from geometry import PolygonDivision
from mission import Missions
from examples import POLYGONS

POLYGON = POLYGONS[0] 
STARTING_POINT_INDEX = 1
RESIZE_SCALE = 0.9

def main():
	division = PolygonDivision(POLYGON)
	
	division.split(point_index=STARTING_POINT_INDEX)
	division.resize(scale=RESIZE_SCALE)
	division.print()

	missions = Missions(
		drones=['drone01', 'drone02'],
		polygons=division.split_polygons,
		options={
			'alt': 3,
			'speed': 2,
			'save_path': 'missions',
			'close_loop': False
		}
	)

	missions.generate()
	missions.save()

	division.plot()

if __name__ == "__main__":
	main()