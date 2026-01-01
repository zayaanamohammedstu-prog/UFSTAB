"""
Database models for OratorHub
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    """User model for authentication and authorization"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(120))
    role = db.Column(db.String(20), default='user')  # user, judge, admin, organizer
    institution = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    tournaments_organized = db.relationship('Tournament', back_populates='organizer', lazy='dynamic')
    registrations = db.relationship('Registration', back_populates='user', lazy='dynamic')
    judge_assignments = db.relationship('JudgeAssignment', back_populates='judge', lazy='dynamic')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password against hash"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'full_name': self.full_name,
            'role': self.role,
            'institution': self.institution,
            'created_at': self.created_at.isoformat(),
            'is_active': self.is_active
        }

class Tournament(db.Model):
    """Tournament model"""
    __tablename__ = 'tournaments'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    format = db.Column(db.String(50), nullable=False)  # BP, APDA, WSDC, etc.
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    venue = db.Column(db.String(200))
    num_rounds = db.Column(db.Integer, default=5)
    registration_fee = db.Column(db.Float, default=0.0)
    max_participants = db.Column(db.Integer)
    registration_deadline = db.Column(db.DateTime)
    event_type = db.Column(db.String(20), default='in-person')  # in-person, virtual, hybrid
    status = db.Column(db.String(20), default='upcoming')  # upcoming, ongoing, completed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign Keys
    organizer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    organizer = db.relationship('User', back_populates='tournaments_organized')
    registrations = db.relationship('Registration', back_populates='tournament', lazy='dynamic', cascade='all, delete-orphan')
    rounds = db.relationship('Round', back_populates='tournament', lazy='dynamic', cascade='all, delete-orphan')
    teams = db.relationship('Team', back_populates='tournament', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'format': self.format,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat(),
            'venue': self.venue,
            'num_rounds': self.num_rounds,
            'registration_fee': self.registration_fee,
            'max_participants': self.max_participants,
            'registration_deadline': self.registration_deadline.isoformat() if self.registration_deadline else None,
            'event_type': self.event_type,
            'status': self.status,
            'organizer': self.organizer.to_dict() if self.organizer else None
        }

class Registration(db.Model):
    """Registration model for tournament participants"""
    __tablename__ = 'registrations'
    
    id = db.Column(db.Integer, primary_key=True)
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournaments.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    registration_type = db.Column(db.String(20), nullable=False)  # individual, team
    team_name = db.Column(db.String(200))
    partner_name = db.Column(db.String(120))
    partner_email = db.Column(db.String(120))
    payment_status = db.Column(db.String(20), default='pending')  # pending, completed, refunded
    payment_id = db.Column(db.String(200))
    status = db.Column(db.String(20), default='pending')  # pending, confirmed, waitlist, cancelled
    document_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tournament = db.relationship('Tournament', back_populates='registrations')
    user = db.relationship('User', back_populates='registrations')
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'tournament_id': self.tournament_id,
            'user': self.user.to_dict() if self.user else None,
            'registration_type': self.registration_type,
            'team_name': self.team_name,
            'partner_name': self.partner_name,
            'payment_status': self.payment_status,
            'status': self.status,
            'created_at': self.created_at.isoformat()
        }

class Team(db.Model):
    """Team model for debate teams"""
    __tablename__ = 'teams'
    
    id = db.Column(db.Integer, primary_key=True)
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournaments.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    institution = db.Column(db.String(200))
    speaker1_name = db.Column(db.String(120), nullable=False)
    speaker2_name = db.Column(db.String(120), nullable=False)
    points = db.Column(db.Integer, default=0)
    wins = db.Column(db.Integer, default=0)
    speaker_points = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    tournament = db.relationship('Tournament', back_populates='teams')
    pairings = db.relationship('Pairing', back_populates='team', lazy='dynamic')
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'institution': self.institution,
            'speaker1_name': self.speaker1_name,
            'speaker2_name': self.speaker2_name,
            'points': self.points,
            'wins': self.wins,
            'speaker_points': self.speaker_points
        }

class Round(db.Model):
    """Round model for tournament rounds"""
    __tablename__ = 'rounds'
    
    id = db.Column(db.Integer, primary_key=True)
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournaments.id'), nullable=False)
    round_number = db.Column(db.Integer, nullable=False)
    motion = db.Column(db.Text)
    info_slide = db.Column(db.Text)
    motion_release_time = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='pending')  # pending, active, completed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    tournament = db.relationship('Tournament', back_populates='rounds')
    pairings = db.relationship('Pairing', back_populates='round', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'round_number': self.round_number,
            'motion': self.motion,
            'info_slide': self.info_slide,
            'motion_release_time': self.motion_release_time.isoformat() if self.motion_release_time else None,
            'status': self.status
        }

class Pairing(db.Model):
    """Pairing model for team matchups in rounds"""
    __tablename__ = 'pairings'
    
    id = db.Column(db.Integer, primary_key=True)
    round_id = db.Column(db.Integer, db.ForeignKey('rounds.id'), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    room = db.Column(db.String(100))
    position = db.Column(db.String(10))  # OG, OO, CG, CO for BP
    
    # Relationships
    round = db.relationship('Round', back_populates='pairings')
    team = db.relationship('Team', back_populates='pairings')
    scores = db.relationship('Score', back_populates='pairing', lazy='dynamic', cascade='all, delete-orphan')
    judge_assignments = db.relationship('JudgeAssignment', back_populates='pairing', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'team': self.team.to_dict() if self.team else None,
            'room': self.room,
            'position': self.position
        }

class JudgeAssignment(db.Model):
    """Judge assignment model"""
    __tablename__ = 'judge_assignments'
    
    id = db.Column(db.Integer, primary_key=True)
    pairing_id = db.Column(db.Integer, db.ForeignKey('pairings.id'), nullable=False)
    judge_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    role = db.Column(db.String(20))  # chair, wing, trainee
    
    # Relationships
    pairing = db.relationship('Pairing', back_populates='judge_assignments')
    judge = db.relationship('User', back_populates='judge_assignments')
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'judge': self.judge.to_dict() if self.judge else None,
            'role': self.role
        }

class Score(db.Model):
    """Score model for speaker scores"""
    __tablename__ = 'scores'
    
    id = db.Column(db.Integer, primary_key=True)
    pairing_id = db.Column(db.Integer, db.ForeignKey('pairings.id'), nullable=False)
    speaker_name = db.Column(db.String(120), nullable=False)
    score = db.Column(db.Float, nullable=False)
    feedback = db.Column(db.Text)
    rank = db.Column(db.Integer)  # Team rank in room
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    pairing = db.relationship('Pairing', back_populates='scores')
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'speaker_name': self.speaker_name,
            'score': self.score,
            'feedback': self.feedback,
            'rank': self.rank
        }

class Feedback(db.Model):
    """Feedback model for structured feedback"""
    __tablename__ = 'feedback'
    
    id = db.Column(db.Integer, primary_key=True)
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournaments.id'))
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'))
    judge_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    round_number = db.Column(db.Integer)
    content_score = db.Column(db.Integer)
    style_score = db.Column(db.Integer)
    strategy_score = db.Column(db.Integer)
    comments = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'round_number': self.round_number,
            'content_score': self.content_score,
            'style_score': self.style_score,
            'strategy_score': self.strategy_score,
            'comments': self.comments,
            'created_at': self.created_at.isoformat()
        }
