from django.core.mail import send_mail
from django.template.loader import get_template
from django.conf import settings


def send_order_email_confirmation(order, **kwargs):
    """
    Send email to customer with order details.
    """
    context = {
        'order': order,
    }
    message = get_template("order_confirmation.html").render(context)
    send_mail(
        subject="Order confirmation",
        message='',
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[order.email],
        fail_silently=False,
        html_message=message
    )


def send_order_shipped_email(order, **kwargs):
    """
    Send email to customer with order details.
    """
    context = {
        'order': order,
    }
    message = get_template("order_shipped.html").render(context)
    send_mail(
        subject="Order shipped confirmation",
        message='',
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[order.email],
        fail_silently=False,
        html_message=message
    )


def send_order_delivered_mail(order):
    """
    Send email to customer with order details.
    """
    context = {
        'order': order,
    }
    message = get_template("order_delivered.html").render(context)
    send_mail(
        subject="Order delivered confirmation",
        message='',
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[order.email],
        fail_silently=False,
        html_message=message
    )
