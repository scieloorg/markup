from django.http import HttpResponseRedirect
from django.utils.translation import gettext as _
from wagtail.contrib.modeladmin.options import (
    ModelAdmin,
    ModelAdminGroup,
    modeladmin_register,
)
from wagtail.contrib.modeladmin.views import CreateView

from markup_doc.models import ( 
    ArticleDocx,
    ArticleDocxMarkup,
)
from config.menu import get_menu_order
from markup_doc.tasks import get_labels


class ArticleDocxCreateView(CreateView):
    def form_valid(self, form):
        self.object = form.save_all(self.request.user)
        self.object.estatus = 1
        self.object.save()
        get_labels.delay(self.object.title)
        return HttpResponseRedirect(self.get_success_url())


class ArticleDocxAdmin(ModelAdmin):
    model = ArticleDocx
    create_view_class = ArticleDocxCreateView
    menu_label = _("Documents")
    menu_icon = "folder"
    menu_order = 1
    add_to_settings_menu = False  # or True to add your model to the Settings sub-menu
    exclude_from_explorer = (
        False  # or True to exclude pages of this type from Wagtail's explorer view
    )
    list_per_page = 20
    list_display = (
        "title",
        "estatus"
    )


class ArticleDocxMarkupCreateView(CreateView):
    def form_valid(self, form):
        self.object = form.save_all(self.request.user)
        return HttpResponseRedirect(self.get_success_url())


class ArticleDocxMarkupAdmin(ModelAdmin):
    model = ArticleDocxMarkup
    create_view_class = ArticleDocxMarkupCreateView
    menu_label = _("Documents Markup")
    menu_icon = "folder"
    menu_order = 1
    add_to_settings_menu = False  # or True to add your model to the Settings sub-menu
    exclude_from_explorer = (
        False  # or True to exclude pages of this type from Wagtail's explorer view
    )
    list_per_page = 20


class MarkupAdminGroup(ModelAdminGroup):
    menu_label = _("Markup")
    menu_icon = "folder-open-inverse"
    menu_order = 1
    items = (ArticleDocxAdmin, ArticleDocxMarkupAdmin)

modeladmin_register(MarkupAdminGroup)