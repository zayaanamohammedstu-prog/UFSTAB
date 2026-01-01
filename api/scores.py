"""
Scores API endpoints
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Score, Pairing, Team, User

scores_bp = Blueprint('scores', __name__)

@scores_bp.route('', methods=['POST'])
@jwt_required()
def create_score():
    """Create a new score"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['pairing_id', 'speaker_name', 'score']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Check pairing exists
    pairing = Pairing.query.get(data['pairing_id'])
    if not pairing:
        return jsonify({'error': 'Pairing not found'}), 404
    
    # Check authorization (must be judge or organizer)
    tournament = pairing.round.tournament
    user = User.query.get(user_id)
    
    is_authorized = (
        tournament.organizer_id == user_id or
        user.role in ['admin', 'judge']
    )
    
    if not is_authorized:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Create score
    score = Score(
        pairing_id=data['pairing_id'],
        speaker_name=data['speaker_name'],
        score=data['score'],
        feedback=data.get('feedback'),
        rank=data.get('rank')
    )
    
    db.session.add(score)
    db.session.commit()
    
    # Update team standings
    if score.rank:
        update_team_standings(pairing.team_id, score.score, score.rank)
    
    return jsonify({
        'message': 'Score created successfully',
        'score': score.to_dict()
    }), 201

@scores_bp.route('/pairing/<int:pairing_id>', methods=['GET'])
def get_pairing_scores(pairing_id):
    """Get all scores for a pairing"""
    pairing = Pairing.query.get(pairing_id)
    
    if not pairing:
        return jsonify({'error': 'Pairing not found'}), 404
    
    scores = pairing.scores.all()
    return jsonify([s.to_dict() for s in scores]), 200

@scores_bp.route('/<int:score_id>', methods=['PUT'])
@jwt_required()
def update_score(score_id):
    """Update a score"""
    user_id = get_jwt_identity()
    score = Score.query.get(score_id)
    
    if not score:
        return jsonify({'error': 'Score not found'}), 404
    
    # Check authorization
    tournament = score.pairing.round.tournament
    user = User.query.get(user_id)
    
    is_authorized = (
        tournament.organizer_id == user_id or
        user.role in ['admin', 'judge']
    )
    
    if not is_authorized:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    
    # Update fields
    if 'score' in data:
        score.score = data['score']
    if 'feedback' in data:
        score.feedback = data['feedback']
    if 'rank' in data:
        score.rank = data['rank']
    
    db.session.commit()
    
    # Update team standings
    if score.rank:
        update_team_standings(score.pairing.team_id, score.score, score.rank)
    
    return jsonify({
        'message': 'Score updated successfully',
        'score': score.to_dict()
    }), 200

@scores_bp.route('/<int:score_id>', methods=['DELETE'])
@jwt_required()
def delete_score(score_id):
    """Delete a score"""
    user_id = get_jwt_identity()
    score = Score.query.get(score_id)
    
    if not score:
        return jsonify({'error': 'Score not found'}), 404
    
    # Check authorization
    tournament = score.pairing.round.tournament
    user = User.query.get(user_id)
    
    is_authorized = (
        tournament.organizer_id == user_id or
        user.role == 'admin'
    )
    
    if not is_authorized:
        return jsonify({'error': 'Unauthorized'}), 403
    
    db.session.delete(score)
    db.session.commit()
    
    return jsonify({'message': 'Score deleted successfully'}), 200

def update_team_standings(team_id, score_value, rank):
    """Update team points and speaker points"""
    team = Team.query.get(team_id)
    if not team:
        return
    
    # BP points: 1st=3pts, 2nd=2pts, 3rd=1pt, 4th=0pts
    points_map = {1: 3, 2: 2, 3: 1, 4: 0}
    team.points += points_map.get(rank, 0)
    
    if rank == 1:
        team.wins += 1
    
    team.speaker_points += score_value
    db.session.commit()
