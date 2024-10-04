from config import celery_app
from markup_doc.models import ArticleDocx, ArticleDocxMarkup
import time
import json
import re
from markuplib.function_docx import functionsDocx
from .choices import order_labels


@celery_app.task()
def get_labels(title):
    article_docx = ArticleDocx.objects.get(title=title)
    doc = functionsDocx.openDocx(article_docx.file.path)
    content = functionsDocx().extractContent(doc, article_docx.file.path)
    article_docx_markup = ArticleDocxMarkup.objects.create()
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
                    'image' : item.get('image')#ImageModel.objects.get(id=item.get('image'))
                    
                }

            stream_data_body.append(obj)

        elif item.get('type') == 'table':
            obj = {}
            obj['type'] = 'paragraph'
            obj['value'] = {
                'label' : '<table>',
                'paragraph' : item.get('table')
            }

            stream_data_body.append(obj)

        elif item.get('type') == 'list':
            obj = {}
            obj['type'] = 'paragraph'
            obj['value'] = {
                'label' : '<list>',
                'paragraph' : item.get('list')
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
                                body = True if "size" in result[1] and result[1]["size"] == 16 else False
                                #Si está en el body y encuentra Referencias pasa al back
                                if body and item.get('text') == 'Referencias':
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
            
            if result:
                if label in ['<abstract>']:
                    del order_labels[label]
                obj['type'] = 'paragraph_with_language' if "lan" in result[1] and result[1]["lan"] else 'paragraph'

                obj['value'] = { 
                                    'label' : label,
                                    'paragraph' : item.get('text') 
                                        }
                
                if body:
                    stream_data_body.append(obj)
                elif back:
                    stream_data_back.append(obj)
                else:
                    stream_data.append(obj)
    
    article_docx_markup.content = stream_data
    article_docx_markup.content_body = stream_data_body
    article_docx_markup.content_back = stream_data_back
    article_docx_markup.save()

    article_docx.estatus = 2
    article_docx.save()