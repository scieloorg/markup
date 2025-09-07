from django.http import HttpResponseRedirect
from django.utils.translation import gettext_lazy as _
from django.contrib import messages

from wagtail.snippets.views.snippets import (
    CreateView,
    EditView,
    SnippetViewSet,
    SnippetViewSetGroup
)

from model_ai.models import ( 
    LlamaModel,
    DownloadStatus,
)

from wagtail.snippets.models import register_snippet
from model_ai.tasks import download_model


class LlamaModelCreateView(CreateView):
    def form_valid(self, form):
        data = form.cleaned_data

        if data.get("is_local"):
            if not data.get("name_model"):  # Esto detecta '', None o False
                messages.error(self.request, _("Model name is required."))
                return self.form_invalid(form)

            if not data.get("name_file"):
                messages.error(self.request, _("Model file is required."))
                return self.form_invalid(form)

            if not data.get("hf_token"):
                messages.error(self.request, _("Hugging Face token is required."))
                return self.form_invalid(form)
            self.object = form.save_all(self.request.user)

            self.object.download_status = DownloadStatus.DOWNLOADING
            self.object.save()
            messages.success(self.request, _("Model created and download started."))
            download_model.delay(form.instance.id)
        else:
            if not data.get("api_url"):
                messages.error(self.request, _("API AI URL is required."))
                return self.form_invalid(form)

            self.object = form.save_all(self.request.user)
            messages.success(self.request, _("Model created, use API AI."))
        
        return HttpResponseRedirect(self.get_success_url())


class LlamaModelEditView(EditView):
    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        form.instance.save()
        data = form.cleaned_data
        if form.instance.is_local:
            if form.instance.download_status != DownloadStatus.DOWNLOADING and form.instance.download_status != DownloadStatus.DOWNLOADED:
                if not data.get("name_model"):
                    messages.error(self.request, _("Model name is required."))
                    return self.form_invalid(form)

                if not data.get("name_file"):
                    messages.error(self.request, _("Model file is required."))
                    return self.form_invalid(form)

                if not data.get("hf_token"):
                    messages.error(self.request, _("Hugging Face token is required."))
                    return self.form_invalid(form)

                form.instance.download_status = DownloadStatus.DOWNLOADING
                #download_model.delay(form.instance.id)
                form.instance.save()
                messages.success(self.request, _("Model updated and download started."))
            else:
                messages.success(self.request, _("Model updated and already downloaded."))
        else:
            if not data.get("api_url"):
                messages.error(self.request, _("API AI URL is required."))
                return self.form_invalid(form)

            form.instance.save()
            messages.success(self.request, _("Model updated, use API AI."))

        return HttpResponseRedirect(self.get_success_url())


class LlamaModelViewSet(SnippetViewSet):
    model = LlamaModel
    add_view_class = LlamaModelCreateView
    edit_view_class = LlamaModelEditView
    menu_label = _("Llama Model")
    menu_icon = "folder"
    menu_order = 1
    add_to_settings_menu = False  # or True to add your model to the Settings sub-menu
    exclude_from_explorer = (
        False  # or True to exclude pages of this type from Wagtail's explorer view
    )
    list_per_page = 20
    list_display = (
        "display_name_model",
        "is_local",
        "get_download_status_display"
    )

"""
class MarkupSnippetViewSetGroup(SnippetViewSetGroup):
    menu_name = 'markup_docx'
    menu_label = _('Markup Docx')
    menu_icon = "folder-open-inverse"
    menu_order = get_menu_order('markup_docx')
    items = (
        UploadDocxViewSet,
        MarkupXMLViewSet,
    )
"""

register_snippet(LlamaModelViewSet)