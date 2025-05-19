import docx
from docx.oxml.table import CT_Tbl
from docx.oxml.text.paragraph import CT_P
from docx.oxml.ns import qn
from lxml import etree, objectify
from wagtail.images import get_image_model
from django.core.files.base import ContentFile
import zipfile
import os

ImageModel = get_image_model()


class functionsDocx:

    def openDocx(filename):
        doc = docx.Document(filename)
        return doc

    # Función: solo reemplaza mfenced que NO tengan atributos open/close y que usen |
    def replace_mfenced_pipe_only(self, mathml_root):
        mml_ns = "http://www.w3.org/1998/Math/MathML"
        for mfenced in mathml_root.xpath(".//mml:mfenced", namespaces={"mml": mml_ns}):
            has_open = mfenced.get("open")
            has_close = mfenced.get("close")
            separators = mfenced.get("separators", "")

            # Solo reemplazar si: no tiene open/close y usa barra
            if not has_open and not has_close and separators == "|":
                mrow = etree.Element(f"{{{mml_ns}}}mrow")

                mo_open = etree.Element(f"{{{mml_ns}}}mo")
                mo_open.text = "("
                mo_close = etree.Element(f"{{{mml_ns}}}mo")
                mo_close.text = ")"

                mrow.append(mo_open)
                for child in list(mfenced):
                    mrow.append(child)
                mrow.append(mo_close)

                parent = mfenced.getparent()
                if parent is not None:
                    parent.replace(mfenced, mrow)


    def extract_numbering_info(self, docx_path):
        # Diccionario para mapear numId a su tipo (numerada o viñeta)
        numbering_map = {}
        namespaces = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'

        # Abrir el archivo DOCX como un archivo ZIP
        with zipfile.ZipFile(docx_path, 'r') as docx:
            # Verificar si existe el archivo numbering.xml
            if 'word/numbering.xml' in docx.namelist():
                # Extraer el archivo numbering.xml
                numbering_xml = docx.read('word/numbering.xml')
                # Parsear el XML
                numbering_tree = etree.fromstring(numbering_xml)

                # Buscar todas las definiciones abstractas de numeración
                for abstract_num in numbering_tree.findall('.//w:abstractNum', namespaces=numbering_tree.nsmap):
                    abstract_num_id = abstract_num.get(namespaces+'abstractNumId')
                    # Revisar los niveles dentro de la definición abstracta
                    for lvl in abstract_num.findall('.//w:lvl', namespaces=abstract_num.nsmap):
                        num_fmt = lvl.find('.//w:numFmt', lvl.nsmap).get(namespaces+'val')
                        ilvl = lvl.get(namespaces+'ilvl')

                        # Asignar el tipo según el valor de numFmt
                        if abstract_num_id not in numbering_map:
                            numbering_map[abstract_num_id] = {}

                        numbering_map[abstract_num_id][ilvl] = num_fmt

                # Relacionar numId con su abstractNumId
                for num in numbering_tree.findall('.//w:num', namespaces=numbering_tree.nsmap):
                    num_id = num.get(namespaces+'numId')
                    abstract_num_id = num.find('.//w:abstractNumId', namespaces=num.nsmap).get(namespaces+'val')
                    if abstract_num_id in numbering_map:
                        numbering_map[abstract_num_id]['numId'] = num_id
            else:
                numbering_map = None

        return numbering_map


    def extractContent(self, doc, doc_path):

        list_types = self.extract_numbering_info(doc_path)

        # Obtener el directorio actual del archivo .py
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))

        # Construir la ruta completa al archivo XSLT
        xslt_path = os.path.join(BASE_DIR, "omml2mml.xsl")

        # Cargar XSLT y prepararlo
        xslt = etree.parse(xslt_path)
        transform = etree.XSLT(xslt)

        def extrae_Tabla(element):
            # Inicializa la estructura HTML de la tabla
            html = "<table border='1'>\n"

            # Almacena las combinaciones para las celdas
            rowspan_dict = {}  # {(row, col): rowspan_count}
            colspan_dict = {}  # {(row, col): colspan_count}

            # Itera sobre las filas de la tabla
            for i, row in enumerate(element.xpath('.//w:tr')):
                html += "  <tr>\n"
                # Itera sobre las celdas de cada fila
                j = 0  # índice de columna
                for cell in row.xpath('.//w:tc'):
                    # Revisa si la celda está en una posición afectada por rowspan
                    while (i, j) in rowspan_dict and rowspan_dict[(i, j)] > 0:
                        # Reduce el contador de rowspan
                        rowspan_dict[(i, j)] -= 1
                        j += 1  # Mueve a la siguiente columna

                    # Revisa las propiedades de la celda para rowspan y colspan
                    cell_props = cell.xpath('.//w:tcPr')
                    rowspan = 1
                    colspan = 1

                    # Procesa rowspan (vMerge)
                    v_merge_fin = False
                    v_merge = cell.xpath('.//w:vMerge')
                    if v_merge:
                        v_merge_val = v_merge[0].get(qn('w:val'))
                        if v_merge_val == "restart":
                            # Es el inicio de una combinación vertical
                            rowspan = 1
                            # Busca el total de filas combinadas contando hacia abajo
                            k = i + 1
                            while k < len(element.xpath('.//w:tr')):
                                next_cell = element.xpath('.//w:tr')[k].xpath('.//w:tc')[j]
                                next_merge = next_cell.xpath('.//w:tcPr//w:vMerge')
                                if next_merge and next_merge[0].get(qn('w:val')) is None:
                                    rowspan += 1
                                else:
                                    break
                                k += 1

                            for k in range(rowspan):
                                rowspan_dict[(i + k, j)] = rowspan - k - 1
                        else:
                            v_merge_fin = True

                    # Procesa colspan (gridSpan)
                    grid_span = cell.xpath('.//w:gridSpan')
                    if grid_span:
                        colspan = int(grid_span[0].get(qn('w:val')))
                        for k in range(colspan):
                            colspan_dict[(i, j + k)] = colspan - k - 1

                    if not v_merge_fin:
                        # Obtén el contenido del texto de la celda
                        cell_text = "<br>".join([t.text for t in cell.xpath('.//w:t')])

                        # Determina el tag a usar (th para el encabezado, td para celdas normales)
                        tag = "th" if i == 0 else "td"

                        # Construye la celda en HTML
                        cell_html = f"    <{tag}"
                        if rowspan > 1:
                            cell_html += f' rowspan="{rowspan}"'
                        if colspan > 1:
                            cell_html += f' colspan="{colspan}"'
                        cell_html += f">{cell_text}</{tag}>\n"

                        html += cell_html
                    j += 1 + (colspan - 1)  # Avanza las columnas tomando en cuenta el colspan

                html += "  </tr>\n"

            html += "</table>"
            return html

        content = []
        images = []

        current_list = []
        current_num_id = None
        numId = None
        namespaces_p = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
        for element in doc.element.body:            
            if isinstance(element, CT_P):
                obj = {}

                namespaces = {
                    'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
                    'a': 'http://schemas.openxmlformats.org/drawingml/2006/main'
                }

                obj_image = False
                obj_formula = False

                for drawing in element.findall('.//w:drawing', namespaces=namespaces):
                    if drawing.find('.//a:blip', namespaces=namespaces) is not None:
                        blip = drawing.find('.//a:blip', namespaces=namespaces)
                        if blip is not None:
                            obj_image = True

                            rId = blip.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed')
                            image_part = doc.part.related_parts[rId]
                            image_data = image_part.blob
                            image_name = image_part.partname.split('/')[-1]
                            
                            if image_name not in images:
                                images.append(image_name)

                                # Guardar la imagen en Wagtail
                                wagtail_image = ImageModel.objects.create(
                                    title=image_name,
                                    file=ContentFile(image_data, name=image_name)
                                )
                                
                                # Referenciar la imagen guardada en el objeto
                                obj['type'] = 'image'
                                obj['image'] = wagtail_image.id
                
                
                ns_math = {
                    'm': 'http://schemas.openxmlformats.org/officeDocument/2006/math',
                    'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
                }

                for formula in element.findall('.//m:oMathPara', namespaces=ns_math):
                    obj_formula = True
                    mathml_result = transform(formula)
                    mathml_root = etree.fromstring(str(mathml_result))
                    self.replace_mfenced_pipe_only(mathml_root)
                    obj['type'] = 'formula'
                    obj['formula'] = etree.tostring(mathml_root, pretty_print=True, encoding='unicode')
                
                
                if not obj_image:
                    paragraph = element
                    text_paragraph = []

                    # Determina si es parte de una lista
                    is_numPr = paragraph.find('.//w:numPr', namespaces=paragraph.nsmap) is not None

                    # obtiene id y nivel
                    if is_numPr:
                        numPr = paragraph.find('.//w:numPr', namespaces=paragraph.nsmap)
                        numId = numPr.find('.//w:numId', namespaces=paragraph.nsmap).get(namespaces_p + 'val')
                        type = [(key, objt) for key, objt in list_types.items() if objt['numId'] == numId]

                        #Es una lista diferente
                        if numId != current_num_id:
                            current_num_id = numId
                            if len(current_list) > 0:
                                current_list.append('[/list]')
                                objl = {}
                                objl['type'] = 'list'
                                objl['list'] = '\n'.join(current_list)
                                current_list = []
                                content.append(objl)
                            list_type = 'bullet'
                            if type[0][1][str(0)] == 'decimal':
                                list_type = 'order'

                            current_list.append(f'[list list-type="{list_type}"]')
                    else:
                        #Se terminaron de agregar elementos a la lista
                        if len(current_list) > 0:
                            current_list.append('[/list]')
                            objl = {}
                            objl['type'] = 'list'
                            objl['list'] = '\n'.join(current_list)
                            current_list = []
                            content.append(objl)

                    for child in paragraph:
                        if child.tag == '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}r':
                            sz_element = child.find('.//w:sz', namespaces=child.nsmap)
                            if sz_element is not None:
                                xml_string = etree.tostring(sz_element, pretty_print=True, encoding='unicode')
                                namespaces = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'

                                size_element = objectify.fromstring(xml_string)
                                font_size_value = size_element.get(namespaces+'val')


                                color_element = child.find('.//w:color', namespaces=child.nsmap)
                                if color_element is not None:
                                    xml_string_color = etree.tostring(color_element, pretty_print=True, encoding='unicode')
                                    object_element = objectify.fromstring(xml_string_color)
                                    color_value = object_element.get(namespaces + 'val')
                                    obj['color'] = color_value

                                obj['font_size'] = int(font_size_value)/2
                                obj['bold'] = child.find('.//w:b', namespaces=child.nsmap) is not None
                                obj['italic'] = child.find('.//w:i', namespaces=child.nsmap) is not None
                                if obj['italic']:
                                    text_paragraph.append('[style name="italic"]' + child.text + '[/style]')
                                else:
                                    text_paragraph.append(child.text)

                        if child.tag == f"{{{ns_math['m']}}}oMath":
                            if 'text' not in obj or not isinstance(obj['text'], list):
                                obj['type'] = 'compound'
                                obj['text'] = []
                            if len(text_paragraph) > 0:
                                obj2 = {}
                                obj2['type'] = 'text'
                                obj2['value'] = ' '.join(text_paragraph)
                                obj['text'].append(obj2)
                                text_paragraph = []

                            mathml_result = transform(child)
                            mathml_root = etree.fromstring(str(mathml_result))
                            self.replace_mfenced_pipe_only(mathml_root)
                            obj2 = {}
                            obj2['type'] = 'formula'
                            obj2['value'] = etree.tostring(mathml_root, pretty_print=True, encoding='unicode')
                            obj['text'].append(obj2)

                    if 'text' not in obj:    
                        obj['text'] = ' '.join(text_paragraph)

                        if is_numPr:
                            if 'font_size' in obj:
                                del obj['font_size']
                            current_list.append(f'[list-item]{obj["text"]}[/list-item]')
            
            elif isinstance(element, CT_Tbl):
                table = element
                table_data = extrae_Tabla(element)
                obj = {}
                obj['type'] = 'table'
                obj['table'] = table_data
                
            
            content.append(obj)

        return content
