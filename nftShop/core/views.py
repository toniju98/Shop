import math
import random
import string
from django.contrib.auth import login, logout
from django.contrib.auth import authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.views.generic import ListView, DetailView, View
from django.http import JsonResponse
from eth_account.messages import encode_defunct
from web3.auto import w3
from users.models import MyUser
from .forms import CheckoutForm
from .models import Item, OrderItem, Order, Address
from .signals import send_order_email_confirmation


def get_nonce(request):
    """returns the nonce for an existing user or creates user and returns his nonce

    :param request:
    :return: json with nonce
    """
    if request.method == 'POST':
        wallet = request.POST["wallet"]
        has_nft = request.POST["has_nft"]
        user = authenticate(request, wallet=wallet, password=None, has_nft=has_nft)
        response_data = {
            'nonce': user.nonce,
        }
        return JsonResponse(response_data)


def verify_user(request):
    """verifies the signature sent by frontend and generates new nonce

    :param request:
    :return: json answer if verification successful
    """
    if request.method == 'POST':
        wallet = request.POST["wallet"]
        signature = request.POST["signature"]
        user = MyUser.objects.get(wallet=wallet)
        message_hash = encode_defunct(text=str(user.nonce))
        signer = w3.eth.account.recover_message(signable_message=message_hash, signature=signature)
        if signer.lower() == wallet:
            user.nonce = math.floor(random.random() * 1000000)
            user.save()
        response_data = {
            'verified': (signer.lower() == wallet),
        }
        return JsonResponse(response_data)


def login_user(request):
    """login user
    :param request:
    :return:
    """
    if request.method == 'POST':
        wallet = request.POST["wallet"]
        user = MyUser.objects.get(wallet=wallet)
        if user is not None:
            login(request, user, backend='users.backend.SettingsBackend')
            # Redirect to a success page.
            return redirect("core:home")
        else:
            # Return an 'invalid login' error message.
            messages.warning(request, "Wrong login!")
            return redirect("core:home")


def logout_user(request):
    """logout user

    :param request:
    :return:
    """
    if request.method == 'POST':
        logout(request)
    return redirect("core:home")


def login_message(request):
    """shows message if not logged in

    :param request:
    :return:
    """
    messages.warning(request, "Please login first!")
    return redirect("core:home")


# TODO: check
def create_ref_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))


def products(request):
    """render products html

    :param request:
    :return:
    """
    context = {
        'items': Item.objects.all()
    }
    return render(request, "products.html", context)


def is_valid_form(values):
    """check if form entries not empty

    :param values:
    :return:
    """
    valid = True
    for field in values:
        if field == '':
            valid = False
    return valid


# TODO: check
class CheckoutView(View):
    """checkout view

    """

    def get(self, *args, **kwargs):
        """gets all orders from cart

        :param args:
        :param kwargs:
        :return:
        """
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            form = CheckoutForm()
            context = {
                'form': form,
                'order': order,
            }
            return render(self.request, "checkout.html", context)
        except ObjectDoesNotExist:
            messages.info(self.request, "You do not have an active order")
            return redirect("core:checkout")

    # TODO: check
    def post(self, *args, **kwargs):
        """sends filled out checkout form

        :param args:
        :param kwargs:
        :return:
        """
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if form.is_valid():
                print("HI")

                print("User is entering a new shipping address")
                name = form.cleaned_data.get('name')
                forename = form.cleaned_data.get('forename')
                email = form.cleaned_data.get('email')
                shipping_address1 = form.cleaned_data.get(
                    'shipping_address')
                shipping_country = form.cleaned_data.get(
                    'shipping_country')
                shipping_zip = form.cleaned_data.get('shipping_zip')

                if is_valid_form([shipping_address1, shipping_country, shipping_zip, name, forename, email]):
                    shipping_address = Address(
                        user=self.request.user,
                        street_address=shipping_address1,
                        country=shipping_country,
                        zip=shipping_zip,
                        address_type='S'
                    )
                    shipping_address.save()
                    order.name = name
                    order.forename = forename
                    order.email = email
                    order.shipping_address = shipping_address
                    order.save()
                else:
                    messages.info(
                        self.request, "Please fill in the required shipping address fields")
                    # TODO: minus quantity
                    # TODO: clean cart
                order.ordered = True
                order.save()
                messages.info(
                    self.request, "Order placed")
                send_order_email_confirmation(order)
                return redirect("core:home")
            else:
                messages.warning(self.request, "Check the form!")
                return redirect("core:checkout")
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect("core:order-summary")


def get_category(request, category):
    """return category for products

    :param request:
    :param category:
    :return:
    """
    items = Item.objects.filter(category=category)
    context = {
        'object_list': items
    }
    return render(request, 'home.html', context)


class HomeView(ListView):
    """main page

    """
    model = Item
    template_name = "home.html"


class OrderSummaryView(LoginRequiredMixin, View):
    """view for cart

    """
    login_url = '/login-message'
    redirect_field_name = None

    def get(self, *args, **kwargs):
        """returns all orders in the cart

        :param args:
        :param kwargs:
        :return:
        """
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'object': order
            }
            return render(self.request, 'order_summary.html', context)
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect("/")


class ItemDetailView(DetailView):
    """product details template

    """
    model = Item
    template_name = "product.html"


# TODO: check
@login_required(redirect_field_name=None, login_url='/login-message')
def add_to_cart(request, slug, size=None):
    """adds product to cart

    :param request:
    :param slug:
    :param size:
    :return:
    """
    item = get_object_or_404(Item, slug=slug)
    if size is None:
        product_size = request.POST["size"]
    else:
        product_size = size

    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        size=product_size,
        ordered=False,
    )

    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug, size=product_size).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "This item quantity was updated.")
            return redirect("core:order-summary")
        else:
            order.items.add(order_item)
            messages.info(request, "This item was added to your cart.")
            return redirect("core:order-summary")
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(
            user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, "This item was added to your cart.")
        return redirect("core:order-summary")


@login_required(redirect_field_name=None, login_url='/login-message')
def remove_from_cart(request, slug, size):
    """remove product from cart

    :param request:
    :param slug:
    :param size:
    :return:
    """
    item = get_object_or_404(Item, slug=slug)

    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False, received=False, being_delivered=False,
        refund_requested=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                size=size,
                user=request.user,
                ordered=False
            )[0]
            order.items.remove(order_item)
            order_item.delete()
            messages.info(request, "This item was removed from your cart.")
            return redirect("core:order-summary")
        else:
            messages.info(request, "This item was not in your cart")
            return redirect("core:product", slug=slug)
    else:
        messages.info(request, "You do not have an active order")
        return redirect("core:product", slug=slug)


@login_required
def remove_single_item_from_cart(request, slug, size):
    """remove one item from cart

    :param request:
    :param slug:
    :param size:
    :return:
    """
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False, received=False, being_delivered=False,
        refund_requested=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                size=size,
                user=request.user,
                ordered=False
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)
            messages.info(request, "This item quantity was updated.")
            return redirect("core:order-summary")
        else:
            messages.info(request, "This item was not in your cart")
            return redirect("core:product", slug=slug)
    else:
        messages.info(request, "You do not have an active order")
        return redirect("core:product", slug=slug)
