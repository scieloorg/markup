from config import celery_app
from reference.marker import mark_references
from reference.models import Reference, ElementCitation, ReferenceStatus
import json
from lxml import etree
import re

meses = {
    "enero": "01", "febrero": "02", "marzo": "03", "abril": "04", "mayo": "05", "junio": "06",
    "julio": "07", "agosto": "08", "septiembre": "09", "octubre": "10", "noviembre": "11", "diciembre": "12",
    "january": "01", "february": "02", "march": "03", "april": "04", "may": "05", "june": "06",
    "july": "07", "august": "08", "september": "09", "october": "10", "november": "11", "december": "12",
    "janeiro": "01", "fevereiro": "02", "março": "03", "abril": "04", "maio": "05", "junho": "06",
    "julho": "07", "agosto": "08", "setembro": "09", "outubro": "10", "novembro": "11", "dezembro": "12"
}

def get_number_of_month(texto):
    texto = texto.lower()
    for mes, numero in meses.items():
        if re.search(rf"\b{mes}\b", texto):
            return numero
    return None  # Si no encuentra un mes

def get_xml(json_reference):
    json_reference = json.loads(json_reference)
    root = etree.Element('element-citation',
                           attrib = {
                               'publication-type': json_reference['reftype'],
                           })
    
    if json_reference['reftype'] in ['webpage', 'data']:
        NSMAP = {'xlink': 'http://www.w3.org/1999/xlink'}
        root = etree.Element('element-citation',
                        attrib = {
                            'publication-type': json_reference['reftype'],
                        },nsmap=NSMAP)
  
    if 'authors' in json_reference:
        person_group = etree.SubElement(root, "person-group",
                                           attrib = {
                                               'person-group-type': 'author',
                                           }
                                       )
        for author in json_reference['authors']:
            name = etree.Element('name')
            if 'fname' in author:
                etree.SubElement(name, 'surname').text = author['fname']
            if 'surname' in author:
                etree.SubElement(name, 'given-names').text = author['surname']
            if 'collab' in author:
                etree.SubElement(name, 'collab').text = author['collab']
            person_group.append(name)

    if json_reference['reftype'] == 'journal':
        if 'title' in json_reference:
            etree.SubElement(root, 'article-title').text = json_reference['title']
        if 'source' in json_reference:
            etree.SubElement(root, 'source').text = json_reference['source']
        if 'vol' in json_reference:
            etree.SubElement(root, 'volume').text = str(json_reference['vol'])
        if 'num' in json_reference:
            etree.SubElement(root, 'issue').text = str(json_reference['num'])
        if 'pages' in json_reference and len(str(json_reference['pages']).split('-')) > 0:
            etree.SubElement(root, 'fpage').text = str(json_reference['pages']).split('-')[0].strip()
        if 'pages' in json_reference and len(str(json_reference['pages']).split('-')) > 1:
            etree.SubElement(root, 'lpage').text = str(json_reference['pages']).split('-')[1].strip()
        if 'doi' in json_reference:
            etree.SubElement(root, 'doi', attrib = { 'pub-id-type': 'doi' }).text = json_reference['doi']

    if json_reference['reftype'] == 'thesis':
        if 'title' in json_reference:
            etree.SubElement(root, 'source').text = json_reference['title']
        if 'degree' in json_reference:
            etree.SubElement(root, 'comment', attrib = { 'content-type': 'degree' }).text = json_reference['degree']
        if 'organization' in json_reference:
            etree.SubElement(root, 'publisher-name').text = json_reference['organization']
  
    if json_reference['reftype'] in ['webpage', 'data']:
        if 'title' in json_reference:
            etree.SubElement(root, 'source').text = json_reference['title']
        if 'uri' in json_reference:
            etree.SubElement(root, 'ext-link', attrib = {
                                               'ext-link-type': 'uri',
                                               '{http://www.w3.org/1999/xlink}href': json_reference['uri']
                                                }).text = json_reference['uri']
        if 'organization' in json_reference:
            etree.SubElement(root, 'publisher-name').text = json_reference['organization']
        if 'country' in json_reference:
            etree.SubElement(root, 'publisher-loc').text = json_reference['country']
        if 'doi' in json_reference:
            etree.SubElement(root, 'doi', attrib = { 'pub-id-type': 'doi' }).text = json_reference['doi']
        if 'access_date' in json_reference:
            match = re.search(r'\b\d{4}\b', json_reference['access_date'])
            year = match.group()
            month = get_number_of_month(json_reference['access_date'])
            etree.SubElement(root, 'date-in-citation', attrib = { 
                                                        'content-type': 'access-date',
                                                        'iso-8601-date': year+'-'+month+'-00'
                                                         }).text = json_reference['access_date']

    if 'date' in json_reference:
        etree.SubElement(root, 'year').text = str(json_reference['date'])


    return root
  

#@celery_app.task()
def get_reference(obj_id):
   obj_reference = Reference.objects.get(id=obj_id)
   marked = mark_references(obj_reference.mixed_citation)
   for item in marked:
       for i in item['choices']:
           ElementCitation.objects.create(
               reference=obj_reference,
               marked=i,
               marked_xml=etree.tostring(get_xml(i), pretty_print=True, encoding='unicode')
           )
   obj_reference.estatus = ReferenceStatus.READY
   obj_reference.save()
