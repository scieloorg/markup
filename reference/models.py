from django.db import models
from core.models import (
    CommonControlField,
)
from wagtail.models import Orderable
from wagtail.admin.panels import FieldPanel, InlinePanel
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from django.utils.translation import gettext as _
from django.core.validators import MinValueValidator, MaxValueValidator
from core.forms import CoreAdminModelForm


class ReferenceStatus(models.IntegerChoices):
    NO_REFERENCE = 0, _("No reference")
    CREATING = 1, _("Creating reference")
    READY = 2, _("Reference ready")


# Create your models here
class Reference(CommonControlField, ClusterableModel):
    mixed_citation = models.TextField(("Mixed Citation"), null=False, blank=True)

    estatus = models.IntegerField(
        _("Reference estatus"),
        choices=ReferenceStatus.choices,
        blank=True,
        default=ReferenceStatus.NO_REFERENCE
    )

    panels = [
        FieldPanel('mixed_citation'),
        InlinePanel('element_citation')
    ]

    base_form_class = CoreAdminModelForm

    def __str__(self):
        return self.mixed_citation


class ElementCitation(Orderable):
    reference = ParentalKey(
        Reference, on_delete=models.SET_NULL, related_name="element_citation", null=True
    )
    marked = models.JSONField(_("Marked"), default=dict, blank=True)
    marked_xml = models.TextField(_("Marked XML"), blank=True)

    score = models.IntegerField(
        null=True, 
        blank=True,
        validators=[
            MinValueValidator(1),  # Mínimo 1
            MaxValueValidator(10)  # Máximo 10
        ],
        help_text="Rating from 1 to 10"
    )

    panels = [
            FieldPanel("marked"),
            FieldPanel("marked_xml"),
            FieldPanel("score"),
            ]
