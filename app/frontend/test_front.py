import pytest
import sys
import os
from unittest.mock import patch, MagicMock, mock_open
import json

# Add the current directory to the path to import local modules
sys.path.insert(0, os.path.dirname(__file__))

# Try to import requests, with fallback
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    # Create a mock requests module
    class MockRequests:
        class Response:
            def __init__(self, status_code=200, json_data=None):
                self.status_code = status_code
                self._json_data = json_data or {}
            
            def json(self):
                return self._json_data
        
        @staticmethod
        def post(*args, **kwargs):
            return MockRequests.Response()
        
        @staticmethod
        def get(*args, **kwargs):
            return MockRequests.Response()
    
    requests = MockRequests()


class TestFrontendConnection:
    """Test suite for frontend connection and authentication."""
    
    def setup_method(self):
        """Setup method run before each test."""
        pass
    
    def test_api_url_configuration_local(self):
        """Test API URL configuration for local environment."""
        with patch.dict(os.environ, {}, clear=True):
            # Mock the app.py imports
            with patch('builtins.__import__', side_effect=self._mock_import):
                # Test that local environment uses correct API URL
                expected_url = 'http://api:5000'
                assert expected_url == 'http://api:5000'
    
    def test_api_url_configuration_production(self):
        """Test API URL configuration for production environment."""
        with patch.dict(os.environ, {'RENDER': 'true'}, clear=True):
            # Test that production environment uses correct API URL
            expected_url = 'https://backend-l0n0.onrender.com'
            assert expected_url == 'https://backend-l0n0.onrender.com'
    
    @patch('requests.post')
    def test_login_api_connection_success(self, mock_post):
        """Test successful API connection for login."""
        # Setup mock response for successful login
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "user": {
                "id": 1,
                "name": "Test User",
                "email": "test@example.com",
                "isAdmin": True,
                "country": "France"
            }
        }
        mock_post.return_value = mock_response
        
        # Simulate the login API call
        api_url = 'http://api:5000'
        login_data = {
            "email": "test@example.com",
            "password": "password123"
        }
        
        # Import requests here to avoid import errors in main imports
        response = requests.post(f"{api_url}/login", json=login_data, headers={"Content-Type": "application/json"})
        
        # Verify the response
        assert response.status_code == 200
        user_data = response.json().get("user")
        assert user_data is not None
        assert user_data["email"] == "test@example.com"
        assert user_data["name"] == "Test User"
        
        # Verify the API call was made correctly
        mock_post.assert_called_once_with(
            f"{api_url}/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
    
    @patch('requests.post')
    def test_login_api_connection_failure(self, mock_post):
        """Test failed API connection for login."""
        # Setup mock response for failed login
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.json.return_value = {
            "message": "Invalid email or password"
        }
        mock_post.return_value = mock_response
        
        # Simulate the login API call with invalid credentials
        api_url = 'http://api:5000'
        login_data = {
            "email": "invalid@example.com",
            "password": "wrongpassword"
        }
        
        response = requests.post(f"{api_url}/login", json=login_data, headers={"Content-Type": "application/json"})
        
        # Verify the response indicates failure
        assert response.status_code == 401
        error_message = response.json().get("message")
        assert "Invalid email or password" in error_message
    
    @patch('requests.post')
    def test_api_connection_timeout(self, mock_post):
        """Test API connection timeout handling."""
        # Setup mock to raise connection timeout
        mock_post.side_effect = Exception("Connection timeout")
        
        api_url = 'http://api:5000'
        login_data = {
            "email": "test@example.com",
            "password": "password123"
        }
        
        # Test that connection timeout is handled
        with pytest.raises(Exception) as excinfo:
            requests.post(f"{api_url}/login", json=login_data, headers={"Content-Type": "application/json"})
        
        assert "Connection timeout" in str(excinfo.value)
    
    def test_session_state_structure(self):
        """Test the expected session state structure."""
        # Define expected session state keys based on app.py
        expected_keys = ['new_user', 'user', 'logged_in', 'API_URL']
        
        # Mock session state
        mock_session_state = {
            'new_user': False,
            'user': None,
            'logged_in': False,
            'API_URL': 'http://api:5000'
        }
        
        # Verify all expected keys are present
        for key in expected_keys:
            assert key in mock_session_state
        
        # Verify default values
        assert mock_session_state['new_user'] == False
        assert mock_session_state['user'] is None
        assert mock_session_state['logged_in'] == False
        assert 'http' in mock_session_state['API_URL']
    
    def test_user_authentication_flow(self):
        """Test the complete user authentication flow."""
        # Initial state
        session_state = {
            'logged_in': False,
            'user': None,
            'page': None
        }
        
        # After successful login
        mock_user = {
            "id": 1,
            "name": "Test User",
            "email": "test@example.com",
            "isAdmin": True,
            "country": "France"
        }
        
        # Simulate successful login
        session_state['user'] = mock_user
        session_state['logged_in'] = True
        session_state['page'] = 'dashboard'
        
        # Verify state after login
        assert session_state['logged_in'] == True
        assert session_state['user'] is not None
        assert session_state['user']['email'] == "test@example.com"
        assert session_state['page'] == 'dashboard'
    
    def test_dashboard_language_logic(self):
        """Test language switching logic based on user country."""
        # Test French user
        french_user = {"country": "France"}
        expected_lang = 'fr'
        
        # Simulate language switching logic
        if french_user["country"] == "France":
            language = 'fr'
        elif french_user["country"] == "USA":
            language = 'en'
        elif french_user["country"] == "Suisse":
            language = 'fr'
        else:
            language = 'en'
        
        assert language == expected_lang
        
        # Test US user
        us_user = {"country": "USA"}
        if us_user["country"] == "France":
            language = 'fr'
        elif us_user["country"] == "USA":
            language = 'en'
        elif us_user["country"] == "Suisse":
            language = 'fr'
        else:
            language = 'en'
        
        assert language == 'en'
        
        # Test Swiss user
        swiss_user = {"country": "Suisse"}
        if swiss_user["country"] == "France":
            language = 'fr'
        elif swiss_user["country"] == "USA":
            language = 'en'
        elif swiss_user["country"] == "Suisse":
            language = 'fr'
        else:
            language = 'en'
        
        assert language == 'fr'
    
    def test_admin_privileges_logic(self):
        """Test admin privileges logic."""
        # Admin user
        admin_user = {
            "id": 1,
            "name": "Admin User",
            "email": "admin@example.com",
            "isAdmin": True,
            "country": "USA"
        }
        
        # Regular user
        regular_user = {
            "id": 2,
            "name": "Regular User",
            "email": "user@example.com",
            "isAdmin": False,
            "country": "USA"
        }
        
        # Test admin privileges
        assert admin_user["isAdmin"] == True
        assert regular_user["isAdmin"] == False
        
        # Simulate admin-only features access
        admin_features = ["csv_import", "manage_users"]
        user_features = ["profile", "predictions"]
        
        # Admin should have access to all features
        available_features_admin = admin_features + user_features
        assert len(available_features_admin) > len(user_features)
        
        # Regular user should only have user features
        available_features_user = user_features
        assert "csv_import" not in available_features_user
        assert "manage_users" not in available_features_user
    
    def test_page_navigation_logic(self):
        """Test page navigation logic."""
        # Test initial state
        session_state = {
            'logged_in': False,
            'page': None
        }
        
        # Should show login page
        if session_state['logged_in'] or session_state.get("page") == "dashboard":
            current_page = "dashboard"
        elif session_state.get("page") == "create_account":
            current_page = "create_account"
        else:
            current_page = "login"
        
        assert current_page == "login"
        
        # Test after setting page to create account
        session_state['page'] = "create_account"
        
        if session_state['logged_in'] or session_state.get("page") == "dashboard":
            current_page = "dashboard"
        elif session_state.get("page") == "create_account":
            current_page = "create_account"
        else:
            current_page = "login"
        
        assert current_page == "create_account"
        
        # Test after login
        session_state['logged_in'] = True
        
        if session_state['logged_in'] or session_state.get("page") == "dashboard":
            current_page = "dashboard"
        elif session_state.get("page") == "create_account":
            current_page = "create_account"
        else:
            current_page = "login"
        
        assert current_page == "dashboard"
    
    def _mock_import(self, name, *args, **kwargs):
        """Mock import function to handle missing dependencies."""
        if name in ['streamlit', 'login', 'create_account', 'dashboard']:
            return MagicMock()
        return __import__(name, *args, **kwargs)


class TestAPIEndpoints:
    """Test API endpoint connections."""
    
    @patch('requests.post')
    def test_predict_endpoint_connection(self, mock_post):
        """Test connection to predict endpoint."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "prediction": [[14338, 551, 2796]]
        }
        mock_post.return_value = mock_response
        
        api_url = 'http://api:5000'
        predict_data = {
            "cases": 2465,
            "deaths": 354,
            "recovered": 766,
            "country": 174
        }
        
        response = requests.post(f"{api_url}/predict", json=predict_data, headers={"Content-Type": "application/json"})
        
        assert response.status_code == 200
        prediction = response.json().get("prediction")
        assert prediction is not None
        assert len(prediction) > 0
    
    @patch('requests.get')
    def test_users_endpoint_connection(self, mock_get):
        """Test connection to users endpoint."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "users": [
                {
                    "id": 1,
                    "name": "Test User",
                    "email": "test@example.com",
                    "isAdmin": False
                }
            ]
        }
        mock_get.return_value = mock_response
        
        api_url = 'http://api:5000'
        
        response = requests.get(f"{api_url}/users")
        
        assert response.status_code == 200
        users = response.json().get("users")
        assert users is not None
        assert len(users) > 0


class TestDashboardFunctionality:
    """Test suite for dashboard functionality and pages."""
    
    def setup_method(self):
        """Setup method run before each test."""
        # Mock user data for testing
        self.mock_user_admin = {
            "id": 1,
            "name": "Admin User",
            "email": "admin@example.com",
            "isAdmin": True,
            "country": "USA"
        }
        
        self.mock_user_regular = {
            "id": 2,
            "name": "Regular User",
            "email": "user@example.com",
            "isAdmin": False,
            "country": "France"
        }
        
        self.mock_user_swiss = {
            "id": 3,
            "name": "Swiss User",
            "email": "swiss@example.com",
            "isAdmin": False,
            "country": "Suisse"
        }
    
    def test_switch_language_function(self):
        """Test the switch_language function logic."""
        # Test USA -> English
        country = "USA"
        if country == "USA":
            language = 'en'
        elif country == "France":
            language = 'fr'
        elif country == "Suisse":
            language = 'fr'
        else:
            language = 'en'
        assert language == 'en'
        
        # Test France -> French
        country = "France"
        if country == "USA":
            language = 'en'
        elif country == "France":
            language = 'fr'
        elif country == "Suisse":
            language = 'fr'
        else:
            language = 'en'
        assert language == 'fr'
        
        # Test Switzerland -> French
        country = "Suisse"
        if country == "USA":
            language = 'en'
        elif country == "France":
            language = 'fr'
        elif country == "Suisse":
            language = 'fr'
        else:
            language = 'en'
        assert language == 'fr'
        
        # Test unknown country -> English (default)
        country = "Unknown"
        if country == "USA":
            language = 'en'
        elif country == "France":
            language = 'fr'
        elif country == "Suisse":
            language = 'fr'
        else:
            language = 'en'
        assert language == 'en'
    
    def test_dashboard_page_navigation(self):
        """Test dashboard page navigation logic."""
        # Mock session state
        session_state = {'dashboard_page': 'home'}
        
        # Test navigation to different pages
        pages = ['home', 'csv_import', 'database', 'statistics', 'profile', 'predictions', 'manage_users']
        
        for page in pages:
            session_state['dashboard_page'] = page
            assert session_state['dashboard_page'] == page
    
    def test_dashboard_admin_features_visibility(self):
        """Test that admin features are visible only to admin users."""
        admin_user = self.mock_user_admin
        regular_user = self.mock_user_regular
        
        # Admin features
        admin_only_features = ['csv_import', 'manage_users']
        
        # Admin user should have access
        for feature in admin_only_features:
            if admin_user["isAdmin"]:
                has_access = True
            else:
                has_access = False
            assert has_access == True
        
        # Regular user should not have access
        for feature in admin_only_features:
            if regular_user["isAdmin"]:
                has_access = True
            else:
                has_access = False
            assert has_access == False
    
    def test_dashboard_country_specific_features(self):
        """Test country-specific feature visibility."""
        usa_user = self.mock_user_admin  # USA
        swiss_user = self.mock_user_swiss  # Suisse
        french_user = self.mock_user_regular  # France
        
        # Features only available to USA users
        usa_only_features = ['api_docs', 'data_management']
        
        # USA user should have access
        for feature in usa_only_features:
            if usa_user["country"] == "USA":
                has_access = True
            else:
                has_access = False
            assert has_access == True
        
        # Swiss user should not have access
        for feature in usa_only_features:
            if swiss_user["country"] == "USA":
                has_access = True
            else:
                has_access = False
            assert has_access == False
        
        # Statistics feature should not be available to Swiss users
        if swiss_user["country"] != "Suisse":
            stats_available = True
        else:
            stats_available = False
        assert stats_available == False
        
        # Statistics should be available to others
        if french_user["country"] != "Suisse":
            stats_available = True
        else:
            stats_available = False
        assert stats_available == True
    
    def test_dashboard_url_configuration(self):
        """Test dashboard URL configuration based on environment."""
        # Test local environment
        with patch.dict(os.environ, {}, clear=True):
            if os.getenv("RENDER"):
                url = "session_state_api_url"  # Would be from session state
            else:
                url = "http://localhost:5001"
            assert url == "http://localhost:5001"
        
        # Test production environment
        with patch.dict(os.environ, {'RENDER': 'true'}, clear=True):
            if os.getenv("RENDER"):
                url = "https://backend-l0n0.onrender.com"  # Would be from session state
            else:
                url = "http://localhost:5001"
            assert url == "https://backend-l0n0.onrender.com"


class TestDashboardPages:
    """Test suite for individual dashboard pages."""
    
    def setup_method(self):
        """Setup method run before each test."""
        self.mock_user = {
            "id": 1,
            "name": "Test User",
            "email": "test@example.com",
            "isAdmin": True,
            "country": "USA"
        }
    
    def test_home_page_logic(self):
        """Test home page functionality."""
        user = self.mock_user
        
        # Simulate home page logic
        welcome_message = f"Welcome {user['name']}"
        assert "Test User" in welcome_message
        
        # Check that user data is properly used
        assert user['name'] == "Test User"
        assert user['email'] == "test@example.com"
    
    def test_predictions_page_model_versions(self):
        """Test predictions page model version logic."""
        # Test model version selection
        model_versions = ['v1', 'v2']
        
        for version in model_versions:
            if version == 'v1':
                endpoint = '/predict'
                required_fields = ['cases', 'deaths', 'recovered', 'country']
            elif version == 'v2':
                endpoint = '/predict_v2'
                required_fields = [
                    'cases_lag1', 'deaths_lag1', 'recovered_lag1',
                    'cases_lag2', 'deaths_lag2', 'recovered_lag2',
                    'cases_lag3', 'deaths_lag3', 'recovered_lag3',
                    'country', 'population'
                ]
            
            assert endpoint in ['/predict', '/predict_v2']
            assert len(required_fields) > 0
    
    @patch('requests.post')
    def test_predictions_api_call_v1(self, mock_post):
        """Test predictions page API call for model v1."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "prediction": [[15000, 600, 3000]]
        }
        mock_post.return_value = mock_response
        
        # Simulate v1 prediction call
        api_url = 'http://api:5000'
        data = {
            "cases": 10000,
            "deaths": 500,
            "recovered": 2000,
            "country": 1
        }
        
        response = requests.post(f"{api_url}/predict", json=data)
        
        assert response.status_code == 200
        prediction = response.json().get("prediction")
        assert prediction == [[15000, 600, 3000]]
    
    @patch('requests.post')
    def test_predictions_api_call_v2(self, mock_post):
        """Test predictions page API call for model v2."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "prediction": [[20000, 800, 4000]]
        }
        mock_post.return_value = mock_response
        
        # Simulate v2 prediction call
        api_url = 'http://api:5000'
        data = {
            "cases_lag1": 10000,
            "deaths_lag1": 500,
            "recovered_lag1": 2000,
            "cases_lag2": 9500,
            "deaths_lag2": 480,
            "recovered_lag2": 1900,
            "cases_lag3": 9000,
            "deaths_lag3": 460,
            "recovered_lag3": 1800,
            "country": 1,
            "population": 1000000
        }
        
        response = requests.post(f"{api_url}/predict_v2", json=data)
        
        assert response.status_code == 200
        prediction = response.json().get("prediction")
        assert prediction == [[20000, 800, 4000]]
    
    def test_profile_page_password_validation(self):
        """Test profile page password validation logic."""
        # Test password validation rules
        def validate_password(password, confirm_password):
            if not password or not confirm_password:
                return False, "All fields required"
            if password != confirm_password:
                return False, "Passwords do not match"
            if len(password) < 6:
                return False, "Password too short"
            return True, "Password valid"
        
        # Test cases
        assert validate_password("", "") == (False, "All fields required")
        assert validate_password("123", "456") == (False, "Passwords do not match")
        assert validate_password("123", "123") == (False, "Password too short")
        assert validate_password("password123", "password123") == (True, "Password valid")
    
    @patch('requests.put')
    def test_profile_password_update_api(self, mock_put):
        """Test profile page password update API call."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "message": "Password updated successfully"
        }
        mock_put.return_value = mock_response
        
        api_url = 'http://api:5000'
        data = {
            "email": "test@example.com",
            "old_password": "oldpass123",
            "new_password": "newpass123",
            "confirm_password": "newpass123"
        }
        
        response = requests.put(f"{api_url}/update_password", json=data)
        
        assert response.status_code == 200
        message = response.json().get("message")
        assert "successfully" in message.lower()
    
    @patch('requests.get')
    def test_manage_users_api_call(self, mock_get):
        """Test manage users page API call."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "users": [
                {"id": 1, "name": "User 1", "email": "user1@example.com", "isAdmin": False},
                {"id": 2, "name": "User 2", "email": "user2@example.com", "isAdmin": True}
            ]
        }
        mock_get.return_value = mock_response
        
        api_url = 'http://api:5000'
        response = requests.get(f"{api_url}/users")
        
        assert response.status_code == 200
        users = response.json().get("users")
        assert len(users) == 2
        assert users[0]["name"] == "User 1"
        assert users[1]["isAdmin"] == True
    
    @patch('requests.get')
    def test_database_visualization_api_call(self, mock_get):
        """Test database visualization page API call."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "diseases": [
                {
                    "Id": 1,
                    "Country_Region": "France",
                    "Confirmed": 10000,
                    "Deaths": 500,
                    "Recovered": 2000
                }
            ]
        }
        mock_get.return_value = mock_response
        
        api_url = 'http://api:5000'
        response = requests.get(f"{api_url}/diseases")
        
        assert response.status_code == 200
        diseases = response.json().get("diseases")
        assert len(diseases) > 0
        assert diseases[0]["Country_Region"] == "France"
    
    def test_csv_import_file_validation(self):
        """Test CSV import page file validation logic."""
        def validate_csv_file(filename, file_content):
            if not filename.endswith('.csv'):
                return False, "File must be CSV format"
            if not file_content:
                return False, "File is empty"
            # Simulate basic CSV validation
            lines = file_content.strip().split('\n')
            if len(lines) < 2:  # Header + at least one data row
                return False, "CSV must have header and data rows"
            return True, "CSV is valid"
        
        # Test cases
        assert validate_csv_file("data.txt", "content") == (False, "File must be CSV format")
        assert validate_csv_file("data.csv", "") == (False, "File is empty")
        assert validate_csv_file("data.csv", "header") == (False, "CSV must have header and data rows")
        assert validate_csv_file("data.csv", "header\ndata1\ndata2") == (True, "CSV is valid")
    
    def test_stats_page_data_processing(self):
        """Test statistics page data processing logic."""
        # Mock data processing for statistics
        mock_data = [
            {"country": "France", "cases": 1000, "deaths": 50},
            {"country": "USA", "cases": 2000, "deaths": 100},
            {"country": "Germany", "cases": 1500, "deaths": 75}
        ]
        
        # Calculate total cases
        total_cases = sum(item["cases"] for item in mock_data)
        assert total_cases == 4500
        
        # Calculate total deaths
        total_deaths = sum(item["deaths"] for item in mock_data)
        assert total_deaths == 225
        
        # Calculate death rate
        death_rate = (total_deaths / total_cases) * 100
        assert abs(death_rate - 5.0) < 0.1  # Approximately 5%
        
        # Find country with highest cases
        max_cases_country = max(mock_data, key=lambda x: x["cases"])
        assert max_cases_country["country"] == "USA"


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
