from django.http import HttpResponseRedirect
from django.utils.translation import gettext as _
from wagtail.contrib.modeladmin.options import (
    ModelAdmin,
    ModelAdminGroup,
    modeladmin_register,
)
from wagtail.contrib.modeladmin.views import CreateView, EditView

from markup_doc.models import ( 
    ArticleDocx,
    ArticleDocxMarkup,
    UploadDocx,
    MarkupXML
)
from config.menu import get_menu_order
from markup_doc.tasks import get_labels, update_xml
from django.urls import path, reverse
from django.utils.html import format_html
from wagtail.admin import messages
from wagtail.admin.views import generic

from django.shortcuts import redirect, get_object_or_404
from django.views import View

from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction


@receiver(post_save, sender=UploadDocx)
def handle_uploadxml_create(sender, instance, created, **kwargs):
    if created:
        # Establece estatus si no viene del formulario
        if instance.estatus != 1:
            instance.estatus = 1
            instance.save(update_fields=["estatus"])
        
        # Lanza tarea Celery con el título
        transaction.on_commit(lambda: get_labels.delay(instance.title))


@receiver(post_save, sender=MarkupXML)
def trigger_update_xml(sender, instance, created, **kwargs):
    if not created:
        prev = MarkupXML.objects.get(id=instance.id)
        if prev.estatus == 3:
            MarkupXML.objects.filter(id=instance.id).update(estatus=2)
        else:
            if instance.estatus != 1:
                #MarkupXML.objects.filter(id=instance.id).update(estatus=1)
                instance.estatus = 1
                instance.save(update_fields=["estatus"])
                transaction.on_commit(lambda: update_xml.delay(instance.id, instance.content.get_prep_value(), instance.content_body.get_prep_value()))


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


class UploadDocxViewSet(SnippetViewSet):
    model = UploadDocx
    menu_label = _("UploadDocx")
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


class MarkupXMLViewSet(SnippetViewSet):
    model = MarkupXML
    menu_label = _("MarkupXML")
    menu_icon = "folder"
    menu_order = 1
    add_to_settings_menu = False  # or True to add your model to the Settings sub-menu
    exclude_from_explorer = (
        False  # or True to exclude pages of this type from Wagtail's explorer view
    )
    
    list_display=("title", )


    list_per_page = 20


register_snippet(UploadDocxViewSet)
register_snippet(MarkupXMLViewSet)