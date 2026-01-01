"""
Tournament API endpoints
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from models import db, Tournament, User

tournaments_bp = Blueprint('tournaments', __name__)

@tournaments_bp.route('', methods=['GET'])
def get_tournaments():
    """Get all tournaments"""
    tournaments = Tournament.query.all()
    return jsonify([t.to_dict() for t in tournaments]), 200

@tournaments_bp.route('/<int:tournament_id>', methods=['GET'])
def get_tournament(tournament_id):
    """Get a specific tournament"""
    tournament = Tournament.query.get(tournament_id)
    
    if not tournament:
        return jsonify({'error': 'Tournament not found'}), 404
    
    return jsonify(tournament.to_dict()), 200

@tournaments_bp.route('', methods=['POST'])
@jwt_required()
def create_tournament():
    """Create a new tournament"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user or user.role not in ['admin', 'organizer']:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['name', 'format', 'start_date', 'end_date']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Create tournament
    tournament = Tournament(
        name=data['name'],
        description=data.get('description'),
        format=data['format'],
        start_date=datetime.fromisoformat(data['start_date'].replace('Z', '+00:00')),
        end_date=datetime.fromisoformat(data['end_date'].replace('Z', '+00:00')),
        venue=data.get('venue'),
        num_rounds=data.get('num_rounds', 5),
        registration_fee=data.get('registration_fee', 0.0),
        max_participants=data.get('max_participants'),
        registration_deadline=datetime.fromisoformat(data['registration_deadline'].replace('Z', '+00:00')) if data.get('registration_deadline') else None,
        event_type=data.get('event_type', 'in-person'),
        organizer_id=user_id
    )
    
    db.session.add(tournament)
    db.session.commit()
    
    return jsonify({
        'message': 'Tournament created successfully',
        'tournament': tournament.to_dict()
    }), 201

@tournaments_bp.route('/<int:tournament_id>', methods=['PUT'])
@jwt_required()
def update_tournament(tournament_id):
    """Update a tournament"""
    user_id = get_jwt_identity()
    tournament = Tournament.query.get(tournament_id)
    
    if not tournament:
        return jsonify({'error': 'Tournament not found'}), 404
    
    if tournament.organizer_id != user_id:
        user = User.query.get(user_id)
        if not user or user.role != 'admin':
            return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    
    # Update fields
    if 'name' in data:
        tournament.name = data['name']
    if 'description' in data:
        tournament.description = data['description']
    if 'format' in data:
        tournament.format = data['format']
    if 'start_date' in data:
        tournament.start_date = datetime.fromisoformat(data['start_date'].replace('Z', '+00:00'))
    if 'end_date' in data:
        tournament.end_date = datetime.fromisoformat(data['end_date'].replace('Z', '+00:00'))
    if 'venue' in data:
        tournament.venue = data['venue']
    if 'num_rounds' in data:
        tournament.num_rounds = data['num_rounds']
    if 'registration_fee' in data:
        tournament.registration_fee = data['registration_fee']
    if 'max_participants' in data:
        tournament.max_participants = data['max_participants']
    if 'status' in data:
        tournament.status = data['status']
    if 'event_type' in data:
        tournament.event_type = data['event_type']
    
    db.session.commit()
    
    return jsonify({
        'message': 'Tournament updated successfully',
        'tournament': tournament.to_dict()
    }), 200

@tournaments_bp.route('/<int:tournament_id>', methods=['DELETE'])
@jwt_required()
def delete_tournament(tournament_id):
    """Delete a tournament"""
    user_id = get_jwt_identity()
    tournament = Tournament.query.get(tournament_id)
    
    if not tournament:
        return jsonify({'error': 'Tournament not found'}), 404
    
    if tournament.organizer_id != user_id:
        user = User.query.get(user_id)
        if not user or user.role != 'admin':
            return jsonify({'error': 'Unauthorized'}), 403
    
    db.session.delete(tournament)
    db.session.commit()
    
    return jsonify({'message': 'Tournament deleted successfully'}), 200

@tournaments_bp.route('/<int:tournament_id>/teams', methods=['GET'])
def get_tournament_teams(tournament_id):
    """Get all teams for a tournament"""
    tournament = Tournament.query.get(tournament_id)
    
    if not tournament:
        return jsonify({'error': 'Tournament not found'}), 404
    
    teams = tournament.teams.all()
    return jsonify([t.to_dict() for t in teams]), 200

@tournaments_bp.route('/<int:tournament_id>/standings', methods=['GET'])
def get_tournament_standings(tournament_id):
    """Get tournament standings"""
    tournament = Tournament.query.get(tournament_id)
    
    if not tournament:
        return jsonify({'error': 'Tournament not found'}), 404
    
    # Get teams sorted by points, then speaker points
    teams = tournament.teams.order_by(
        db.desc('points'),
        db.desc('speaker_points')
    ).all()
    
    standings = []
    for rank, team in enumerate(teams, 1):
        team_dict = team.to_dict()
        team_dict['rank'] = rank
        standings.append(team_dict)
    
    return jsonify(standings), 200
