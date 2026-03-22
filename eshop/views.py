from django.shortcuts import render, get_object_or_404, redirect
from .models import (
    Category,
    Product,
    CartItem,
    Order,
    OrderItem,
    ProductReview,
    Cart,
    EshopUser,
)
from django.http import Http404
from .forms import ReviewForm, OrderForm

from django.views.decorators.csrf import csrf_protect
from django.contrib.auth import login, logout, get_user_model, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from .forms import UserRegisterForm, UserLoginForm
from django.contrib.auth import update_session_auth_hash

# from django.urls import reverse
# from django.utils import timezone
# from django.db.models import Count, Avg
import logging

from .forms import UserProfileUpdateForm, CustomPasswordChangeForm

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
User = get_user_model()


logger = logging.getLogger(__name__)


@csrf_protect
def register_view(request):
    if request.method == "POST":
        logger.debug(f"Incoming request data: {request.POST}")

        form = UserRegisterForm(request.POST)

        if form.is_valid():
            # Save the user
            user = form.save()
            messages.success(request, f"Account created for {user.username}!")

            # Log the user in
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password1")

            # Authenticate and login
            authenticated_user = authenticate(
                request, username=username, password=password
            )
            if authenticated_user:
                login(request, authenticated_user)
                logger.info(f"User {username} logged in successfully")
                return redirect("eshop:home")
            else:
                logger.warning(f"Could not authenticate user {username}")
                return redirect("eshop:login")
        else:
            # Log validation errors
            logger.error(f"Form validation errors: {dict(form.errors)}")

            # Don't add messages here - let the template display field errors
            # This prevents duplicate error messages
            pass

    else:
        form = UserRegisterForm()

    return render(request, "eshop/register.html", {"form": form})


@csrf_protect
def login_view(request):
    if request.method == "POST":
        # data = request.POST.cleaned_data
        data = {
            "username": request.POST.get("username"),
            "password": request.POST.get("password"),
        }
        form = AuthenticationForm(request, data=data)

        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, "You have been logged in!")
            return redirect("eshop:home")  # Redirect to home page
        else:
            if not User.objects.filter(username=data["username"]).exists():
                form.errors["__all__"] = "User not found"
            else:
                form.errors["__all__"] = "Incvalid login credentials."

            # Also log the errors for debugging
            logger.error(f"Form validation errors: {dict(form.errors)}")

    else:
        form = UserLoginForm()
    return render(request, "eshop/login.html", {"form": form})


@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out!")
    return redirect("eshop:home")  # Redirect to home page after logout


@login_required
def profile_view(request):
    """
    Display user profile with recent orders and reviews
    """
    user = request.user

    # Get user's orders
    recent_orders = (
        Order.objects.filter(user=user).order_by("-created_at")[:5]
        if hasattr(user, "order_set")
        else []
    )

    # Get user's reviews
    recent_reviews = (
        ProductReview.objects.filter(user=user).order_by("-created_at")[:5]
        if hasattr(user, "review_set")
        else []
    )

    # Calculate statistics
    total_orders = (
        Order.objects.filter(user=user).count() if hasattr(user, "order_set") else 0
    )
    total_reviews = (
        ProductReview.objects.filter(user=user).count()
        if hasattr(user, "review_set")
        else 0
    )

    context = {
        "profile": user,
        "recent_orders": recent_orders,
        "recent_reviews": recent_reviews,
        "total_orders": total_orders,
        "total_reviews": total_reviews,
    }

    return render(request, "eshop/profile.html", context)


@login_required
def update_profile_view(request):
    """
    Handle profile update
    """
    if request.method == "POST":
        form = UserProfileUpdateForm(request.POST, request.FILES, instance=request.user)

        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated successfully!")
            return redirect("eshop:profile")
        else:
            # Add form errors to messages
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.title()}: {error}")
            return redirect("eshop:profile")

    return redirect("eshop:profile")


@login_required
def change_password_view(request):
    """
    Handle password change
    """
    if request.method == "POST":
        form = CustomPasswordChangeForm(request.user, request.POST)

        if form.is_valid():
            user = form.save()
            # Update session to keep user logged in
            update_session_auth_hash(request, user)
            messages.success(request, "Your password was successfully updated!")
            return redirect("eshop:profile")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
            return redirect("eshop:profile")

    return redirect("eshop:profile")


@login_required
def delete_profile_image_view(request):
    """
    Delete user profile image
    """
    if request.method == "POST":
        if request.user.profile_image:
            request.user.profile_image.delete()
            request.user.save()
            messages.success(request, "Profile image deleted successfully!")
        else:
            messages.info(request, "No profile image to delete.")

    return redirect("eshop:profile")


@login_required
def deactivate_account_view(request):
    """
    Deactivate user account
    """
    if request.method == "POST":
        user = request.user
        user.is_active = False
        user.save()
        messages.success(
            request, "Your account has been deactivated. We're sad to see you go!"
        )
        return redirect("eshop:home")

    return redirect("eshop:profile")


@login_required
def newsletter_toggle_view(request):
    """
    Toggle newsletter subscription
    """
    if request.method == "POST":
        request.user.newsletter_subscribed = not request.user.newsletter_subscribed
        request.user.save()

        status = (
            "subscribed to"
            if request.user.newsletter_subscribed
            else "unsubscribed from"
        )
        messages.success(request, f"You have successfully {status} our newsletter!")

    return redirect("eshop:profile")


def home(request):
    categories = Category.objects.all()
    return render(request, "eshop/home.html", {"categories": categories})


# products functions
def product_list(request):
    products = Product.objects.filter(available=True)  # Only show available products
    context = {"products": products}
    return render(request, "eshop/product_list.html", context)


def product_detail(request, slug):
    product = get_object_or_404(
        Product, slug=slug, available=True
    )  # Only show available products
    context = {"product": product}
    return render(request, "eshop/product_detail.html", context)


# category functions
def category_list(request):
    categories = Category.objects.all()
    context = {"categories": categories}
    return render(request, "eshop/category_list.html", context)


def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(
        category=category, available=True
    )  # Only show available products
    context = {"category": category, "products": products}
    return render(request, "eshop/category_detail.html", context)


# cart functions
@login_required(
    login_url="eshop:login"
)  # Redirect to login page if user is not logged in
def view_cart(request):
    try:
        cart = request.user.cart
    except Cart.DoesNotExist:
        cart = Cart.objects.create(user=request.user)
    cart_items = cart.items.all()
    context = {"cart_items": cart_items, "cart": cart}
    return render(request, "eshop/cart.html", context)


@login_required(login_url="eshop:login")
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product)

    if not item_created:
        cart_item.quantity += 1
        cart_item.save()
    return redirect("eshop:view_cart")  # Redirect to cart view


@login_required
def remove_from_cart(request, cart_item_id):
    try:
        cart_item = CartItem.objects.get(
            pk=cart_item_id, cart__user=request.user
        )  # Ensure user owns the item
        cart_item.delete()
    except CartItem.DoesNotExist:
        raise Http404("Cart item does not exist")
    return redirect("eshop:view_cart")


@login_required
def update_cart(request, cart_item_id):
    try:
        cart_item = CartItem.objects.get(pk=cart_item_id, cart__user=request.user)
        quantity = int(request.POST.get("quantity", 1))  # Get quantity from form
        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
        else:
            cart_item.delete()
    except CartItem.DoesNotExist:
        raise Http404("Cart item does not exist")
    return redirect("eshop:view_cart")


# order functions
@login_required(login_url="eshop:login")
def create_order(request):
    cart = Cart.objects.get(user=request.user)  # Assuming a user has one cart
    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            order = Order.objects.create(
                user=request.user,
                first_name=form.cleaned_data["first_name"],
                last_name=form.cleaned_data["last_name"],
                email=form.cleaned_data["email"],
                address=form.cleaned_data["address"],
                postal_code=form.cleaned_data["postal_code"],
                city=form.cleaned_data["city"],
            )
            for item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    price=item.product.price,
                    quantity=item.quantity,
                )
            # Clear the cart after successful order creation
            cart.items.all().delete()
            return redirect(
                "eshop:orders_list"
            )  # Use the namespace 'eshop:orders_list'
    else:
        initial = {}
        if request.user.is_authenticated:
            initial.update(
                {
                    "name": request.user.get_full_name() or request.user.username,
                    "email": request.user.email or "",
                    "phone": getattr(request.user, "phone_number", ""),
                    "address": getattr(request.user.profile, "phone_number", "")
                    if hasattr(request.user, "profile")
                    else "",
                }
            )
        form = OrderForm(initial=initial)
    context = {"form": form, "cart": cart}
    return render(request, "eshop/create_order.html", context)


@login_required(login_url="eshop:login")
def orders_list(request):
    orders = Order.objects.filter(user=request.user).order_by("-created")
    context = {"orders": orders}
    return render(request, "eshop/orders_list.html", context)


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    context = {"order": order}
    return render(request, "eshop/order_detail.html", context)


# product review functions
def product_reviews(request, product_slug):
    product = get_object_or_404(Product, slug=product_slug)
    reviews = ProductReview.objects.filter(product=product).order_by(
        "-created"
    )  # Most recent first
    context = {"product": product, "reviews": reviews}
    return render(request, "eshop/product_reviews.html", context)


@login_required(login_url="eshop:login")
def add_review(request, product_slug):
    product = get_object_or_404(Product, slug=product_slug)
    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)  # Don't save yet
            review.product = product
            review.user = request.user  # Assign current user to review
            review.save()
            return redirect(
                "product_detail", slug=product.slug
            )  # Redirect back to product detail
    else:
        form = ReviewForm()
    context = {"product": product, "form": form}
    return render(request, "eshop/add_review.html", context)


def all_reviews(request):
    reviews = ProductReview.objects.all().order_by("-created")
    return render(request, "eshop/all_reviews.html", {"reviews": reviews})


def choose_product_for_review(request):
    products = Product.objects.filter(available=True)
    return render(
        request, "eshop/choose_product_for_review.html", {"products": products}
    )


def about_view(request):
    return render(request, "eshop/about.html")


def contact_view(request):
    return render(request, "eshop/contact.html")
