from config import celery_app
from django.core.files.base import ContentFile
from markup_doc.models import UploadDocx, MarkupXML #ArticleDocx, ArticleDocxMarkup
import re, json, langid, math
from markuplib.function_docx import functionsDocx
from packtools.sps.formats.sps_xml.contrib import build_contrib_author
from markup_doc.xml import get_xml
from markup_doc.labeling_utils import (
    split_in_three,
    create_special_content_object,
    process_reference,
    process_references,
    extract_keywords,
    create_labeled_object2,
    get_data_first_block,
    getLLM
)
from markup_doc.models import(
    ProcessStatus
)
from markup_doc.sync_api import sync_journals_from_api
from model_ai.generic_llama import GenericLlama
from model_ai.function_llama import functionsLlama
from reference.config_gemini import create_prompt_reference

def clean_labels(text):
    # Eliminar etiquetas tipo [kwd] o [sectitle], incluso si tienen espacios como [/ doctitle ]
    text = re.sub(r'\[\s*/?\s*\w+(?:\s+[^\]]+)?\s*\]', '', text)

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
    xml, stream_data_body = get_xml(instance, content_head, content_body_dict, instance_content_back)

    instance.content_body = stream_data_body
    # Guardar el XML en el campo `file_xml`
    #archive_xml = ContentFile(xml)  # Crea un archivo temporal en memoria
    instance.estatus = ProcessStatus.PROCESSED
    #instance.file_xml.save("archivo.xml", archive_xml)  # Guarda en el campo `file_xml`
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
        'body_trans': False,
        'body': False,
        'back': False,
        'references': False
    }
    counts = {
        'numref': 0,
        'numtab': 0,
        'numfig': 0,
        'numeq': 0
    }

    next_item  = None
    obj_reference = []
    llama_model = False

    for i, item in enumerate(content):
        if next_item:
            next_item = None
            continue

        obj = {}
        if item.get('type') in [
                                    '<abstract>', 
                                    '<date-accepted>', 
                                    '<date-received>',
                                    '<kwd-group>'
                                    ]:
            if item.get('type') == '<abstract>':
                if i + 1 < len(content):
                    obj['type'] = 'paragraph'
                    obj['value'] = {
                        'label': '<abstract-title>',
                        'paragraph': item.get('text')
                    }
                    stream_data.append(obj.copy())

                    next_item = content[i + 1]
                    obj['type'] = 'paragraph_with_language'
                    obj['value'] = {
                        'label': '<abstract>',
                        'paragraph': next_item.get('text'),
                        'language': langid.classify(next_item.get('text'))[0] or None
                    }
                    stream_data.append(obj.copy())
            
            elif item.get('type') == '<kwd-group>':
                keywords = extract_keywords(item.get('text'))
                obj['type'] = 'paragraph'
                obj['value'] = {
                        'label': '<kwd-title>',
                        'paragraph': keywords['title']
                    }
                stream_data.append(obj.copy())

                obj['type'] = 'paragraph_with_language'
                obj['value'] = {
                        'label': '<kwd-group>',
                        'paragraph': keywords['keywords'],
                        'language': langid.classify(keywords['title'].replace('<italic>', '').replace('</italic>', ''))[0] or None
                    }
                stream_data.append(obj.copy())

            else:        
                obj['type'] = 'paragraph'
                obj['value'] = {
                    'label': item.get('type') ,
                    'paragraph': item.get('text')
                }
                stream_data.append(obj.copy())
            continue

        if item.get('type') == 'first_block':
            first_block = GenericLlama(type='prompt', temperature=0.1)

            if getLLM() == 'GEMINI':
                output = first_block.run(functionsLlama.getFirstMetadata(clean_labels(item.get('text'))))
                match = re.search(r'\{.*\}', output, re.DOTALL)
                if match:
                    output = match.group(0)
                    output = json.loads(output)
            
            if getLLM() == 'LLAMA':

                output_author = get_data_first_block(clean_labels(item.get('text')), 'author', user_id)
                
                output_affiliation = get_data_first_block(clean_labels(item.get('text')), 'affiliation', user_id)
                
                output_doi = get_data_first_block(clean_labels(item.get('text')), 'doi', user_id)
                
                output_title = get_data_first_block(clean_labels(item.get('text')), 'title', user_id)

                # 1. Parsear cada salida
                doi_section = output_doi
                titles = output_title
                authors = output_author
                affiliations = output_affiliation

                # 2. Combinar en un único JSON
                output = {
                    "doi": doi_section.get("doi", ""),
                    "section": doi_section.get("section", ""),
                    "titles": titles,
                    "authors": authors,
                    "affiliations": affiliations
                }

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
                    'affid': auth['aff'],
                    'char': auth['char']
                }
                stream_data.append(obj.copy())

            for i, aff in enumerate(output['affiliations']):
                obj['type'] = 'aff_paragraph'
                obj['value'] = {
                    'label': '<aff>',
                    'affid': aff['aff'],
                    'char': aff['char'],
                    'orgname': aff['orgname'],
                    'orgdiv2': aff['orgdiv2'],
                    'orgdiv1': aff['orgdiv1'],
                    'zipcode': aff['postal'],
                    'city': aff['city'],
                    'country': aff['name_country'],
                    'code_country': aff['code_country'],
                    'state': aff['state'],
                    'text_aff': aff['text_aff'],
                    #'original': aff['original']
                }
                stream_data.append(obj.copy())

        if item.get('type') in ['image', 'table', 'list', 'compound']:
            obj, counts = create_special_content_object(item, stream_data_body, counts)
            stream_data_body.append(obj)
            continue

        if item.get('text') is None or item.get('text') == '':
            state['label_next'] = state['label_next_reset'] if state['reset'] else state['label_next']
            if state['back']:
                state['back'] = False
                state['body'] = False
                state['references'] = True
        else:

            obj, result, state = create_labeled_object2(i, item, state, sections)
                        
            if result:           
                if item.get('text').lower() in ['introducción', 'introduction', 'introdução'] and state['references']:
                    state['body_trans'] = True
                    obj_trans = {
                            'type': 'paragraph_with_language',
                            'value': {
                                'label': '<translate-body>',
                                'paragraph': 'Translate'
                            }
                        }
                    stream_data_body.append(obj_trans)    
                if state['body']:
                    if state['references']:
                        if state['body_trans']:
                            stream_data_body.append(obj)
                        else:
                            stream_data.append(obj)
                    else:
                        stream_data_body.append(obj)
                elif state['back']:
                    if state['label'] == '<sec>':
                        stream_data_back.append(obj)
                    if state['label'] == '<p>':
                        num_ref = num_ref + 1
                        #obj = {}#process_reference(num_ref, obj, user_id)
                        obj_reference.append({"num_ref": num_ref, "obj": obj, "text": obj['value']['paragraph'],})
                    #stream_data_back.append(obj)
                else:
                    stream_data.append(obj)
    
    num_refs = [item["num_ref"] for item in obj_reference]

    if getLLM() == 'LLAMA':
        for obj_ref in obj_reference:
            obj = process_reference(obj_ref['num_ref'], obj_ref['obj'], user_id)
            stream_data_back.append(obj)

    else:
        chunks = split_in_three(obj_reference)
        output=[]

        for chunk in chunks:
            if len(chunk) > 0:
                text_references = "\n".join([item["text"] for item in chunk]).replace('<italic>', '').replace('</italic>', '')
                prompt_reference = create_prompt_reference(text_references)

                result = first_block.run(prompt_reference) 

                match = re.search(r'\[.*\]', result, re.DOTALL)
                if match:
                    parsed = json.loads(match.group(0))
                    output.extend(parsed)  # Agrega a la lista de salida
    
        stream_data_back.extend(process_references(num_refs, output))

    article_docx_markup.content = stream_data
    article_docx_markup.content_body = stream_data_body
    article_docx_markup.content_back = stream_data_back
    article_docx_markup.save()

    article_docx.estatus = ProcessStatus.PROCESSED
    article_docx.save()

    xml, stream_data_body = get_xml(article_docx, stream_data, stream_data_body, stream_data_back)
    article_docx_markup.content_body = stream_data_body

    # Guardar el XML en el campo `file_xml`
    #archive_xml = ContentFile(xml)  # Crea un archivo temporal en memoria
    #article_docx_markup.file_xml.save("archivo.xml", archive_xml)  # Guarda en el campo `file_xml`
    article_docx_markup.text_xml = xml
    article_docx.save()


@celery_app.task()
def task_sync_journals_from_api():
    sync_journals_from_api()
