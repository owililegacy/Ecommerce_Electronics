from django import forms
from .models import Order, ProductReview
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Customize field labels for better UX
        self.fields["username"].label = "Username"
        self.fields["email"].label = "Email Address"
        self.fields["password1"].label = "Password"
        self.fields["password2"].label = "Confirm Password"

        # Add CSS classes and placeholders
        for field_name, field in self.fields.items():
            field.widget.attrs.update(
                {"class": "form-control w-100", "placeholder": field.label}
            )

            # Remove default help texts for cleaner look
            if field_name in ["password1", "password2"]:
                field.help_text = None

    def clean(self):
        """Custom validation with single, clear error messages per field"""
        cleaned_data = super().clean()
        errors = {}

        # Username validation
        username = cleaned_data.get("username")
        if username:
            if len(username) < 3:
                errors["username"] = "Username must be at least 3 characters long."
            elif User.objects.filter(username=username).exists():
                errors["username"] = "This username is already taken."

        # Email validation
        email = cleaned_data.get("email")
        if email:
            if User.objects.filter(email=email).exists():
                errors["email"] = "This email is already registered."

        # Password validation
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2:
            if password1 != password2:
                errors["password2"] = "Passwords do not match."
            elif len(password1) < 8:
                errors["password1"] = "Password must be at least 8 characters long."
            elif not any(char.isdigit() for char in password1):
                errors["password1"] = "Password must contain at least one number."
            elif not any(char.isupper() for char in password1):
                errors["password1"] = (
                    "Password must contain at least one uppercase letter."
                )

        # Add errors to the form
        for field, message in errors.items():
            self.add_error(field, message)

        return cleaned_data

    def get_error_messages_as_strings(self):
        """Convert form errors to string messages for messaging system"""
        error_messages = []
        for field, errors in self.errors.items():
            if isinstance(errors, (list, tuple)):
                error_text = errors[0]
            else:
                error_text = str(errors)

            if field == "__all__":
                error_messages.append(error_text)
            else:
                field_label = (
                    self.fields[field].label if field in self.fields else field
                )
                error_messages.append(f"{field_label}: {error_text}")

        return error_messages


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
    class Meta:
        model = Order
        fields = ["first_name", "last_name", "email", "address", "postal_code", "city"]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "address": forms.TextInput(attrs={"class": "form-control"}),
            "postal_code": forms.TextInput(attrs={"class": "form-control"}),
            "city": forms.TextInput(attrs={"class": "form-control"}),
        }


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
