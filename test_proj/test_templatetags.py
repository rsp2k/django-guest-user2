"""
Tests for guest_user template tags.
"""
import pytest
from django.contrib.auth import get_user_model
from django.template import Context, Template, TemplateSyntaxError
from django.template.loader import get_template
from django.test import RequestFactory
from guest_user.functions import get_guest_model


@pytest.mark.django_db
class TestGuestUserTemplateTag:
    """Test the is_guest_user template filter."""
    
    def test_load_guest_user_templatetags(self):
        """Test that guest_user template tags can be loaded."""
        template_string = "{% load guest_user %}"
        template = Template(template_string)
        # Should not raise an exception
        assert template is not None
    
    def test_is_guest_user_filter_with_guest_user(self):
        """Test is_guest_user filter returns True for guest users."""
        GuestModel = get_guest_model()
        guest_user = GuestModel.objects.create_guest_user()
        
        template_string = """
        {% load guest_user %}
        {% if user|is_guest_user %}guest{% else %}not_guest{% endif %}
        """
        
        template = Template(template_string)
        context = Context({"user": guest_user})
        result = template.render(context).strip()
        
        assert result == "guest"
    
    def test_is_guest_user_filter_with_regular_user(self):
        """Test is_guest_user filter returns False for regular users."""
        UserModel = get_user_model()
        regular_user = UserModel.objects.create_user("testuser", password="test123")
        
        template_string = """
        {% load guest_user %}
        {% if user|is_guest_user %}guest{% else %}not_guest{% endif %}
        """
        
        template = Template(template_string)
        context = Context({"user": regular_user})
        result = template.render(context).strip()
        
        assert result == "not_guest"
    
    def test_is_guest_user_filter_with_anonymous_user(self):
        """Test is_guest_user filter returns False for anonymous users."""
        from django.contrib.auth.models import AnonymousUser
        
        anonymous_user = AnonymousUser()
        
        template_string = """
        {% load guest_user %}
        {% if user|is_guest_user %}guest{% else %}not_guest{% endif %}
        """
        
        template = Template(template_string)
        context = Context({"user": anonymous_user})
        result = template.render(context).strip()
        
        assert result == "not_guest"
    
    def test_is_guest_user_filter_with_none(self):
        """Test is_guest_user filter handles None gracefully."""
        template_string = """
        {% load guest_user %}
        {% if user|is_guest_user %}guest{% else %}not_guest{% endif %}
        """
        
        template = Template(template_string)
        context = Context({"user": None})
        result = template.render(context).strip()
        
        assert result == "not_guest"
    
    def test_is_guest_user_filter_practical_usage(self):
        """Test practical template usage scenarios."""
        GuestModel = get_guest_model()
        UserModel = get_user_model()
        
        guest_user = GuestModel.objects.create_guest_user()
        regular_user = UserModel.objects.create_user("regular", password="test123")
        
        template_string = """
        {% load guest_user %}
        {% if user|is_guest_user %}
            <div class="guest-banner">Welcome guest! <a href="/convert/">Create account</a></div>
        {% else %}
            <div class="user-welcome">Hello {{ user.username }}!</div>
        {% endif %}
        """
        
        template = Template(template_string)
        
        # Test with guest user
        context = Context({"user": guest_user})
        result = template.render(context).strip()
        assert "guest-banner" in result
        assert "Create account" in result
        
        # Test with regular user
        context = Context({"user": regular_user})
        result = template.render(context).strip()
        assert "user-welcome" in result
        assert "Hello regular!" in result
    
    def test_is_guest_user_filter_in_conditional_blocks(self):
        """Test filter usage in various conditional contexts."""
        GuestModel = get_guest_model()
        guest_user = GuestModel.objects.create_guest_user()
        
        template_string = """
        {% load guest_user %}
        {% if user|is_guest_user and user.is_authenticated %}
            authenticated_guest
        {% elif user|is_guest_user %}
            guest_not_authenticated
        {% else %}
            not_guest
        {% endif %}
        """
        
        template = Template(template_string)
        context = Context({"user": guest_user})
        result = template.render(context).strip()
        
        # Guest users should be authenticated
        assert result == "authenticated_guest"
    
    def test_is_guest_user_filter_multiple_users(self):
        """Test filter with multiple user types in same template."""
        GuestModel = get_guest_model()
        UserModel = get_user_model()
        
        guest_user = GuestModel.objects.create_guest_user()
        regular_user = UserModel.objects.create_user("regular", password="test123")
        
        template_string = """
        {% load guest_user %}
        Guest: {% if guest|is_guest_user %}yes{% else %}no{% endif %}
        Regular: {% if regular|is_guest_user %}yes{% else %}no{% endif %}
        """
        
        template = Template(template_string)
        context = Context({
            "guest": guest_user,
            "regular": regular_user
        })
        result = template.render(context).strip()
        
        assert "Guest: yes" in result
        assert "Regular: no" in result
    
    def test_is_guest_user_filter_chaining(self):
        """Test filter can be chained with other filters."""
        GuestModel = get_guest_model()
        guest_user = GuestModel.objects.create_guest_user()
        
        template_string = """
        {% load guest_user %}
        {{ user|is_guest_user|yesno:"Guest User,Regular User" }}
        """
        
        template = Template(template_string)
        context = Context({"user": guest_user})
        result = template.render(context).strip()
        
        assert result == "Guest User"
    
    def test_is_guest_user_filter_with_converted_user(self):
        """Test filter correctly identifies converted users as non-guests."""
        from guest_user.forms import UserCreationForm
        
        GuestModel = get_guest_model()
        guest_user = GuestModel.objects.create_guest_user()
        
        # Convert the guest user
        form_data = {
            "username": "converted_user",
            "password1": "complexpassword123",
            "password2": "complexpassword123",
        }
        form = UserCreationForm(instance=guest_user, data=form_data)
        assert form.is_valid()
        converted_user = GuestModel.objects.convert(form)
        
        template_string = """
        {% load guest_user %}
        {% if user|is_guest_user %}guest{% else %}regular{% endif %}
        """
        
        template = Template(template_string)
        context = Context({"user": converted_user})
        result = template.render(context).strip()
        
        assert result == "regular"
    
    def test_template_tag_documentation_examples(self):
        """Test examples from the template tag docstring."""
        GuestModel = get_guest_model()
        guest_user = GuestModel.objects.create_guest_user()
        
        # Example from docstring
        template_string = """
        {% load guest_user %}
        {% if user|is_guest_user %}
            Hello guest.
        {% endif %}
        """
        
        template = Template(template_string)
        context = Context({"user": guest_user})
        result = template.render(context).strip()
        
        assert "Hello guest." in result
    
    def test_is_guest_user_filter_with_request_context(self):
        """Test filter works correctly in request context processor scenario."""
        from django.contrib.auth.models import AnonymousUser
        
        GuestModel = get_guest_model()
        guest_user = GuestModel.objects.create_guest_user()
        
        rf = RequestFactory()
        request = rf.get("/")
        request.user = guest_user
        
        template_string = """
        {% load guest_user %}
        User: {{ request.user.username }}
        Is guest: {% if request.user|is_guest_user %}yes{% else %}no{% endif %}
        """
        
        template = Template(template_string)
        context = Context({"request": request})
        result = template.render(context)
        
        assert f"User: {guest_user.username}" in result
        assert "Is guest: yes" in result


class TestTemplateTagIntegration:
    """Test template tag integration with Django template system."""
    
    def test_template_tag_namespace_isolation(self):
        """Test that guest_user tags don't conflict with other template tags."""
        template_string = """
        {% load guest_user %}
        {% load staticfiles %}
        {% if user|is_guest_user %}guest{% else %}regular{% endif %}
        """
        
        # Should be able to load both without conflict
        try:
            template = Template(template_string)
            assert template is not None
        except TemplateSyntaxError:
            # staticfiles might not be available in test environment
            # Try with a built-in tag instead
            template_string = """
            {% load guest_user %}
            {% if user|is_guest_user %}guest{% else %}regular{% endif %}
            {% now "Y-m-d" %}
            """
            template = Template(template_string)
            assert template is not None
    
    @pytest.mark.django_db
    def test_template_tag_with_template_file(self):
        """Test that template tags work when loaded from template files."""
        GuestModel = get_guest_model()
        guest_user = GuestModel.objects.create_guest_user()
        
        # This would typically be tested with actual template files
        # For now, we simulate with Template object
        template_content = """
        {% load guest_user %}
        <!DOCTYPE html>
        <html>
        <head><title>Test</title></head>
        <body>
            {% if user|is_guest_user %}
                <div id="guest-notice">
                    <p>You're browsing as a guest.</p>
                    <a href="/convert/">Create an account</a>
                </div>
            {% else %}
                <div id="user-welcome">
                    <p>Welcome back, {{ user.username }}!</p>
                </div>
            {% endif %}
        </body>
        </html>
        """
        
        template = Template(template_content)
        context = Context({"user": guest_user})
        result = template.render(context)
        
        assert "guest-notice" in result
        assert "You're browsing as a guest." in result
        assert "Create an account" in result
        assert "user-welcome" not in result
    
    @pytest.mark.django_db
    def test_template_tag_performance(self):
        """Test that template tag doesn't cause performance issues."""
        import time
        
        GuestModel = get_guest_model()
        guest_user = GuestModel.objects.create_guest_user()
        
        template_string = """
        {% load guest_user %}
        {% for i in range %}
            {% if user|is_guest_user %}G{% else %}R{% endif %}
        {% endfor %}
        """
        
        template = Template(template_string)
        context = Context({
            "user": guest_user,
            "range": range(100)  # Test with repeated filter usage
        })
        
        start_time = time.time()
        result = template.render(context)
        end_time = time.time()
        
        # Should complete quickly (less than 1 second for 100 iterations)
        assert end_time - start_time < 1.0
        # Should render correctly
        assert "G" * 100 in result.replace("\n", "").replace(" ", "")
