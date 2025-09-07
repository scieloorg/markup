from django.db import models
from django import forms
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from wagtail.admin.panels import FieldPanel
from core.models import (
    CommonControlField,
)
from core.forms import CoreAdminModelForm


class MaskedPasswordWidget(forms.PasswordInput):
    def __init__(self, attrs=None):
        super().__init__(attrs=attrs, render_value=True)

    def render(self, name, value, attrs=None, renderer=None):
        return super().render(name, value, attrs, renderer)


class DownloadStatus(models.IntegerChoices):
        NO_MODEL = 1, _("No model")
        DOWNLOADING = 2, _("Downloading model")
        DOWNLOADED = 3, _("Model downloaded")
        ERROR = 4, _("Download error")


class DisabledSelect(forms.Select):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.attrs.update({'disabled': 'disabled'})


class LlamaModel(CommonControlField):
    #is_local = models.BooleanField(_("Use local model"), default=False)
    name_model = models.CharField(_("Hugging Face model name"), blank=True, max_length=255)
    name_file = models.CharField(_("Model file"), blank=True, max_length=255)
    hf_token = models.CharField(_("Hugging Face token"), blank=True, max_length=255)
    download_status = models.IntegerField(
        _("Local model estatus"),
        choices=DownloadStatus.choices,
        blank=True,
        default=DownloadStatus.NO_MODEL
    )
    api_url = models.URLField(
        verbose_name=_("URL Markapi"),
        blank=True,
        null=True,
        help_text="Enter the AI API URL."
    )
    #is_gemini = models.BooleanField(_("Use API Gemini"), default=False)
    api_key_gemini = models.CharField(_("API KEY Gemini"), blank=True, max_length=255)


    panels = [
        #FieldPanel("is_local"),
        FieldPanel("name_model"),
        FieldPanel("name_file"),
        FieldPanel("hf_token", widget=MaskedPasswordWidget()),
        FieldPanel("download_status", widget=DisabledSelect(choices=DownloadStatus.choices)),
        FieldPanel("api_url"),
        #FieldPanel("is_gemini"),
        FieldPanel("api_key_gemini", widget=MaskedPasswordWidget()),
    ]

    base_form_class = CoreAdminModelForm

    def display_name_model(self):
        return self.name_model if self.name_model and self.is_local else self.api_url

    def clean(self):
        if not self.pk and LlamaModel.objects.exists():
            raise ValidationError(_("Only one instance of LlamaModel is allowed."))

    def __str__(self):
        return self.name_model