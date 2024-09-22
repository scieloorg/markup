import docx
from docx.oxml.table import CT_Tbl
from docx.oxml.text.paragraph import CT_P
from docx.oxml.ns import qn
from lxml import etree, objectify
from wagtail.images import get_image_model
from django.core.files.base import ContentFile

ImageModel = get_image_model()


class functionsDocx:

    def openDocx(filename):
        doc = docx.Document(filename)
        return doc


    def extractContent(doc):

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

        for element in doc.element.body:            
            if isinstance(element, CT_P):
                obj = {}

                namespaces = {
                    'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
                    'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
                }

                obj_image = False

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

                if not obj_image:
                    paragraph = element
                    obj['text'] = paragraph.text

                    for run in paragraph.findall('.//w:r', namespaces=paragraph.nsmap):
                        sz_element = run.find('.//w:sz', namespaces=run.nsmap)
                        if sz_element is not None:
                            xml_string = etree.tostring(sz_element, pretty_print=True, encoding='unicode')
                            namespaces = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'

                            size_element = objectify.fromstring(xml_string)
                            font_size_value = size_element.get(namespaces+'val')


                            color_element = run.find('.//w:color', namespaces=run.nsmap)
                            if color_element is not None:
                                xml_string_color = etree.tostring(color_element, pretty_print=True, encoding='unicode')
                                object_element = objectify.fromstring(xml_string_color)
                                color_value = object_element.get(namespaces + 'val')
                                obj['color'] = color_value

                            obj['font_size'] = int(font_size_value)/2
                            obj['bold'] = run.find('.//w:b', namespaces=run.nsmap) is not None
                            obj['italic'] = run.find('.//w:i', namespaces=run.nsmap) is not None
            
            elif isinstance(element, CT_Tbl):
                table = element
                table_data = extrae_Tabla(element)
                obj = {}
                obj['type'] = 'table'
                obj['table'] = table_data
                
            
            content.append(obj)

        return content
