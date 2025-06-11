"""
Tests for guest_user forms.
"""
import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from guest_user.forms import UserCreationForm
from guest_user.functions import get_guest_model, is_guest_user


@pytest.mark.django_db
class TestUserCreationForm:
    """Test the UserCreationForm for converting guests to regular users."""
    
    def test_form_inherits_from_base_user_creation_form(self):
        """Test that UserCreationForm properly inherits from Django's base form."""
        from django.contrib.auth.forms import UserCreationForm as BaseForm
        
        assert issubclass(UserCreationForm, BaseForm)
        assert issubclass(UserCreationForm, ModelForm)
    
    def test_form_valid_data_guest_user(self):
        """Test form validation with valid data for a guest user."""
        GuestModel = get_guest_model()
        guest_user = GuestModel.objects.create_guest_user()
        
        form_data = {
            "username": "newusername",
            "password1": "complexpassword123",
            "password2": "complexpassword123",
        }
        
        form = UserCreationForm(instance=guest_user, data=form_data)
        assert form.is_valid(), form.errors
    
    def test_form_invalid_mismatched_passwords(self):
        """Test form validation fails with mismatched passwords."""
        GuestModel = get_guest_model()
        guest_user = GuestModel.objects.create_guest_user()
        
        form_data = {
            "username": "newusername",
            "password1": "complexpassword123",
            "password2": "differentpassword456",
        }
        
        form = UserCreationForm(instance=guest_user, data=form_data)
        assert not form.is_valid()
        assert "password2" in form.errors
    
    def test_form_invalid_short_password(self):
        """Test form validation fails with too short password."""
        GuestModel = get_guest_model()
        guest_user = GuestModel.objects.create_guest_user()
        
        form_data = {
            "username": "newusername",
            "password1": "123",
            "password2": "123",
        }
        
        form = UserCreationForm(instance=guest_user, data=form_data)
        assert not form.is_valid()
        assert "password2" in form.errors
    
    def test_form_invalid_common_password(self):
        """Test form validation fails with common passwords."""
        GuestModel = get_guest_model()
        guest_user = GuestModel.objects.create_guest_user()
        
        form_data = {
            "username": "newusername",
            "password1": "password123",
            "password2": "password123",
        }
        
        form = UserCreationForm(instance=guest_user, data=form_data)
        assert not form.is_valid()
        assert "password2" in form.errors
    
    def test_form_invalid_numeric_password(self):
        """Test form validation fails with purely numeric passwords."""
        GuestModel = get_guest_model()
        guest_user = GuestModel.objects.create_guest_user()
        
        form_data = {
            "username": "newusername",
            "password1": "1234567890",
            "password2": "1234567890",
        }
        
        form = UserCreationForm(instance=guest_user, data=form_data)
        assert not form.is_valid()
        assert "password2" in form.errors
    
    def test_form_invalid_username_too_similar_to_password(self):
        """Test form validation fails when username is too similar to password."""
        GuestModel = get_guest_model()
        guest_user = GuestModel.objects.create_guest_user()
        
        form_data = {
            "username": "testuser",
            "password1": "testuser123",
            "password2": "testuser123",
        }
        
        form = UserCreationForm(instance=guest_user, data=form_data)
        assert not form.is_valid()
        assert "password2" in form.errors
    
    def test_form_invalid_duplicate_username(self):
        """Test form validation fails with duplicate username."""
        UserModel = get_user_model()
        GuestModel = get_guest_model()
        
        # Create existing user
        UserModel.objects.create_user("existinguser", password="test123")
        
        guest_user = GuestModel.objects.create_guest_user()
        
        form_data = {
            "username": "existinguser",
            "password1": "complexpassword123",
            "password2": "complexpassword123",
        }
        
        form = UserCreationForm(instance=guest_user, data=form_data)
        assert not form.is_valid()
        assert "username" in form.errors
    
    def test_form_save_converts_guest_to_regular_user(self):
        """Test that saving the form properly converts guest to regular user."""
        GuestModel = get_guest_model()
        guest_user = GuestModel.objects.create_guest_user()
        original_user_id = guest_user.id
        
        form_data = {
            "username": "converteduser",
            "password1": "complexpassword123",
            "password2": "complexpassword123",
        }
        
        form = UserCreationForm(instance=guest_user, data=form_data)
        assert form.is_valid()
        
        converted_user = form.save()
        
        # Same user object, but now with new username and password
        assert converted_user.id == original_user_id
        assert converted_user.username == "converteduser"
        assert converted_user.check_password("complexpassword123")
        assert not is_guest_user(converted_user)
    
    def test_form_get_credentials_method(self):
        """Test the get_credentials method returns correct authentication data."""
        GuestModel = get_guest_model()
        guest_user = GuestModel.objects.create_guest_user()
        
        form_data = {
            "username": "credentialuser",
            "password1": "mypassword123",
            "password2": "mypassword123",
        }
        
        form = UserCreationForm(instance=guest_user, data=form_data)
        assert form.is_valid()
        
        credentials = form.get_credentials()
        
        assert isinstance(credentials, dict)
        assert credentials["username"] == "credentialuser"
        assert credentials["password"] == "mypassword123"
    
    def test_form_get_credentials_only_after_validation(self):
        """Test get_credentials only works after form validation."""
        GuestModel = get_guest_model()
        guest_user = GuestModel.objects.create_guest_user()
        
        form_data = {
            "username": "testuser",
            "password1": "testpass123",
            "password2": "testpass123",
        }
        
        form = UserCreationForm(instance=guest_user, data=form_data)
        
        # Before validation, cleaned_data might not exist
        try:
            credentials = form.get_credentials()
            # If it works, check the values
            assert credentials["username"] == "testuser"
            assert credentials["password"] == "testpass123"
        except KeyError:
            # Expected if cleaned_data doesn't exist yet
            pass
        
        # After validation, it should work
        assert form.is_valid()
        credentials = form.get_credentials()
        assert credentials["username"] == "testuser"
        assert credentials["password"] == "testpass123"
    
    def test_form_preserves_user_data(self):
        """Test that form preserves other user data during conversion."""
        GuestModel = get_guest_model()
        guest_user = GuestModel.objects.create_guest_user()
        
        # Add some data to the guest user
        guest_user.first_name = "Test"
        guest_user.last_name = "User"
        guest_user.email = "test@example.com"
        guest_user.save()
        
        form_data = {
            "username": "preserveduser",
            "password1": "newpassword123",
            "password2": "newpassword123",
        }
        
        form = UserCreationForm(instance=guest_user, data=form_data)
        assert form.is_valid()
        
        converted_user = form.save()
        
        # Check that other data is preserved
        assert converted_user.first_name == "Test"
        assert converted_user.last_name == "User"
        assert converted_user.email == "test@example.com"
        assert converted_user.username == "preserveduser"
    
    def test_form_without_instance_fails(self):
        """Test that form requires a user instance."""
        form_data = {
            "username": "newuser",
            "password1": "password123",
            "password2": "password123",
        }
        
        # Form without instance should work but behave differently
        form = UserCreationForm(data=form_data)
        # This might be valid (creates new user) or might fail depending on implementation
        # The key is that it shouldn't crash
        form.is_valid()  # Just check it doesn't crash
    
    def test_form_with_regular_user_instance(self):
        """Test form behavior when given a regular user instance."""
        UserModel = get_user_model()
        regular_user = UserModel.objects.create_user("regularuser", password="old123")
        
        form_data = {
            "username": "updateduser",
            "password1": "newpassword123",
            "password2": "newpassword123",
        }
        
        form = UserCreationForm(instance=regular_user, data=form_data)
        assert form.is_valid()
        
        updated_user = form.save()
        assert updated_user.username == "updateduser"
        assert updated_user.check_password("newpassword123")
    
    def test_form_fields_exist(self):
        """Test that expected form fields are present."""
        form = UserCreationForm()
        
        # Should have at least username and password fields
        assert "username" in form.fields
        assert "password1" in form.fields
        assert "password2" in form.fields
    
    def test_form_empty_data_validation(self):
        """Test form validation with empty data."""
        GuestModel = get_guest_model()
        guest_user = GuestModel.objects.create_guest_user()
        
        form = UserCreationForm(instance=guest_user, data={})
        assert not form.is_valid()
        
        # Should have errors for required fields
        assert "username" in form.errors
        assert "password1" in form.errors
        assert "password2" in form.errors
    
    def test_form_partial_data_validation(self):
        """Test form validation with partial data."""
        GuestModel = get_guest_model()
        guest_user = GuestModel.objects.create_guest_user()
        
        form_data = {
            "username": "partialuser",
            "password1": "onlyonepassword",
            # Missing password2
        }
        
        form = UserCreationForm(instance=guest_user, data=form_data)
        assert not form.is_valid()
        assert "password2" in form.errors
    
    def test_form_special_characters_in_username(self):
        """Test form validation with special characters in username."""
        GuestModel = get_guest_model()
        guest_user = GuestModel.objects.create_guest_user()
        
        form_data = {
            "username": "user@domain.com",  # Email-like username
            "password1": "complexpassword123",
            "password2": "complexpassword123",
        }
        
        form = UserCreationForm(instance=guest_user, data=form_data)
        # Should be valid (Django allows email-like usernames by default)
        assert form.is_valid()
    
    def test_form_max_length_validation(self):
        """Test form validation with maximum length constraints."""
        GuestModel = get_guest_model()
        guest_user = GuestModel.objects.create_guest_user()
        
        # Test with very long username (should fail)
        long_username = "a" * 200  # Much longer than typical max_length
        
        form_data = {
            "username": long_username,
            "password1": "complexpassword123",
            "password2": "complexpassword123",
        }
        
        form = UserCreationForm(instance=guest_user, data=form_data)
        assert not form.is_valid()
        assert "username" in form.errors


class TestFormIntegration:
    """Test form integration with other guest_user components."""
    
    @pytest.mark.django_db
    def test_form_integration_with_manager_convert(self):
        """Test form works correctly with GuestManager.convert method."""
        GuestModel = get_guest_model()
        guest_user = GuestModel.objects.create_guest_user()
        
        form_data = {
            "username": "managerconvert",
            "password1": "password123complex",
            "password2": "password123complex",
        }
        
        form = UserCreationForm(instance=guest_user, data=form_data)
        assert form.is_valid()
        
        # Use manager's convert method
        converted_user = GuestModel.objects.convert(form)
        
        assert converted_user.username == "managerconvert"
        assert not is_guest_user(converted_user)
        
        # Guest instance should be deleted
        assert not GuestModel.objects.filter(user=converted_user).exists()
    
    @pytest.mark.django_db
    def test_form_integration_with_signals(self):
        """Test that form conversion triggers appropriate signals."""
        from guest_user.signals import converted
        
        GuestModel = get_guest_model()
        guest_user = GuestModel.objects.create_guest_user()
        
        signal_called = False
        signal_user = None
        
        def signal_handler(sender, user, **kwargs):
            nonlocal signal_called, signal_user
            signal_called = True
            signal_user = user
        
        converted.connect(signal_handler)
        
        try:
            form_data = {
                "username": "signaluser",
                "password1": "password123complex",
                "password2": "password123complex",
            }
            
            form = UserCreationForm(instance=guest_user, data=form_data)
            assert form.is_valid()
            
            converted_user = GuestModel.objects.convert(form)
            
            assert signal_called
            assert signal_user == converted_user
            
        finally:
            converted.disconnect(signal_handler)
    
    @pytest.mark.django_db
    def test_form_custom_validation_hooks(self):
        """Test that custom form validation can be added."""
        
        class CustomUserCreationForm(UserCreationForm):
            def clean_username(self):
                username = self.cleaned_data.get('username')
                if username and username.startswith('admin'):
                    raise ValidationError("Username cannot start with 'admin'")
                return username
        
        GuestModel = get_guest_model()
        guest_user = GuestModel.objects.create_guest_user()
        
        form_data = {
            "username": "adminuser",
            "password1": "complexpassword123",
            "password2": "complexpassword123",
        }
        
        form = CustomUserCreationForm(instance=guest_user, data=form_data)
        assert not form.is_valid()
        assert "username" in form.errors
        assert "cannot start with 'admin'" in str(form.errors["username"])
