import os
import sys

from django.db import models
from django.utils.translation import gettext as _
from django import forms
from django.utils.html import format_html

from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail.admin.panels import FieldPanel, InlinePanel, ObjectList, TabbedInterface
from wagtailautocomplete.edit_handlers import AutocompletePanel
from wagtail.documents.models import Document

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

class ReadOnlyFileWidget(forms.Widget):
    def render(self, name, value, attrs=None, renderer=None):
        if value:
            # Muestra el archivo como un enlace de descarga
            return format_html('<a href="{}" target="_blank" download>{}</a>', value.url, value.name.split('/')[-1])
        return ""

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


class CompoundParagraphBlock(StructBlock):
    label = ChoiceBlock(
                choices=front_labels,
                required=False,
                label=_("Label")
            )
    content = StreamBlock([
        ('text', TextBlock(label=_("Text"))),
        ('formula', TextBlock(label=_("Formula"))),
    ], label=_("Contet"), required=True)

    class Meta:
        label = _("Compound paragraph")


class ImageBlock(StructBlock):
    label = ChoiceBlock(
                choices=front_labels,
                required=False,
                label=_("Label")
            )
    image = ImageChooserBlock(required=True)

    class Meta:
        label = _("Image")


class AuthorParagraphBlock(ParagraphBlock):
    surname = TextBlock(required=False, label=_("Surname"))
    given_names = TextBlock(required=False, label=_("Given names"))
    orcid = TextBlock(required=False, label=_("Orcid"))

    class Meta:
        label = _("Author Paragraph")


class AffParagraphBlock(ParagraphBlock):
    orgname = TextBlock(required=False, label=_("Orgname"))
    orgdiv2 = TextBlock(required=False, label=_("Orgdiv2"))
    orgdiv1 = TextBlock(required=False, label=_("Orgdiv1"))
    zipcode = TextBlock(required=False, label=_("Zipcode"))
    city = TextBlock(required=False, label=_("City"))
    country = TextBlock(required=False, label=_("Country"))

    class Meta:
        label = _("Aff Paragraph")


class RefNameBlock(StructBlock):
    surname = TextBlock(required=False, label=_("Surname"))
    given_names = TextBlock(required=False, label=_("Given names"))


class RefParagraphBlock(ParagraphBlock):
    reftype = TextBlock(required=False, label=_("Ref type"))
    #authors = ListBlock(RefNameBlock(), label=_("Authors"))
    authors = StreamBlock([
        ('Author', RefNameBlock()),
    ], label=_("Authors"), required=False)
    date = TextBlock(required=False, label=_("Date"))
    title = TextBlock(required=False, label=_("Title"))
    source = TextBlock(required=False, label=_("Source"))
    vol = TextBlock(required=False, label=_("Vol"))
    issue = TextBlock(required=False, label=_("Issue"))
    pages = TextBlock(required=False, label=_("Pages"))
    doi = TextBlock(required=False, label=_("DOI"))

    class Meta:
        label = _("Ref Paragraph")


class ArticleDocxMarkup(CommonControlField, ClusterableModel):
    title = models.TextField(_("Document Title"), null=True, blank=True)
    file = models.FileField(
        null=True,
        blank=True,
        verbose_name=_("Document"),
        upload_to='uploads_docx/',
    )
    estatus = models.IntegerField(default=0) 

    file_xml = models.FileField(
        null=True,
        blank=True,
        verbose_name=_("Document xml"),
        upload_to='generate_xml/',
    )

    text_xml = models.TextField(_("Text XML"), null=True, blank=True)

    content = StreamField([
        ('paragraph_with_language', ParagraphWithLanguageBlock()),
        ('paragraph', ParagraphBlock()),
        ('author_paragraph', AuthorParagraphBlock()),
        ('aff_paragraph', AffParagraphBlock()),
    ], blank=True, use_json_field=True)

    content_body = StreamField([
        ('paragraph', ParagraphBlock()),
        ('compound_paragraph', CompoundParagraphBlock()),
        ('image', ImageBlock()),
    ], blank=True, use_json_field=True)

    content_back = StreamField([
        ('paragraph', ParagraphBlock()),
        ('ref_paragraph', RefParagraphBlock()),
    ], blank=True, use_json_field=True)

    panels = [
        FieldPanel("title"),
        FieldPanel("file"),
    ]

    '''panels_front = [
        FieldPanel('content'),
        #InlinePanel("element_docx", label=_("Elements Docx")),
    ]

    panels_body = [
        FieldPanel('content_body'),
    ]

    panels_back = [
        FieldPanel('content_back'),
    ]

    panels_xml = [
        FieldPanel('file_xml', widget=ReadOnlyFileWidget()),
        FieldPanel('text_xml'),
    ]

    edit_handler = TabbedInterface(
        [
            ObjectList(panels_xml, heading=_("XML")),
            ObjectList(panels_front, heading=_("Front")),
            ObjectList(panels_body, heading=_("Body")),
            ObjectList(panels_back, heading=_("Back")),
        ]
    )'''

    def __unicode__(self):
        return f"{self.title} | {self.estatus}"

    def __str__(self):
        return f"{self.title} | {self.estatus}"

    @property
    def url_download(self):
        return self.file_xml.url if self.file_xml else None

    @classmethod
    def create(cls, title, doi):
        obj = cls()
        obj.title = title
        obj.doi = doi
        obj.save()
        return obj

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

    base_form_class = CoreAdminModelForm


class UploadDocx(ArticleDocxMarkup):
    panels = [
        FieldPanel("title"),
        FieldPanel("file"),
    ]

    class Meta:
        proxy = True


class MarkupXML(ArticleDocxMarkup):
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

    panels_xml = [
        FieldPanel('file_xml', widget=ReadOnlyFileWidget()),
        FieldPanel('text_xml'),
    ]

    edit_handler = TabbedInterface(
        [
            ObjectList(panels_xml, heading=_("XML")),
            ObjectList(panels_front, heading=_("Front")),
            ObjectList(panels_body, heading=_("Body")),
            ObjectList(panels_back, heading=_("Back")),
        ]
    )

    class Meta:
        proxy = True