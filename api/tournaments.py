"""
Tournament API endpoints
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
import re
from models import db, Tournament, User

tournaments_bp = Blueprint('tournaments', __name__)

def generate_slug(name, tournament_id=None):
    """Generate a URL-friendly slug from tournament name"""
    # Convert to lowercase and replace spaces with hyphens
    slug = re.sub(r'[^\w\s-]', '', name.lower())
    slug = re.sub(r'[-\s]+', '-', slug).strip('-')
    
    # Ensure uniqueness
    base_slug = slug
    counter = 1
    while True:
        existing = Tournament.query.filter_by(slug=slug).first()
        if not existing or (tournament_id and existing.id == tournament_id):
            break
        slug = f"{base_slug}-{counter}"
        counter += 1
    
    return slug

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
    
    # Generate slug
    slug = generate_slug(data['name'])
    
    # Create tournament
    tournament = Tournament(
        name=data['name'],
        slug=slug,
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
        custom_logo_url=data.get('custom_logo_url'),
        primary_color=data.get('primary_color', '#3b82f6'),
        secondary_color=data.get('secondary_color', '#10b981'),
        custom_css=data.get('custom_css'),
        show_public_tab=data.get('show_public_tab', True),
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
        # Regenerate slug if name changes
        tournament.slug = generate_slug(data['name'], tournament.id)
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
    
    # Update customization fields
    if 'custom_logo_url' in data:
        tournament.custom_logo_url = data['custom_logo_url']
    if 'primary_color' in data:
        tournament.primary_color = data['primary_color']
    if 'secondary_color' in data:
        tournament.secondary_color = data['secondary_color']
    if 'custom_css' in data:
        tournament.custom_css = data['custom_css']
    if 'show_public_tab' in data:
        tournament.show_public_tab = data['show_public_tab']
    
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

@tournaments_bp.route('/public/<slug>', methods=['GET'])
def get_tournament_by_slug(slug):
    """Get tournament by slug for public display (no authentication required)"""
    tournament = Tournament.query.filter_by(slug=slug).first()
    
    if not tournament:
        return jsonify({'error': 'Tournament not found'}), 404
    
    if not tournament.show_public_tab:
        return jsonify({'error': 'Public display is not enabled for this tournament'}), 403
    
    # Return tournament data without sensitive organizer information
    return jsonify(tournament.to_dict(include_organizer=False)), 200

@tournaments_bp.route('/public/<slug>/teams', methods=['GET'])
def get_public_tournament_teams(slug):
    """Get teams for public display"""
    tournament = Tournament.query.filter_by(slug=slug).first()
    
    if not tournament:
        return jsonify({'error': 'Tournament not found'}), 404
    
    if not tournament.show_public_tab:
        return jsonify({'error': 'Public display is not enabled for this tournament'}), 403
    
    teams = tournament.teams.all()
    return jsonify([t.to_dict() for t in teams]), 200

@tournaments_bp.route('/public/<slug>/standings', methods=['GET'])
def get_public_tournament_standings(slug):
    """Get standings for public display"""
    tournament = Tournament.query.filter_by(slug=slug).first()
    
    if not tournament:
        return jsonify({'error': 'Tournament not found'}), 404
    
    if not tournament.show_public_tab:
        return jsonify({'error': 'Public display is not enabled for this tournament'}), 403
    
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
