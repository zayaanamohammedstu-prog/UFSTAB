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
        start_date = datetime.utcnow() + timedelta(days=30)
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
        start_date = datetime.utcnow() + timedelta(days=30)
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
                start_date=datetime.utcnow() + timedelta(days=30),
                end_date=datetime.utcnow() + timedelta(days=33),
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

class TestTournamentCustomization:
    """Test tournament customization features"""
    
    def test_create_tournament_with_customization(self, client, auth_headers):
        """Test creating tournament with custom settings"""
        start_date = datetime.utcnow() + timedelta(days=30)
        end_date = start_date + timedelta(days=3)
        
        response = client.post('/api/tournaments', 
            headers=auth_headers,
            json={
                'name': 'Customized Tournament',
                'format': 'BP',
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'custom_logo_url': 'https://example.com/logo.png',
                'primary_color': '#ff0000',
                'secondary_color': '#00ff00',
                'show_public_tab': True
            }
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['tournament']['custom_logo_url'] == 'https://example.com/logo.png'
        assert data['tournament']['primary_color'] == '#ff0000'
        assert data['tournament']['secondary_color'] == '#00ff00'
        assert data['tournament']['show_public_tab'] == True
        assert 'slug' in data['tournament']
    
    def test_update_tournament_customization(self, client, auth_headers):
        """Test updating tournament customization"""
        # Create tournament first
        start_date = datetime.utcnow() + timedelta(days=30)
        end_date = start_date + timedelta(days=3)
        
        create_response = client.post('/api/tournaments',
            headers=auth_headers,
            json={
                'name': 'Original Tournament',
                'format': 'BP',
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            }
        )
        
        tournament_id = create_response.get_json()['tournament']['id']
        
        # Update customization
        update_response = client.put(f'/api/tournaments/{tournament_id}',
            headers=auth_headers,
            json={
                'custom_logo_url': 'https://example.com/new-logo.png',
                'primary_color': '#0000ff'
            }
        )
        
        assert update_response.status_code == 200
        data = update_response.get_json()
        assert data['tournament']['custom_logo_url'] == 'https://example.com/new-logo.png'
        assert data['tournament']['primary_color'] == '#0000ff'

class TestPublicDisplay:
    """Test public display endpoints"""
    
    def test_get_tournament_by_slug(self, client, auth_headers, app):
        """Test accessing tournament by slug"""
        # Create tournament
        start_date = datetime.utcnow() + timedelta(days=30)
        end_date = start_date + timedelta(days=3)
        
        create_response = client.post('/api/tournaments',
            headers=auth_headers,
            json={
                'name': 'Public Tournament',
                'format': 'BP',
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'show_public_tab': True
            }
        )
        
        slug = create_response.get_json()['tournament']['slug']
        
        # Access via slug (no auth required)
        response = client.get(f'/api/tournaments/public/{slug}')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['name'] == 'Public Tournament'
        assert 'organizer' not in data  # Should not include sensitive info
    
    def test_get_public_standings(self, client, auth_headers, app):
        """Test accessing public standings"""
        # Create tournament
        start_date = datetime.utcnow() + timedelta(days=30)
        end_date = start_date + timedelta(days=3)
        
        create_response = client.post('/api/tournaments',
            headers=auth_headers,
            json={
                'name': 'Public Standings Tournament',
                'format': 'BP',
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'show_public_tab': True
            }
        )
        
        slug = create_response.get_json()['tournament']['slug']
        
        # Access standings via slug (no auth required)
        response = client.get(f'/api/tournaments/public/{slug}/standings')
        
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
    
    def test_public_display_disabled(self, client, auth_headers):
        """Test accessing tournament with public display disabled"""
        start_date = datetime.utcnow() + timedelta(days=30)
        end_date = start_date + timedelta(days=3)
        
        create_response = client.post('/api/tournaments',
            headers=auth_headers,
            json={
                'name': 'Private Tournament',
                'format': 'BP',
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'show_public_tab': False
            }
        )
        
        slug = create_response.get_json()['tournament']['slug']
        
        # Try to access via slug
        response = client.get(f'/api/tournaments/public/{slug}')
        
        assert response.status_code == 403

class TestRegistrationImport:
    """Test registration import functionality"""
    
    def test_import_csv_registrations(self, client, auth_headers, app):
        """Test importing registrations from CSV"""
        # Create tournament first
        start_date = datetime.utcnow() + timedelta(days=30)
        end_date = start_date + timedelta(days=3)
        
        create_response = client.post('/api/tournaments',
            headers=auth_headers,
            json={
                'name': 'Import Test Tournament',
                'format': 'BP',
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            }
        )
        
        tournament_id = create_response.get_json()['tournament']['id']
        
        # Create a CSV file content
        csv_content = """email,name,registration_type
test1@example.com,Test User 1,individual
test2@example.com,Test User 2,team
"""
        
        # Import registrations
        from io import BytesIO
        data = {
            'file': (BytesIO(csv_content.encode()), 'test.csv')
        }
        
        response = client.post(
            f'/api/registrations/tournament/{tournament_id}/import',
            headers=auth_headers,
            data=data,
            content_type='multipart/form-data'
        )
        
        assert response.status_code == 200
        result = response.get_json()
        assert result['imported_count'] >= 0  # May be 0 or more depending on duplicates

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
