import os
import sys

from django.db import models
from django.utils.translation import gettext as _

from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail.admin.panels import FieldPanel, InlinePanel, ObjectList, TabbedInterface
from wagtailautocomplete.edit_handlers import AutocompletePanel

from core.forms import CoreAdminModelForm
from core.models import (
    CommonControlField,
    Language,
    TextWithLang
)
from wagtail.fields import StreamField
from wagtail.blocks import StructBlock, TextBlock, CharBlock, ChoiceBlock, ListBlock, StreamBlock
from wagtail.images.blocks import ImageChooserBlock
from .choices import front_labels

# Create your models here.
class ArticleDocx(CommonControlField):
    title = models.TextField(_("Document Title"), null=True, blank=True)
    file = models.FileField(
        null=True,
        blank=True,
        verbose_name=_("Document"),
        upload_to='uploads_docx/',
    )
    estatus = models.IntegerField(default=0) 

    panels = [
        FieldPanel("title"),
        FieldPanel("file"),
    ]

    base_form_class = CoreAdminModelForm

    def __unicode__(self):
        return f"{self.title} | {self.estatus}"

    def __str__(self):
        return f"{self.title} | {self.estatus}"

    @classmethod
    def get(
        cls,
        title):
        return cls.objects.get(title=title)

    @classmethod
    def update(cls, title, estatus):
        try:
            obj = cls.get(title=title)
        except (cls.DoesNotExist, ValueError):
            pass

        obj.estatus = estatus
        obj.save()
        return obj


class ParagraphWithLanguageBlock(StructBlock):
    label = ChoiceBlock(
                choices=front_labels,
                required=False,
                label=_("Label")
            )
    language = ChoiceBlock(
        queryset=Language.objects.all(),
        required=False,
        label="Language"
    )
    paragraph = TextBlock(required=True, label=_("Title"))

    class Meta:
        label = _("Paragraph with Language")


class ParagraphBlock(StructBlock):
    label = ChoiceBlock(
                choices=front_labels,
                required=False,
                label=_("Label")
            )
    paragraph = TextBlock(required=True, label=_("Paragraph"))

    class Meta:
        label = _("Paragraph")


class ImageBlock(StructBlock):
    label = ChoiceBlock(
                choices=front_labels,
                required=False,
                label=_("Label")
            )
    image = ImageChooserBlock(required=True)

    class Meta:
        label = _("Image")


class ArticleDocxMarkup(CommonControlField, ClusterableModel):
    content = StreamField([
        ('paragraph_with_language', ParagraphWithLanguageBlock()),
        ('paragraph', ParagraphBlock()),
    ], blank=True, use_json_field=True)

    content_body = StreamField([
        ('paragraph', ParagraphBlock()),
        ('image', ImageBlock()),
    ], blank=True, use_json_field=True)

    content_back = StreamField([
        ('paragraph', ParagraphBlock()),
    ], blank=True, use_json_field=True)

    panels_front = [
        FieldPanel('content'),
        #InlinePanel("element_docx", label=_("Elements Docx")),
    ]

    panels_body = [
        FieldPanel('content_body'),
    ]

    panels_back = [
        FieldPanel('content_back'),
    ]

    edit_handler = TabbedInterface(
        [
            ObjectList(panels_front, heading=_("Front")),
            ObjectList(panels_body, heading=_("Body")),
            ObjectList(panels_back, heading=_("Back")),
        ]
    )

    @classmethod
    def create(cls, title, doi):
        obj = cls()
        obj.title = title
        obj.doi = doi
        obj.save()
        return obj

    base_form_class = CoreAdminModelForm

