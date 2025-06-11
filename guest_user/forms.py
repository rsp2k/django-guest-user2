from django.contrib.auth.forms import UserCreationForm as BaseUserCreationForm


class UserCreationForm(BaseUserCreationForm):
    """
    A modelform that creates a standard Django user.

    Custom implementations must implement :meth:`get_credentials`.

    """

    def get_credentials(self) -> dict:
        """
        Get the credentials required to log the user in after conversion.

        The credentials are passed to Django's :func:`authenticate()<django.contrib.auth.authenticate>`.

        :return: Login credentials. This is usually a dict with "username" and "password".

        """
        # Check if form has been validated and cleaned_data exists
        if not hasattr(self, "cleaned_data"):
            raise AttributeError(
                "cleaned_data is not available. Please call is_valid() first."
            )

        return {
            "username": self.cleaned_data["username"],
            "password": self.cleaned_data["password1"],
        }

    def save(self, commit=True):
        """
        Save the form and properly convert guest user to regular user.
        """
        user = super().save(commit=commit)

        if commit and self.instance:
            # Import here to avoid circular imports
            from .functions import get_guest_model

            # Remove the guest instance if it exists
            GuestModel = get_guest_model()
            GuestModel.objects.filter(user=user).delete()

        return user
