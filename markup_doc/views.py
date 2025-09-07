from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest, Http404
from .models import ArticleDocxMarkup
#from .xml import extraer_citas_apa
from django.http import JsonResponse
from markup_doc.models import JournalModel
import json

import io, base64, mimetypes, os
import zipfile
from django.utils.text import slugify

from django.conf import settings
from django.views.decorators.http import require_POST
from django.contrib.staticfiles import finders

from lxml import etree, html as lxml_html
from urllib.parse import urlsplit, unquote
from django.templatetags.static import static
from markup_doc.labeling_utils import (
    proccess_labeled_text,
)
from packtools import XML, HTMLGenerator, catalogs
from packtools.htmlgenerator import get_htmlgenerator
from io import StringIO
from packtools.sps.pid_provider.xml_sps_lib import get_xml_with_pre, XMLWithPre
from .pkg_zip_builder import PkgZipBuilder
from urllib.parse import urlparse
from wagtail.images import get_image_model
from markup_doc.issue_proc import XmlIssueProc


# Create your views here.
def generate_xml(request, id_registro):
    try:
        # Obtener el registro del modelo que contiene el XML
        registro = ArticleDocxMarkup.objects.get(pk=id_registro)
       
        # Obtener el contenido XML del campo
        contenido_xml = registro.text_xml  # Ajusta esto según la estructura de tu modelo
       
        # Crear una respuesta HTTP con el tipo de contenido XML
        response = HttpResponse(contenido_xml, content_type='application/xml')
       
        # Definir el nombre del archivo para descargar
        nombre_archivo = f"document_{id_registro}.xml"
        response['Content-Disposition'] = f'attachment; filename="{nombre_archivo}"'
       
        return response
    except TuModelo.DoesNotExist:
        return HttpResponse("El registro solicitado no existe", status=404)
    except Exception as e:
        return HttpResponse(f"Error al generar el XML: {str(e)}", status=500)


def extract_citation(request):

    if request.method == "POST":
        body = json.loads(request.body)
        text = body.get("text", "")
        pk_register = body.get("pk", "")

        #print(text)
        #print(pk_register)

        # Obtener el registro del modelo que contiene el XML
        registro = ArticleDocxMarkup.objects.get(pk=pk_register)

        #result = extraer_citas_apa(text, registro.content_back.get_prep_value())  # <-- Aquí pasas el texto a tu función normal

        ref = proccess_labeled_text(text, registro.content_back.get_prep_value())
        #text = text.replace(ref[0]['cita'], f"<xref reftype=\"bibr\" rid=\"{ref[0]['refid']}\">{ref[0]['cita']}</xref>")

        return JsonResponse({"refid": ref[0]['refid']})


def get_journal(request):

    if request.method == "POST":
        body = json.loads(request.body)
        text = body.get("text", "")
        pk = body.get("pk", "")

        journal = JournalModel.objects.get(pk=pk)

    return JsonResponse({
        'journal_title': journal.title,
        'short_title': journal.short_title,
        'title_nlm': journal.title_nlm,
        'acronym': journal.acronym,
        'issn': journal.issn,
        'pissn': journal.pissn,
        'eissn': journal.eissn,
        'pubname': journal.pubname,
        # Agrega los campos que necesites
    })


def generate_zip(request):
    if request.method == "POST":
        body = json.loads(request.body)
        id_registro = body.get("pk", "")

    try:
        registro = ArticleDocxMarkup.objects.get(pk=id_registro)
    except ArticleDocxMarkup.DoesNotExist:
        raise Http404("El registro solicitado no existe")

    # Crear XMLWithPre
    contenido_xml = registro.text_xml or ""
    xml_with_pre = get_xml_with_pre(contenido_xml)

    # Crear builder
    builder = PkgZipBuilder(xml_with_pre)

    # Dummy IssueProc con imágenes
    issue_proc = XmlIssueProc(registro)

    # Construir paquete SPS
    import tempfile
    output_folder = tempfile.mkdtemp()

    zip_path = builder.build_sps_package(
        output_folder=output_folder,
        renditions=[],           # PDFs si los tienes
        translations={},         # HTML si los tienes
        main_paragraphs_lang="es",
        issue_proc=issue_proc,
    )

    # Respuesta HTTP
    with open(zip_path, "rb") as fp:
        response = HttpResponse(fp.read(), content_type="application/zip")
    response["Content-Disposition"] = f'attachment; filename="{builder.sps_pkg_name}.zip"'
    return response


def _file_to_data_uri(file_obj, name_hint="file.bin"):
    file_obj.open('rb')
    try:
        data = file_obj.read()
    finally:
        file_obj.close()
    mime, _ = mimetypes.guess_type(name_hint)
    if not mime: mime = 'application/octet-stream'
    b64 = base64.b64encode(data).decode('ascii')
    return f"data:{mime};base64,{b64}"


def _gather_images_from_streamfield(registro):
    """
    Devuelve:
      - by_figid: {figid -> (data_uri, original_basename)}
      - by_basename: {basename -> data_uri}
    """
    by_figid, by_basename = {}, {}
    if not registro.content_body:
        return by_figid, by_basename

    for block in registro.content_body:
        if block.block_type != "image" or not block.value:
            continue
        struct = block.value
        wagtail_image = struct.get("image")
        if not wagtail_image:
            continue

        # nombre original
        original_name = (wagtail_image.file.name or "").split("/")[-1] or f"image-{wagtail_image.pk}"
        data_uri = _file_to_data_uri(wagtail_image.file, original_name)

        # por basename
        by_basename[original_name] = data_uri

        # por figid si existe
        figid = (struct.get("figid") or "").strip()
        if figid:
            by_figid[figid] = (data_uri, original_name)
    return by_figid, by_basename


def ensure_utf8_meta(root):
    # 1) Asegurar estructura html/head/body
    if root.tag.lower() != 'html':
        html = html.Element('html')
        head = html.Element('head')
        body = lxml_html.Element('body')
        html.append(head); html.append(body)
        body.append(root)
        root = html
    else:
        html = root
        head = html.find('head')
        body = html.find('body')
        if head is None:
            head = lxml_html.Element('head'); html.insert(0, head)
        if body is None:
            body = lxml_html.Element('body'); html.append(body)

    # 2) Quitar metas http-equiv=Content-Type (pueden contradecir el charset)
    for m in head.xpath('meta[translate(@http-equiv,"CONTENT-TYPE","content-type")="content-type"]'):
        head.remove(m)

    # 3) Insertar (o normalizar) <meta charset="utf-8"> al principio
    metas = head.xpath('meta[@charset]')
    if metas:
        metas[0].set('charset', 'utf-8')
        head.remove(metas[0]); head.insert(0, metas[0])
    else:
        meta = lxml_html.Element('meta'); meta.set('charset', 'utf-8')
        head.insert(0, meta)

    return root


def ensure_jats_css_link(root):
    head = root.find('.//head')
    if head is None:
        head = lxml_html.Element('head'); root.insert(0, head)

    # Si el XSL ya puso un link a jats-preview.css, reescribe su href
    rewritten = False
    for link in head.xpath('link[@rel="stylesheet"]'):
        href = link.get('href', '')
        if 'jats-preview.css' in href:
            link.set('href', static('jats/jats-preview.css'))
            link.set('type', 'text/css')
            rewritten = True
            break

    # Si no había, añade uno
    if not rewritten:
        link = lxml_html.Element('link')
        link.set('rel', 'stylesheet')
        link.set('type', 'text/css')
        link.set('href', static('jats/jats-preview.css'))
        head.append(link)

    return root


def fix_img_src(html_text):
    Image = get_image_model()
    # Parsear el HTML
    doc = lxml_html.fromstring(html_text)

    # Iterar sobre todas las imágenes
    for img in doc.xpath("//img[@src]"):
        src = img.attrib.get("src")
        if not src or 'open-access' in src:
            continue

        # ejemplo: "image3_pVQTCFR.original.jpg"
        basename = os.path.basename(urlparse(src).path)

        try:
            # Buscar en la base de datos (por nombre de archivo que contenga el basename)
            #image_obj = Image.objects.filter(file__icontains=basename).first()
            image_obj = '/media/images/' + basename
            if image_obj:
                # Obtener la URL real
                #real_url = image_obj.get_rendition("original").url
                #img.attrib["src"] = real_url
                img.attrib["src"] = image_obj
        except Exception:
            # si no hay match, dejarlo como está
            pass

    # Volver a convertir a string
    return lxml_html.tostring(doc, pretty_print=True, encoding="utf-8", method="html").decode("utf-8")


def load_file_content(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def preview_html_post(request):
    # 1) pk desde JSON o formulario
    id_registro = None
    if request.content_type and request.content_type.startswith('application/json'):
        try:
            payload = json.loads(request.body.decode('utf-8'))
            id_registro = int(payload.get('pk'))
        except Exception:
            return HttpResponseBadRequest("pk inválido")
    else:
        id_registro = request.POST.get('pk')
        try:
            id_registro = int(id_registro)
        except Exception:
            return HttpResponseBadRequest("pk inválido")

    try:
        registro = ArticleDocxMarkup.objects.get(pk=id_registro)
    except ArticleDocxMarkup.DoesNotExist:
        raise Http404("Registro no existe")

    if not registro.text_xml or not registro.text_xml.strip():
        return HttpResponse("<h1>Sin XML</h1>", content_type="text/html; charset=utf-8")

    try:
        xml_content = registro.text_xml 
        xml_filelike = StringIO(xml_content)

        parsed_xml = XML(xml_filelike, no_network=True)

        """
        generator = HTMLGenerator.parse(
            parsed_xml,
            valid_only=False,
            output_style="website",
            xslt="3.0"
        )"""

        bootstrap_css = """
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.0-beta1/dist/css/bootstrap.min.css" rel="stylesheet">
        """

        bootstrap_js = """
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.0.0-beta1/dist/js/bootstrap.bundle.min.js"></script>
        """

        print("css:", catalogs.HTML_GEN_DEFAULT_CSS_PATH)
        print("print_css:", catalogs.HTML_GEN_DEFAULT_PRINT_CSS_PATH)
        print("bootstrap_css:", catalogs.HTML_GEN_BOOTSTRAP_CSS_PATH)
        print("article_css:", catalogs.HTML_GEN_ARTICLE_CSS_PATH)
        print("js:", catalogs.HTML_GEN_DEFAULT_JS_PATH)

        # Cargar CSS/JS desde packtools
        css_main = load_file_content(catalogs.HTML_GEN_DEFAULT_CSS_PATH)
        css_print = load_file_content(catalogs.HTML_GEN_DEFAULT_PRINT_CSS_PATH)
        js_main = load_file_content(catalogs.HTML_GEN_DEFAULT_JS_PATH)

        link_css = f"""
        
        <link href=!--"{catalogs.HTML_GEN_ARTICLE_CSS_PATH}" rel="stylesheet"-->
        <link href="{catalogs.HTML_GEN_BOOTSTRAP_CSS_PATH}" rel="stylesheet">
        <!--link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.0-beta1/dist/css/bootstrap.min.css" rel="stylesheet-->
        """

        link_js = f"""
        <!--script src="https://cdn.jsdelivr.net/npm/mathjax@3.0.0/es5/tex-mml-svg.js"></script-->
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.0.0-beta1/dist/js/bootstrap.bundle.min.js"></script>
        """

        #link_css = f"""
        #    <link href="{static('css/article.css')}" rel="stylesheet">
        #    <link href="{static('css/bootstrap.min.css')}" rel="stylesheet">
        #"""

        #link_js = f"""
        #    <script src="{static('js/scielo-bundle-min.js')}"></script>
        #"""

        generator = HTMLGenerator.parse(
            xml_filelike,
            valid_only=False,
            css=catalogs.HTML_GEN_DEFAULT_CSS_PATH,
            print_css=catalogs.HTML_GEN_DEFAULT_PRINT_CSS_PATH,
            js=catalogs.HTML_GEN_DEFAULT_JS_PATH,
            math_elem_preference="mml:math",
            math_js="https://cdn.jsdelivr.net/npm/mathjax@3.0.0/es5/tex-mml-svg.js",
            permlink="",
            url_article_page="",
            url_download_ris="",
            gs_abstract=False,
            output_style="website",
            xslt="3.0",
            bootstrap_css=catalogs.HTML_GEN_BOOTSTRAP_CSS_PATH,
            article_css=catalogs.HTML_GEN_ARTICLE_CSS_PATH,
            design_system_static_img_path=None,
        )

        template = """<!DOCTYPE html>
        <html lang="es">
        <head>
        <meta charset="UTF-8">
        <title>Artículo</title>

        {css}

        <!-- Estilos -->
        <style>
        {css_main}
        </style>

        <style media="print">
        {css_print}
        </style>

        </head>
        <body>
        {content}

        <!-- Scripts -->
        <script>
        {js_main}
        </script>

        {js}
        </body>
        </html>"""

        has_output = False
        for lang, trans_result in generator:
            has_output = True
            html_text = etree.tostring(
                trans_result,
                pretty_print=True,
                encoding="utf-8",
                method="html",
                doctype="<!DOCTYPE html>"
            ).decode("utf-8")

            # corregir las imágenes
            html_text = fix_img_src(html_text)

            # insertar el fragmento dentro de la plantilla
            html_text = template.format(
                                        css_main="",
                                        css_print="",
                                        css=link_css, 
                                        js=link_js,
                                        js_main="",
                                        content=html_text
                                        )

        # 3) Postprocesado: meta, css, imágenes
        root = lxml_html.fromstring(html_text)
        root = ensure_utf8_meta(root)
        root = ensure_jats_css_link(root)

        by_figid, _by_basename = _gather_images_from_streamfield(registro)
        href_to_datauri = {
            f"{fid}.jpeg".lower(): data_uri
            for fid, (data_uri, _orig) in by_figid.items() if fid
        }

        for img in root.xpath('//img[@src]'):
            src = img.get('src', '')
            if src.startswith('data:'):
                continue
            base = unquote(os.path.basename(urlsplit(src).path)).lower()
            data_uri = href_to_datauri.get(base)
            if data_uri:
                img.set('src', data_uri)
            else:
                img.set('src', settings.MEDIA_URL + base)

        final_html = lxml_html.tostring(
            root,
            encoding='unicode',
            method='html',
            doctype='<!DOCTYPE html>',
            pretty_print=True
        )

        return HttpResponse(html_text, content_type="text/html; charset=utf-8")

    except Exception as exc:
        return HttpResponse(
            f"<h1>Error al generar HTML</h1><pre>{exc}</pre>",
            content_type="text/html; charset=utf-8"
        )


def xml_to_collapsible_html(xml_string):
    try:
        root = etree.fromstring(xml_string.encode("utf-8"))
    except Exception as e:
        return f"<pre>Error al parsear XML: {e}</pre>"

    def render_node(node):
        # Construir apertura con atributos coloreados
        attrs = ""
        for k, v in node.attrib.items():
            attrs += f' <span class="attr">{k}</span>="<span class="value">{v}</span>"'

        # Ej: <tag attr="valor">
        tag_open = f"&lt;<span class='tag'>{node.tag}</span>{attrs}&gt;"

        # Texto dentro del nodo
        text_html = ""
        if (node.text or "").strip():
            text_html = f"<div class='text'>{node.text.strip()}</div>"

        # Renderizar hijos recursivamente
        children_html = "".join(render_node(child) for child in node)

        # Nodo hoja (sin texto ni hijos)
        if not children_html and not text_html:
            return f"<div>{tag_open}&lt;/<span class='tag'>{node.tag}</span>&gt;</div>"

        # Nodo con contenido
        return f"""
        <details open>
          <summary>{tag_open}</summary>
          {text_html}
          {children_html}
          <div>&lt;/<span class='tag'>{node.tag}</span>&gt;</div>
        </details>
        """

    return render_node(root)


def preview_xml_tree(request):
    # 1) pk desde JSON o formulario
    id_registro = None
    if request.content_type and request.content_type.startswith('application/json'):
        try:
            payload = json.loads(request.body.decode('utf-8'))
            id_registro = int(payload.get('pk'))
        except Exception:
            return HttpResponseBadRequest("pk inválido")
    else:
        id_registro = request.POST.get('pk')
        try:
            id_registro = int(id_registro)
        except Exception:
            return HttpResponseBadRequest("pk inválido")

    try:
        registro = ArticleDocxMarkup.objects.get(pk=id_registro)
    except ArticleDocxMarkup.DoesNotExist:
        raise Http404("Registro no existe")

    xml_string = registro.text_xml or ""
    if not xml_string.strip():
        return HttpResponse("<h1>Sin XML</h1>", content_type="text/html; charset=utf-8")

    collapsible_html = xml_to_collapsible_html(xml_string)

    final_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <style>
        body {{
          font-family: monospace;
          background: #1e1e1e;
          color: #ffffff;
          padding: 1em;
        }}
        details {{
          margin-left: 1em;
        }}
        summary::marker {{
          color: #888;
        }}
        .tag {{
          color: #569CD6; /* azul etiquetas */
        }}
        .attr {{
          color: #D69D85; /* naranja atributos */
        }}
        .value {{
          color: #CE9178; /* rojo/marrón claro valores */
        }}
        .text {{
          color: #D4D4D4; /* gris claro texto */
          margin-left: 1em;
        }}
      </style>
    </head>
    <body>
      <h2 style="color:#ccc;">Collapsible XML view</h2>
      {collapsible_html}
    </body>
    </html>
    """

    return HttpResponse(final_html, content_type="text/html; charset=utf-8")