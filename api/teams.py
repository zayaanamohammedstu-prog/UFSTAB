"""
Teams API endpoints
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Team, Tournament, User

teams_bp = Blueprint('teams', __name__)

@teams_bp.route('', methods=['POST'])
@jwt_required()
def create_team():
    """Create a new team"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['tournament_id', 'name', 'speaker1_name', 'speaker2_name']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Check tournament exists and user is organizer
    tournament = Tournament.query.get(data['tournament_id'])
    if not tournament:
        return jsonify({'error': 'Tournament not found'}), 404
    
    if tournament.organizer_id != user_id:
        user = User.query.get(user_id)
        if not user or user.role != 'admin':
            return jsonify({'error': 'Unauthorized'}), 403
    
    # Create team
    team = Team(
        tournament_id=data['tournament_id'],
        name=data['name'],
        institution=data.get('institution'),
        speaker1_name=data['speaker1_name'],
        speaker2_name=data['speaker2_name']
    )
    
    db.session.add(team)
    db.session.commit()
    
    return jsonify({
        'message': 'Team created successfully',
        'team': team.to_dict()
    }), 201

@teams_bp.route('/<int:team_id>', methods=['GET'])
def get_team(team_id):
    """Get a specific team"""
    team = Team.query.get(team_id)
    
    if not team:
        return jsonify({'error': 'Team not found'}), 404
    
    return jsonify(team.to_dict()), 200

@teams_bp.route('/<int:team_id>', methods=['PUT'])
@jwt_required()
def update_team(team_id):
    """Update a team"""
    user_id = get_jwt_identity()
    team = Team.query.get(team_id)
    
    if not team:
        return jsonify({'error': 'Team not found'}), 404
    
    # Check authorization
    tournament = team.tournament
    if tournament.organizer_id != user_id:
        user = User.query.get(user_id)
        if not user or user.role != 'admin':
            return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    
    # Update fields
    if 'name' in data:
        team.name = data['name']
    if 'institution' in data:
        team.institution = data['institution']
    if 'speaker1_name' in data:
        team.speaker1_name = data['speaker1_name']
    if 'speaker2_name' in data:
        team.speaker2_name = data['speaker2_name']
    
    db.session.commit()
    
    return jsonify({
        'message': 'Team updated successfully',
        'team': team.to_dict()
    }), 200

@teams_bp.route('/<int:team_id>', methods=['DELETE'])
@jwt_required()
def delete_team(team_id):
    """Delete a team"""
    user_id = get_jwt_identity()
    team = Team.query.get(team_id)
    
    if not team:
        return jsonify({'error': 'Team not found'}), 404
    
    # Check authorization
    tournament = team.tournament
    if tournament.organizer_id != user_id:
        user = User.query.get(user_id)
        if not user or user.role != 'admin':
            return jsonify({'error': 'Unauthorized'}), 403
    
    db.session.delete(team)
    db.session.commit()
    
    return jsonify({'message': 'Team deleted successfully'}), 200
