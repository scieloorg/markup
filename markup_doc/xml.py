from lxml import etree
import re, html, os
from markup_doc.labeling_utils import (
    extract_subsection,
    proccess_labeled_text,
    proccess_special_content,
    append_fragment
)
from wagtail.images import get_image_model
from urllib.parse import urlparse


def extract_date(texto):
    try:
        # Patrón para detectar YYYY-MM-DD, YYYY/MM/DD, DD-MM-YYYY, DD/MM/YYYY
        patron_fecha = r'\b(\d{4})[-/](\d{2})[-/](\d{2})\b|\b(\d{2})[-/](\d{2})[-/](\d{4})\b'
        
        match = re.search(patron_fecha, texto)
        if match:
            if match.group(1):  # Formato YYYY-MM-DD o YYYY/MM/DD
                año = match.group(1)
                mes = match.group(2).zfill(2)
                dia = match.group(3).zfill(2)
            else:  # Formato DD-MM-YYYY o DD/MM/YYYY
                dia = match.group(4).zfill(2)
                mes = match.group(5).zfill(2)
                año = match.group(6)
            return (dia, mes, año)
    except:
        pass
    
    return None  # No se encontró


def get_xml(article_docx, data_front, data, data_back):
    # Crear el elemento raíz
    nsmap = {
        'mml': 'http://www.w3.org/1998/Math/MathML',
        'xlink': 'http://www.w3.org/1999/xlink'
    }
    root = etree.Element('article',
                            nsmap=nsmap,
                            attrib={ 
                                'article-type': 'research-article',
                                'dtd-version': '1.1',
                                'specific-use': 'sps-1.9',
                                '{http://www.w3.org/XML/1998/namespace}lang': article_docx.language or 'en'}
                                #'{http://www.w3.org/1998/Math/MathML}mml': 'http://www.w3.org/1998/Math/MathML',
                                #'{http://www.w3.org/1999/xlink}xlink': 'http://www.w3.org/1999/xlink'}
                        )

    # Añadir un elemento hijo
    front = etree.SubElement(root, "front")
    body = etree.SubElement(root, "body")
    back = etree.SubElement(root, "back")
    node_reflist = etree.SubElement(back, 'ref-list')

    subsec = None
    num_table = 1
    continue_t = False
    arr_subarticle = []

    node = etree.SubElement(front, 'journal-meta')
    
    if article_docx.acronym:
        node_tmp = etree.SubElement(node, 'journal-id')
        node_tmp.set('journal-id-type', 'publisher-id')
        node_tmp.text = article_docx.acronym

    if article_docx.title_nlm:
        node_tmp = etree.SubElement(node, 'journal-id')
        node_tmp.set('journal-id-type', 'nlm-ta')
        node_tmp.text = article_docx.title_nlm

    node_tmp = etree.SubElement(node, 'journal-title-group')

    if article_docx.journal_title:
        node_tmp2 = etree.SubElement(node_tmp, 'journal-title')
        node_tmp2.text = article_docx.journal_title

    if article_docx.short_title:
        node_tmp2 = etree.SubElement(node_tmp, 'abbrev-journal-title')
        node_tmp2.set('abbrev-type', 'publisher')
        node_tmp2.text = article_docx.short_title

    if article_docx.pissn:
        node_tmp = etree.SubElement(node, 'issn')
        node_tmp.set('pub-type', 'ppub')
        node_tmp.text = article_docx.pissn

    if article_docx.eissn:
        node_tmp = etree.SubElement(node, 'issn')
        node_tmp.set('pub-type', 'epub')
        node_tmp.text = article_docx.eissn

    node_tmp = etree.SubElement(node, 'publisher')

    if article_docx.pubname:
        node_tmp2 = etree.SubElement(node_tmp, 'publisher-name')
        node_tmp2.text = article_docx.pubname

    ##### Article Meta

    translates = []
    current_trans = []

    for block in article_docx.content:
        if (
            block.block_type == "paragraph_with_language" 
            and block.value.get("label") == "<translate-front>"
        ):
            # Si ya tenemos contenido acumulado, lo guardamos como parte
            if current_trans:
                translates.append(current_trans)
                current_trans = []
        current_trans.append(block)

    if current_trans:
        translates.append(current_trans)

    for i, data_t in enumerate(translates):
        if i == 0:
            node = etree.SubElement(front, 'article-meta')
        else:
            subarticle = etree.SubElement(root, "sub-article")
            arr_subarticle.append(subarticle)
            subarticle.attrib['article-type'] = "translation"
            subarticle.attrib['id'] = f"S{len(arr_subarticle)}"
            subarticle.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = data_t[0].value['language']

            node = etree.SubElement(subarticle, 'front-stub')

        val = next(
        (b.value['paragraph'] for b in data_t
            if b.block_type == 'paragraph' and b.value.get('label') == '<article-id>'),
            None
        )

        if val:
            node_tmp = etree.SubElement(node, 'article-id')
            node_tmp.set('pub-id-type', 'doi')
            node_tmp.text = val
        
        val = next(
        (b.value['paragraph'] for b in data_t
            if b.block_type == 'paragraph' and b.value.get('label') == '<subject>'),
            None
        )

        if val:
            node_tmp = etree.SubElement(node, 'article-categories')
            node_tmp2 = etree.SubElement(node_tmp, 'subj-group')
            node_tmp2.set('subj-group-type', 'heading')
            node_tmp3 = etree.SubElement(node_tmp2, 'subject')
            node_tmp3.text = val
        
        val = next(
        (b.value['paragraph'] for b in data_t
            if b.block_type == 'paragraph_with_language' and b.value.get('label') == '<article-title>'),
            None
        )

        if val:
            node_tmp = etree.SubElement(node, 'title-group')
            node_tmp2 = etree.SubElement(node_tmp, 'article-title')
            append_fragment(node_tmp2, val)
        
            vals = [
                b
                for b in data_t
                if b.block_type == 'paragraph_with_language' and b.value.get('label') == '<trans-title>'
            ]

            for val in vals:
                node_tmp2 = etree.SubElement(node_tmp, 'trans-title-group')
                node_tmp2.set('{http://www.w3.org/XML/1998/namespace}lang', val.value.get('language'))
                node_tmp3 = etree.SubElement(node_tmp2, 'trans-title')
                append_fragment(node_tmp3, val.value.get('paragraph'))

        node_tmp = etree.SubElement(node, 'contrib-group')

        vals = [
            b
            for b in data_t
            if b.block_type == 'author_paragraph'
            ]
        
        for val in vals:
            node_tmp2 = etree.SubElement(node_tmp, 'contrib')
            node_tmp2.set('contrib-type', 'author')
            if val.value.get('orcid'):
                node_tmp3 = etree.SubElement(node_tmp2, 'contrib-id')
                node_tmp3.set('contrib-id-type', 'orcid')
                node_tmp3.text = val.value.get('orcid')
            node_tmp3 = etree.SubElement(node_tmp2, 'name')
            if val.value.get('surname'):
                node_tmp4 = etree.SubElement(node_tmp3, 'surname')
                append_fragment(node_tmp4, val.value.get('surname'))

            if val.value.get('given_names'):
                node_tmp4 = etree.SubElement(node_tmp3, 'given-names')
                append_fragment(node_tmp4, val.value.get('given_names'))

            if val.value.get('affid'):
                node_tmp3 = etree.SubElement(node_tmp2, 'xref')
                node_tmp3.set('ref-type', 'aff')
                node_tmp3.set('rid', f"aff{val.value.get('affid')}")
                node_tmp3.text = val.value.get('char') or ('*' * int(val.value.get('affid')))

        vals = [
            b
            for b in data_t
            if b.block_type == 'aff_paragraph'
            ]

        for val in vals:
            node_tmp = etree.SubElement(node, 'aff')
            node_tmp.set('id', f"aff{val.value.get('affid')}")

            node_tmp2 = etree.SubElement(node_tmp, 'label')
            node_tmp2.text = val.value.get('char') or ('*' * int(val.value.get('affid')))

            if val.value.get('orgname'):
                node_tmp2 = etree.SubElement(node_tmp, 'institution')
                node_tmp2.set('content-type', 'orgname')
                append_fragment(node_tmp2, val.value.get('orgname'))

            if val.value.get('orgdiv1'):
                node_tmp2 = etree.SubElement(node_tmp, 'institution')
                node_tmp2.set('content-type', 'orgdiv1')
                append_fragment(node_tmp2, val.value.get('orgdiv1'))
            
            if val.value.get('orgdiv2'):
                node_tmp2 = etree.SubElement(node_tmp, 'institution')
                node_tmp2.set('content-type', 'orgdiv2')
                append_fragment(node_tmp2, val.value.get('orgdiv2'))

            node_tmp2 = etree.SubElement(node_tmp, 'addr-line')

            if val.value.get('city'):
                node_tmp3 = etree.SubElement(node_tmp2, 'city')
                append_fragment(node_tmp3, val.value.get('city'))
            
            if val.value.get('state'):
                node_tmp3 = etree.SubElement(node_tmp2, 'state')
                append_fragment(node_tmp3, val.value.get('state'))
            
            if val.value.get('country'):
                node_tmp2 = etree.SubElement(node_tmp, 'country')
                node_tmp2.set('country', val.value.get('code_country'))
                append_fragment(node_tmp2, val.value.get('code_country'))
        
        node_tmp = etree.SubElement(node, 'author-notes')

        for val in vals:

            if val.value.get('text_aff'):
                node_tmp2 = etree.SubElement(node_tmp, 'fn')
                node_tmp2.set('fn-type', 'other')
                node_tmp2.set('id', f"fn{val.value.get('affid')}")
                
                node_tmp3 = etree.SubElement(node_tmp2, 'label')
                node_tmp3.text = val.value.get('char') or ('*' * int(val.value.get('affid')))

                node_tmp3 = etree.SubElement(node_tmp2, 'p')
                append_fragment(node_tmp3, val.value.get('text_aff'))
        
        if article_docx.artdate:
            node_tmp = etree.SubElement(node, 'pub-date')
            node_tmp.set('date-type', 'pub')
            node_tmp.set('publication-format', 'electronic')

            node_tmp2 = etree.SubElement(node_tmp, 'day')
            node_tmp2.text = article_docx.artdate.strftime("%d")

            node_tmp2 = etree.SubElement(node_tmp, 'month')
            node_tmp2.text = article_docx.artdate.strftime("%m")

            node_tmp2 = etree.SubElement(node_tmp, 'year')
            node_tmp2.text = article_docx.artdate.strftime("%Y")
        
        if article_docx.dateiso:
            node_tmp = etree.SubElement(node, 'pub-date')
            node_tmp.set('date-type', 'collection')
            node_tmp.set('publication-format', 'electronic')

            if article_docx.dateiso.split('-')[2] and article_docx.dateiso.split('-')[2] != '00':
                node_tmp2 = etree.SubElement(node_tmp, 'day')
                node_tmp2.text = article_docx.dateiso.split('-')[2]

            if article_docx.dateiso.split('-')[1] and article_docx.dateiso.split('-')[1] != '00':
                node_tmp2 = etree.SubElement(node_tmp, 'month')
                node_tmp2.text = article_docx.dateiso.split('-')[1]

            node_tmp2 = etree.SubElement(node_tmp, 'year')
            node_tmp2.text = article_docx.dateiso.split('-')[0]

        if article_docx.vol:
            node_tmp = etree.SubElement(node, 'volume')
            node_tmp.text = str(article_docx.vol)

        if article_docx.issue:
            node_tmp = etree.SubElement(node, 'issue')
            node_tmp.text = str(article_docx.issue)
        
        if article_docx.elocatid:
            node_tmp = etree.SubElement(node, 'elocation-id')
            node_tmp.text = article_docx.elocatid

        node_tmp = etree.SubElement(node, 'history')

        val = next(
        (b.value['paragraph'] for b in data_t
            if b.block_type == 'paragraph' and b.value.get('label') == '<date-received>'),
            None
        )

        date = extract_date(val)

        if date:
            node_tmp2 = etree.SubElement(node_tmp, 'date')
            node_tmp2.set('date-type', 'received')
            
            node_tmp3 = etree.SubElement(node_tmp2, 'day')
            node_tmp3.text = date[0]

            node_tmp3 = etree.SubElement(node_tmp2, 'month')
            node_tmp3.text = date[1]

            node_tmp3 = etree.SubElement(node_tmp2, 'year')
            node_tmp3.text = date[2]

        val = next(
        (b.value['paragraph'] for b in data_t
            if b.block_type == 'paragraph' and b.value.get('label') == '<date-accepted>'),
            None
        )

        date = extract_date(val)

        if date:
            node_tmp2 = etree.SubElement(node_tmp, 'date')
            node_tmp2.set('date-type', 'accepted')
            
            node_tmp3 = etree.SubElement(node_tmp2, 'day')
            node_tmp3.text = date[0]

            node_tmp3 = etree.SubElement(node_tmp2, 'month')
            node_tmp3.text = date[1]

            node_tmp3 = etree.SubElement(node_tmp2, 'year')
            node_tmp3.text = date[2]
        
        node_tmp = etree.SubElement(node, 'permissions')

        if article_docx.license:
            node_tmp2 = etree.SubElement(node_tmp, 'license')
            node_tmp2.set('license-type', 'open-access')
            node_tmp2.set("{http://www.w3.org/1999/xlink}href", article_docx.license)
            node_tmp2.set("{http://www.w3.org/XML/1998/namespace}lang", article_docx.language)

            node_tmp3 = etree.SubElement(node_tmp2, 'license-p')
            node_tmp3.text = "Este es un artículo con licencia..."
        
        vals = [
            b
            for b in data_t
            if b.block_type == 'paragraph'
            and b.value.get('label') == '<abstract-title>'
            ]

        vals2 = [
            b
            for b in data_t
            if b.block_type == 'paragraph_with_language'
            and b.value.get('label') == '<abstract>'
            ]

        node_tmp = etree.SubElement(node, 'abstract')

        if vals[0]:
            node_tmp2 = etree.SubElement(node_tmp, 'title')
            append_fragment(node_tmp2, vals[0].value.get('paragraph'))

        if vals2[0]:

            # Encuentra su índice original en article_docx.content
            last_index = data_t.index(vals2[0])

            # Recorre los bloques siguientes
            following_paragraphs = []
            for block in data_t[last_index:]:
                if (block.block_type == 'paragraph' and block.value.get('label') == '<p>') or (block.block_type == 'paragraph_with_language' and block.value.get('label') == '<abstract>'):
                    subsection = extract_subsection(block.value.get('paragraph'))

                    if subsection['title']:
                        node_tmp2 = etree.SubElement(node_tmp, 'sec')
                        node_tmp3 = etree.SubElement(node_tmp2, 'title')
                        append_fragment(node_tmp3, subsection['title'])
                        node_tmp3 = etree.SubElement(node_tmp2, 'p')
                        append_fragment(node_tmp3, subsection['content'])
                    else:
                        node_tmp2 = etree.SubElement(node_tmp, 'p')
                        append_fragment(node_tmp2, subsection['content'])
                else:
                    break

        for i, val in enumerate(vals[1:], start=1):
            node_tmp = etree.SubElement(node, 'trans-abstract')
            node_tmp.set("{http://www.w3.org/XML/1998/namespace}lang", vals2[i].value.get('language'))

            node_tmp2 = etree.SubElement(node_tmp, 'title')
            append_fragment(node_tmp2, val.value.get('paragraph'))

            last_index = data_t.index(vals2[i])

            # Recorre los bloques siguientes
            following_paragraphs = []
            for block in data_t[last_index:]:
                if (block.block_type == 'paragraph' and block.value.get('label') == '<p>') or (block.block_type == 'paragraph_with_language' and block.value.get('label') == '<abstract>'):
                    subsection = extract_subsection(block.value.get('paragraph'))

                    if subsection['title']:
                        node_tmp2 = etree.SubElement(node_tmp, 'sec')
                        node_tmp3 = etree.SubElement(node_tmp2, 'title')
                        append_fragment(node_tmp3, subsection['title'])
                        node_tmp3 = etree.SubElement(node_tmp2, 'p')
                        append_fragment(node_tmp3, subsection['content'])
                    else:
                        node_tmp2 = etree.SubElement(node_tmp, 'p')
                        append_fragment(node_tmp2, subsection['content'])
                else:
                    break

        vals = [
            b
            for b in data_t
            if b.block_type == 'paragraph'
            and b.value.get('label') == '<kwd-title>'
            ]

        vals2 = [
            b
            for b in data_t
            if b.block_type == 'paragraph_with_language'
            and b.value.get('label') == '<kwd-group>'
            ]
        
        for i, val in enumerate(vals):
            node_tmp = etree.SubElement(node, 'kwd-group')
            node_tmp.set("{http://www.w3.org/XML/1998/namespace}lang", vals2[i].value.get('language'))

            node_tmp2 = etree.SubElement(node_tmp, 'title')
            append_fragment(node_tmp2, val.value.get('paragraph'))
            #node_tmp2.text = val.value.get('paragraph')

            for kw in vals2[i].value.get('paragraph').split(', '):
                node_tmp2 = etree.SubElement(node_tmp, 'kwd')
                append_fragment(node_tmp2, kw)
    
    countFN = 0
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
            append_fragment(node_title, d['value']['paragraph'])
            
            subsec = False

        if d['value']['label'] == '<sub-sec>':
            subsec = True
            node_sec = etree.SubElement(node, 'sec')
            node_title = etree.SubElement(node_sec, 'title')
            #if re.search(r'^\[style name="italic"\](.*?)\[/style\]$', d['value']['paragraph']):
            if re.search(r'^<italic>(.*?)</italic>$', d['value']['paragraph']):
                #sech = d['value']['paragraph'].replace('[style name="italic"]', '').replace('[/style]', '')
                sech = d['value']['paragraph']
                node_subtitle = etree.SubElement(node_title, 'italic')
                append_fragment(node_subtitle, sech)
                #node_subtitle.text = sech
            else:
                #node_title.text = d['value']['paragraph'].replace('[style name="italic"]', '<italic>').replace('[/style]', '</italic>')
                pass

        if d['value']['label'] == '<list>':
            re_search = re.search(r'list list-type="(.*?)"\]', d['value']['paragraph'])
            list_type = re_search.group(1)
            attrib={'list-type': list_type}

            if subsec:
                node_p = etree.SubElement(node_sec, 'p')
                node_list = etree.SubElement(node_p, 'list', attrib=attrib)
            else:
                node_p = etree.SubElement(node, 'p')
                node_list = etree.SubElement(node_p, 'list', attrib=attrib)

            content_list = re.search(r'\[list list-type="[^"]*"\](.*?)\[/list\]', d['value']['paragraph'], re.DOTALL)
            content_list = content_list.group(1)
            node_list_text = content_list \
                            .replace('[list-item]', '<list-item><p>') \
                            .replace('[/list-item]', '</p></list-item>')
                            #.replace('[style name="italic"]', '<italic>').replace('[/style]', '</italic>') \

            node_list_text = etree.fromstring(f"<root>{node_list_text}</root>")

            for child in node_list_text:
                node_list.append(child)
        
        if d['value']['label'] == '<table>' or d['value']['label'] == '<table-caption>':
            
            attrib={'id': d['value']['tabid']}
        
            if subsec:
                node_p = etree.SubElement(node_sec, 'p')
                node_table = etree.SubElement(node_p, 'table-wrap', attrib=attrib)
            else:
                node_p = etree.SubElement(node, 'p')
                node_table = etree.SubElement(node_p, 'table-wrap', attrib=attrib)
            
            node_label = etree.SubElement(node_table, 'label')
            append_fragment(node_label, d.get('value', {}).get('tablabel'))
            
            node_caption = etree.SubElement(node_table, 'caption')
            node_title = etree.SubElement(node_caption, 'title')
            append_fragment(node_title, d.get('value', {}).get('title'))
                
            node_table_text = d['value']['content']

            # Quitar saltos de línea y espacios extra
            node_table_text = re.sub(r"\s*\n\s*", "", node_table_text).replace('<br>','')

            # Parsear la tabla como fragmento XML/HTML
            tabla_element = etree.XML(node_table_text)

            # Insertar en el XML principal
            node_table.append(tabla_element)

            node_foot = etree.SubElement(node_p, 'table-wrap-foot')

        if d['value']['label'] == '<table-foot>':
            countFN += 1
            node_fn = etree.SubElement(node_foot, 'fn', attrib={"id":f"TFN{str(countFN)}"})
            node_fnp = etree.SubElement(node_fn, 'p')
            append_fragment(node_fnp, d['value']['paragraph'])

        if d['value']['label'] == '<fig>':
            
            attrib={'id': d['value']['figid']}
        
            if subsec:
                node_p = etree.SubElement(node_sec, 'p')
                node_fig = etree.SubElement(node_p, 'fig', attrib=attrib)
            else:
                node_p = etree.SubElement(node, 'p')
                node_fig = etree.SubElement(node_p, 'fig', attrib=attrib)

            etree.SubElement(node_fig, 'label').text = d['value']['figlabel']
            node_caption = etree.SubElement(node_fig, 'caption')
            etree.SubElement(node_caption, 'title').text = d['value']['title'] if 'title' in d['value'] else None 

            Image = get_image_model()
            image_id = d['value']['image']
            image_obj = Image.objects.get(pk=image_id)
            file_name = os.path.basename(image_obj.file.name)
            original_url = image_obj.get_rendition('original').url
            original_filename = os.path.basename(urlparse(original_url).path)

            #node_caption = etree.SubElement(node_fig, 'graphic', attrib={'{http://www.w3.org/1999/xlink}ref': f"{d['value']['figid']}.jpeg"})
            node_caption = etree.SubElement(node_fig, 'graphic', attrib={'{http://www.w3.org/1999/xlink}href': original_filename})
        
        if d['value']['label'] == '<fig-attrib>':

            node_attrib = etree.SubElement(node_fig, 'attrib')
            append_fragment(node_attrib, d['value']['paragraph'])

        if d['value']['label'] == '<disp-formula>':
            attrib={'id': d['value']['eid']}
        
            if subsec:
                node_p = etree.SubElement(node_sec, 'p')
                node_f = etree.SubElement(node_p, 'disp-formula', attrib=attrib)
            else:
                node_p = etree.SubElement(node, 'p')
                node_f = etree.SubElement(node_p, 'disp-formula', attrib=attrib)


            for c in d['value']['content']:
                if c['type'] == 'text':
                    node_t = etree.SubElement(node_f, 'label')
                    append_fragment(node_t, c['value'])
                if c['type'] == 'formula':
                    append_fragment(node_f, c['value'])
        
        if d['value']['label'] == '<inline-formula>':
            attrib={'id': d['value']['eid']}
        
            if subsec:
                node_p = etree.SubElement(node_sec, 'p')
            else:
                node_p = etree.SubElement(node, 'p')

            content = ''
            for c in d['value']['content']:
                if c['type'] == 'text':
                    content += c['value']
                if c['type'] == 'formula':
                    node_f = etree.Element('inline-formula', attrib=attrib)
                    append_fragment(node_f, c['value'])
                    content += etree.tostring(node_f, pretty_print=True, encoding="unicode")
                    
            append_fragment(node_p, content)

        if d['value']['label'] == '<p>':
            if subsec:
                node_p = etree.SubElement(node_sec, 'p')
            else:
                node_p = etree.SubElement(node, 'p')

            #refs = extraer_citas_apa(d['value']['paragraph'].replace('[style name="italic"]', '').replace('[/style]', ''), data_back)
            #refs = extraer_citas_apa(d['value']['paragraph'].replace('<italic>', '').replace('</italic>', ''), data_back)
            if 'xref' not in d['value']['paragraph']:
                refs = proccess_labeled_text(d['value']['paragraph'], data_back)
                for r in refs:
                    #print(f"r in refs: {r}")
                    d['value']['paragraph'] = d['value']['paragraph'].replace(r['cita'], f"<xref ref-type=\"bibr\" rid=\"{r['refid']}\">{r['cita']}</xref>")
                    """
                    if 'et al' in r['cita']:
                        et_al_replace = r['cita'].replace('et al', '<italic>et al</italic>')
                        d['value']['paragraph'] = d['value']['paragraph'].replace(et_al_replace, f"<xref reftype=\"bibr\" rid=\"{r['refid']}\">{et_al_replace}</xref>")
                    else:
                        #print(r['cita'])
                        d['value']['paragraph'] = d['value']['paragraph'].replace(r['cita'], f"<xref reftype=\"bibr\" rid=\"{r['refid']}\">{r['cita']}</xref>")
                    """

                elements = proccess_special_content(d['value']['paragraph'], data)
                for e in elements:
                    d['value']['paragraph'] = d['value']['paragraph'].replace(e['label'], f"<xref ref-type=\"{e['reftype']}\" rid=\"{e['id']}\">{e['label']}</xref>")

            append_fragment(node_p, d['value']['paragraph'])

            #if re.search(r'^\[style name="italic"\](.*?)\[/style\]$', d['value']['paragraph']):
            #if re.search(r'^<italic>(.*?)</italic>$', d['value']['paragraph']):
            #    node_title.text = ''
                #ph = d['value']['paragraph'].replace('<italic>', '').replace('</italic>', '')
                #node_subtitle = etree.SubElement(node_title, 'italic')
                #node_subtitle.text = ph
                #node_subtitle = etree.fromstring(f"<root>{d['value']['paragraph']}</root>")
                #for child in node_subtitle:
                #    node_title.append(child)
            #else:
                #node_p.text = d['value']['paragraph'].replace('[style name="italic"]', '<italic>').replace('[/style]', '</italic>')
                #p_text = d['value']['paragraph'].replace('[style name="italic"]', '<italic>').replace('[/style]', '</italic>')
             #   append_fragment(node_p, d['value']['paragraph'])
                #node_p.text = d['value']['paragraph'].replace('[style name="italic"]', '<italic>').replace('[/style]', '</italic>')
                #p_text = d['value']['paragraph']
                #try:
                    #node_text = etree.fromstring(f"<root>{p_text}</root>")
                    #for child in node_text:
                        #node_p.append(child)
                #except Exception as e:
                    #print(p_text)
                    #print(e)
        
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

                    #if re.search(r'^\[style name="italic"\](.*?)\[/style\]$', val['value']):
                    if re.search(r'^<italic>(.*?)</italic>$', val['value']):
                        node_title.text = ''
                        #ph = val['value'].replace('[style name="italic"]', '').replace('[/style]', '')
                        ph = val['value']
                        node_subtitle = etree.fromstring(f"<root>{ph}</root>")
                        for child in node_subtitle:
                            node_title.append(child)
                    else:
                        #p_text += val['value'].replace('[style name="italic"]', '<italic>').replace('[/style]', '</italic>').replace('xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math"', '')
                        p_text += val['value'].replace('xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math"', '')

            node_text = etree.fromstring(f"<root><disp-formula>{p_text}</disp-formula></root>")
            for child in node_text:
                node_p.append(child)
            
    for i, d in enumerate(data_back):
        if d['value']['label'] == '<sec>':
            node_tit = etree.SubElement(node_reflist, 'title')
            append_fragment(node_tit, d['value']['paragraph'])
        if d['value']['label'] == '<p>':
            values = d['value']
            node_ref = etree.SubElement(node_reflist, 'ref', attrib={"id": values['refid']})
            #node_label = etree.SubElement(node_ref, 'label')
            #append_fragment(node_label, values['refid'].replace('B', ''))
            node_mix = etree.SubElement(node_ref, 'mixed-citation')
            append_fragment(node_mix, values['paragraph'])

            if values['reftype'] == 'journal':
                node_elem = etree.SubElement(node_ref, 'element-citation', attrib={"publication-type": values['reftype']})
                node_person = etree.SubElement(node_elem, 'person-group', attrib={"person-group-type": "author"})
                for a in values['authors']:
                    node_name = etree.SubElement(node_person, 'name')
                    node_sname = etree.SubElement(node_name, 'surname')
                    node_gname = etree.SubElement(node_name, 'given-names')
                    append_fragment(node_sname, a['value']['surname'])
                    append_fragment(node_gname, a['value']['given_names'])

                append_fragment(etree.SubElement(node_ref, 'article-title'), values['title'])
                append_fragment(etree.SubElement(node_ref, 'source'), values['source'])
                append_fragment(etree.SubElement(node_ref, 'year'), str(values['date']))
                append_fragment(etree.SubElement(node_ref, 'volume'), str(values['vol']))
                append_fragment(etree.SubElement(node_ref, 'issue'), str(values['issue']))
                
                if values['fpage'] and values['fpage'][0] == 'e':
                    append_fragment(etree.SubElement(node_ref, 'elocation-id'), values['fpage'])
                else:
                    append_fragment(etree.SubElement(node_ref, 'fpage'), str(values['fpage']))
                    append_fragment(etree.SubElement(node_ref, 'lpage'), str(values['lpage']))

                append_fragment(etree.SubElement(node_ref, 'pub-id', attrib={"pub-id-type": "doi"}), values['doi'])

                if values['uri']:
                    append_fragment(etree.SubElement(node_ref, 'ext-link', 
                        attrib={
                            "ext-link-type": "uri",
                            "{http://www.w3.org/1999/xlink}href": values['uri']
                        }),
                        values['uri'])
            
            if values['reftype'] == 'book':
                node_elem = etree.SubElement(node_ref, 'element-citation', attrib={"publication-type": values['reftype']})
                node_person = etree.SubElement(node_elem, 'person-group', attrib={"person-group-type": "author"})
                for a in values['authors']:
                    node_name = etree.SubElement(node_person, 'name')
                    node_sname = etree.SubElement(node_name, 'surname')
                    node_gname = etree.SubElement(node_name, 'given-names')
                    append_fragment(node_sname, a['value']['surname'])
                    append_fragment(node_gname, a['value']['given_names'])

                append_fragment(etree.SubElement(node_ref, 'part-title'), values['chapter'])
                append_fragment(etree.SubElement(node_ref, 'source'), values['source'])
                append_fragment(etree.SubElement(node_ref, 'edition'), values['edition'])
                append_fragment(etree.SubElement(node_ref, 'publisher-loc'), values['location'])
                append_fragment(etree.SubElement(node_ref, 'publisher-name'), values['organization'])
                append_fragment(etree.SubElement(node_ref, 'year'), str(values['date']))
                append_fragment(etree.SubElement(node_ref, 'fpage'), str(values['fpage']))
                append_fragment(etree.SubElement(node_ref, 'lpage'), str(values['lpage']))
            

            if values['reftype'] == 'data':
                node_elem = etree.SubElement(node_ref, 'element-citation', attrib={"publication-type": values['reftype']})
                node_person = etree.SubElement(node_elem, 'person-group', attrib={"person-group-type": "author"})
                for a in values['authors']:
                    node_name = etree.SubElement(node_person, 'name')
                    node_sname = etree.SubElement(node_name, 'surname')
                    node_gname = etree.SubElement(node_name, 'given-names')
                    append_fragment(node_sname, a['value']['surname'])
                    append_fragment(node_gname, a['value']['given_names'])

                append_fragment(etree.SubElement(node_ref, 'data-title'), values['title'])
                append_fragment(etree.SubElement(node_ref, 'version'), values['version'])
                append_fragment(etree.SubElement(node_ref, 'year'), str(values['date']))
                append_fragment(etree.SubElement(node_ref, 'source'), values['source'])
                append_fragment(etree.SubElement(node_ref, 'pub-id', attrib={"pub-id-type": "doi"}), values['doi'])
                append_fragment(etree.SubElement(node_ref, 'ext-link', 
                    attrib={
                        "ext-link-type": "uri",
                        "{http://www.w3.org/1999/xlink}href": values['uri']
                    }),
                    values['uri'])
            
            if values['reftype'] == 'webpage':
                node_elem = etree.SubElement(node_ref, 'element-citation', attrib={"publication-type": values['reftype']})
                node_person = etree.SubElement(node_elem, 'person-group', attrib={"person-group-type": "author"})
                for a in values['authors']:
                    node_name = etree.SubElement(node_person, 'name')
                    node_sname = etree.SubElement(node_name, 'surname')
                    node_gname = etree.SubElement(node_name, 'given-names')
                    append_fragment(node_sname, a['value']['surname'])
                    append_fragment(node_gname, a['value']['given_names'])

                append_fragment(etree.SubElement(node_ref, 'source'), values['source'])
                append_fragment(etree.SubElement(node_ref, 'ext-link', 
                    attrib={
                        "ext-link-type": "uri",
                        "{http://www.w3.org/1999/xlink}href": values['uri']
                    }),
                    values['uri'])
                append_fragment(etree.SubElement(node_ref, 'access-date'), values['access_date'])

            if values['reftype'] == 'confproc':
                node_elem = etree.SubElement(node_ref, 'element-citation', attrib={"publication-type": values['reftype']})
                node_person = etree.SubElement(node_elem, 'person-group', attrib={"person-group-type": "author"})
                for a in values['authors']:
                    node_name = etree.SubElement(node_person, 'name')
                    node_sname = etree.SubElement(node_name, 'surname')
                    node_gname = etree.SubElement(node_name, 'given-names')
                    append_fragment(node_sname, a['value']['surname'])
                    append_fragment(node_gname, a['value']['given_names'])

                append_fragment(etree.SubElement(node_ref, 'source'), values['source'])
                append_fragment(etree.SubElement(node_ref, 'conf-name'), values['title'])
                append_fragment(etree.SubElement(node_ref, 'conf-num'), str(values['issue']))
                append_fragment(etree.SubElement(node_ref, 'conf-date'), str(values['date']))
                append_fragment(etree.SubElement(node_ref, 'conf-loc'), values['location'])
                append_fragment(etree.SubElement(node_ref, 'publisher-loc'), values['org_location'])
                append_fragment(etree.SubElement(node_ref, 'publisher-name'), values['organization'])
                append_fragment(etree.SubElement(node_ref, 'page'), values['pages'])

            if values['reftype'] == 'thesis':
                node_elem = etree.SubElement(node_ref, 'element-citation', attrib={"publication-type": values['reftype']})
                node_person = etree.SubElement(node_elem, 'person-group', attrib={"person-group-type": "author"})
                for a in values['authors']:
                    node_name = etree.SubElement(node_person, 'name')
                    node_sname = etree.SubElement(node_name, 'surname')
                    node_gname = etree.SubElement(node_name, 'given-names')
                    append_fragment(node_sname, a['value']['surname'])
                    append_fragment(node_gname, a['value']['given_names'])

                append_fragment(etree.SubElement(node_ref, 'source'), values['source'])
                append_fragment(etree.SubElement(node_ref, 'publisher-loc'), values['org_location'])
                append_fragment(etree.SubElement(node_ref, 'publisher-name'), values['organization'])
                append_fragment(etree.SubElement(node_ref, 'year'), str(values['date']))
                append_fragment(etree.SubElement(node_ref, 'page'), values['pages'])

    # Convertir a una cadena XML
    xml_como_texto = etree.tostring(root, pretty_print=True, encoding="unicode")

    return xml_como_texto, data