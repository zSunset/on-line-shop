import weasyprint
from io import BytesIO
from celery import shared_task
from orders.models import Order
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.conf import settings


@shared_task
def payment_completed(order_id):
    '''
    Задание по отправке уведомлений по электронной почте
    при успешной оплате
    '''
    order = Order.objects.get(id=order_id)
    # Создает счет фактуру по электронной почте
    subject = f'My shop = Invoice no/ {order.id}'
    message = 'Please, find attached the invoice for your recent purchase.'
    email = EmailMessage(
        subject, message, 'admin@myshop.com', [order.email])
    # сгенерировать pdf
    html = render_to_string(
        'orders/order/pdf.html', {'order': order})
    out = BytesIO()
    stylesheets = [weasyprint.CSS(settings.STATIC_ROOT / 'css/prf.css')]
    weasyprint.HTML(string=html).write_pdf(out, stylesheets=stylesheets)
    # прикрепить pdf
    email.attach(f'order_{order.id}.pdf', out.getvalue(), 'aplication/pdf')
    # отправить электронное письмо
    email.send()
