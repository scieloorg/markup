import requests
import json
from .choices import order_labels

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
        prev_element = stream_data_body[-1]
        prev_element['value']['label'] = '<table-caption>'

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


def process_reference(obj):

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
        obj['type'] = 'ref_paragraph'
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
