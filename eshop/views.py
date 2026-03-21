from django.shortcuts import render, get_object_or_404, redirect
from .models import Category, Product, CartItem, Order, OrderItem, ProductReview, Cart
from django.http import Http404
from .forms import ReviewForm, OrderForm
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from .forms import UserRegisterForm, UserLoginForm
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
User = get_user_model()


def register_view_prev(request):
    if request.method == "POST":
        logger.debug(f"Incoming request data: {request.POST}")
        data = {
            "username": request.POST.get("username"),
            "email": request.POST.get("email"),
            "password1": request.POST.get("password1"),
            "password2": request.POST.get("password2"),
        }
        form = UserRegisterForm(data)
        logger.info(f"Valid: {form.is_valid()} {form.cleaned_data}")
        if form.is_valid():
            if User.objects.filter(username=data["username"]).exists():
                messages.error(
                    request, f"User with username: {data['username']} already exists."
                )
                return render(request, "eshop/register.html", {"form": form})
            if data.get("email", None):
                if User.objects.filter(username=data["username"]).exists():
                    messages.error(
                        request,
                        f"Account with email: {data['email']} already exists.",
                    )
                    return render(request, "eshop/register.html", {"form": form})
            form.save()
            messages.success(request, f"Account created for {data['username']}!")
            return redirect("eshop:login")  # Redirect to login page after registration
    else:
        form = UserRegisterForm()
    return render(request, "eshop/register.html", {"form": form})


def register_view(request):
    if request.method == "POST":
        logger.debug(f"Incoming request data: {request.POST}")

        form = UserRegisterForm(request.POST)
        logger.info(
            f"Valid: {form.is_valid()} {form.cleaned_data if form.is_valid() else 'Form invalid'}"
        )

        if form.is_valid():
            # Form validation already handles uniqueness checks via clean() method
            # No need to duplicate database queries here
            user = form.save()
            messages.success(request, f"Account created for {user.username}!")
            # Login user
            username = request.POST.get('username')
            user = None
            if username:
                user = User.objects.filter(username=username)
            if user and user.exists():
                login(request, user.first())
                return redirect("eshop:home")
            else:
                return redirect("eshop:login")
        else:
            # Extract and format errors as strings instead of lists
            for field, errors in form.errors.items():
                # Get the first error message as a string
                error_msg = errors[0] if isinstance(errors, list) else str(errors)

                if field == "__all__":
                    messages.error(request, error_msg)
                else:
                    # Get the field label for better readability
                    field_label = (
                        form.fields[field].label if field in form.fields else field
                    )
                    messages.error(request, f"{field_label}: {error_msg}")

            # Also log the errors for debugging
            logger.error(f"Form validation errors: {dict(form.errors)}")

    else:
        form = UserRegisterForm()

    return render(request, "eshop/register.html", {"form": form})


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


@login_required()
def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out!")
    return redirect("eshop:home")  # Redirect to home page after logout


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
        form = OrderForm()
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
