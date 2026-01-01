"""
Basic tests for OratorHub API
"""
import pytest
from app import create_app
from models import db, User, Tournament
from datetime import datetime, timedelta

@pytest.fixture
def app():
    """Create and configure a test app"""
    app = create_app('testing')
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """Create a test client"""
    return app.test_client()

@pytest.fixture
def auth_headers(client):
    """Get authentication headers"""
    # Register a user
    response = client.post('/api/auth/register', json={
        'email': 'test@example.com',
        'username': 'testuser',
        'password': 'testpass123',
        'full_name': 'Test User',
        'role': 'organizer'
    })
    
    data = response.get_json()
    token = data['access_token']
    
    return {'Authorization': f'Bearer {token}'}

class TestAuth:
    """Test authentication endpoints"""
    
    def test_register(self, client):
        """Test user registration"""
        response = client.post('/api/auth/register', json={
            'email': 'newuser@example.com',
            'username': 'newuser',
            'password': 'password123',
            'full_name': 'New User'
        })
        
        assert response.status_code == 201
        data = response.get_json()
        assert 'access_token' in data
        assert data['user']['email'] == 'newuser@example.com'
    
    def test_login(self, client):
        """Test user login"""
        # First register
        client.post('/api/auth/register', json={
            'email': 'login@example.com',
            'username': 'loginuser',
            'password': 'loginpass123'
        })
        
        # Then login
        response = client.post('/api/auth/login', json={
            'email': 'login@example.com',
            'password': 'loginpass123'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'access_token' in data
    
    def test_get_current_user(self, client, auth_headers):
        """Test getting current user"""
        response = client.get('/api/auth/me', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['email'] == 'test@example.com'

class TestTournaments:
    """Test tournament endpoints"""
    
    def test_create_tournament(self, client, auth_headers):
        """Test tournament creation"""
        start_date = datetime.now() + timedelta(days=30)
        end_date = start_date + timedelta(days=3)
        
        response = client.post('/api/tournaments', 
            headers=auth_headers,
            json={
                'name': 'Test Tournament',
                'format': 'BP',
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'venue': 'Test Venue',
                'num_rounds': 5,
                'registration_fee': 50.0
            }
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['tournament']['name'] == 'Test Tournament'
        assert data['tournament']['format'] == 'BP'
    
    def test_get_tournaments(self, client):
        """Test getting all tournaments"""
        response = client.get('/api/tournaments')
        
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
    
    def test_update_tournament(self, client, auth_headers):
        """Test updating a tournament"""
        # Create tournament first
        start_date = datetime.now() + timedelta(days=30)
        end_date = start_date + timedelta(days=3)
        
        create_response = client.post('/api/tournaments',
            headers=auth_headers,
            json={
                'name': 'Original Name',
                'format': 'BP',
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            }
        )
        
        tournament_id = create_response.get_json()['tournament']['id']
        
        # Update tournament
        update_response = client.put(f'/api/tournaments/{tournament_id}',
            headers=auth_headers,
            json={
                'name': 'Updated Name'
            }
        )
        
        assert update_response.status_code == 200
        data = update_response.get_json()
        assert data['tournament']['name'] == 'Updated Name'

class TestTeams:
    """Test team endpoints"""
    
    def test_create_team(self, client, auth_headers, app):
        """Test team creation"""
        # Create tournament first
        with app.app_context():
            user = User.query.filter_by(email='test@example.com').first()
            tournament = Tournament(
                name='Test Tournament',
                format='BP',
                start_date=datetime.now() + timedelta(days=30),
                end_date=datetime.now() + timedelta(days=33),
                organizer_id=user.id
            )
            db.session.add(tournament)
            db.session.commit()
            tournament_id = tournament.id
        
        # Create team
        response = client.post('/api/teams',
            headers=auth_headers,
            json={
                'tournament_id': tournament_id,
                'name': 'Test Team',
                'institution': 'Test University',
                'speaker1_name': 'Speaker One',
                'speaker2_name': 'Speaker Two'
            }
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['team']['name'] == 'Test Team'

class TestHealth:
    """Test health check endpoint"""
    
    def test_health_check(self, client):
        """Test health check"""
        response = client.get('/api/health')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'healthy'
        assert data['service'] == 'OratorHub API'

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
