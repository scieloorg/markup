from django.http import HttpResponseRedirect
from django.utils.translation import gettext as _
from wagtail_modeladmin.options import (
    ModelAdmin,
    ModelAdminGroup,
    modeladmin_register,
)
from wagtail_modeladmin.views import CreateView
from wagtail.admin.menu import MenuItem

from reference.data_utils import get_reference

from reference.models import ( 
    Reference
)

class ReferenceCreateView(CreateView):
    def form_valid(self, form):

        # Obtener el contenido de mixed_citation del formulario
        mixed_citation_text = form.cleaned_data['mixed_citation'].strip()
        lineas = mixed_citation_text.split("\n")  # Dividir por saltos de línea

        # Crear un nuevo objeto Reference por cada línea válida
        for linea in lineas:
            linea = linea.strip()  # Eliminar espacios adicionales en cada línea
            if linea:  # Evitar procesar líneas vacías
                new_reference = Reference.objects.create(
                    mixed_citation=linea,
                    estatus=1,  # Estatus predeterminado
                    creator=self.request.user,  # Usuario asociado
                )
                get_reference.delay(new_reference.id)
                print(f"Creado Reference: {new_reference.mixed_citation}")

        # Redirigir después de la creación de los objetos
        return HttpResponseRedirect(self.get_success_url())
        


class ReferenceAdmin(ModelAdmin):
    model = Reference
    create_view_class = ReferenceCreateView
    #edit_view_class = ArticleDocxEditView
    menu_label = _("Reference")
    menu_icon = "folder"
    menu_order = 1
    add_to_settings_menu = False  # or True to add your model to the Settings sub-menu
    exclude_from_explorer = (
        False  # or True to exclude pages of this type from Wagtail's explorer view
    )
    list_per_page = 20


modeladmin_register(ReferenceAdmin)