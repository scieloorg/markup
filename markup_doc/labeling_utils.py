import requests
import json
import re
from lxml import etree
from .choices import order_labels
from rest_framework_simplejwt.tokens import RefreshToken
from model_ai.models import LlamaModel


def getLLM():
    model_ai = LlamaModel.objects.first()

    if model_ai.api_key_gemini:
        return 'GEMINI'
    else:
        return 'LLAMA'
    

def split_in_three(obj_reference, chunk_size=15):
    if not obj_reference:
        return []
    return [obj_reference[i:i + chunk_size] 
            for i in range(0, len(obj_reference), chunk_size)]


def extract_label_and_title(text):
    """
    Extrae el Label (Figura/Figure/Tabla/Table/Tabela + número) y el Title (resto del texto limpio).
    Ignora mayúsculas y minúsculas y limpia puntuación/espacios entre el número y el título.
    """
    # Acepta Figura/Figure y Tabla/Table/Tabela
    pattern = r'\b(Imagen|Imágen|Image|Imagem|Figura|Figure|Tabla|Table|Tabela)\s+(\d+)\b'
    match = re.search(pattern, text, re.IGNORECASE)

    if match:
        word = match.group(1).capitalize()   # Normaliza capitalización
        number = match.group(2)
        label = f"{word} {number}"

        # Texto después del número
        rest = text[match.end():]

        # Quita puntuación/espacios iniciales (.,;: guiones, etc.)
        rest_clean = re.sub(r'^[\s\.,;:–—-]+', '', rest)

        return {"label": label, "title": rest_clean.strip()}
    else:
        return {"label": None, "title": text.strip()}


def create_special_content_object(item, stream_data_body, counts):
    """Create objects for special content types (image, table, list, compound)"""
    obj = {}

    if item.get('type') == 'image':
        obj = {}
        counts['numfig'] += 1
        obj['type'] = 'image'
        obj['value'] = {
                'figid' : f"f{counts['numfig']}",
                'label' : '<fig>',
                'image' : item.get('image')
            }
        
         #Obitiene el elemento aterior
        try:
            prev_element = stream_data_body[-1]
            label_title = extract_label_and_title(prev_element['value']['paragraph'])
            obj['value']['figlabel'] = label_title['label']
            obj['value']['title'] = label_title['title']
            stream_data_body.pop(-1)
        except:
            pass

    elif item.get('type') == 'table':
        obj = {}
        counts['numtab'] += 1
        obj['type'] = 'table'
        obj['value'] = {
            'tabid' : f"t{counts['numtab']}",
            'label' : '<table>',
            'content' : item.get('table')
        }

        #Obitiene el elemento aterior
        try:
            prev_element = stream_data_body[-1]
            label_title = extract_label_and_title(prev_element['value']['paragraph'])
            obj['value']['tablabel'] = label_title['label']
            obj['value']['title'] = label_title['title']
            stream_data_body.pop(-1)
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
        counts['numeq'] += 1
        obj['type'] = 'compound_paragraph'
        obj['value'] = {
            'eid' : f"e{counts['numeq']}",
            #'label' : '<formula>',
            'content': item.get('text')
        }
        text_count = sum(
            1 for c in obj['value']['content']
            if c['type'] == 'text'
        )
        
        if text_count > 1:
            obj['value']['label'] = '<inline-formula>'
            return obj, counts

        if text_count == 0:
            obj['value']['label'] = '<disp-formula>'
            return obj, counts
        
        text_value = next(
            item['value']
            for item in obj['value']['content']
            if item['type'] == 'text'
        )
        text = is_number_parenthesis(text_value)
        if text:
            obj['value']['label'] = '<disp-formula>'
            next(
                item
                for item in obj['value']['content']
                if item['type'] == 'text'
            )['value'] = text
        else:
            obj['value']['label'] = '<inline-formula>'

    return obj, counts


from django.contrib.auth import get_user_model

User = get_user_model()


def process_reference(num_ref, obj, user_id):
    payload = {
        'reference': obj['value']['paragraph']
    }

    model = LlamaModel.objects.first()

    if model.name_file:
        user = User.objects.get(pk=user_id)
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token

        #url = "http://172.17.0.1:8400/api/v1/mix_citation/reference/"
        #url = "http://172.17.0.1:8009/api/v1/mix_citation/reference/"
        url = "http://django:8000/api/v1/reference/"    

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
        obj['value'] = {
                    'paragraph': ref_json.get('full_text', None),
                    'label': '<p>',
                    'reftype': ref_json.get('reftype', None),
                    'refid': 'B'+str(num_ref),
                    'date': ref_json.get('date', None),
                    'title': ref_json.get('title', None),
                    'chapter': ref_json.get('chapter', None),
                    'edition': ref_json.get('edition', None),
                    'source': ref_json.get('source', None),
                    'vol': ref_json.get('vol', None),
                    'issue': ref_json.get('num', None),
                    'pages': ref_json.get('pages', None),
                    'lpage': ref_json.get('lpage', None),
                    'fpage': ref_json.get('fpage', None),
                    'doi': ref_json.get('doi', None),
                    'access_id': ref_json.get('access_id', None),
                    'degree': ref_json.get('degree', None),
                    'organization': ref_json.get('organization', None),
                    'location': ref_json.get('location', None),
                    'org_location': ref_json.get('org_location', None),
                    'num_pages': ref_json.get('num_pages', None),
                    'uri': ref_json.get('uri', None),
                    'version': ref_json.get('version', None),
                    'access_date': ref_json.get('access_date', None),
                    'authors': []
        }
        authors = ref_json.get('authors', [])
        for author in authors:
            obj_auth = {}
            obj_auth['type'] = 'Author'
            obj_auth['value'] = {}
            obj_auth['value']['surname'] = author.get('surname', None)
            obj_auth['value']['given_names'] = author.get('fname', None)
            obj['value']['authors'].append(obj_auth)
        
    return obj


def process_references(num_refs, references):
    arr_references = []

    for i, ref_json in enumerate(references):
        obj = {}
        obj['type'] = 'ref_paragraph'
        obj['value'] = {
                    'paragraph': ref_json.get('full_text', None),
                    'label': '<p>',
                    'reftype': ref_json.get('reftype', None),
                    'refid': 'B'+str(num_refs[i] if i < len(num_refs) else ''),
                    'date': ref_json.get('date', None),
                    'title': ref_json.get('title', None),
                    'chapter': ref_json.get('chapter', None),
                    'edition': ref_json.get('edition', None),
                    'source': ref_json.get('source', None),
                    'vol': ref_json.get('vol', None),
                    'issue': ref_json.get('num', None),
                    'pages': ref_json.get('pages', None),
                    'lpage': ref_json.get('lpage', None),
                    'fpage': ref_json.get('fpage', None),
                    'doi': ref_json.get('doi', None),
                    'access_id': ref_json.get('access_id', None),
                    'degree': ref_json.get('degree', None),
                    'organization': ref_json.get('organization', None),
                    'location': ref_json.get('location', None),
                    'org_location': ref_json.get('org_location', None),
                    'num_pages': ref_json.get('num_pages', None),
                    'uri': ref_json.get('uri', None),
                    'version': ref_json.get('version', None),
                    'access_date': ref_json.get('access_date', None),
                    'authors': []
        }
        authors = ref_json.get('authors', [])
        for author in authors:
            obj_auth = {}
            obj_auth['type'] = 'Author'
            obj_auth['value'] = {}
            obj_auth['value']['surname'] = author.get('surname', None)
            obj_auth['value']['given_names'] = author.get('fname', None)
            obj['value']['authors'].append(obj_auth)
        arr_references.append(obj)
    
    return arr_references


def get_data_first_block(text, metadata, user_id):
    payload = {
        'text': text,
        'metadata': metadata
    }

    model = LlamaModel.objects.first()

    if model.name_file:
        user = User.objects.get(pk=user_id)
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token

        url = "http://django:8000/api/v1/first_block/"    

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        response_json = response.json()
        message_str = response_json['message']

        resp_json = json.loads(message_str)
        
    return resp_json

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


def extract_keywords(text):
    # Quitar punto final si existe
    text = text.strip()
    if text.endswith('.'):
        text = text[:-1].strip()

    # Ver si contiene una etiqueta con dos puntos
    match = re.match(r'(?i)\s*(.+?)\s*:\s*(.+)', text)
    
    if match:
        label = match.group(1).strip()
        content = match.group(2).strip()
    else:
        label = None
        content = text

    # Separar por punto y coma o coma
    keywords = re.split(r'\s*[;,]\s*', content)
    clean_keywords = [p.strip() for p in keywords if p.strip()]
    clean_keywords = ", ".join(keywords)

    return {"title": label, "keywords": clean_keywords}


def extract_subsection(text):
    # Quitar punto final si existe
    text = text.strip()

    # Ver si contiene una etiqueta con dos puntos
    match = re.match(r'(?i)\s*(.+?)\s*:\s*(.+)', text)
    
    if match:
        label = match.group(1).strip()
        content = match.group(2).strip()
    else:
        label = None
        content = text

    return {"title": label, "content": content}


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

    if state.get('body') and re.search(r"^(refer)", item.get('text').lower()) and match_section(item, sections):
        state['label'] = '<sec>'
        state['body'] = False
        state['back'] = True
        obj['type'] = 'paragraph'
        obj['value'] = {
            'label': state['label'],
            'paragraph': item.get('text')
        }
    
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

    if re.search(r"^(translation)", item.get('text').lower()):
        state['label'] = '<translate-fron>'
        state['body'] = False
        state['back'] = False
        obj['type'] = 'paragraph_with_language'
        obj['value'] = {
            'label': state['label'],
            'paragraph': item.get('text')
        }

    return obj, result, state


def buscar_refid_por_surname_y_date(data_back, surname_buscado, date_buscado):
    """
    Busca un bloque RefParagraphBlock que contenga un author con el surname especificado
    y que coincida con la fecha dada. Retorna el refid si encuentra una coincidencia.
    """
    for bloque in data_back:  # Reemplaza 'contenido' con el nombre de tu StreamField
        if bloque['type'] == 'ref_paragraph':  # o el nombre que usaste en el StreamField
            data = bloque['value']

            # Verificar la fecha
            if str(data.get('date')) != str(date_buscado[:4]):
                continue

            # Revisar autores
            authors = data.get('authors', [])

            surname_buscados = surname_buscado.split(',')

            for surname_buscado in surname_buscados:
                if ' y ' in surname_buscado or ' and ' in surname_buscado or ' e ' in surname_buscado or ' & ' in surname_buscado:
                    if ' y ' in surname_buscado:
                        surname1 = surname_buscado.split(' y ')[0].strip().lower()
                        surname2 = surname_buscado.split(' y ')[1].strip().lower()
                    
                    if ' and ' in surname_buscado:
                        surname1 = surname_buscado.split(' and ')[0].strip().lower()
                        surname2 = surname_buscado.split(' and ')[1].strip().lower()

                    if ' & ' in surname_buscado:
                        surname1 = surname_buscado.split(' & ')[0].strip().lower()
                        surname2 = surname_buscado.split(' & ')[1].strip().lower()
                    
                    if ' e ' in surname_buscado:
                        surname1 = surname_buscado.split(' e ')[0].strip().lower()
                        surname2 = surname_buscado.split(' e ')[1].strip().lower()

                    for author_bloque in authors:
                        if author_bloque['type'] == 'Author':
                            author_data = author_bloque['value']
                            if surname1 in (author_data.get('surname') or '').lower() + ' ' + (author_data.get('given_names') or '').lower():
                                for author_bloque2 in authors:
                                    if author_bloque2['type'] == 'Author':
                                        author_data = author_bloque2['value']
                                        if surname2 in (author_data.get('surname') or '').lower() + ' ' + (author_data.get('given_names') or '').lower():
                                            return data.get('refid')

                for author_bloque in authors:
                    if author_bloque['type'] == 'Author':
                        author_data = author_bloque['value']

                        if surname_buscado.strip().lower() in (author_data.get('surname') or '').lower() + ' ' + (author_data.get('given_names') or '').lower():
                            return data.get('refid')
            
            if surname_buscado.strip().lower() in (data.get('paragraph') or '').lower():
                return data.get('refid')

    return None


def extract_citation_apa(texto, data_back):
    """
    Extrae citas en formato APA dentro de un texto y devuelve:
    - la cita completa,
    - el primer autor,
    - el año.
    Acepta múltiples espacios entre palabras y símbolos.
    """
    
    # Preposiciones comunes en apellidos
    preposiciones = r'(?:de|del|la|los|las|da|do|dos|das|van|von)'
    # Apellido compuesto o con preposición (incluye caracteres portugueses: ç, ã, õ, etc.)
    apellido = rf'[A-ZÁÉÍÓÚÑÇÃÕÂÊÎÔÛ][a-záéíóúñçãõâêîôû]+(?:[-‐\s]+(?:{preposiciones})?\s*[A-ZÁÉÍÓÚÑÇÃÕÂÊÎÔÛ]?[a-záéíóúñçãõâêîôû]+)*'
    resultados = []
    
    # 1. Buscar todas las citas dentro de paréntesis
    for paren in re.finditer(r'\(([^)]+)\)', texto):
        contenido_completo = paren.group(1)
        
        # Si hay punto y coma, dividir las citas
        if ';' in contenido_completo:
            partes = [parte for parte in contenido_completo.split(';')]
        else:
            partes = [contenido_completo]
        
        # Variable para rastrear el contexto de autores dentro del mismo paréntesis
        autores_en_parentesis = []
        
        for i, parte in enumerate(partes):
            parte = parte  # Agregar strip aquí para limpiar espacios
            if not parte:
                continue
            
            # Caso especial: solo año (para citas como "2017" después de "2014;")
            # MEJORADO: Solo aplicar si hay citas previas EN EL MISMO PARÉNTESIS
            if re.match(r'^\s*\d{4}[a-z]?\s*$', parte):
                # Solo usar el último autor si hay autores en el mismo paréntesis
                if autores_en_parentesis:
                    ultimo_autor = autores_en_parentesis[-1]
                    refid = buscar_refid_por_surname_y_date(data_back, ultimo_autor, parte)
                    resultados.append({
                        "cita": parte,
                        "autor": ultimo_autor,
                        "anio": parte,
                        "refid": refid
                    })
                # Si no hay autores previos en el paréntesis, ignorar (posible error)
                continue
            
            # Patrones para diferentes tipos de citas
            cita_encontrada = False
            
            # Patrón 1: Múltiples autores con & y coma antes del año
            # Ejemplo: "Porta, Lopez-De-Silanes, & Shleifer, 1999"
            pattern1 = rf'(?P<autores>{apellido}(?:\s*,\s*{apellido})*\s*,?\s*&\s*{apellido})\s*,\s*(?P<anio>\d{{4}}[a-z]?)'
            match = re.search(pattern1, parte)
            if match:
                autores_completos = match.group("autores")
                anio = match.group("anio")
                primer_autor = re.split(r'\s*,\s*', autores_completos)[0]
                autores_en_parentesis.append(primer_autor)
                refid = buscar_refid_por_surname_y_date(data_back, primer_autor, anio)
                resultados.append({
                    "cita": parte,
                    "autor": primer_autor,
                    "anio": anio,
                    "refid": refid
                })
                cita_encontrada = True
            
            # Patrón 2: Múltiples autores con & SIN coma antes del año
            # Ejemplo: "Silva, Peixoto, & Tizziotti 2021"
            if not cita_encontrada:
                pattern2 = rf'(?P<autores>{apellido}(?:\s*,\s*{apellido})*\s*,?\s*&\s*{apellido})\s+(?P<anio>\d{{4}}[a-z]?)'
                match = re.search(pattern2, parte)
                if match:
                    autores_completos = match.group("autores")
                    anio = match.group("anio")
                    primer_autor = re.split(r'\s*,\s*', autores_completos)[0]
                    autores_en_parentesis.append(primer_autor)
                    refid = buscar_refid_por_surname_y_date(data_back, primer_autor, anio)
                    resultados.append({
                        "cita": parte,
                        "autor": primer_autor,
                        "anio": anio,
                        "refid": refid
                    })
                    cita_encontrada = True
            
            # Patrón 3: Dos autores con & (simple)
            # Ejemplo: "Crisóstomo & Brandão, 2019"
            if not cita_encontrada:
                pattern3 = rf'(?P<autor1>{apellido})\s*&\s*(?P<autor2>{apellido})\s*,\s*(?P<anio>\d{{4}}[a-z]?)'
                match = re.search(pattern3, parte)
                if match:
                    primer_autor = match.group("autor1")
                    anio = match.group("anio")
                    autores_en_parentesis.append(primer_autor)
                    refid = buscar_refid_por_surname_y_date(data_back, primer_autor, anio)
                    resultados.append({
                        "cita": parte,
                        "autor": primer_autor,
                        "anio": anio,
                        "refid": refid
                    })
                    cita_encontrada = True
            
            # Patrón 4: Autor con "et al." con coma
            # Ejemplo: "Brandão et al., 2019"
            if not cita_encontrada:
                pattern4 = rf'(?P<autor>{apellido})\s+et\s+al\s*\.?\s*,\s*(?P<anio>\d{{4}}[a-z]?)'
                match = re.search(pattern4, parte)
                if match:
                    autor = match.group("autor")
                    anio = match.group("anio")
                    autores_en_parentesis.append(autor)
                    refid = buscar_refid_por_surname_y_date(data_back, autor, anio)
                    resultados.append({
                        "cita": parte,
                        "autor": autor,
                        "anio": anio,
                        "refid": refid
                    })
                    cita_encontrada = True
            
            # Patrón 5: Autor con "et al." sin coma
            # Ejemplo: "Brandão et al. 2019"
            if not cita_encontrada:
                pattern5 = rf'(?P<autor>{apellido})\s+et\s+al\s*\.?\s+(?P<anio>\d{{4}}[a-z]?)'
                match = re.search(pattern5, parte)
                if match:
                    autor = match.group("autor")
                    anio = match.group("anio")
                    autores_en_parentesis.append(autor)
                    refid = buscar_refid_por_surname_y_date(data_back, autor, anio)
                    resultados.append({
                        "cita": parte,
                        "autor": autor,
                        "anio": anio,
                        "refid": refid
                    })
                    cita_encontrada = True
            
            # Patrón 6: Múltiples autores solo con comas (sin &)
            # Ejemplo: "Adam, Tene, Mucci, Beck, 2020" o "Correia, Amaral, Louvet, 2014a"
            if not cita_encontrada:
                pattern6 = rf'(?P<autores>{apellido}(?:\s*,\s*{apellido}){{2,}})\s*,\s*(?P<anio>\d{{4}}[a-z]?)'
                match = re.search(pattern6, parte)
                if match:
                    autores_completos = match.group("autores")
                    anio = match.group("anio")
                    primer_autor = re.split(r'\s*,\s*', autores_completos)[0]
                    autores_en_parentesis.append(primer_autor)
                    refid = buscar_refid_por_surname_y_date(data_back, primer_autor, anio)
                    resultados.append({
                        "cita": parte,
                        "autor": primer_autor,
                        "anio": anio,
                        "refid": refid
                    })
                    cita_encontrada = True
            
            # Patrón 7: Autor simple con coma
            # Ejemplo: "Smith, 2020"
            if not cita_encontrada:
                pattern7 = rf'(?P<autor>{apellido})\s*,\s*(?P<anio>\d{{4}}[a-z]?)'
                match = re.search(pattern7, parte)
                if match:
                    autor = match.group("autor")
                    anio = match.group("anio")
                    autores_en_parentesis.append(autor)
                    refid = buscar_refid_por_surname_y_date(data_back, autor, anio)
                    resultados.append({
                        "cita": parte,
                        "autor": autor,
                        "anio": anio,
                        "refid": refid
                    })
                    cita_encontrada = True
    
    # 2. Citas fuera del paréntesis: Nombre (2000) o Nombre et al. (2000)
    # MEJORADO: Filtrar citas que están precedidas por preposiciones
    
    # Lista de preposiciones a evitar
    preposiciones_evitar = ['de', 'del', 'la', 'los', 'las', 'da', 'do', 'dos', 'das', 'van', 'von']
    
    # Patrón para citas con múltiples años: Autor (2018, 2019)
    patron_multiples_años = rf'(?P<autor>{apellido})(?:\s*[-‐]\s*{apellido})*(?:\s+et\s+al\s*\.?|\s+(?:y|and|&)\s+{apellido})?\s*\(\s*(?P<años>\d{{4}}[a-z]?(?:\s*,\s*\d{{4}}[a-z]?)+)\s*\)'
    
    for match in re.finditer(patron_multiples_años, texto):
        # Verificar que no haya preposición antes de la cita
        inicio_match = match.start()
        texto_anterior = texto[:inicio_match].split()
        
        # Si hay palabras antes y la última es una preposición, saltarse esta cita
        if texto_anterior and texto_anterior[-1].lower() in preposiciones_evitar:
            continue
            
        autor = match.group("autor")
        años_str = match.group("años")
        # Separar los años y crear una cita para cada uno
        años = [año for año in años_str.split(',')]
        
        for año in años:
            refid = buscar_refid_por_surname_y_date(data_back, autor, año)
            resultados.append({
                "cita": f"{autor} et al. ({año})" if "et al" in match.group(0) else f"{autor} ({año})",
                "autor": autor,
                "anio": año,
                "refid": refid
            })
    
    # Patrón para citas simples: Nombre (2000) o Nombre et al. (2000)
    patron_afuera = rf'(?P<autor>{apellido})(?:\s*[-‐]\s*{apellido})*(?:\s+et\s+al\s*\.?|\s+(?:y|and|&)\s+{apellido})?\s*\(\s*(?P<anio>\d{{4}}[a-z]?)\s*\)'
    
    for match in re.finditer(patron_afuera, texto):
        # Verificar que no haya preposición antes de la cita
        inicio_match = match.start()
        texto_anterior = texto[:inicio_match].split()
        
        # Si hay palabras antes y la última es una preposición, saltarse esta cita
        if texto_anterior and texto_anterior[-1].lower() in preposiciones_evitar:
            continue
            
        autor = match.group("autor")
        anio = match.group("anio")
        
        # Verificar que no sea parte de una cita con múltiples años ya procesada
        cita_completa = match.group(0)
        es_multiple = False
        for resultado in resultados:
            if resultado["autor"] == autor and resultado["anio"] == anio and "," in cita_completa:
                es_multiple = True
                break
        
        if not es_multiple:
            refid = buscar_refid_por_surname_y_date(data_back, autor, anio)
            resultados.append({
                "cita": cita_completa,
                "autor": autor,
                "anio": anio,
                "refid": refid
            })
    
    return resultados


def clean_labels(texto):
    """
    Elimina todas las etiquetas XML del texto.
    """
    # Patrón para encontrar etiquetas XML (apertura y cierre)
    patron_etiquetas = r'<[^>]+>'
    texto_limpio = re.sub(patron_etiquetas, '', texto)
    
    # Limpiar espacios múltiples que puedan haber quedado
    #texto_limpio = re.sub(r'\s+', ' ', texto_limpio)
    
    return texto_limpio#.strip()


def map_text(texto):
    """
    Crea un mapa de TODO lo que esté etiquetado en el texto.
    Clave: texto sin etiquetas, Valor: texto con etiquetas
    """
    mapa = {}
    
    # Buscar TODAS las etiquetas y su contenido
    patron = r'<[^>]+>.*?</[^>]+>|<[^/>]+/>'
    matches = re.findall(patron, texto, re.DOTALL)
    
    for match in matches:
        contenido_limpio = clean_labels(match)#.strip()
        if contenido_limpio:  # Solo si hay contenido real
            mapa[contenido_limpio] = match#.strip()
    
    return mapa


def search_position(texto, substring):
    """
    Encuentra todas las posiciones donde aparece un substring en el texto.
    """
    posiciones = []
    inicio = 0
    while True:
        pos = texto.find(substring, inicio)
        if pos == -1:
            break
        posiciones.append((pos, pos + len(substring)))
        inicio = pos + 1
    return posiciones


def extract_labels(texto_original, texto_limpio, pos_inicio, pos_fin):
    """
    Extrae un fragmento específico del texto original basado en posiciones del texto limpio.
    """
    contador_chars_limpios = 0
    resultado = ""
    dentro_del_rango = False
    
    i = 0
    while i < len(texto_original) and contador_chars_limpios <= pos_fin:
        char = texto_original[i]
        
        if char == '<':
            # Encontrar el final de la etiqueta
            fin_etiqueta = texto_original.find('>', i)
            if fin_etiqueta != -1:
                etiqueta = texto_original[i:fin_etiqueta + 1]
                
                # Si estamos dentro del rango, incluir la etiqueta
                if dentro_del_rango:
                    resultado += etiqueta
                
                i = fin_etiqueta + 1
                continue
        
        # Verificar si entramos o salimos del rango
        if contador_chars_limpios == pos_inicio:
            dentro_del_rango = True
        elif contador_chars_limpios == pos_fin:
            dentro_del_rango = False
            break
        
        # Si estamos dentro del rango, incluir el caracter
        if dentro_del_rango:
            resultado += char
        
        contador_chars_limpios += 1
        i += 1
    
    return resultado


def restore_labels_ref(ref, mapa_etiquetado, texto_original, texto_limpio):
    """
    Restaura las etiquetas en una referencia específica usando el mapa y verificando posición.
    Solo reemplaza si el contenido estaba realmente etiquetado en esa posición específica.
    """
    # Encontrar todas las posiciones donde aparece esta ref en el texto limpio
    posiciones_ref = search_position(texto_limpio, ref)
    
    if not posiciones_ref:
        return ref
    
    # Para cada posición, extraer el fragmento original y ver si contiene etiquetas
    mejores_candidatos = []
    
    for pos_inicio, pos_fin in posiciones_ref:
        fragmento_original = extract_labels(
            texto_original, texto_limpio, pos_inicio, pos_fin
        )
        
        # Si el fragmento original es diferente al ref, significa que tenía etiquetas
        if fragmento_original != ref:
            mejores_candidatos.append(fragmento_original)
    
    # Si encontramos candidatos con etiquetas, devolver el primero
    if mejores_candidatos:
        return mejores_candidatos[0]
    
    # Si no hay candidatos con etiquetas, devolver el ref original sin modificar
    return ref


def proccess_labeled_text(texto, data_back):
    """
    Procesa un texto eliminando etiquetas XML, extrae citas APA y las devuelve
    con sus etiquetas originales restauradas.
    
    Args:
        texto (str): Texto original con etiquetas XML
        extraer_citas_apa (function): Función que extrae citas del texto limpio
    
    Returns:
        list: Lista de citas con etiquetas XML restauradas
    """
    
    # Crear mapa de transformaciones
    mapa_transformaciones = map_text(texto)
    #print(f"mapa: {mapa_transformaciones}")
    
    # Limpiar texto eliminando etiquetas
    texto_limpio = clean_labels(texto)
    
    # Extraer citas del texto limpio
    refs = extract_citation_apa(texto_limpio, data_back)
    #print(f"refs: {refs}")

     # 4. Para cada ref, usar posición para restaurar solo lo que realmente estaba etiquetado
    refs_con_etiquetas = []
    for ref in refs:
        ref_restaurada = ref
        ref_restaurada['cita'] = restore_labels_ref(ref['cita'], mapa_transformaciones, texto, texto_limpio)
        refs_con_etiquetas.append(ref_restaurada)
    
    return refs_con_etiquetas


def search_special_id(data_body, label):
    for d in data_body: 
        if d['type'] in ['image', 'table']:
            data = d['value']
            clean_label = re.sub(r'^[\s\.,;:–—-]+', '', label).capitalize()

            if d['type'] == 'image':
                if clean_label == data['figlabel']:
                    return data.get('figid')
                if data['figid'][0] == clean_label.lower()[0] and data['figid'][1] in clean_label.lower():
                    return data.get('figid')
            
            if d['type'] == 'table':
                if clean_label == data['tablabel']:
                    return data.get('tabid')
                if data['tabid'][0] == clean_label.lower()[0] and data['tabid'][1] in clean_label.lower():
                    return data.get('tabid')
    
    for d in data_body: 
        if d['type'] in ['compound_paragraph']:
            data = d['value']
            clean_label = re.sub(r'^[\s\.,;:–—-]+', '', label).lower()

            if d['type'] == 'compound_paragraph':
                if data['eid'][0] in clean_label[0] and data['eid'][1] in clean_label:
                    return data.get('eid')

    return None


def is_number_parenthesis(text):
    pattern = re.compile(r'^\s*\(\s*(\d+)\s*\)\s*$')
    match = pattern.fullmatch(text)
    if match:
        return f"({match.group(1)})"
    return None


def proccess_special_content(text, data_body):
    # normaliza espacios no separables por si acaso
    text = re.sub(r'[\u00A0\u2007\u202F]', ' ', text)

    pattern = r"""
        (?<!\w)                                   # inicio no al medio de una palabra
        (?:
            Imagen|Imágen|Image|Imagem|
            Figura|Figure|
            Tabla|Table|Tabela|
            Ecuaci[oó]n|Equa(?:ç[aã]o|cao)|Equation|
            F[oó]rmula|Formula|
            Eq\.|Ec\.|Form\.|F[óo]rm\.
        )\s*
        (?:\(\s*\d+\s*\)|\d+)                     # 1  o  (1)
        (?!\w)                                    # que no siga una letra/número
    """

    res = []
    dict_type = {'f': 'fig', 't': 'table', 'e': 'disp-formula'}

    try:
        for match in re.finditer(pattern, text, re.IGNORECASE | re.UNICODE | re.VERBOSE):
            label = match.group(0)
            
            id = search_special_id(data_body, label)
            
            res.append({
                "label": label,
                "id": id,
                "reftype": dict_type.get(id[0].lower(), 'other')
            })
    except Exception as exc:
        print(f'ERROR proccess_special_content: {exc}')
        pass

    return res


def remove_unpaired_tags(text):
    # Match opening/closing tags, capturing only the tag name (before any space or >)
    pattern = re.compile(r'<(/?)([a-zA-Z0-9]+)(?:\s[^>]*)?>')
    
    result = []
    stack = []  # Stores (tag_name, position_in_result)
    
    i = 0
    for match in pattern.finditer(text):
        is_closing, tag_name = match.groups()
        is_closing = bool(is_closing)
        
        # Text between tags
        if match.start() > i:
            result.append(text[i:match.start()])
        
        tag_text = text[match.start():match.end()]
        
        if not is_closing:
            # Opening tag
            stack.append((tag_name, len(result)))
            result.append(tag_text)
        else:
            # Closing tag
            if stack and stack[-1][0] == tag_name:
                stack.pop()
                result.append(tag_text)
            else:
                # Orphan closing tag - skip
                pass
        
        i = match.end()
    
    # Append remaining text
    if i < len(text):
        result.append(text[i:])
    
    # Remove unclosed opening tags
    for tag_name, pos in sorted(stack, reverse=True, key=lambda x: x[1]):
        result.pop(pos)
    
    return ''.join(result)


def append_fragment(node_dest, val):
    if not val:
        parent = node_dest.getparent()
        if parent:
            parent.remove(node_dest)
        return

    # 1) Limpiezas mínimas
    #    - eliminar <br> / <br/>
    #    - quitar saltos de línea
    clean = re.sub(r"(?i)<br\s*/?>", "", val)
    clean = clean.replace("\n", "")

    # normaliza entidades problemáticas
    clean = clean.replace("&nbsp;", " ")
    clean = re.sub(r'&(?!\w+;|#\d+;)', '&amp;', clean)

    clean = remove_unpaired_tags(clean)

    if clean == "":
        parent = node_dest.getparent()
        if parent:
            parent.remove(node_dest)
        return

    # 2) Si no hay etiquetas, es texto plano
    if "<" not in clean:
        node_dest.text = (node_dest.text or "") + clean
        return

    # 3) Envolver para que sea XML bien formado aunque empiece con texto
    wrapper = etree.XML(f"<_wrap_>{clean}</_wrap_>")

    # 4) Pasar el texto inicial (antes del primer tag)
    if wrapper.text:
        node_dest.text = (node_dest.text or "") + wrapper.text

    # 5) Mover cada hijo al destino (sus .tail se conservan)
    for child in list(wrapper):
        node_dest.append(child)

        