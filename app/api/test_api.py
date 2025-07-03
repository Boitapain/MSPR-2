"""
Unit tests for the API endpoints in app.api.api
"""
import unittest
from unittest.mock import patch, MagicMock
from app.api.api import app

class ApiTestCase(unittest.TestCase):
    """Test case for API endpoints in app.api.api"""
    # pylint: disable=too-many-public-methods
    def setUp(self):
        """Set up test client for API tests."""
        self.app = app.test_client()
        self.app.testing = True

    @patch("app.api.api.get_users")
    def test_get_users_success(self, mock_get_users):
        """Test successful retrieval of users."""
        mock_get_users.return_value = [{"id": 1, "name": "Test"}]
        response = self.app.get('/users')
        self.assertEqual(response.status_code, 200)
        self.assertIn("users", response.get_json())

    @patch("app.api.api.get_users")
    def test_get_users_not_found(self, mock_get_users):
        """Test users not found scenario."""
        mock_get_users.return_value = []
        response = self.app.get('/users')
        self.assertEqual(response.status_code, 404)
        self.assertIn("message", response.get_json())

    @patch("app.api.api.add_user")
    def test_register_success(self, _):
        """Test successful user registration."""
        payload = {"name": "Test", "email": "test@test.com", "password": "pass"}
        response = self.app.post('/register', json=payload)
        self.assertEqual(response.status_code, 201)
        self.assertIn("User registered successfully", response.get_data(as_text=True))

    def test_register_missing_fields(self):
        """Test registration with missing fields."""
        payload = {"name": "", "email": "", "password": ""}
        response = self.app.post('/register', json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn("All fields are required", response.get_data(as_text=True))

    @patch("app.api.api.add_user", side_effect=Exception("DB error"))
    def test_register_exception(self, _):
        """Test registration exception handling."""
        payload = {"name": "Test", "email": "test@test.com", "password": "pass"}
        response = self.app.post('/register', json=payload)
        self.assertEqual(response.status_code, 500)
        self.assertIn("DB error", response.get_data(as_text=True))

    @patch("app.api.api.authenticate_user")
    def test_login_success(self, mock_auth):
        """Test successful login."""
        mock_auth.return_value = {"id": 1, "name": "Test"}
        payload = {"email": "test@test.com", "password": "pass"}
        response = self.app.post('/login', json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertIn("user", response.get_json())

    @patch("app.api.api.authenticate_user")
    def test_login_fail(self, mock_auth):
        """Test login failure with invalid credentials."""
        mock_auth.return_value = None
        payload = {"email": "test@test.com", "password": "wrong"}
        response = self.app.post('/login', json=payload)
        self.assertEqual(response.status_code, 401)
        self.assertIn("Invalid email or password", response.get_data(as_text=True))

    @patch("app.api.api.get_diseases")
    def test_get_diseases_success(self, mock_get_diseases):
        """Test successful retrieval of diseases."""
        mock_get_diseases.return_value = [{"id": 1, "name": "Flu"}]
        response = self.app.get('/diseases')
        self.assertEqual(response.status_code, 200)
        self.assertIn("diseases", response.get_json())

    @patch("app.api.api.get_diseases")
    def test_get_diseases_not_found(self, mock_get_diseases):
        """Test diseases not found scenario."""
        mock_get_diseases.return_value = []
        response = self.app.get('/diseases')
        self.assertEqual(response.status_code, 404)
        self.assertIn("No diseases found", response.get_data(as_text=True))

    @patch("app.api.api.update_diseases")
    @patch("pandas.read_json")
    def test_update_diseases_success(self, mock_read_json, _):
        """Test successful update of diseases."""
        mock_read_json.return_value = MagicMock(
            isnull=MagicMock(
                return_value=MagicMock(
                    values=MagicMock(any=lambda: False)
                )
            )
        )
        response = self.app.put('/update_diseases_route', json={"diseases": "[]"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("Diseases updated successfully", response.get_data(as_text=True))

    def test_update_diseases_no_data(self):
        """Test update diseases with no data provided."""
        response = self.app.put('/update_diseases_route', json={})
        self.assertEqual(response.status_code, 400)
        self.assertIn("No data provided", response.get_data(as_text=True))

    @patch("pandas.read_json")
    def test_update_diseases_null_values(self, mock_read_json):
        """Test update diseases with null values in data."""
        mock_read_json.return_value = MagicMock(
            isnull=MagicMock(
                return_value=MagicMock(
                    values=MagicMock(any=lambda: True)
                )
            )
        )
        response = self.app.put('/update_diseases_route', json={"diseases": "[]"})
        self.assertEqual(response.status_code, 400)
        self.assertIn("Data contains null values", response.get_data(as_text=True))

    @patch("app.api.api.update_diseases", side_effect=Exception("Update error"))
    @patch("pandas.read_json")
    def test_update_diseases_exception(self, mock_read_json, _):
        """Test update diseases exception handling."""
        mock_read_json.return_value = MagicMock(
            isnull=MagicMock(
                return_value=MagicMock(
                    values=MagicMock(any=lambda: False)
                )
            )
        )
        response = self.app.put('/update_diseases_route', json={"diseases": "[]"})
        self.assertEqual(response.status_code, 500)
        self.assertIn("Update error", response.get_data(as_text=True))

    @patch("app.api.api.db_update_users")
    @patch("pandas.read_json")
    # pylint: disable=unused-argument
    def test_update_users_success(self, mock_read_json, mock_db_update_users):
        """Test successful update of users."""
        mock_read_json.return_value = MagicMock(
            isnull=MagicMock(
                return_value=MagicMock(
                    values=MagicMock(any=lambda: False)
                )
            )
        )
        mock_db_update_users.return_value = True
        payload = {"users": "[]"}
        response = self.app.put('/update_users', json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Users updated successfully", response.get_data(as_text=True))

    def test_update_users_no_data(self):
        """Test update users with no data provided."""
        response = self.app.put('/update_users', json={})
        self.assertEqual(response.status_code, 400)
        self.assertIn("No data provided", response.get_data(as_text=True))

    @patch("pandas.read_json")
    def test_update_users_null_values(self, mock_read_json):
        """Test update users with null values in data."""
        mock_read_json.return_value = MagicMock(
            isnull=MagicMock(
                return_value=MagicMock(
                    values=MagicMock(any=lambda: True)
                )
            )
        )
        payload = {"users": "[]"}
        response = self.app.put('/update_users', json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Data contains null values", response.get_data(as_text=True))

    @patch("app.api.api.db_update_users", side_effect=Exception("Update users error"))
    @patch("pandas.read_json")
    # pylint: disable=unused-argument
    def test_update_users_exception(self, mock_read_json, mock_db_update_users):
        """Test update users exception handling."""
        mock_read_json.return_value = MagicMock(
            isnull=MagicMock(
                return_value=MagicMock(
                    values=MagicMock(any=lambda: False)
                )
            )
        )
        payload = {"users": "[]"}
        response = self.app.put('/update_users', json=payload)
        self.assertEqual(response.status_code, 500)
        self.assertIn("Update users error", response.get_data(as_text=True))

    @patch("app.api.api.update_user_password")
    # pylint: disable=unused-argument
    def test_update_password_success(self, mock_update_user_password):
        """Test successful password update."""
        mock_update_user_password.return_value = True
        payload = {
            "email": "test@test.com",
            "old_password": "old",
            "new_password": "new",
            "confirm_password": "new"
        }
        response = self.app.put('/update_password', json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["message"], "Mot de passe mis à jour avec succès.")

    @patch("app.api.api.update_user_password")
    # pylint: disable=unused-argument
    def test_update_password_fail(self, mock_update_user_password):
        """Test password update failure (wrong old password)."""
        mock_update_user_password.return_value = False
        payload = {
            "email": "test@test.com",
            "old_password": "wrong",
            "new_password": "new",
            "confirm_password": "new"
        }
        response = self.app.put('/update_password', json=payload)
        self.assertEqual(response.status_code, 401)
        self.assertIn("Ancien mot de passe incorrect.", response.get_data(as_text=True))

    def test_update_password_missing_fields(self):
        """Test update password with missing fields."""
        payload = {
            "email": "",
            "old_password": "",
            "new_password": "",
            "confirm_password": ""
        }
        response = self.app.put('/update_password', json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Tous les champs sont requis.", response.get_data(as_text=True))

    def test_update_password_mismatch(self):
        """Test update password with mismatched new and confirm password."""
        payload = {
            "email": "test@test.com",
            "old_password": "old",
            "new_password": "new1",
            "confirm_password": "new2"
        }
        response = self.app.put('/update_password', json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn(
            "Les nouveaux mots de passe ne correspondent pas.",
            response.get_data(as_text=True)
        )

    @patch("app.api.api.update_user_password", side_effect=Exception("Update password error"))
    # pylint: disable=unused-argument
    def test_update_password_exception(self, mock_update_user_password):
        """Test update password exception handling."""
        payload = {
            "email": "test@test.com",
            "old_password": "old",
            "new_password": "new",
            "confirm_password": "new"
        }
        response = self.app.put('/update_password', json=payload)
        self.assertEqual(response.status_code, 500)
        # Do not check for message, as Flask returns a default 500 page

    @patch("pickle.load")
    @patch("builtins.open")
    def test_predict_success(self, mock_open_builtin, mock_pickle_load):
        """Test successful prediction with three values."""
        mock_model = MagicMock()
        mock_prediction = MagicMock()
        mock_prediction.tolist.return_value = [[14338, 551, 2796]]
        mock_model.predict.return_value = mock_prediction
        mock_pickle_load.return_value = mock_model

        payload = {
            "cases": 2465,
            "deaths": 354,
            "recovered": 766,
            "country": 174
        }
        response = self.app.post('/predict', json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertIn("prediction", response.get_json())
        self.assertEqual(response.get_json()["prediction"], [[14338, 551, 2796]])
        
    def test_predict_missing_field(self):
        """Test predict route with missing required field (should fail)."""
        payload = {
            "cases": 2465,
            "deaths": 354,
            # "recovered" is missing
            "country": 174
        }
        response = self.app.post('/predict', json=payload)
        self.assertEqual(response.status_code, 500)  # Should fail, expecting error due to missing field
        self.assertIn("recovered", response.get_data(as_text=True))
        
    @patch("pickle.load")
    @patch("builtins.open")
    def test_predict_wrong_result(self, mock_open_builtin, mock_pickle_load):
        """Test predict route returns wrong prediction (should fail if matches expected)."""
        mock_model = MagicMock()
        mock_prediction = MagicMock()
        # Simulate a wrong prediction
        mock_prediction.tolist.return_value = [[999, 888, 777]]
        mock_model.predict.return_value = mock_prediction
        mock_pickle_load.return_value = mock_model

        payload = {
            "cases": 53342,
            "deaths": 3421,
            "recovered": 9065,
            "country": 62
        }
        response = self.app.post('/predict', json=payload)
        self.assertEqual(response.status_code, 200)
        # This will fail if the prediction matches the expected correct result
        self.assertNotEqual(response.get_json()["prediction"], [[138933, 15056, 49670]])

    @patch("pickle.load")
    @patch("builtins.open")
    def test_predict_v2_success(self, mock_open_builtin, mock_pickle_load):
        """Test successful prediction with predict_v2 route."""
        mock_model = MagicMock()
        mock_prediction = MagicMock()
        mock_prediction.tolist.return_value = [[25000, 800, 5000]]
        mock_model.predict.return_value = mock_prediction
        mock_pickle_load.return_value = mock_model

        payload = {
            "cases_lag1": 10000,
            "deaths_lag1": 200,
            "recovered_lag1": 2000,
            "cases_lag2": 9500,
            "deaths_lag2": 190,
            "recovered_lag2": 1900,
            "cases_lag3": 9000,
            "deaths_lag3": 180,
            "recovered_lag3": 1800,
            "country": 174,
            "population": 67000000
        }
        response = self.app.post('/predict_v2', json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertIn("prediction", response.get_json())
        self.assertEqual(response.get_json()["prediction"], [[25000, 800, 5000]])

    def test_predict_v2_no_data(self):
        """Test predict_v2 route with no data provided."""
        response = self.app.post('/predict_v2', json={})
        self.assertEqual(response.status_code, 400)
        self.assertIn("No data provided", response.get_data(as_text=True))

    def test_predict_v2_missing_field(self):
        """Test predict_v2 route with missing required field."""
        payload = {
            "cases_lag1": 10000,
            "deaths_lag1": 200,
            "recovered_lag1": 2000,
            "cases_lag2": 9500,
            "deaths_lag2": 190,
            "recovered_lag2": 1900,
            "cases_lag3": 9000,
            "deaths_lag3": 180,
            "recovered_lag3": 1800,
            "country": 174
            # "population" is missing
        }
        response = self.app.post('/predict_v2', json=payload)
        self.assertEqual(response.status_code, 500)
        self.assertIn("population", response.get_data(as_text=True))

    @patch("pickle.load")
    @patch("builtins.open")
    def test_predict_v2_model_error(self, mock_open_builtin, mock_pickle_load):
        """Test predict_v2 route with model prediction error."""
        mock_model = MagicMock()
        mock_model.predict.side_effect = Exception("Model prediction failed")
        mock_pickle_load.return_value = mock_model

        payload = {
            "cases_lag1": 10000,
            "deaths_lag1": 200,
            "recovered_lag1": 2000,
            "cases_lag2": 9500,
            "deaths_lag2": 190,
            "recovered_lag2": 1900,
            "cases_lag3": 9000,
            "deaths_lag3": 180,
            "recovered_lag3": 1800,
            "country": 174,
            "population": 67000000
        }
        response = self.app.post('/predict_v2', json=payload)
        self.assertEqual(response.status_code, 500)
        self.assertIn("Model prediction failed", response.get_data(as_text=True))

    @patch("pickle.load", side_effect=Exception("Model file not found"))
    @patch("builtins.open")
    def test_predict_v2_model_load_error(self, mock_open_builtin, mock_pickle_load):
        """Test predict_v2 route with model loading error."""
        payload = {
            "cases_lag1": 10000,
            "deaths_lag1": 200,
            "recovered_lag1": 2000,
            "cases_lag2": 9500,
            "deaths_lag2": 190,
            "recovered_lag2": 1900,
            "cases_lag3": 9000,
            "deaths_lag3": 180,
            "recovered_lag3": 1800,
            "country": 174,
            "population": 67000000
        }
        response = self.app.post('/predict_v2', json=payload)
        self.assertEqual(response.status_code, 500)
        self.assertIn("Model file not found", response.get_data(as_text=True))

    @patch("pickle.load")
    @patch("builtins.open")
    def test_predict_v2_with_zero_population(self, mock_open_builtin, mock_pickle_load):
        """Test predict_v2 route with zero population (division by zero case)."""
        mock_model = MagicMock()
        mock_prediction = MagicMock()
        mock_prediction.tolist.return_value = [[float('inf'), float('inf'), float('inf')]]
        mock_model.predict.return_value = mock_prediction
        mock_pickle_load.return_value = mock_model

        payload = {
            "cases_lag1": 10000,
            "deaths_lag1": 200,
            "recovered_lag1": 2000,
            "cases_lag2": 9500,
            "deaths_lag2": 190,
            "recovered_lag2": 1900,
            "cases_lag3": 9000,
            "deaths_lag3": 180,
            "recovered_lag3": 1800,
            "country": 174,
            "population": 0
        }
        response = self.app.post('/predict_v2', json=payload)
        # Should handle division by zero gracefully
        self.assertEqual(response.status_code, 200)

    @patch("pickle.load")
    @patch("builtins.open")
    def test_predict_v2_negative_values(self, mock_open_builtin, mock_pickle_load):
        """Test predict_v2 route with negative input values."""
        mock_model = MagicMock()
        mock_prediction = MagicMock()
        mock_prediction.tolist.return_value = [[15000, 300, 3000]]
        mock_model.predict.return_value = mock_prediction
        mock_pickle_load.return_value = mock_model

        payload = {
            "cases_lag1": -1000,  # Negative values
            "deaths_lag1": -50,
            "recovered_lag1": -200,
            "cases_lag2": -950,
            "deaths_lag2": -45,
            "recovered_lag2": -190,
            "cases_lag3": -900,
            "deaths_lag3": -40,
            "recovered_lag3": -180,
            "country": 174,
            "population": 67000000
        }
        response = self.app.post('/predict_v2', json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertIn("prediction", response.get_json())
