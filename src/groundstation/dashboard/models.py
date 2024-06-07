from db_config import db

class Mission(db.Model):
	__tablename__ = 'mission'
	id = db.Column(db.Integer, primary_key=True)
	groundstation = db.Column(db.String(255), nullable=False)
	drone_id = db.Column(db.String(255), nullable=False)
	mission_id = db.Column(db.String(255), nullable=False)
	paused = db.Column(db.Boolean, default=False)