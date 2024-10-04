import pytest
from django.contrib.auth import get_user_model
from django.test import RequestFactory

from guest_user.backends import GuestBackend
from guest_user.functions import get_guest_model

TEST_REQUEST_URL = "/some-url/"


@pytest.fixture
def backend():
    return GuestBackend()


@pytest.mark.django_db
def test_backend_without_user(backend):
    request = RequestFactory().get(TEST_REQUEST_URL)
    assert backend.authenticate(request=request, username="doesnotexist") is None


@pytest.mark.django_db
def test_backend_does_not_authenticate_normal_user(backend):
    UserModel = get_user_model()
    request = RequestFactory().get(TEST_REQUEST_URL)
    user = UserModel.objects.create_user(username="demo", password="hunter2")
    assert backend.authenticate(request=request, username=user.username) is None


@pytest.mark.django_db
def test_backend_authenticates_guest_user(backend):
    GuestModel = get_guest_model()
    guest = GuestModel.objects.create_guest_user()

    backend_guest = backend.authenticate(request=None, username=guest.username)
    assert backend_guest.username == guest.username


@pytest.mark.django_db
def test_backend_authenticates_guest_user_with_request(backend):
    GuestModel = get_guest_model()
    request = RequestFactory().get(TEST_REQUEST_URL)
    guest = GuestModel.objects.create_guest_user(request=request)

    backend_guest = backend.authenticate(request=request, username=guest.username)
    assert backend_guest.username == guest.username
