from config import celery_app
from django.core.files.base import ContentFile
from markup_doc.models import UploadDocx, MarkupXML #ArticleDocx, ArticleDocxMarkup
import re, json
from markuplib.function_docx import functionsDocx
from packtools.sps.formats.sps_xml.contrib import build_contrib_author
from markup_doc.xml import get_xml
from markup_doc.labeling_utils import (
    create_special_content_object,
    process_reference,
    create_labeled_object2
)
from markup_doc.sync_api import sync_journals_from_api
from model_ai.generic_llama import GenericLlama
from model_ai.function_llama import functionsLlama

def clean_labels(text):
    # Reemplazar etiquetas de salto de línea por saltos reales
    #text = re.sub(r'<br\s*/?>', '\n', text, flags=re.IGNORECASE)
    #text = re.sub(r'</p\s*>', '\n', text, flags=re.IGNORECASE)

    # Eliminar etiquetas tipo [kwd] o [sectitle], incluso si tienen espacios como [/ doctitle ]
    text = re.sub(r'\[\s*/?\s*\w+(?:\s+[^\]]+)?\s*\]', '', text)

    # Eliminar todas las etiquetas <...>
    #text = re.sub(r'<[^>]+>', '', text)

    # Reemplazar múltiples espacios por uno solo
    text = re.sub(r'[ \t]+', ' ', text)

    # Eliminar espacios antes de los signos de puntuación
    text = re.sub(r'\s+([;:,.])', r'\1', text)

    # Normalizar múltiples saltos de línea
    text = re.sub(r'\n+', '\n', text)

    # Quitar espacios al principio y final
    return text.strip()

@celery_app.task()
def update_xml(instance_id, instance_content, instance_content_body, instance_content_back):
    instance = MarkupXML.objects.get(id=instance_id)
    content_head = instance_content
    content_body_dict = instance_content_body
    xml = get_xml(instance, content_head, content_body_dict, instance_content_back)

    # Guardar el XML en el campo `file_xml`
    archive_xml = ContentFile(xml)  # Crea un archivo temporal en memoria
    instance.estatus = 2
    instance.file_xml.save("archivo.xml", archive_xml)  # Guarda en el campo `file_xml`
    instance.text_xml = xml

    instance.save()


@celery_app.task()
def get_labels(title, user_id):
    article_docx = UploadDocx.objects.get(title=title)
    doc = functionsDocx.openDocx(article_docx.file.path)
    sections, content = functionsDocx().extractContent(doc, article_docx.file.path)
    article_docx_markup = article_docx
    text_title = ''
    text_paragraph = ''
    stream_data = []
    stream_data_body = []
    stream_data_back = []
    num_ref=0
    state = {
        'label': None,
        'label_next': None,
        'label_next_reset': None,
        'reset': False,
        'repeat': None,
        'header': False,
        'body': False,
        'back': False
    }

    for i, item in enumerate(content):
        obj = {}
        if item.get('type') == 'first_block':
            first_block = GenericLlama(type='prompt', temperature=0.1)

            output = first_block.run(functionsLlama.getFirstMetadata(clean_labels(item.get('text'))))
            output = output["choices"][0]["text"]

            match = re.search(r'\{.*\}', output, re.DOTALL)
            if match:
                output = match.group(0)

            output = json.loads(output)

            obj['type'] = 'paragraph'
            obj['value'] = {
                'label': '<article-id>',
                'paragraph': output['doi']
            }
            stream_data.append(obj.copy())
            obj['value'] = {
                'label': '<subject>',
                'paragraph': output['section']
            }
            stream_data.append(obj.copy())
            for i, tit in enumerate(output['titles']):
                obj['type'] = 'paragraph_with_language'
                obj['value'] = {
                    'label': '<article-title>' if i == 0 else '<trans-title>',
                    'paragraph': tit['title'],
                    'language': tit['language']
                }
                stream_data.append(obj.copy())

            for i, auth in enumerate(output['authors']):
                obj['type'] = 'author_paragraph'
                obj['value'] = {
                    'label': '<contrib>',
                    'surname': auth['surname'],
                    'given_names': auth['name'],
                    'orcid': auth['orcid'],
                    'affid': auth['aff']
                }
                stream_data.append(obj.copy())

            for i, aff in enumerate(output['affiliations']):
                obj['type'] = 'aff_paragraph'
                obj['value'] = {
                    'label': '<aff>',
                    'affid': aff['aff'],
                    'orgname': aff['orgname'],
                    'orgdiv2': aff['orgdiv2'],
                    'orgdiv1': aff['orgdiv1'],
                    'zipcode': aff['postal'],
                    'city': aff['city'],
                    'country': aff['country']
                }
                stream_data.append(obj.copy())

        if item.get('type') in ['image', 'table', 'list', 'compound']:
            obj = create_special_content_object(item, stream_data_body)
            stream_data_body.append(obj)
            continue

        if item.get('text') == '':
            state['label_next'] = state['label_next_reset'] if state['reset'] else state['label_next']
        else:

            obj, result, state = create_labeled_object2(i, item, state, sections)
                        
            if result:                
                if state['body']:
                    stream_data_body.append(obj)
                elif state['back']:
                    if state['label'] == '<p>':
                        num_ref = num_ref + 1
                        obj = process_reference(num_ref, obj, user_id)
                    stream_data_back.append(obj)
                else:
                    stream_data.append(obj)
    
    xml = get_xml(article_docx, stream_data, stream_data_body, stream_data_back)

    # Guardar el XML en el campo `file_xml`
    archive_xml = ContentFile(xml)  # Crea un archivo temporal en memoria
    article_docx_markup.file_xml.save("archivo.xml", archive_xml)  # Guarda en el campo `file_xml`
    article_docx_markup.text_xml = xml

    article_docx_markup.content = stream_data
    article_docx_markup.content_body = stream_data_body
    article_docx_markup.content_back = stream_data_back
    article_docx_markup.save()

    article_docx.estatus = 2
    article_docx.save()


@celery_app.task()
def task_sync_journals_from_api():
    sync_journals_from_api()