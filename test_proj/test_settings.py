import pytest
from django.test import RequestFactory

from guest_user.functions import get_guest_model
from guest_user.models import GuestManager

from .models import CustomGuest


@pytest.mark.django_db
def test_setting_enabled(settings, client):
    settings.GUEST_USER_ENABLED = False

    response = client.get("/allow_guest_user/")
    assert response.status_code == 200
    assert response.context["user"].is_anonymous


def my_name_generator(**kwargs):
    return "custom_name"


TEST_USERNAME = "custom_name"
TEST_REQUEST_URL = "/some-url/"


def my_name_generator_using_request(request=None):
    prefix = ""
    if request:
        prefix = request.COOKIES['username_prefix']
    return f"{prefix}{TEST_USERNAME}"


def test_setting_name_generator(settings):
    settings.GUEST_USER_NAME_GENERATOR = "test_proj.test_settings.my_name_generator"
    assert GuestManager().generate_username() == TEST_USERNAME


def test_setting_name_generator_passing_request(settings):
    settings.GUEST_USER_NAME_GENERATOR = "test_proj.test_settings.my_name_generator"
    request = RequestFactory().get(TEST_REQUEST_URL)
    assert GuestManager().generate_username(request=request) == TEST_USERNAME


def test_setting_name_generator_using_request(settings):
    TEST_PREFIX = 'the_prefix_'
    request = RequestFactory().get(TEST_REQUEST_URL)
    request.COOKIES['username_prefix'] = TEST_PREFIX

    settings.GUEST_USER_NAME_GENERATOR = "test_proj.test_settings.my_name_generator_using_request"
    assert GuestManager().generate_username(request=request) == f"{TEST_PREFIX}{TEST_USERNAME}"


def test_setting_model(settings):
    """Check swappable Guest model."""
    settings.GUEST_USER_MODEL = "test_proj.CustomGuest"

    assert get_guest_model() == CustomGuest


@pytest.mark.django_db
def test_setting_model_create(settings):
    """Check swappable Guest model."""
    settings.GUEST_USER_MODEL = "test_proj.CustomGuest"

    guest = get_guest_model().objects.create_guest_user()
    guest_instance = CustomGuest.objects.get(user=guest.pk)
    assert guest_instance.extra_data == "dummy"
