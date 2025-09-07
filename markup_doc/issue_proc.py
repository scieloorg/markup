from lxml import etree
from urllib.parse import urlparse
from packtools.sps.pid_provider.xml_sps_lib import get_xml_with_pre
import os


class Asset:
    def __init__(self, wagtail_image):
        self.file = wagtail_image.file  # tiene .path (ruta absoluta)
        self.original_href = wagtail_image.file.name  # nombre en el storage


class XmlIssueProc:
    def __init__(self, registro):
        self.registro = registro
        self.xmltree = self._extract_xml_tree()
        self.journal_proc = self._extract_journal_proc()
        self.issue_folder = self._extract_issue_folder()
    
    def _extract_xml_tree(self):
        return get_xml_with_pre(self.registro.text_xml).xmltree

    def _extract_journal_proc(self):
        acron = self.xmltree.findtext(".//journal-id[@journal-id-type='publisher-id']")
        return type("JournalProc", (), {"acron": acron or "journal"})

    def _get_issn(self):
        issn = self.xmltree.findtext(".//issn[@pub-type='epub']")
        if not issn:
            issn = self.xmltree.findtext(".//issn[@pub-type='ppub']")
        return issn

    def _extract_issue_folder(self, lot=None):
        issn = self._get_issn() or ""
        acron = self.journal_proc.acron or ""
        vol = (self.xmltree.findtext(".//volume") or "").strip()
        issue = (self.xmltree.findtext(".//issue") or "").strip().lower()
        year = self.xmltree.findtext(".//pub-date[@date-type='collection']/year")

        parts = [p for p in [issn, acron] if p]

        # volumen
        if vol:
            parts.append(f"v{vol}")

        # issue puede ser número, suplemento o especial
        if issue:
            if issue.startswith("suppl"):
                # suplemento de volumen → v10s2
                parts[-1] = parts[-1] + f"s{issue.replace('suppl','').strip()}"
            elif "suppl" in issue:
                # suplemento de número → v10n4s2
                tokens = issue.split()
                num = tokens[0]
                sup = tokens[1:]
                parts.append(f"n{num}")
                sup_num = "".join(sup).replace("suppl", "").strip()
                parts[-1] = parts[-1] + f"s{sup_num}"
            elif issue.startswith("spe"):
                # número especial → v10nspe1
                parts[-1] = parts[-1] + f"nspe{issue.replace('spe','').strip()}"
            else:
                # número normal → v4n10
                parts.append(f"n{issue}")

        # carpeta de publicación continua con lote
        if lot and year:
            lot_str = f"{lot:02d}{year[-2:]}"
            parts.append(lot_str)

        return "-".join(parts)

    def build_pkg_name(self, lang=None):
        issn = self._get_issn() or ""
        acron = self.journal_proc.acron or ""

        # base igual que issue_folder, pero sin el ISSN y acron aún
        vol = (self.xmltree.findtext(".//volume") or "").strip()
        issue = (self.xmltree.findtext(".//issue") or "").strip().lower()

        parts = [issn, acron]

        if vol:
            parts.append(vol)

        if issue:
            if issue.startswith("suppl"):
                # suplemento de volumen
                parts[-1] = parts[-1] + f"s{issue.replace('suppl','').strip()}"
            elif "suppl" in issue:
                # suplemento de número
                tokens = issue.split()
                num = tokens[0]
                sup = tokens[1:]
                parts.append(num)
                sup_num = "".join(sup).replace("suppl", "").strip()
                parts[-1] = parts[-1] + f"s{sup_num}"
            elif issue.startswith("spe"):
                # número especial
                parts[-1] = parts[-1] + f"nspe{issue.replace('spe','').strip()}"
            else:
                # número normal
                parts.append(issue)

        # ARTID
        elocation = self.xmltree.findtext(".//elocation-id")
        fpage = self.xmltree.findtext(".//fpage")
        pid = self.xmltree.findtext(".//article-id[@specific-use='scielo-v2']")

        if elocation:
            parts.append(elocation.strip())
        elif fpage:
            parts.append(fpage.strip())
        elif pid:
            parts.append(pid.strip())
        else:
            parts.append("na")  # fallback si no hay nada

        # idioma solo si es traducción
        if lang:
            parts.append(lang)

        return "-".join(parts)

    def find_asset(self, basename, name):
        """
        Devuelve las imágenes del StreamField como Asset
        si coinciden con el nombre puesto en el XML (original_filename)
        o con el nombre real en storage.
        """
        assets = []
        if self.registro.content_body:
            for block in self.registro.content_body:
                if block.block_type == "image" and block.value:
                    wagtail_image = block.value.get("image")
                    if not wagtail_image:
                        continue

                    # Nombre real en storage (ej: foto1.abcd1234.jpg)
                    storage_basename = os.path.basename(wagtail_image.file.name)

                    # Nombre usado en el XML (ej: foto1.jpg)
                    original_url = wagtail_image.get_rendition("original").url
                    xml_basename = os.path.basename(urlparse(original_url).path)

                    # Si coincide con cualquiera → se acepta
                    if basename in (storage_basename, xml_basename):
                        assets.append(Asset(wagtail_image))

        return assets
