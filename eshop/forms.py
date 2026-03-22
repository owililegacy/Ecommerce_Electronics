from django import forms
from .models import Order, ProductReview
from django.contrib.auth.models import User
from django.contrib.auth.forms import (
    UserCreationForm,
    AuthenticationForm,
    PasswordChangeForm,
)
from .models import EshopUser
import re


class UserRegisterForm(UserCreationForm):
    """
    Registration form for new users with improved error handling
    """

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={
                "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent",
                "placeholder": "Enter your email",
            }
        ),
    )

    phone_number = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent",
                "placeholder": "+1234567890",
            }
        ),
    )

    class Meta:
        model = EshopUser
        fields = ["username", "email", "password1", "password2", "phone_number"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Customize labels
        self.fields["username"].label = "Username"
        self.fields["email"].label = "Email Address"
        self.fields["password1"].label = "Password"
        self.fields["password2"].label = "Confirm Password"
        self.fields["phone_number"].label = "Phone Number (Optional)"

        # Apply Tailwind CSS classes to all fields
        for field_name, field in self.fields.items():
            # Don't override existing classes, just add Tailwind classes
            existing_classes = field.widget.attrs.get("class", "")
            field.widget.attrs.update(
                {
                    "class": f"{existing_classes} w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent transition-all duration-200",
                    "placeholder": field.label,
                }
            )

        # Special handling for password fields to add padding for eye icon
        self.fields["password1"].widget.attrs.update({"class": "pr-10"})
        self.fields["password2"].widget.attrs.update({"class": "pr-10"})

    def clean_email(self):
        """
        Validate email uniqueness
        """
        email = self.cleaned_data.get("email")
        if email and EshopUser.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email

    def clean_username(self):
        """
        Validate username
        """
        username = self.cleaned_data.get("username")
        if username:
            if len(username) < 3:
                raise forms.ValidationError(
                    "Username must be at least 3 characters long."
                )
            if EshopUser.objects.filter(username=username).exists():
                raise forms.ValidationError("This username is already taken.")
        return username

    def clean_password1(self):
        """
        Validate password strength - returns only first error
        """
        password = self.cleaned_data.get("password1")

        if not password:
            return password

        # Check each validation rule in order of importance
        if len(password) < 8:
            raise forms.ValidationError("Password must be at least 8 characters long.")

        if not re.search(r"[A-Z]", password):
            raise forms.ValidationError(
                "Password must contain at least one uppercase letter."
            )

        if not re.search(r"[a-z]", password):
            raise forms.ValidationError(
                "Password must contain at least one lowercase letter."
            )

        if not re.search(r"\d", password):
            raise forms.ValidationError("Password must contain at least one number.")

        # Optional: Check for special characters
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            # This is a warning, not an error - you can add it as a help text instead
            pass

        return password

    def clean_password2(self):
        """
        Validate password confirmation - returns only first error
        """
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match.")

        return password2

    def clean_phone_number(self):
        """
        Validate phone number format
        """
        phone = self.cleaned_data.get("phone_number")
        if phone:
            # Simple phone validation (can be customized)
            if not re.match(r"^\+?1?\d{9,15}$", phone):
                raise forms.ValidationError(
                    "Enter a valid phone number (e.g., +1234567890)"
                )
        return phone

    def add_error(self, field, error):
        """
        Override add_error to ensure only the first error is stored per field
        """
        if field in self._errors:
            # If there's already an error for this field, don't add another
            return
        super().add_error(field, error)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if self.cleaned_data.get("phone_number"):
            user.phone_number = self.cleaned_data["phone_number"]
        if commit:
            user.save()
        return user


class UserProfileUpdateForm(forms.ModelForm):
    """
    Form for updating user profile information
    """

    class Meta:
        model = EshopUser
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "address",
            "profile_image",
            "date_of_birth",
            "newsletter_subscribed",
        ]
        widgets = {
            "username": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500",
                    "placeholder": "Username",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500",
                    "placeholder": "Email address",
                }
            ),
            "first_name": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500",
                    "placeholder": "First name",
                }
            ),
            "last_name": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500",
                    "placeholder": "Last name",
                }
            ),
            "phone_number": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500",
                    "placeholder": "+1234567890",
                }
            ),
            "address": forms.Textarea(
                attrs={
                    "rows": 3,
                    "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500",
                    "placeholder": "Your address",
                }
            ),
            "date_of_birth": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500",
                }
            ),
            "newsletter_subscribed": forms.CheckboxInput(
                attrs={
                    "class": "form-checkbox h-5 w-5 text-orange-600 rounded focus:ring-orange-500"
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Mark required fields
        self.fields["username"].required = True
        self.fields["email"].required = True

    def clean_email(self):
        """
        Validate email uniqueness excluding current user
        """
        email = self.cleaned_data.get("email")
        if self.instance and self.instance.pk:
            if (
                EshopUser.objects.filter(email=email)
                .exclude(pk=self.instance.pk)
                .exists()
            ):
                raise forms.ValidationError("This email is already registered.")
        return email

    def clean_username(self):
        """
        Validate username uniqueness excluding current user
        """
        username = self.cleaned_data.get("username")
        if self.instance and self.instance.pk:
            if (
                EshopUser.objects.filter(username=username)
                .exclude(pk=self.instance.pk)
                .exists()
            ):
                raise forms.ValidationError("This username is already taken.")
        return username


class CustomPasswordChangeForm(PasswordChangeForm):
    """
    Custom password change form with better styling
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update(
                {
                    "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent",
                    "placeholder": field.label,
                }
            )


class UserLoginForm(AuthenticationForm):
    class Meta:
        model = User
        fields = ["username", "password"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Customize field labels for better UX
        self.fields["username"].label = "Username"
        self.fields["password"].label = "Password"

        # Add CSS classes and placeholders
        for field_name, field in self.fields.items():
            field.widget.attrs.update(
                {"class": "form-control w-100", "placeholder": field.label}
            )

            # Remove default help texts for cleaner look
            if field_name == "password":
                field.help_text = None

    def clean(self):
        """Custom validation with single, clear error messages per field"""
        cleaned_data = super().clean()
        errors = {}

        # Username validation
        username = cleaned_data.get("username")
        if username:
            if not User.objects.filter(username=username).exists():
                errors["username"] = "User not found."

        # Add errors to the form
        for field, message in errors.items():
            self.add_error(field, message)

        return cleaned_data


class OrderForm(forms.ModelForm):
    name = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent",
                "placeholder": "Full Name",
            }
        ),
    )

    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(
            attrs={
                "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent",
                "placeholder": "Email Address",
            }
        ),
    )

    phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent",
                "placeholder": "+1234567890",
            }
        ),
    )

    class Meta:
        model = Order
        fields = ["name", "email", "phone", "address", "postal_code", "city"]
        widgets = {
            "address": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent",
                    "placeholder": "Street Address",
                }
            ),
            "postal_code": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent",
                    "placeholder": "Postal Code",
                }
            ),
            "city": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent",
                    "placeholder": "City",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        # Set initial values for authenticated users
        if user and user.is_authenticated:
            # Get full name
            full_name = user.get_full_name() or user.username
            self.fields["name"].initial = full_name
            self.fields["email"].initial = user.email

            # Set phone if available
            if hasattr(user, "phone_number") and user.phone_number:
                self.fields["phone"].initial = user.phone_number
            elif hasattr(user, "phone") and user.phone:
                self.fields["phone"].initial = user.phone

        # Apply consistent styling to all fields
        for field_name, field in self.fields.items():
            # Don't override existing classes
            if "class" not in field.widget.attrs:
                field.widget.attrs.update(
                    {
                        "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                    }
                )

            # Add placeholder if not set
            if "placeholder" not in field.widget.attrs:
                field.widget.attrs["placeholder"] = field.label

    def clean_phone(self):
        """Validate phone number format"""
        phone = self.cleaned_data.get("phone")
        if phone:
            # Basic phone validation (adjust regex as needed)
            import re

            if not re.match(r"^\+?1?\d{9,15}$", phone):
                raise forms.ValidationError(
                    "Enter a valid phone number (e.g., +1234567890)"
                )
        return phone

    def clean_email(self):
        """Validate email if provided"""
        email = self.cleaned_data.get("email")
        if email and "@" not in email:
            raise forms.ValidationError("Enter a valid email address")
        return email


class ReviewForm(forms.ModelForm):
    class Meta:
        model = ProductReview
        fields = ["rating", "comment"]
        widgets = {
            "rating": forms.NumberInput(
                attrs={"class": "form-control", "min": 1, "max": 5}
            ),
            "comment": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
        }
