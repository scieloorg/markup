from config import celery_app
from django.core.files.base import ContentFile
from markup_doc.models import UploadDocx, MarkupXML #ArticleDocx, ArticleDocxMarkup
import time
import json
import re
from markuplib.function_docx import functionsDocx
from markuplib.function_llama import functionsLlama
from .choices import order_labels
from lxml import etree
from packtools.sps.formats.sps_xml.contrib import build_contrib_author
import requests

def clean_str(text, chars="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 .,;!?-<>/\\"):
    return "".join(c for c in text if c in chars)

def get_xml(data_front, data):
    # Crear el elemento raíz
    root = etree.Element('article',
                            attrib={ 
                                'article-type': 'research-article',
                                'dtd-version': '1.1',
                                'specific-use': 'sps-1.9',
                                '{http://www.w3.org/XML/1998/namespace}lang': 'en',
                                '{http://www.w3.org/1998/Math/MathML}mml': 'http://www.w3.org/1998/Math/MathML',
                                '{http://www.w3.org/1999/xlink}xlink': 'http://www.w3.org/1999/xlink'}
                        )

    # Añadir un elemento hijo
    front = etree.SubElement(root, "front")
    body = etree.SubElement(root, "body")
    subsec = None
    num_table = 1
    continue_t = False

    """
    for i, d in enumerate(data_front):
        if d['value']['label'] == '<contrib>':
            data_c = {
                "contrib_type": "author",
                "orcid": "0000-0001-8528-2091",
                "scopus": "24771926600",
                "surname": "Einstein",
                "given_names": "Albert",
                "affiliations": [
                    {"rid": "aff1", "text": "1"}
                ]
            }
            front.append(build_contrib_author(data_c))

        if d['value']['label'] == '<abstract>':
            data_a = {
                "title": "Resumo",
                "lang": None,
                "secs": [
                    {"title": "Objetivo", "p": "Verificar a sensibilidade ..."},
                    {"title": "Métodos", "p": "Durante quatro meses ..."}
                ]
            }
            front.append(build_abstract(data_a))
    """

    for i, d in enumerate(data):
        node = body

        if continue_t:
            continue_t = False
            continue

        if d['value']['label'] == '<sec>':
            val_p = d['value']['paragraph'].lower()
            attrib={}
            if re.search(r"^(intro|sinops|synops)", val_p):
                attrib={'sec-type': 'intro'}
            elif re.search(r"^(caso|case)", val_p):
                attrib={'sec-type': 'cases'}
            elif re.search(r"^(conclus|comment|coment)", val_p):
                attrib={'sec-type': 'conclusions'}
            elif re.search(r"^(discus)", val_p):
                attrib={'sec-type': 'discussion'}
            elif re.search(r"^(materia)", val_p):
                attrib={'sec-type': 'materials'}
            elif re.search(r"^(proced|method|métod|metod)", val_p):
                attrib={'sec-type': 'methods'}
            elif re.search(r"^(result|statement|finding|declara|hallaz)", val_p):
                attrib={'sec-type': 'results'}
            elif re.search(r"^(subject|participant|patient|pacient|assunt|sujeto)", val_p):
                attrib={'sec-type': 'subjects'}
            elif re.search(r"^(suplement|material)", val_p):
                attrib={'sec-type': 'supplementary-material'}

            node = etree.SubElement(body, 'sec', attrib=attrib)    
            node_title = etree.SubElement(node, 'title')
            node_title.text = d['value']['paragraph']
            subsec = False

        if d['value']['label'] == '<sub-sec>':
            subsec = True
            node_sec = etree.SubElement(node, 'sec')
            node_title = etree.SubElement(node_sec, 'title')
            if re.search(r'^\[style name="italic"\](.*?)\[/style\]$', d['value']['paragraph']):
                sech = d['value']['paragraph'].replace('[style name="italic"]', '').replace('[/style]', '')
                node_subtitle = etree.SubElement(node_title, 'italic')
                node_subtitle.text = sech
            else:
                node_title.text = d['value']['paragraph'].replace('[style name="italic"]', '<italic>').replace('[/style]', '</italic>')

        if d['value']['label'] == '<list>':
            re_search = re.search(r'list list-type="(.*?)"\]', d['value']['paragraph'])
            list_type = re_search.group(1)
            attrib={'list-type': list_type}

            if subsec:
                node_list = etree.SubElement(node_sec, 'list', attrib=attrib)
            else:
                node_list = etree.SubElement(node, 'list', attrib=attrib)

            content_list = re.search(r'\[list list-type="[^"]*"\](.*?)\[/list\]', d['value']['paragraph'], re.DOTALL)
            content_list = content_list.group(1)
            node_list_text = content_list \
                            .replace('[style name="italic"]', '<italic>').replace('[/style]', '</italic>') \
                            .replace('[list-item]', '<list-item><p>') \
                            .replace('[/list-item]', '</p></list-item>')

            node_list_text = etree.fromstring(f"<root>{node_list_text}</root>")

            for child in node_list_text:
                node_list.append(child)
        
        if d['value']['label'] == '<table>' or d['value']['label'] == '<table-caption>':
            
            attrib={'id': 't'+str(num_table)}
        
            if subsec:
                node_table = etree.SubElement(node_sec, 'table-wrap', attrib=attrib)
            else:
                node_table = etree.SubElement(node, 'table-wrap', attrib=attrib)
            
            if d['value']['label'] == '<table-caption>':
                etree.SubElement(node_table, 'label').text = d['value']['paragraph'].split('.')[0]
                node_caption = etree.SubElement(node_table, 'caption')
                if '.' in d['value']['paragraph']:
                    etree.SubElement(node_caption, 'title').text = d['value']['paragraph'].split('.', 1)[1]
                else:
                    etree.SubElement(node_caption, 'title').text = d['value']['paragraph']
                
                content_table = data[i+1]['value']['paragraph']

                continue_t = True
            else:
                content_table = d['value']['paragraph']
                
            node_table_text = content_table \
                                .replace('[style name="italic"]', '<italic>').replace('[/style]', '</italic>')

            node_table_text = node_table_text.replace('<br>','&#10;')

            node_table_text = etree.fromstring(f"<root>{node_table_text}</root>")

            for child in node_table_text:
                node_table.append(child)

            num_table = num_table + 1

        
        if d['value']['label'] == '<p>':
            if subsec:
                node_p = etree.SubElement(node_sec, 'p')
            else:
                node_p = etree.SubElement(node, 'p')

            if re.search(r'^\[style name="italic"\](.*?)\[/style\]$', d['value']['paragraph']):
                node_title.text = ''
                ph = d['value']['paragraph'].replace('[style name="italic"]', '').replace('[/style]', '')
                #node_subtitle = etree.SubElement(node_title, 'italic')
                #node_subtitle.text = ph
                node_subtitle = etree.fromstring(f"<root>{ph}</root>")
                for child in node_subtitle:
                    node_title.append(child)
            else:
                node_p.text = d['value']['paragraph'].replace('[style name="italic"]', '<italic>').replace('[/style]', '</italic>')
                p_text = d['value']['paragraph'].replace('[style name="italic"]', '<italic>').replace('[/style]', '</italic>')
                node_text = etree.fromstring(f"<root>{p_text}</root>")
                for child in node_text:
                    node_p.append(child)
        
        if d['value']['label'] == '<formula>':
            if subsec:
                node_p = etree.SubElement(node_sec, 'p')
            else:
                node_p = etree.SubElement(node, 'p')

            p_text = ''
            if 'content' in d['value']:
                for val in d['value']['content']:
                    if val['type'] == 'text':
                        type_val = 'text'
                    else:
                        type_val = 'formula'

                    if re.search(r'^\[style name="italic"\](.*?)\[/style\]$', val['value']):
                        node_title.text = ''
                        ph = val['value'].replace('[style name="italic"]', '').replace('[/style]', '')
                        node_subtitle = etree.fromstring(f"<root>{ph}</root>")
                        for child in node_subtitle:
                            node_title.append(child)
                    else:
                        p_text += val['value'].replace('[style name="italic"]', '<italic>').replace('[/style]', '</italic>').replace('xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math"', '')
                        
            node_text = etree.fromstring(f"<root><disp-formula>{p_text}</disp-formula></root>")
            for child in node_text:
                node_p.append(child)            
            
    # Convertir a una cadena XML
    xml_como_texto = etree.tostring(root, pretty_print=True, encoding="unicode")

    return xml_como_texto


@celery_app.task()
def update_xml(instance_id):
    instance = MarkupXML.objects.get(id=instance_id)
    content_head = instance.content.get_prep_value()
    content_body_dict = instance.content_body.get_prep_value()
    xml = get_xml(content_head, content_body_dict)

    # Guardar el XML en el campo `file_xml`
    archive_xml = ContentFile(xml)  # Crea un archivo temporal en memoria
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
    header = False
    body = False
    back = False

    label_next = None
    reset = False
    repeat = None
    for i, item in enumerate(content):
        if item.get('type') == 'image':
            obj = {}
            obj['type'] = 'image'
            obj['value'] = { 
                    'label' : '<fig>',
                    'image' : item.get('image')
                    
                }

            stream_data_body.append(obj)

        elif item.get('type') == 'table':
            obj = {}
            obj['type'] = 'paragraph'
            obj['value'] = {
                'label' : '<table>',
                'paragraph' : item.get('table')
            }

            #Obitiene el elemento aterior
            prev_element = stream_data_body[-1]
            prev_element['value']['label'] = '<table-caption>'

            stream_data_body.append(obj)

        elif item.get('type') == 'list':
            obj = {}
            obj['type'] = 'paragraph'
            obj['value'] = {
                'label' : '<list>',
                'paragraph' : item.get('list')
            }
            stream_data_body.append(obj)
        
        elif item.get('type') == 'compound':
            obj = {}
            obj['type'] = 'compound_paragraph'
            obj['value'] = {
                'label' : '<formula>',
                'content': item.get('text')
            }
            stream_data_body.append(obj)

        elif item.get('text') == '':
            label_next = label_next_reset if reset else label_next
        else:
            obj = {}
            obj_body = {}
            result = []
            #Busca que cumpla con la posición en el documento
            result = next((
                            (key, obj_ol) for key, 
                            obj_ol in order_labels.items() 
                            if "pos" in obj_ol and
                            obj_ol["pos"] == (i+1)
                        ), None)
            #Si cumple con alguna, ahí termina
            if result:
                label = result[0]
                res_obj = result[1]
            else:
                #Busca si existe definida una etiqueta siguiente
                if label_next:
                    #Realiza este bloqe si la etiqueta se puede repetir
                    if repeat:
                        #Si existe una propiedad regex busca si cumple con la expresión
                        result = next((
                            (key, obj_ol) for key, 
                            obj_ol in order_labels.items()
                            if "regex" in obj_ol and
                            re.search(obj_ol["regex"], item.get('text'))
                        ), None)
                        if result:
                            label = result[0]
                        else:
                            #Busca si cumple con el tamaño y grosor
                            result = next((
                                    (key, obj_ol) for key, 
                                    obj_ol in order_labels.items()
                                    if "size" in obj_ol and
                                    "bold" in obj_ol and
                                    obj_ol["size"] == item.get('font_size') and 
                                    obj_ol["bold"] == item.get('bold')
                                ), None)
                            if result:
                                label = result[0]
                                repeat = None
                                reset = None
                                label_next = result[1]["next"]
                                body = True if "size" in result[1] and result[1]["size"] == 16 else False
                                #Si está en el body y encuentra Referencias pasa al back
                                if body and re.search(r"^(refer)", item.get('text').lower()):
                                    body = False
                                    back = True
                    if not result:
                        #Busca si cumple con el tamaño de letra y es la etiqueta siguiente
                        result = next((
                                (key, obj_ol) for key, 
                                obj_ol in order_labels.items()
                                if "size" in obj_ol and
                                obj_ol["size"] == item.get('font_size') and key == label_next
                            ), None)
                        if result:
                            label = result[0]
                            label_next_reset = result[1]["next"] if "next" in result[1] else None
                            reset = True if "reset" in result[1] else None
                            repeat = True if "repeat" in result[1] else None
                #Si no hay etiqueta next
                else:
                    #Busca que cumpla con size y con bold
                    result = next((
                                    (key, obj_ol) for key, 
                                    obj_ol in order_labels.items()
                                    if "size" in obj_ol and
                                    "bold" in obj_ol and
                                    obj_ol["size"] == item.get('font_size') and 
                                    obj_ol["bold"] == item.get('bold')
                                ), None)
                    if result:
                        label = result[0]
                        label_next = result[1]["next"]
                        #Si está en el body y encuentra Referencias pasa al back
                        if body and re.search(r"^(refer)", item.get('text').lower()):
                            body = False
                            back = True
                    else:
                        #Busca que cumpla con size y con italic
                        result = next((
                                        (key, obj_ol) for key, 
                                        obj_ol in order_labels.items()
                                        if "size" in obj_ol and
                                        "italic" in obj_ol and
                                        obj_ol["size"] == item.get('font_size') and 
                                        obj_ol["italic"] == item.get('italic')
                                    ), None)
                        if result:
                            label = re.sub(r"-\d+", "", result[0])
                            label_next = result[1]["next"]
                        else:
                            #Busca si tiene propiedad regex y cumpla con la expresión
                            result = next((
                                (key, obj_ol) for key, 
                                obj_ol in order_labels.items()
                                if "regex" in obj_ol and
                                re.search(obj_ol["regex"], item.get('text'))
                            ), None)
                            if result:
                                label = result[0]
                            else:
                                #Párrafo
                                result = next((
                                    (key, obj_ol) for key, 
                                    obj_ol in order_labels.items()
                                    if "size" in obj_ol and
                                    "next" in obj_ol and
                                    obj_ol["size"] == item.get('font_size') and 
                                    obj_ol["next"] == '<p>'
                                ), None)
                            if result:
                                label = result[0]
            
            if result:
                if label in ['<abstract>']:
                    del order_labels[label]
                obj['type'] = 'paragraph_with_language' if "lan" in result[1] and result[1]["lan"] else 'paragraph'

                obj['value'] = { 
                                    'label' : label,
                                    'paragraph' : item.get('text') 
                                        }
                
                if label == '<contrib>':
                    obj['type'] = 'author_paragraph'

                if label == '<aff>':
                    obj['type'] = 'aff_paragraph'
                
                if body:
                    stream_data_body.append(obj)
                elif back:
                    if label == '<p>':
                        obj['type'] = 'ref_paragraph'

                        url = "URL_API/api/v1/mix_citation/reference/"

                        payload = {
                            'reference': obj['value']['paragraph']
                        }

                        headers = {
                            'Authorization': 'Bearer KEY',
                            'Content-Type': 'application/json'
                        }

                        response = requests.post(url, json=payload, headers=headers)

                        if response.status_code == 200:
                            response_json = response.json()
                            message_str = response_json['message']

                            json_str = message_str.replace('reference: ', '', 1)

                            ref_json = json.loads(json_str)

                            #ref_json = json.loads(response)
                            obj['value']['reftype'] = ref_json.get('reftype', None)
                            obj['value']['date'] = ref_json.get('date', None)
                            obj['value']['title'] = ref_json.get('title', None)
                            obj['value']['source'] = ref_json.get('source', None)
                            obj['value']['vol'] = ref_json.get('vol', None)
                            obj['value']['issue'] = ref_json.get('issue', None)
                            obj['value']['pages'] = ref_json.get('pages', None)
                            obj['value']['doi'] = ref_json.get('doi', None)
                            obj['value']['authors'] = []
                            if ref_json['authors']:
                                for author in ref_json['authors']:
                                    obj_auth = {}
                                    obj_auth['type'] = 'Author'
                                    obj_auth['value'] = {}
                                    obj_auth['value']['surname'] = author.get('surname', None)
                                    obj_auth['value']['given_names'] = author.get('fname', None)
                                    obj['value']['authors'].append(obj_auth)
 
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