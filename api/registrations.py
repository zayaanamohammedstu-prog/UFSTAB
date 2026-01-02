"""
Registration API endpoints
"""
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
import os
import csv
import io
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

@registrations_bp.route('/tournament/<int:tournament_id>/import', methods=['POST'])
@jwt_required()
def import_registrations(tournament_id):
    """Import registrations from CSV file (Google Forms export or Excel)"""
    user_id = get_jwt_identity()
    tournament = Tournament.query.get(tournament_id)
    
    if not tournament:
        return jsonify({'error': 'Tournament not found'}), 404
    
    # Only organizer can import registrations
    if tournament.organizer_id != user_id:
        user = User.query.get(user_id)
        if not user or user.role != 'admin':
            return jsonify({'error': 'Unauthorized'}), 403
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Check file extension
    if not file.filename.lower().endswith(('.csv', '.xlsx', '.xls')):
        return jsonify({'error': 'File must be CSV or Excel format'}), 400
    
    try:
        imported_count = 0
        errors = []
        
        # Handle CSV files
        if file.filename.lower().endswith('.csv'):
            # Read CSV file
            stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
            csv_reader = csv.DictReader(stream)
            
            for row_num, row in enumerate(csv_reader, start=2):
                try:
                    # Expected columns: email, name, registration_type, team_name, partner_name, partner_email
                    # These can be customized based on Google Forms column names
                    
                    # Try to find or create user by email
                    email = row.get('email') or row.get('Email') or row.get('Email Address')
                    name = row.get('name') or row.get('Name') or row.get('Full Name')
                    
                    if not email:
                        errors.append(f"Row {row_num}: Missing email address")
                        continue
                    
                    # Find or create user
                    user = User.query.filter_by(email=email).first()
                    if not user:
                        # Create a basic user account
                        username = email.split('@')[0]
                        # Ensure unique username
                        base_username = username
                        counter = 1
                        while User.query.filter_by(username=username).first():
                            username = f"{base_username}{counter}"
                            counter += 1
                        
                        user = User(
                            email=email,
                            username=username,
                            full_name=name if name else email.split('@')[0],
                            role='user'
                        )
                        user.set_password('changeme123')  # Default password
                        db.session.add(user)
                        db.session.flush()  # Get user ID without committing
                    
                    # Check if already registered
                    existing = Registration.query.filter_by(
                        tournament_id=tournament_id,
                        user_id=user.id
                    ).first()
                    
                    if existing:
                        errors.append(f"Row {row_num}: {email} already registered")
                        continue
                    
                    # Get registration details
                    reg_type = row.get('registration_type') or row.get('Registration Type') or 'individual'
                    team_name = row.get('team_name') or row.get('Team Name')
                    partner_name = row.get('partner_name') or row.get('Partner Name')
                    partner_email = row.get('partner_email') or row.get('Partner Email')
                    
                    # Create registration
                    registration = Registration(
                        tournament_id=tournament_id,
                        user_id=user.id,
                        registration_type=reg_type.lower() if reg_type else 'individual',
                        team_name=team_name,
                        partner_name=partner_name,
                        partner_email=partner_email,
                        status='confirmed',  # Auto-confirm imported registrations
                        payment_status='completed'  # Assume payment is handled
                    )
                    
                    db.session.add(registration)
                    imported_count += 1
                    
                except Exception as e:
                    errors.append(f"Row {row_num}: {str(e)}")
        
        # Handle Excel files
        elif file.filename.lower().endswith(('.xlsx', '.xls')):
            try:
                import openpyxl
                workbook = openpyxl.load_workbook(file)
                sheet = workbook.active
                
                # Get headers from first row
                headers = [cell.value for cell in sheet[1]]
                
                for row_num, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=2):
                    try:
                        row_dict = dict(zip(headers, row))
                        
                        email = row_dict.get('email') or row_dict.get('Email') or row_dict.get('Email Address')
                        name = row_dict.get('name') or row_dict.get('Name') or row_dict.get('Full Name')
                        
                        if not email:
                            errors.append(f"Row {row_num}: Missing email address")
                            continue
                        
                        # Find or create user
                        user = User.query.filter_by(email=email).first()
                        if not user:
                            username = email.split('@')[0]
                            base_username = username
                            counter = 1
                            while User.query.filter_by(username=username).first():
                                username = f"{base_username}{counter}"
                                counter += 1
                            
                            user = User(
                                email=email,
                                username=username,
                                full_name=name if name else email.split('@')[0],
                                role='user'
                            )
                            user.set_password('changeme123')
                            db.session.add(user)
                            db.session.flush()
                        
                        # Check if already registered
                        existing = Registration.query.filter_by(
                            tournament_id=tournament_id,
                            user_id=user.id
                        ).first()
                        
                        if existing:
                            errors.append(f"Row {row_num}: {email} already registered")
                            continue
                        
                        reg_type = row_dict.get('registration_type') or row_dict.get('Registration Type') or 'individual'
                        team_name = row_dict.get('team_name') or row_dict.get('Team Name')
                        partner_name = row_dict.get('partner_name') or row_dict.get('Partner Name')
                        partner_email = row_dict.get('partner_email') or row_dict.get('Partner Email')
                        
                        registration = Registration(
                            tournament_id=tournament_id,
                            user_id=user.id,
                            registration_type=reg_type.lower() if reg_type else 'individual',
                            team_name=team_name,
                            partner_name=partner_name,
                            partner_email=partner_email,
                            status='confirmed',
                            payment_status='completed'
                        )
                        
                        db.session.add(registration)
                        imported_count += 1
                        
                    except Exception as e:
                        errors.append(f"Row {row_num}: {str(e)}")
                        
            except ImportError:
                return jsonify({'error': 'Excel support not available. Please install openpyxl.'}), 400
        
        # Commit all changes
        db.session.commit()
        
        return jsonify({
            'message': f'Import completed. {imported_count} registrations imported.',
            'imported_count': imported_count,
            'errors': errors
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Import failed: {str(e)}'}), 500
