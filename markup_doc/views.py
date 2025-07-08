from django.shortcuts import render
from django.http import HttpResponse
from .models import ArticleDocxMarkup
from .xml import extraer_citas_apa
from django.http import JsonResponse
from markup_doc.models import JournalModel
import json


# Create your views here.
def generate_xml(request, id_registro):
    try:
        # Obtener el registro del modelo que contiene el XML
        registro = ArticleDocxMarkup.objects.get(pk=id_registro)
       
        # Obtener el contenido XML del campo
        contenido_xml = registro.text_xml  # Ajusta esto según la estructura de tu modelo
       
        # Crear una respuesta HTTP con el tipo de contenido XML
        response = HttpResponse(contenido_xml, content_type='application/xml')
       
        # Definir el nombre del archivo para descargar
        nombre_archivo = f"document_{id_registro}.xml"
        response['Content-Disposition'] = f'attachment; filename="{nombre_archivo}"'
       
        return response
    except TuModelo.DoesNotExist:
        return HttpResponse("El registro solicitado no existe", status=404)
    except Exception as e:
        return HttpResponse(f"Error al generar el XML: {str(e)}", status=500)


def extract_citation(request):

    if request.method == "POST":
        body = json.loads(request.body)
        text = body.get("text", "")
        pk_register = body.get("pk", "")

        print(text)
        print(pk_register)

        # Obtener el registro del modelo que contiene el XML
        registro = ArticleDocxMarkup.objects.get(pk=pk_register)

        result = extraer_citas_apa(text, registro.content_back.get_prep_value())  # <-- Aquí pasas el texto a tu función normal
        return JsonResponse({"refid": result[0]['refid']})


def get_journal(request):

    if request.method == "POST":
        body = json.loads(request.body)
        text = body.get("text", "")
        pk = body.get("pk", "")

        journal = JournalModel.objects.get(pk=pk)

    return JsonResponse({
        'journal_title': journal.title,
        'short_title': journal.short_title,
        'title_nlm': journal.title_nlm,
        'acronym': journal.acronym,
        'issn': journal.issn,
        'pissn': journal.pissn,
        'eissn': journal.eissn,
        'pubname': journal.pubname,
        # Agrega los campos que necesites
    })


def journal_autocomplete(request):
    q = request.GET.get("q", "")
    collection_id = request.GET.get("collection_id")

    journals = JournalModel.objects.all()

    if collection_id:
        journals = journals.filter(collection_id=collection_id)
    if q:
        journals = journals.filter(name__icontains=q)

    return JsonResponse({
        "results": [{"id": j.id, "text": j.name} for j in journals[:10]]
    })
