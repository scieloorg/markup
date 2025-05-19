from llama_cpp import Llama
import os

class functionsLlama:

    def getReference(text_reference):
        current_file_path = os.path.abspath(__file__)
        current_directory = os.path.dirname(current_file_path)
        print(current_directory)
        llm = Llama(model_path="/app/markuplib/llama-3.2/llama-3.2-3b-instruct-q4_k_m.gguf")

        messages = [
        {   'role': 'system',
            'content': 'You are an assistant who distinguishes all the components of a citation in an article with output in JSON'
        },
        {   'role': 'user',
            'content': 'Bachman, S., J. Moat, A. W. Hill, J. de la Torre and B. Scott. 2011. Supporting Red List threat assessments with GeoCAT: geospatial conservation assessment tool. ZooKeys 150: 117-126. DOI: https://doi.org/10.3897/zookeys.150.2109'
        },
        {   'role': 'assistant',
            'content': {
                    'reftype': 'journal',
                    'authors':  [
                        {   'surname': 'Bachman', 'fname': 'S.' },
                        {   'surname': 'Moat', 'fname': 'J.' },
                        {   'surname': 'Hill', 'fname': 'A. W.' },
                        {   'surname': 'de la Torre', 'fname': 'J.' },
                        {   'surname': 'Scott', 'fname': 'B.' },
                    ],
                    'date': 2011,
                    'title': 'Supporting Red List threat assessments with GeoCAT: geospatial conservation assessment tool',
                    'source': 'ZooKeys',
                    'vol': '150',
                    'num': None,
                    'pages': '117-126',
                    'doi': '10.3897/zookeys.150.2109',
            }
        },
        {   'role': 'user',
            #'content': 'Bouman, R. W., P. J. A. Keβler, I. R. H. Telford, J. J. Bruhl and P. C. Van Welzen. 2018. Subgeneric delimitation of the plant genus Phyllanthus (Phyllanthaceae). Blumea 63(2): 167-198. DOI: https://doi.org/10.3767/blumea.2018.63.02.14'
            'content': 'Brunel, J. F. 1987. Sur le genre Phyllanthus L. et quelques genres voisins de la Tribu des Phyllantheae Dumort. (Euphorbiaceae, Phyllantheae) en Afrique intertropicale et à Madagascar. Thèse de doctorat de l’Université L. Pasteur. Strasbourg, France. 760 pp.'
        },
        {   'role': 'assistant',
            'content': {
                    'reftype': 'Thesis',
                    'authors':  [
                        {   'surname': 'Brunel', 'fname': 'J. F.' },
                    ],
                    'date': 1987,
                    'title': 'Sur le genre Phyllanthus L. et quelques genres voisins de la Tribu des Phyllantheae Dumort. (Euphorbiaceae, Phyllantheae) en Afrique intertropicale et à Madagascar',
                    'degree': 'doctorat',
                    'organization': 'l’Université L. Pasteur',
                    'city': 'Strasbourg',
                    'country': 'France',
                    'num_pages': 760
            },
        },
        {
            'role': 'user',
            #'content': 'Mejía Ruiz, Patricia, 2018, "Usos sociales de la muerte celebrando la vida. Un acercamiento antropológico a los rituales de muerte entre los yaquis de Sonora", Proyecto capitular de tesis de doctorado, El Colegio de Michoacán (doctorado en Ciencias Sociales en el Área de Estudios Rurales).'
            #'content': 'Díaz Roig, Mercedes, 1983, “La danza de la conquista”, Nueva Revista de Filología Hispánica, vol. 32, núm. 1, México, El Colegio de México, pp. 176-195.'
            #'content': 'Lerma Rodríguez, Enriqueta, 2013, "Cuando los chichi’ales llegan: la conceptualización de la muerte entre los yaquis", Nueva Antropología, vol. 26, núm. 79, pp. 29-47.'
            'content': text_reference
        }
        ]

        response_format={
        'type': 'json_object',
        'schema':{
            'type': 'object',
            'properties': {
                'reftype': {'type': 'string', 'enum': ['journal', 'thesis']},
                'authors': {'type': 'array',
                            'items': {
                                        'type': 'object',
                                        'properties': {
                                            'surname': {'type': 'string'},
                                            'fname': {'type': 'string'}
                                        }
                                }
                            },
                'date': {'type': 'integer'},
                'title': {'type': 'string'},
                'source': {'type': 'string'},
                'vol': {'type': 'integer'},
                'num': {'type': 'integer'},
                'pages': {'type': 'string'},
                'doi': {'type': 'string'},
                'degree': {'type': 'string'},
                'organization': {'type': 'string'},
                'city': {'type': 'string'},
                'country': {'type': 'string'},
                'num_pages': {'type': 'integer'},
            },
            'required':{
                'journal': ['reftype', 'authors', 'date', 'title', 'source', 'vol', 'num', 'pages', 'doi'],
                'thesis': ['reftype', 'authors', 'date', 'title', 'degree', 'organization', 'city', 'country', 'num_pages']
            }
        }
        }

        output = llm.create_chat_completion(messages=messages, response_format=response_format, max_tokens=4000, temperature=0.5, top_p=0.5)
        return(output['choices'][0]['message']['content'])
