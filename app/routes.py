from flask import Blueprint, request, jsonify
from .models import db, Player, Match

# Create a Blueprint for organizing routes
bp = Blueprint('routes', __name__)

# Example response to check if API is running
@bp.route('/', methods=['GET'])
def home():
    return jsonify({"message": "Welcome to the SCUTTA API!"})

@bp.route('/register-player', methods=['POST'])
def register_player():
    data = request.json  # Expecting {"names": ["Player1", "Player2", ...]}
    if not data or "names" not in data:
        return jsonify({"error": "Names are required"}), 400

    names = data["names"]
    response = {"registered": [], "already_exists": []}

    for name in names:
        if Player.query.filter_by(name=name).first():
            response["already_exists"].append(name)
        else:
            player = Player(name=name)
            db.session.add(player)
            response["registered"].append(name)

    db.session.commit()
    return jsonify(response)

@bp.route('/submit-match', methods=['POST'])
def submit_match():
    data = request.json  # Expecting {"winner": "Player1", "loser": "Player2", "set_score": "3:0"}
    if not data or not all(k in data for k in ("winner", "loser", "set_score")):
        return jsonify({"error": "Winner, loser, and set_score are required"}), 400

    winner = Player.query.filter_by(name=data["winner"]).first()
    loser = Player.query.filter_by(name=data["loser"]).first()

    if not winner or not loser:
        return jsonify({"error": "Winner or loser does not exist in database"}), 400

    match = Match(
        winner_id=winner.id,
        loser_id=loser.id,
        set_score=data["set_score"]
    )
    db.session.add(match)
    db.session.commit()

    return jsonify({"message": "Match submitted successfully!"})

@bp.route('/approve-match', methods=['POST'])
def approve_match():
    data = request.json  # Expecting {"match_ids": [1, 2, 3]} for selected approvals
    if not data or "match_ids" not in data:
        return jsonify({"error": "Match IDs are required"}), 400

    matches = Match.query.filter(Match.id.in_(data["match_ids"])).all()
    for match in matches:
        if not match.is_approved:
            # Update winner stats
            winner = Player.query.get(match.winner_id)
            winner.win_count += 1
            winner.match_count += 1

            # Update loser stats
            loser = Player.query.get(match.loser_id)
            loser.loss_count += 1
            loser.match_count += 1

            # Mark match as approved
            match.is_approved = True

            # Recalculate win rates
            winner.update_win_rate()
            loser.update_win_rate()

    db.session.commit()
    return jsonify({"message": f"{len(matches)} matches approved!"})

@bp.route('/leaderboard/<category>', methods=['GET'])
def leaderboard(category):
    valid_categories = {
        "wins": Player.win_count.desc(),
        "losses": Player.loss_count.desc(),
        "win_rate": Player.win_rate.desc(),
        "matches": Player.match_count.desc(),
        "opponents": Player.unique_opponents.desc()
    }

    if category not in valid_categories:
        return jsonify({"error": f"Invalid category. Choose from {list(valid_categories.keys())}"}), 400

    players = Player.query.order_by(valid_categories[category]).limit(10).all()
    response = [
        {"name": player.name, "rank": player.rank, category: getattr(player, category)}
        for player in players
    ]

    return jsonify(response)
