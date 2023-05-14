import csv
import datetime
from django.http import HttpResponse
from django.contrib import admin
from django.utils.safestring import mark_safe
from django.urls import reverse
from .models import Order, OrderItem


class OrderItemInLine(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']


def order_stripe_payment(obj):
    url = obj.get_stripe_url()
    if obj.stripe_id:
        html = f'<a href="{url}" target="_blank">{obj.stripe_id}</a>'
        return mark_safe(html)
    return ''


order_stripe_payment.short_description = 'Stripe payment'


def export_to_csv(modeladmin, request, queryset):
    opts = modeladmin.model._meta
    content_disposition = f'attachment; filename={opts.verbose_name}.csv'
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = content_disposition
    writer = csv.writer(response)
    fields = [field for field in opts.get_fields() if not
              field.many_to_many and not field.one_to_many]
    # Записать первую строку с информацией заголовка
    writer.writerow([field.verbose_name for field in fields])
    # Записать строки данных
    for obj in queryset:
        data_row = []
        for field in fields:
            value = getattr(obj, field.name)
            if isinstance(value, datetime.datetime):
                value = value.strftime('%d/%m/%Y')
            data_row.append(value)
    writer.writerow(data_row)
    return response


export_to_csv.short_description = 'Export to CSV'


def order_detail(obj):
    url = reverse('orders:admin_order_detail', args=[obj.id])
    return mark_safe(f'<a href="{url}">View</a>')


def order_pdf(obj):
    url = reverse('orders:admin_order_pdf', args=[obj.id])
    return mark_safe(f'<a href="{url}">PDF</a>')


order_pdf.short_description = 'Invoice'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'first_name', 'last_name', 'email',
                    'address', 'postal_code', 'city', 'paid', order_stripe_payment, order_detail, order_pdf, 'created', 'updated']
    list_filter = ['paid', 'created', 'updated']
    inlines = [OrderItemInLine]
    actions = [export_to_csv]
