"""File: core/wagtail_hooks.py."""

from django.templatetags.static import static
from django.utils.html import format_html
from wagtail import hooks
from wagtail.admin.navigation import get_site_for_user
from wagtail.admin.site_summary import SummaryItem
from wagtail.contrib.modeladmin.options import (
    ModelAdmin,
    ModelAdminGroup,
    modeladmin_register,
)
from core.models import Gender
from config.menu import get_menu_order, WAGTAIL_MENU_APPS_ORDER
from config.menu import get_menu_order

@hooks.register("insert_global_admin_css", order=100)
def global_admin_css():
    """Add /static/css/custom.css to the admin."""
    """Add /static/admin/css/custom.css to the admin."""
    return format_html(
        '<link rel="stylesheet" href="{}">', static("admin/css/custom.css")
    )


@hooks.register("insert_global_admin_js", order=100)
def global_admin_js():
    """Add /static/css/custom.js to the admin."""
    """Add /static/admin/css/custom.js to the admin."""
    return format_html('<script src="{}"></script>', static("admin/js/custom.js"))


@hooks.register("construct_homepage_summary_items", order=1)
def remove_all_summary_items(request, items):
    items.clear()


class GenderAdmin(ModelAdmin):
    model = Gender
    menu_icon = "folder"
    menu_order = 600
    add_to_settings_menu = False
    exclude_from_explorer = False
    list_display = (
        "code",
        "gender",
    )

    search_fields = (
        "code",
        "gender",
    )


@hooks.register('construct_main_menu')
def reorder_menu_items(request, menu_items):
    for item in menu_items:
        if item.label in WAGTAIL_MENU_APPS_ORDER:
            item.order = get_menu_order(item.label)


@hooks.register('construct_main_menu')
def remove_menu_items(request, menu_items):
    if not request.user.is_superuser:
        menu_items[:] = [item for item in menu_items if item.name not in ['documents', 'explorer', 'reports']]