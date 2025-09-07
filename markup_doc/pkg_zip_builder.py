from zipfile import ZipFile, ZIP_DEFLATED
import os, sys

from packtools.sps.models.v2.article_assets import ArticleAssets
from packtools.sps.models.article_and_subarticles import ArticleAndSubArticles

class PkgZipBuilder:
    def __init__(self, xml_with_pre):
        self.xml_with_pre = xml_with_pre
        self.sps_pkg_name = xml_with_pre.sps_pkg_name
        self.components = {}
        self.texts = {}

    def build_sps_package(
        self,
        output_folder,
        renditions,
        translations,
        main_paragraphs_lang,
        issue_proc,
    ):
        """
        A partir do XML original ou gerado a partir do HTML, e
        dos ativos digitais, todos registrados em MigratedFile,
        cria o zip com nome no padrão SPS (ISSN-ACRON-VOL-NUM-SUPPL-ARTICLE) e
        o armazena em SPSPkg.not_optimised_zip_file.
        Neste momento o XML não contém pid v3.
        """
        # gera nome de pacote padrão SPS ISSN-ACRON-VOL-NUM-SUPPL-ARTICLE

        sps_pkg_zip_path = os.path.join(output_folder, f"{self.sps_pkg_name}.zip")

        # cria pacote zip
        with ZipFile(sps_pkg_zip_path, "w", compression=ZIP_DEFLATED) as zf:

            # A partir do XML, obtém os nomes dos arquivos dos ativos digitais
            self._build_sps_package_add_assets(zf, issue_proc)

            # add renditions (pdf) to zip
            result = self._build_sps_package_add_renditions(
                zf, renditions, translations, main_paragraphs_lang
            )
            self.texts.update(result)

            # adiciona XML em zip
            self._build_sps_package_add_xml(zf)

        return sps_pkg_zip_path

    def _build_sps_package_add_renditions(
        self, zf, renditions, translations, main_paragraphs_lang
    ):
        xml = ArticleAndSubArticles(self.xml_with_pre.xmltree)
        xml_langs = []
        for item in xml.data:
            if item.get("lang"):
                xml_langs.append(item.get("lang"))

        pdf_langs = []

        for rendition in renditions:
            try:
                if rendition.lang:
                    sps_filename = f"{self.sps_pkg_name}-{rendition.lang}.pdf"
                    pdf_langs.append(rendition.lang)
                else:
                    sps_filename = f"{self.sps_pkg_name}.pdf"
                    pdf_langs.append(xml_langs[0])

                zf.write(rendition.file.path, arcname=sps_filename)

                self.components[sps_filename] = {
                    "lang": rendition.lang,
                    "legacy_uri": rendition.original_href,
                    "component_type": "rendition",
                }
            except Exception as e:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                self.components[rendition.original_name] = {
                    "failures": format_traceback(exc_traceback),
                }
        html_langs = list(translations.keys())
        try:
            if main_paragraphs_lang:
                html_langs.append(main_paragraphs_lang)
        except Exception as e:
            pass

        return {
            "xml_langs": xml_langs,
            "pdf_langs": pdf_langs,
            "html_langs": html_langs,
        }

    def _build_sps_package_add_assets(self, zf, issue_proc):
        replacements = {}
        subdir = os.path.join(
            issue_proc.journal_proc.acron,
            issue_proc.issue_folder,
        )
        xml_assets = ArticleAssets(self.xml_with_pre.xmltree)
        for xml_graphic in xml_assets.items:
            try:
                if replacements.get(xml_graphic.xlink_href):
                    continue

                basename = os.path.basename(xml_graphic.xlink_href)
                name, ext = os.path.splitext(basename)
                
                found = False

                # procura a "imagem" no contexto do "issue"
                for asset in issue_proc.find_asset(basename, name):
                    found = True
                    self._build_sps_package_add_asset(
                        zf,
                        asset,
                        xml_graphic,
                        replacements,
                    )

                if not found:
                    self.components[xml_graphic.xlink_href] = {
                        "failures": "Not found",
                    }

            except Exception as e:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                #self.components[xml_graphic.xlink_href] = {
                #    "failures": format_traceback(exc_traceback),
                #}
                print(e)
                print(exc_traceback)
        xml_assets.replace_names(replacements)

    def _build_sps_package_add_asset(
        self,
        zf,
        asset,
        xml_graphic,
        replacements,
    ):
        try:
            # obtém o nome do arquivo no padrão sps
            sps_filename = xml_graphic.name_canonical(self.sps_pkg_name)

            # indica a troca de href original para o padrão SPS
            replacements[xml_graphic.xlink_href] = sps_filename

            # adiciona arquivo ao zip
            zf.write(asset.file.path, arcname=sps_filename)

            component_type = (
                "supplementary-material"
                if xml_graphic.is_supplementary_material
                else "asset"
            )
            self.components[sps_filename] = {
                "xml_elem_id": xml_graphic.id,
                "legacy_uri": asset.original_href,
                "component_type": component_type,
            }
        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            #self.components[xml_graphic.xlink_href] = {
            #    "failures": format_traceback(exc_traceback),
            #}
            print(e)
            print(exc_traceback)

    def _build_sps_package_add_xml(self, zf):
        try:
            sps_xml_name = self.sps_pkg_name + ".xml"
            zf.writestr(sps_xml_name, self.xml_with_pre.tostring(pretty_print=True))
            self.components[sps_xml_name] = {"component_type": "xml"}
        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            #self.components[sps_xml_name] = {
                #"component_type": "xml",
                #"failures": format_traceback(exc_traceback),
            #}
            print(e)
            print(exc_traceback)
