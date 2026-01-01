"""
Registration API endpoints
"""
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
import os
from models import db, Registration, Tournament, User

registrations_bp = Blueprint('registrations', __name__)

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@registrations_bp.route('', methods=['POST'])
@jwt_required()
def create_registration():
    """Create a new registration"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    # Validate required fields
    if 'tournament_id' not in data or 'registration_type' not in data:
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Check tournament exists
    tournament = Tournament.query.get(data['tournament_id'])
    if not tournament:
        return jsonify({'error': 'Tournament not found'}), 404
    
    # Check if already registered
    existing = Registration.query.filter_by(
        tournament_id=data['tournament_id'],
        user_id=user_id
    ).first()
    
    if existing:
        return jsonify({'error': 'Already registered for this tournament'}), 400
    
    # Check if tournament is full
    if tournament.max_participants:
        current_count = Registration.query.filter_by(
            tournament_id=data['tournament_id'],
            status='confirmed'
        ).count()
        
        if current_count >= tournament.max_participants:
            status = 'waitlist'
        else:
            status = 'pending'
    else:
        status = 'pending'
    
    # Create registration
    registration = Registration(
        tournament_id=data['tournament_id'],
        user_id=user_id,
        registration_type=data['registration_type'],
        team_name=data.get('team_name'),
        partner_name=data.get('partner_name'),
        partner_email=data.get('partner_email'),
        status=status
    )
    
    db.session.add(registration)
    db.session.commit()
    
    return jsonify({
        'message': 'Registration created successfully',
        'registration': registration.to_dict()
    }), 201

@registrations_bp.route('/<int:registration_id>/upload', methods=['POST'])
@jwt_required()
def upload_document(registration_id):
    """Upload document for registration"""
    user_id = get_jwt_identity()
    registration = Registration.query.get(registration_id)
    
    if not registration:
        return jsonify({'error': 'Registration not found'}), 404
    
    if registration.user_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed'}), 400
    
    # Save file
    filename = secure_filename(f"{user_id}_{registration_id}_{file.filename}")
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    
    # Update registration
    registration.document_url = filepath
    db.session.commit()
    
    return jsonify({
        'message': 'Document uploaded successfully',
        'filename': filename
    }), 200

@registrations_bp.route('/<int:registration_id>/payment', methods=['POST'])
@jwt_required()
def process_payment(registration_id):
    """Process payment for registration"""
    user_id = get_jwt_identity()
    registration = Registration.query.get(registration_id)
    
    if not registration:
        return jsonify({'error': 'Registration not found'}), 404
    
    if registration.user_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    
    # In production, integrate with Stripe API
    # For now, just mark as completed
    registration.payment_status = 'completed'
    registration.payment_id = data.get('payment_id', 'manual')
    registration.status = 'confirmed'
    
    db.session.commit()
    
    return jsonify({
        'message': 'Payment processed successfully',
        'registration': registration.to_dict()
    }), 200

@registrations_bp.route('/tournament/<int:tournament_id>', methods=['GET'])
@jwt_required()
def get_tournament_registrations(tournament_id):
    """Get all registrations for a tournament"""
    user_id = get_jwt_identity()
    tournament = Tournament.query.get(tournament_id)
    
    if not tournament:
        return jsonify({'error': 'Tournament not found'}), 404
    
    # Only organizer can view all registrations
    if tournament.organizer_id != user_id:
        user = User.query.get(user_id)
        if not user or user.role != 'admin':
            return jsonify({'error': 'Unauthorized'}), 403
    
    registrations = Registration.query.filter_by(tournament_id=tournament_id).all()
    return jsonify([r.to_dict() for r in registrations]), 200

@registrations_bp.route('/my-registrations', methods=['GET'])
@jwt_required()
def get_my_registrations():
    """Get current user's registrations"""
    user_id = get_jwt_identity()
    registrations = Registration.query.filter_by(user_id=user_id).all()
    return jsonify([r.to_dict() for r in registrations]), 200

@registrations_bp.route('/<int:registration_id>', methods=['DELETE'])
@jwt_required()
def cancel_registration(registration_id):
    """Cancel a registration"""
    user_id = get_jwt_identity()
    registration = Registration.query.get(registration_id)
    
    if not registration:
        return jsonify({'error': 'Registration not found'}), 404
    
    if registration.user_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    registration.status = 'cancelled'
    db.session.commit()
    
    # Check waitlist and promote next person
    if registration.tournament.max_participants:
        waitlist = Registration.query.filter_by(
            tournament_id=registration.tournament_id,
            status='waitlist'
        ).order_by(Registration.created_at).first()
        
        if waitlist:
            waitlist.status = 'pending'
            db.session.commit()
    
    return jsonify({'message': 'Registration cancelled successfully'}), 200
