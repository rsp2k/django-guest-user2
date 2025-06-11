"""
Tests for guest_user management commands.
"""

from datetime import timedelta
from io import StringIO

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import override_settings
from django.utils.timezone import now
from guest_user.functions import get_guest_model


@pytest.mark.django_db
def test_delete_expired_users_command_exists():
    """Test that the delete_expired_users command can be imported and called."""
    try:
        call_command("delete_expired_users", verbosity=0)
    except CommandError:
        pytest.fail("delete_expired_users command should exist and be callable")


@pytest.mark.django_db
def test_delete_expired_users_no_users():
    """Test command behavior when no guest users exist."""
    GuestModel = get_guest_model()

    # Ensure no guest users exist
    assert GuestModel.objects.count() == 0

    # Command should run without error
    out = StringIO()
    call_command("delete_expired_users", stdout=out, verbosity=1)

    # Should still have no users
    assert GuestModel.objects.count() == 0


@pytest.mark.django_db
def test_delete_expired_users_no_expired():
    """Test command behavior when guest users exist but none are expired."""
    GuestModel = get_guest_model()

    # Create some non-expired guest users
    for _ in range(3):
        GuestModel.objects.create_guest_user()

    assert GuestModel.objects.count() == 3

    # Run the command
    out = StringIO()
    call_command("delete_expired_users", stdout=out, verbosity=1)

    # All users should still exist (not expired)
    assert GuestModel.objects.count() == 3


@pytest.mark.django_db
def test_delete_expired_users_with_expired():
    """Test command deletes expired guest users but keeps valid ones."""
    GuestModel = get_guest_model()

    # Create some current guest users
    for _ in range(2):
        GuestModel.objects.create_guest_user()

    # Create some expired guest users
    expired_users = []
    for _ in range(3):
        user = GuestModel.objects.create_guest_user()
        expired_users.append(user)

    # Force update the created_at timestamp to make them expired
    old_timestamp = now() - timedelta(days=25)  # Default MAX_AGE is ~2 weeks
    GuestModel.objects.filter(user__in=[u.user for u in expired_users]).update(
        created_at=old_timestamp
    )

    # Verify we have 5 total users, 3 expired
    assert GuestModel.objects.count() == 5
    assert GuestModel.objects.filter_expired().count() == 3

    # Run the command
    out = StringIO()
    call_command("delete_expired_users", stdout=out, verbosity=1)

    # Should have 2 users left (the non-expired ones)
    assert GuestModel.objects.count() == 2
    assert GuestModel.objects.filter_expired().count() == 0


@pytest.mark.django_db
def test_delete_expired_users_all_expired():
    """Test command when all guest users are expired."""
    GuestModel = get_guest_model()

    # Create expired guest users
    for _ in range(4):
        GuestModel.objects.create_guest_user()

    # Make them all expired
    old_timestamp = now() - timedelta(days=30)
    GuestModel.objects.all().update(created_at=old_timestamp)

    assert GuestModel.objects.count() == 4
    assert GuestModel.objects.filter_expired().count() == 4

    # Run the command
    call_command("delete_expired_users", verbosity=0)

    # All users should be deleted
    assert GuestModel.objects.count() == 0


@pytest.mark.django_db
@override_settings(GUEST_USER_MAX_AGE=3600)  # 1 hour
def test_delete_expired_users_custom_max_age():
    """Test command respects custom MAX_AGE setting."""
    GuestModel = get_guest_model()

    # Create a user that would be valid with default settings but expired with 1 hour
    user = GuestModel.objects.create_guest_user()

    # Set timestamp to 2 hours ago (expired with 1 hour MAX_AGE)
    old_timestamp = now() - timedelta(hours=2)
    GuestModel.objects.filter(user=user.user).update(created_at=old_timestamp)

    assert GuestModel.objects.count() == 1
    assert GuestModel.objects.filter_expired().count() == 1

    # Run the command
    call_command("delete_expired_users", verbosity=0)

    # User should be deleted due to custom MAX_AGE
    assert GuestModel.objects.count() == 0


@pytest.mark.django_db
def test_delete_expired_users_command_output():
    """Test command output at different verbosity levels."""
    GuestModel = get_guest_model()

    # Create some expired users
    for _ in range(2):
        GuestModel.objects.create_guest_user()

    # Make them expired
    old_timestamp = now() - timedelta(days=20)
    GuestModel.objects.all().update(created_at=old_timestamp)

    # Test verbosity 0 (no output)
    out = StringIO()
    call_command("delete_expired_users", stdout=out, verbosity=0)
    assert out.getvalue() == ""

    # Recreate expired users for next test
    for _ in range(2):
        GuestModel.objects.create_guest_user()
    GuestModel.objects.all().update(created_at=old_timestamp)

    # Test verbosity 1 (should have some output)
    out = StringIO()
    call_command("delete_expired_users", stdout=out, verbosity=1)
    # The actual output depends on implementation, just ensure it doesn't crash


@pytest.mark.django_db
def test_delete_expired_users_cascade_behavior():
    """Test that deleting guest users properly cascades to User model."""
    from django.contrib.auth import get_user_model

    GuestModel = get_guest_model()
    UserModel = get_user_model()

    # Create expired guest users
    guest_users = []
    user_ids = []
    for _ in range(3):
        guest = GuestModel.objects.create_guest_user()
        guest_users.append(guest)
        user_ids.append(guest.user.id)

    # Make them expired
    old_timestamp = now() - timedelta(days=25)
    GuestModel.objects.all().update(created_at=old_timestamp)

    # Verify both Guest and User records exist
    assert GuestModel.objects.count() == 3
    assert UserModel.objects.filter(id__in=user_ids).count() == 3

    # Run the command
    call_command("delete_expired_users", verbosity=0)

    # Verify both Guest and User records are deleted (CASCADE)
    assert GuestModel.objects.count() == 0
    assert UserModel.objects.filter(id__in=user_ids).count() == 0


@pytest.mark.django_db
def test_delete_expired_users_mixed_users():
    """Test command only deletes guest users, not regular users."""
    from django.contrib.auth import get_user_model

    GuestModel = get_guest_model()
    UserModel = get_user_model()

    # Create some regular users
    regular_user = UserModel.objects.create_user("regular_user", password="test123")

    # Create some guest users
    guest_users = []
    for _ in range(2):
        guest = GuestModel.objects.create_guest_user()
        guest_users.append(guest)

    # Make guest users expired
    old_timestamp = now() - timedelta(days=25)
    GuestModel.objects.all().update(created_at=old_timestamp)

    # Verify initial state
    assert UserModel.objects.count() == 3  # 1 regular + 2 guests
    assert GuestModel.objects.count() == 2

    # Run the command
    call_command("delete_expired_users", verbosity=0)

    # Regular user should remain, guest users should be deleted
    assert UserModel.objects.count() == 1
    assert GuestModel.objects.count() == 0
    assert UserModel.objects.get(id=regular_user.id)  # Regular user still exists


@pytest.mark.django_db
def test_delete_expired_users_idempotent():
    """Test that running the command multiple times is safe."""
    GuestModel = get_guest_model()

    # Create expired guest users
    for _ in range(2):
        GuestModel.objects.create_guest_user()

    old_timestamp = now() - timedelta(days=25)
    GuestModel.objects.all().update(created_at=old_timestamp)

    assert GuestModel.objects.count() == 2

    # Run command multiple times
    call_command("delete_expired_users", verbosity=0)
    assert GuestModel.objects.count() == 0

    call_command("delete_expired_users", verbosity=0)  # Should not crash
    assert GuestModel.objects.count() == 0

    call_command("delete_expired_users", verbosity=0)  # Should not crash
    assert GuestModel.objects.count() == 0
