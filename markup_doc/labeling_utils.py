import requests
import json
import re
from .choices import order_labels
from rest_framework_simplejwt.tokens import RefreshToken
from model_ai.models import LlamaModel


def create_special_content_object(item, stream_data_body):
    """Create objects for special content types (image, table, list, compound)"""
    obj = {}

    if item.get('type') == 'image':
        obj = {}
        obj['type'] = 'image'
        obj['value'] = { 
                'label' : '<fig>',
                'image' : item.get('image')
                
            }

    elif item.get('type') == 'table':
        obj = {}
        obj['type'] = 'paragraph'
        obj['value'] = {
            'label' : '<table>',
            'paragraph' : item.get('table')
        }

        #Obitiene el elemento aterior
        try:
            prev_element = stream_data_body[-1]
            prev_element['value']['label'] = '<table-caption>'
        except:
            #No hay elemento anterior
            pass

    elif item.get('type') == 'list':
        obj = {}
        obj['type'] = 'paragraph'
        obj['value'] = {
            'label' : '<list>',
            'paragraph' : item.get('list')
        }
    
    elif item.get('type') == 'compound':
        obj = {}
        obj['type'] = 'compound_paragraph'
        obj['value'] = {
            'label' : '<formula>',
            'content': item.get('text')
        }

    return obj


from django.contrib.auth import get_user_model

User = get_user_model()


def process_reference(num_ref, obj, user_id):
    payload = {
        'reference': obj['value']['paragraph']
    }

    model = LlamaModel.objects.first()

    if model.is_local:
        user = User.objects.get(pk=user_id)
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token

        #url = "http://172.17.0.1:8400/api/v1/mix_citation/reference/"
        #url = "http://172.17.0.1:8009/api/v1/mix_citation/reference/"
        url = "http://django:8000/api/v1/mix_citation/reference/"    

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        response_json = response.json()
        message_str = response_json['message']

        json_str = message_str.replace('reference: ', '', 1)

        ref_json = json.loads(json_str)

        #ref_json = json.loads(response)
        obj['type'] = 'ref_paragraph'
        obj['value']['reftype'] = ref_json.get('reftype', None)
        obj['value']['refid'] = 'B'+str(num_ref)
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
        
    return obj


def match_by_position(i, order_labels):
    return next(
        (key_obj for key_obj in order_labels.items()
         if "pos" in key_obj[1] and key_obj[1]["pos"] == (i + 1)),
        None
    )


def match_by_regex(text, order_labels):
    return next(
        (key_obj for key_obj in order_labels.items()
         if "regex" in key_obj[1] and re.search(key_obj[1]["regex"], text)),
        None
    )


def match_by_style_and_size(item, order_labels, style='bold'):
    return next(
        (key_obj for key_obj in order_labels.items()
         if "size" in key_obj[1] and style in key_obj[1] and
         key_obj[1]["size"] == item.get('font_size') and
         key_obj[1][style] == item.get(style)),
        None
    )


def match_next_label(item, label_next, order_labels):
    return next(
        (key_obj for key_obj in order_labels.items()
         if "size" in key_obj[1] and key_obj[1]["size"] == item.get('font_size')
         and key_obj[0] == label_next),
        None
    )


def match_paragraph(item, order_labels):
    return next(
        (key_obj for key_obj in order_labels.items()
         if "size" in key_obj[1] and
         "next" in key_obj[1] and
         key_obj[1]["size"] == item.get('font_size') and
         key_obj[1]["next"] == "<p>"),
        None
    )


def create_labeled_object(i, item, state):
    obj = {}
    result = match_by_position(i, order_labels)

    if result:
        state['label'] = result[0]
    else:
        if state.get('label_next'):
            if state.get('repeat'):
                result = match_by_regex(item.get('text'), order_labels)
                if result:
                    state['label'] = result[0]
                else:
                    result = match_by_style_and_size(item, order_labels, style='bold')
                    if result:
                        state['label'] = result[0]
                        state['repeat'] = None
                        state['reset'] = None
                        state['label_next'] = result[1].get("next")
                        state['body'] = result[1].get("size") == 16
                        if state['body'] and re.search(r"^(refer)", item.get('text').lower()):
                            state['body'] = False
                            state['back'] = True
            if not result:
                result = match_next_label(item, state['label_next'], order_labels)
                if result:
                    state['label'] = result[0]
                    state['label_next_reset'] = result[1].get("next")
                    state['reset'] = result[1].get("reset", False)
                    state['repeat'] = result[1].get("repeat", False)
        else:
            result = match_by_style_and_size(item, order_labels, style='bold')
            if result:
                state['label'] = result[0]
                state['label_next'] = result[1].get("next")
                if state.get('body') and re.search(r"^(refer)", item.get('text').lower()):
                    state['body'] = False
                    state['back'] = True
            else:
                result = match_by_style_and_size(item, order_labels, style='italic')
                if result:
                    state['label'] = re.sub(r"-\d+", "", result[0])
                    state['label_next'] = result[1].get("next")
                else:
                    result = match_by_regex(item.get('text'), order_labels)
                    if result:
                        state['label'] = result[0]
                    else:
                        result = match_paragraph(item, order_labels)
                        if result:
                            state['label'] = result[0]

    if result:
        if state['label'] in ['<abstract>']:
            order_labels.pop(state['label'], None)

        label_info = result[1]
        obj['type'] = 'paragraph_with_language' if label_info.get("lan") else 'paragraph'

        obj['value'] = {
            'label': state['label'],
            'paragraph': item.get('text')
        }

        if state['label'] == '<contrib>':
            obj['type'] = 'author_paragraph'
        elif state['label'] == '<aff>':
            obj['type'] = 'aff_paragraph'

    return obj, result, state


def match_section(item, sections):
    return {'label': '<sec>', 'body': True} if (
        item.get('font_size') == sections[0].get('size') and
        item.get('bold') == sections[0].get('bold') and
        item.get('text', '').isupper() == sections[0].get('isupper')
    ) else None


def match_subsection(item, sections):
    return {'label': '<sub-sec>', 'body': True} if (
        item.get('font_size') == sections[1].get('size') and
        item.get('bold') == sections[1].get('bold') and
        item.get('text', '').isupper() == sections[1].get('isupper')
    ) else None


def create_labeled_object2(i, item, state, sections):
    obj = {}
    result = None

    if match_section(item, sections):
        result = match_section(item, sections)
        state['label'] = result.get('label')
        state['body'] = result.get('body')
    
    if match_subsection(item, sections):
        result = match_subsection(item, sections)
        state['label'] = result.get('label')
        state['body'] = result.get('body')

    if state.get('body') and re.search(r"^(refer)", item.get('text').lower()):
        state['label'] = '<sec>'
        state['body'] = False
        state['back'] = True

    if not result:
        result = {'label': '<p>', 'body': state['body'], 'back': state['back']}
        state['label'] = result.get('label')
        state['body'] = result.get('body')
        state['back'] = result.get('back')

    if result:
        pass
    else:
        if state.get('label_next'):
            if state.get('repeat'):
                result = match_by_regex(item.get('text'), order_labels)
                if result:
                    state['label'] = result[0]
                else:
                    result = match_by_style_and_size(item, order_labels, style='bold')
                    if result:
                        state['label'] = result[0]
                        state['repeat'] = None
                        state['reset'] = None
                        state['label_next'] = result[1].get("next")
                        state['body'] = result[1].get("size") == 16
                        if state['body'] and re.search(r"^(refer)", item.get('text').lower()):
                            state['body'] = False
                            state['back'] = True
            if not result:
                result = match_next_label(item, state['label_next'], order_labels)
                if result:
                    state['label'] = result[0]
                    state['label_next_reset'] = result[1].get("next")
                    state['reset'] = result[1].get("reset", False)
                    state['repeat'] = result[1].get("repeat", False)
        else:
            result = match_by_style_and_size(item, order_labels, style='bold')
            if result:
                state['label'] = result[0]
                state['label_next'] = result[1].get("next")
                if state.get('body') and re.search(r"^(refer)", item.get('text').lower()):
                    state['body'] = False
                    state['back'] = True
            else:
                result = match_by_style_and_size(item, order_labels, style='italic')
                if result:
                    state['label'] = re.sub(r"-\d+", "", result[0])
                    state['label_next'] = result[1].get("next")
                else:
                    result = match_by_regex(item.get('text'), order_labels)
                    if result:
                        state['label'] = result[0]
                    else:
                        result = match_paragraph(item, order_labels)
                        if result:
                            state['label'] = result[0]

    if result:
        if state['label'] in ['<abstract>']:
            order_labels.pop(state['label'], None)

        #label_info = result[1]
        #obj['type'] = 'paragraph_with_language' if label_info.get("lan") else 'paragraph'
        obj['type'] = 'paragraph'

        obj['value'] = {
            'label': state['label'],
            'paragraph': item.get('text')
        }

        if state['label'] == '<contrib>':
            obj['type'] = 'author_paragraph'
        elif state['label'] == '<aff>':
            obj['type'] = 'aff_paragraph'

    return obj, result, state
