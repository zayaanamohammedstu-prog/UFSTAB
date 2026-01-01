"""
Rounds and Pairings API endpoints
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
import random
from models import db, Round, Pairing, Team, Tournament, User, JudgeAssignment

rounds_bp = Blueprint('rounds', __name__)

@rounds_bp.route('', methods=['POST'])
@jwt_required()
def create_round():
    """Create a new round"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    # Validate required fields
    if 'tournament_id' not in data or 'round_number' not in data:
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Check tournament exists and user is organizer
    tournament = Tournament.query.get(data['tournament_id'])
    if not tournament:
        return jsonify({'error': 'Tournament not found'}), 404
    
    if tournament.organizer_id != user_id:
        user = User.query.get(user_id)
        if not user or user.role != 'admin':
            return jsonify({'error': 'Unauthorized'}), 403
    
    # Create round
    round_obj = Round(
        tournament_id=data['tournament_id'],
        round_number=data['round_number'],
        motion=data.get('motion'),
        info_slide=data.get('info_slide'),
        motion_release_time=datetime.fromisoformat(data['motion_release_time'].replace('Z', '+00:00')) if data.get('motion_release_time') else None
    )
    
    db.session.add(round_obj)
    db.session.commit()
    
    return jsonify({
        'message': 'Round created successfully',
        'round': round_obj.to_dict()
    }), 201

@rounds_bp.route('/<int:round_id>/generate-draw', methods=['POST'])
@jwt_required()
def generate_draw(round_id):
    """Generate pairings for a round"""
    user_id = get_jwt_identity()
    round_obj = Round.query.get(round_id)
    
    if not round_obj:
        return jsonify({'error': 'Round not found'}), 404
    
    # Check authorization
    tournament = round_obj.tournament
    if tournament.organizer_id != user_id:
        user = User.query.get(user_id)
        if not user or user.role != 'admin':
            return jsonify({'error': 'Unauthorized'}), 403
    
    # Get all teams
    teams = list(tournament.teams.all())
    
    if len(teams) < 4:
        return jsonify({'error': 'Need at least 4 teams to generate draw'}), 400
    
    # Shuffle teams for random pairing
    random.shuffle(teams)
    
    # Delete existing pairings
    Pairing.query.filter_by(round_id=round_id).delete()
    
    # Create pairings (4 teams per room for BP)
    positions = ['OG', 'OO', 'CG', 'CO']
    room_number = 1
    
    for i in range(0, len(teams) - 3, 4):
        for j, position in enumerate(positions):
            pairing = Pairing(
                round_id=round_id,
                team_id=teams[i + j].id,
                room=f"Room {room_number}",
                position=position
            )
            db.session.add(pairing)
        room_number += 1
    
    round_obj.status = 'active'
    db.session.commit()
    
    return jsonify({
        'message': 'Draw generated successfully',
        'pairings': [p.to_dict() for p in round_obj.pairings.all()]
    }), 200

@rounds_bp.route('/<int:round_id>/pairings', methods=['GET'])
def get_round_pairings(round_id):
    """Get pairings for a round"""
    round_obj = Round.query.get(round_id)
    
    if not round_obj:
        return jsonify({'error': 'Round not found'}), 404
    
    # Group pairings by room
    pairings_by_room = {}
    for pairing in round_obj.pairings.all():
        room = pairing.room
        if room not in pairings_by_room:
            pairings_by_room[room] = []
        
        pairing_dict = pairing.to_dict()
        # Add judge assignments
        pairing_dict['judges'] = [ja.to_dict() for ja in pairing.judge_assignments.all()]
        pairings_by_room[room].append(pairing_dict)
    
    return jsonify({
        'round': round_obj.to_dict(),
        'pairings': pairings_by_room
    }), 200

@rounds_bp.route('/<int:round_id>', methods=['PUT'])
@jwt_required()
def update_round(round_id):
    """Update a round"""
    user_id = get_jwt_identity()
    round_obj = Round.query.get(round_id)
    
    if not round_obj:
        return jsonify({'error': 'Round not found'}), 404
    
    # Check authorization
    tournament = round_obj.tournament
    if tournament.organizer_id != user_id:
        user = User.query.get(user_id)
        if not user or user.role != 'admin':
            return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    
    # Update fields
    if 'motion' in data:
        round_obj.motion = data['motion']
    if 'info_slide' in data:
        round_obj.info_slide = data['info_slide']
    if 'status' in data:
        round_obj.status = data['status']
    if 'motion_release_time' in data:
        round_obj.motion_release_time = datetime.fromisoformat(data['motion_release_time'].replace('Z', '+00:00'))
    
    db.session.commit()
    
    return jsonify({
        'message': 'Round updated successfully',
        'round': round_obj.to_dict()
    }), 200
