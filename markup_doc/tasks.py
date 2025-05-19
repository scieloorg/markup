from config import celery_app
from django.core.files.base import ContentFile
from markup_doc.models import UploadDocx, MarkupXML #ArticleDocx, ArticleDocxMarkup
import re
from markuplib.function_docx import functionsDocx
from packtools.sps.formats.sps_xml.contrib import build_contrib_author
from markup_doc.xml import get_xml
from markup_doc.labeling_utils import (
    create_special_content_object,
    process_reference,
    create_labeled_object
)

@celery_app.task()
def update_xml(instance_id, instance_content, instance_content_body):
    instance = MarkupXML.objects.get(id=instance_id)
    content_head = instance_content
    content_body_dict = instance_content_body
    xml = get_xml(content_head, content_body_dict)

    # Guardar el XML en el campo `file_xml`
    archive_xml = ContentFile(xml)  # Crea un archivo temporal en memoria
    instance.estatus = 3
    instance.file_xml.save("archivo.xml", archive_xml)  # Guarda en el campo `file_xml`
    instance.text_xml = xml

    instance.save()


@celery_app.task()
def get_labels(title):
    article_docx = UploadDocx.objects.get(title=title)
    doc = functionsDocx.openDocx(article_docx.file.path)
    content = functionsDocx().extractContent(doc, article_docx.file.path)
    article_docx_markup = article_docx
    text_title = ''
    text_paragraph = ''
    stream_data = []
    stream_data_body = []
    stream_data_back = []
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

        if item.get('type') in ['image', 'table', 'list', 'compound']:
            obj = create_special_content_object(item, stream_data_body)
            stream_data_body.append(obj)
            continue

        if item.get('text') == '':
            state['label_next'] = state['label_next_reset'] if state['reset'] else state['label_next']
        else:

            obj, result, state = create_labeled_object(i, item, state)
                        
            if result:                
                if state['body']:
                    stream_data_body.append(obj)
                elif state['back']:
                    if state['label'] == '<p>':
                        obj = process_reference(obj)
                    stream_data_back.append(obj)
                else:
                    stream_data.append(obj)
    
    xml = get_xml(stream_data, stream_data_body)

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

