from db_config import db

class Mission(db.Model):
	__tablename__ = 'mission'
	id = db.Column(db.Integer, primary_key=True)
	groundstation = db.Column(db.String(255), nullable=False)
	drone_id = db.Column(db.String(255), nullable=False)
	drone_server = db.Column(db.String(255), nullable=False)
	mission_id = db.Column(db.String(255), nullable=False)
	mission_file = db.Column(db.Integer, db.ForeignKey('mission_file.id', ondelete='CASCADE'), nullable=False)
	paused = db.Column(db.Boolean, default=False)

class MissionFile(db.Model):
	__tablename__ = 'mission_file'
	id = db.Column(db.Integer, primary_key=True)
	file = db.Column(db.String(255), nullable=False)
	center = db.Column(db.Integer, db.ForeignKey('mission_coords.id', ondelete='CASCADE'), nullable=True)
	
class MissionCoords(db.Model):
	__tablename__ = 'mission_coords'
	id = db.Column(db.Integer, primary_key=True)
	mission_file = db.Column(db.Integer, db.ForeignKey('mission_file.id', ondelete='CASCADE'), nullable=False)
	lat = db.Column(db.Float, nullable=False)
	lon = db.Column(db.Float, nullable=False)