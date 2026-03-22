from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator

# from django.utils import timezone
import os


class EshopUser(AbstractUser):
    """
    Custom User Model for Eshop with additional fields
    """

    # Additional fields
    phone_regex = RegexValidator(
        regex=r"^\+?1?\d{9,15}$",
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.",
    )
    phone_number = models.CharField(
        validators=[phone_regex],
        max_length=17,
        blank=True,
        null=True,
        verbose_name="Phone Number",
    )

    address = models.TextField(blank=True, null=True, verbose_name="Address")

    profile_image = models.ImageField(
        upload_to="profile_images/", blank=True, null=True, verbose_name="Profile Image"
    )

    date_of_birth = models.DateField(
        blank=True, null=True, verbose_name="Date of Birth"
    )

    # Preferences
    newsletter_subscribed = models.BooleanField(
        default=False, verbose_name="Subscribe to Newsletter"
    )

    # Timestamps
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Last Updated")

    # Verification fields
    email_verified = models.BooleanField(default=False, verbose_name="Email Verified")

    # Account status
    is_active = models.BooleanField(default=True, verbose_name="Active")

    class Meta:
        app_label = "Users"
        db_table = "users"
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ["-date_joined"]

    def __str__(self):
        return self.get_full_name() or self.username

    def get_full_name(self):
        """
        Return the full name of the user
        """
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username

    def get_short_name(self):
        """
        Return the short name of the user
        """
        return self.first_name or self.username

    def serialize(self):
        """
        Serialize user data for API responses
        """
        data = {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "full_name": self.get_full_name(),
            "phone_number": self.phone_number,
            "address": self.address,
            "date_joined": self.date_joined.isoformat() if self.date_joined else None,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "profile_image": self.profile_image.url if self.profile_image else None,
            "newsletter_subscribed": self.newsletter_subscribed,
            "email_verified": self.email_verified,
        }
        return data

    def save(self, *args, **kwargs):
        """
        Override save to handle profile image cleanup
        """
        if self.pk:
            try:
                old_instance = EshopUser.objects.get(pk=self.pk)
                if (
                    old_instance.profile_image
                    and old_instance.profile_image != self.profile_image
                ):
                    if os.path.isfile(old_instance.profile_image.path):
                        os.remove(old_instance.profile_image.path)
            except EshopUser.DoesNotExist:
                pass
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """
        Override delete to remove profile image from storage
        """
        if self.profile_image and os.path.isfile(self.profile_image.path):
            os.remove(self.profile_image.path)
        super().delete(*args, **kwargs)


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="products"
    )
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)]
    )
    image = models.ImageField(upload_to="products/", blank=True, null=True)
    available = models.BooleanField(default=True)
    stock = models.PositiveIntegerField(default=0)  # Track inventory
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Cart(models.Model):
    user = models.OneToOneField(
        EshopUser, on_delete=models.CASCADE, related_name="cart"
    )  # One cart per user
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart for {self.user.username}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    def get_total_price(self):
        return self.quantity * self.product.price


class Order(models.Model):
    user = models.ForeignKey(EshopUser, on_delete=models.CASCADE, related_name="orders")
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField()
    address = models.CharField(max_length=255)
    postal_code = models.CharField(max_length=20)
    city = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    paid = models.BooleanField(default=False)
    status = models.CharField(
        max_length=50,
        choices=[
            ("PENDING", "Pending"),
            ("PROCESSING", "Processing"),
            ("SHIPPED", "Shipped"),
            ("DELIVERED", "Delivered"),
            ("CANCELLED", "Cancelled"),
        ],
        default="PENDING",
    )

    def get_total_price(self):
        return sum(item.get_total_price() for item in self.items.all())

    def __str__(self):
        return f"Order {self.id}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.DecimalField(
        max_digits=10, decimal_places=2
    )  # Store price at order time
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    def get_total_price(self):
        return self.quantity * self.price  # Use the stored price


class ProductReview(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="reviews"
    )
    user = models.ForeignKey(EshopUser, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review for {self.product.name} by {self.user.username}"
