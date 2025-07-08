from lxml import etree
import re, html


def buscar_refid_por_surname_y_date(data_back, surname_buscado, date_buscado):
    print(surname_buscado)
    print(date_buscado)
    """
    Busca un bloque RefParagraphBlock que contenga un author con el surname especificado
    y que coincida con la fecha dada. Retorna el refid si encuentra una coincidencia.
    """
    for bloque in data_back:  # Reemplaza 'contenido' con el nombre de tu StreamField
        if bloque['type'] == 'ref_paragraph':  # o el nombre que usaste en el StreamField
            data = bloque['value']

            # Verificar la fecha
            if str(data.get('date')) != str(date_buscado):
                continue

            # Revisar autores
            authors = data.get('authors', [])

            if ' y ' in surname_buscado or ' and ' in surname_buscado or ' & ' in surname_buscado:
                if ' y ' in surname_buscado:
                    surname1 = surname_buscado.split(' y ')[0].strip()
                    surname2 = surname_buscado.split(' y ')[1].strip()
                
                if ' and ' in surname_buscado:
                    surname1 = surname_buscado.split(' and ')[0].strip()
                    surname2 = surname_buscado.split(' and ')[1].strip()

                if ' & ' in surname_buscado:
                    surname1 = surname_buscado.split(' & ')[0].strip()
                    surname2 = surname_buscado.split(' & ')[1].strip()

                for author_bloque in authors:
                    if author_bloque['type'] == 'Author':
                        author_data = author_bloque['value']
                        if author_data.get('surname') == surname1:
                            for author_bloque2 in authors:
                                if author_bloque2['type'] == 'Author':
                                    author_data = author_bloque2['value']
                                    if author_data.get('surname') == surname2:
                                        return data.get('refid')

            for author_bloque in authors:
                if author_bloque['type'] == 'Author':
                    author_data = author_bloque['value']
                    print(author_data.get('surname'))
                    if author_data.get('surname') == surname_buscado:
                        print('***'+data.get('refid'))
                        return data.get('refid')

    return None


def extraer_citas_apa(texto, data_back):
    """
    Extrae citas en formato APA dentro de un texto y devuelve:
    - la cita completa,
    - el primer autor,
    - el año.
    Acepta múltiples espacios entre palabras y símbolos.
    """
    
    # Preposiciones comunes en apellidos
    preposiciones = r'(?:de|del|la|los|las|da|do|dos|das|van|von)'

    # Apellido compuesto o con preposición
    apellido = rf'[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(?:[-\s]+(?:{preposiciones})?\s*[A-ZÁÉÍÓÚÑ]?[a-záéíóúñ]+)*'

    # Citas fuera de paréntesis
    patron_afuera = rf'\b(?P<autor>{apellido})(?:\s+(?:et\s+al\s*\.|(y|and|&)\s+{apellido}))?\s*\(\s*(?P<anio>\d{{4}}[a-z]?)\s*\)'
    
    # Citas dentro de paréntesis
    patron_adentro = rf'\(\s*(?P<autor>{apellido})(?:\s+(?:et\s+al\s*\.|(y|and|&)\s+{apellido}))?\s*,\s*(?P<anio>\d{{4}}[a-z]?)\s*\)'

    patron_adentro_multiples = rf'\b(?P<autor>{apellido})(?:\s+(?:et\s+al\s*\.|(y|and|&)\s+{apellido}))?\s*,\s*(?P<anio>\d{{4}}[a-z]?)'

    resultados = []

    # 1. Identificar paréntesis con múltiples citas separadas por ";"
    for paren in re.finditer(r'\(([^)]+;[^)]+)\)', texto):  # si hay punto y coma dentro del paréntesis
        contenido = paren.group(1)
        partes = [parte.strip() for parte in contenido.split(';')]
        for parte in partes:
            match = re.match(patron_adentro_multiples, parte, re.VERBOSE)
            if match:
                autor = match.group("autor")
                anio = match.group("anio")
                refid = buscar_refid_por_surname_y_date(data_back, autor, anio)
                resultados.append({
                    "cita": f"{parte}",  # reconstruir la cita individual
                    "autor": autor,
                    "anio": anio,
                    "refid": refid
                })

    for match in re.finditer(patron_afuera, texto):
        refid = buscar_refid_por_surname_y_date(data_back, match.group("autor"), match.group("anio"))
        resultados.append({
            "cita": match.group(0),
            "autor": match.group("autor"),
            "anio": match.group("anio"),
            "refid": refid
        })

    for match in re.finditer(patron_adentro, texto):
        refid = buscar_refid_por_surname_y_date(data_back, match.group("autor"), match.group("anio"))
        resultados.append({
            "cita": match.group(0),
            "autor": match.group("autor"),
            "anio": match.group("anio"),
            "refid": refid
        })

    return resultados


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
                                '{http://www.w3.org/XML/1998/namespace}lang': 'en'}
                                #'{http://www.w3.org/1998/Math/MathML}mml': 'http://www.w3.org/1998/Math/MathML',
                                #'{http://www.w3.org/1999/xlink}xlink': 'http://www.w3.org/1999/xlink'}
                        )

    # Añadir un elemento hijo
    front = etree.SubElement(root, "front")
    body = etree.SubElement(root, "body")
    subsec = None
    num_table = 1
    continue_t = False

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
            
            if 'paragraph' in d['value']:
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

            #node_table_text = node_table_text.replace('<br>','&#10;')
            node_table_text = html.escape(node_table_text)

            node_table_text = etree.fromstring(f"<root>{node_table_text}</root>")

            for child in node_table_text:
                node_table.append(child)

            num_table = num_table + 1

        
        if d['value']['label'] == '<p>':
            if subsec:
                node_p = etree.SubElement(node_sec, 'p')
            else:
                node_p = etree.SubElement(node, 'p')

            refs = extraer_citas_apa(d['value']['paragraph'].replace('[style name="italic"]', '').replace('[/style]', ''), data_back)
            for r in refs:
                if 'et al' in r['cita']:
                    et_al_replace = r['cita'].replace('et al', '[style name="italic"]et al[/style]')
                    d['value']['paragraph'] = d['value']['paragraph'].replace(et_al_replace, f"<xref reftype=\"bibr\" rid=\"{r['refid']}\">{et_al_replace}</xref>")
                else:
                    d['value']['paragraph'] = d['value']['paragraph'].replace(r['cita'], f"<xref reftype=\"bibr\" rid=\"{r['refid']}\">{r['cita']}</xref>")
                                

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
                try:
                    node_text = etree.fromstring(f"<root>{p_text}</root>")
                    for child in node_text:
                        node_p.append(child)
                except:
                    print(p_text)
        
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