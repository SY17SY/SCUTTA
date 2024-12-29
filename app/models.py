from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False, unique=True)
    previous_rank = db.Column(db.String(10), default=None)
    rank = db.Column(db.String(10), default=None)
    rank_change = db.Column(db.String(10), default=None)
    match_count = db.Column(db.Integer, default=0)
    win_count = db.Column(db.Integer, default=0)
    loss_count = db.Column(db.Integer, default=0)
    win_rate = db.Column(db.Float, default=0.0)
    unique_opponents = db.Column(db.Integer, default=0)

    def update_win_rate(self):
        if self.match_count > 0:
            self.win_rate = self.win_count / self.match_count

class Match(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    winner_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)
    loser_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)
    set_score = db.Column(db.String(10), nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
    is_approved = db.Column(db.Boolean, default=False)
