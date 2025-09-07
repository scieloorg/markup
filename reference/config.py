import json

MESSAGES = [
        {   'role': 'system',
            'content': 'You are an assistant who distinguishes all the components of a citation in an article with output in JSON'
        },
        {   'role': 'user',
            'content': 'Bachman, S., J. Moat, A. W. Hill, J. de la Torre and B. Scott. 2011. Supporting Red List threat assessments with GeoCAT: geospatial conservation assessment tool. ZooKeys 150: 117-126. DOI: https://doi.org/10.3897/zookeys.150.2109'
        },
        {   'role': 'assistant',
            'content': json.dumps({
                    'reftype': 'journal',
                    'authors':  [
                        {   'surname': 'Bachman', 'fname': 'S.' },
                        {   'surname': 'Moat', 'fname': 'J.' },
                        {   'surname': 'Hill', 'fname': 'A. W.' },
                        {   'surname': 'de la Torre', 'fname': 'J.' },
                        {   'surname': 'Scott', 'fname': 'B.' },
                    ],
                    'full_text': 'Bachman, S., J. Moat, A. W. Hill, J. de la Torre and B. Scott. 2011. Supporting Red List threat assessments with GeoCAT: geospatial conservation assessment tool. ZooKeys 150: 117-126. DOI: https://doi.org/10.3897/zookeys.150.2109',
                    'date': 2011,
                    'title': 'Supporting Red List threat assessments with GeoCAT: geospatial conservation assessment tool',
                    'source': 'ZooKeys',
                    'vol': '150',
                    'num': None,
                    'fpage': '117',
                    'lpage': '126',
                    'doi': '10.3897/zookeys.150.2109',
            })
        },
        {   'role': 'user',
            'content': 'Brunel, J. F. 1987. Sur le genre Phyllanthus L. et quelques genres voisins de la Tribu des Phyllantheae Dumort. (Euphorbiaceae, Phyllantheae) en Afrique intertropicale et à Madagascar. Thèse de doctorat de l’Université L. Pasteur. Strasbourg, France. 760 pp.'
        },
        {   'role': 'assistant',
            'content': json.dumps({
                    'reftype': 'Thesis',
                    'authors':  [
                        {   'surname': 'Brunel', 'fname': 'J. F.' },
                    ],
                    'full_text': 'Brunel, J. F. 1987. Sur le genre Phyllanthus L. et quelques genres voisins de la Tribu des Phyllantheae Dumort. (Euphorbiaceae, Phyllantheae) en Afrique intertropicale et à Madagascar. Thèse de doctorat de l’Université L. Pasteur. Strasbourg, France. 760 pp.',
                    'date': 1987,
                    'source': 'Sur le genre Phyllanthus L. et quelques genres voisins de la Tribu des Phyllantheae Dumort. (Euphorbiaceae, Phyllantheae) en Afrique intertropicale et à Madagascar',
                    'degree': 'doctorat',
                    'organization': 'l’Université L. Pasteur',
                    'city': 'Strasbourg',
                    'location': 'Strasbourg, France',
                    'num_pages': 760
            }),
        },
        {
            'role': 'user',
            'content': 'Hernández-López, L. 1995. The endemic flora of Jalisco, Mexico: Centers of endemism and implications for conservation. Tesis de maestría. Universidad de Wisconsin. Madison, USA. 74 pp.'
        },
        {   'role': 'assistant',
            'content': json.dumps({
                    'reftype': 'Thesis',
                    'authors':  [
                        {   'surname': 'Hernández-López', 'fname': 'L.' },
                    ],
                    'full_text': 'Hernández-López, L. 1995. The endemic flora of Jalisco, Mexico: Centers of endemism and implications for conservation. Tesis de maestría. Universidad de Wisconsin. Madison, USA. 74 pp.',
                    'date': 1995,
                    'source': 'The endemic flora of Jalisco, Mexico: Centers of endemism and implications for conservation',
                    'degree': 'maestría',
                    'organization': 'Universidad de Wisconsin',
                    'location': 'Madison, USA',
                    'num_pages': 74
            }),
        },
        {
            'role': 'user',
            'content': 'Schimper, A. F. W. 1903. Plant geography upon a physiological basis. Clarendon Press. Oxford, UK. 839 pp.'
        },
        {
            'role': 'assistant',
            'content': json.dumps({
                'reftype': 'book',
                'authors':[
                    {   'surname': 'Schimper', 'fname': 'A. F. W.' },
                ],
                'full_text': 'Schimper, A. F. W. 1903. Plant geography upon a physiological basis. Clarendon Press. Oxford, UK. 839 pp.',
                'date': 1903,
                'source': 'Plant geography upon a physiological basis',
                'organization': 'Clarendon Press',
                'location': 'Oxford, UK',
                'num_pages': 839
            })
        },
        {
            'role': 'user',
            'content': 'Correa, M. D., C. Galdames and M. Stapf. 2004. Catálogo de Plantas Vasculares de Panamá. Smithsonian Tropical Research Institute. Ciudad de Panamá, Panamá. 599 pp.'
        },
        {
            'role': 'assistant',
            'content': json.dumps({
                'reftype': 'book',
                'authors':[
                    {   'surname': 'Correa', 'fname': 'M. D.' },
                    {   'surname': 'Galdames', 'fname': 'C.' },
                    {   'surname': 'Stapf', 'fname': 'M.' },
                ],
                'full_text': 'Correa, M. D., C. Galdames and M. Stapf. 2004. Catálogo de Plantas Vasculares de Panamá. Smithsonian Tropical Research Institute. Ciudad de Panamá, Panamá. 599 pp.',
                'date': 2004,
                'source': 'Catálogo de Plantas Vasculares de Panamá',
                'organization': 'Smithsonian Tropical Research Institute',
                'location': 'Ciudad de Panamá, Panamá',
                'num_pages': 599
            })
        },
        {
            'role': 'user',
            'content': 'Hernández-López, L. 2019. Las especies endémicas de plantas en el estado de Jalisco: su distribución y conservación. Comisión Nacional para el Conocimiento y Uso de la Biodiversidad (CONABIO). Cd. Mx., México. https://doi.org/10.15468/ktvqds (consultado diciembre de 2019).'
        },
        {
            'role': 'assistant',
            'content': json.dumps({
                'reftype': 'data',
                'authors':[
                    {   'surname': 'Hernández-López', 'fname': 'L.' },
                ],
                'full_text': 'Hernández-López, L. 2019. Las especies endémicas de plantas en el estado de Jalisco: su distribución y conservación. Comisión Nacional para el Conocimiento y Uso de la Biodiversidad (CONABIO). Cd. Mx., México. https://doi.org/10.15468/ktvqds (consultado diciembre de 2019).',
                'date': 2019,
                'title': 'Las especies endémicas de plantas en el estado de Jalisco: su distribución y conservación',
                'source': 'Comisión Nacional para el Conocimiento y Uso de la Biodiversidad (CONABIO)',
                'location': 'Cd. Mx. México',
                'doi': '10.15468/ktvqds',
                'access_date': 'diciembre de 2019'
            })
        },
        {
            'role': 'user',
            'content': 'INAFED. 2010. Enciclopedia de los Municipios y Delegaciones de México: Jalisco. Instituto Nacional para el Federalismo y el Desarrollo Municipal. http://www.inafed.gob.mx/ work/enciclopedia/EMM21puebla/index.html (consultado diciembre de 2018).'
        },
        {
            'role': 'assistant',
            'content': json.dumps({
                'reftype': 'webpage',
                'authors':[
                    {   'collab': 'INAFED' },
                ],
                'full_text': 'INAFED. 2010. Enciclopedia de los Municipios y Delegaciones de México: Jalisco. Instituto Nacional para el Federalismo y el Desarrollo Municipal. http://www.inafed.gob.mx/ work/enciclopedia/EMM21puebla/index.html (consultado diciembre de 2018).',
                'date': 2010,
                'source': 'Enciclopedia de los Municipios y Delegaciones de México: Jalisco',
                'organization': 'Instituto Nacional para el Federalismo y el Desarrollo Municipal',
                'uri': 'http://www.inafed.gob.mx/ work/enciclopedia/EMM21puebla/index.html',
                'access_date': 'diciembre de 2018'
            })
        },
        {
            'role': 'user',
            'content': 'Nikon Corporation. 1991-2006. NIS- Elements, version 2.33. Tokio, Japón.'
        },
        {
            'role': 'assistant',
            'content': json.dumps({
                'reftype': 'software',
                'authors':[
                    {   'collab': 'Nikon Corporation' },
                ],
                'full_text': 'Nikon Corporation. 1991-2006. NIS- Elements, version 2.33. Tokio, Japón.',
                'date': 2006,
                'source': 'NIS- Elements',
                'version': '2.33',
                'city': 'Tokio',
                'country': 'Japón',
            })
        },
        {
            'role': 'user',
            'content': 'Furton EJ, Dort V, editors. Addiction and compulsive behaviors. Proceedings of the 17th Workshop for Bishops; 1999; Dallas, TX. Boston: National Catholic Bioethics Center (US); 2000. 258 p.'
        },
        {
            'role': 'assistant',
            'content': json.dumps({
                    'reftype': 'confproc',
                    'full_text': 'Furton EJ, Dort V, editors. Addiction and compulsive behaviors. Proceedings of the 17th Workshop for Bishops; 1999; Dallas, TX. Boston: National Catholic Bioethics Center (US); 2000. 258 p.',
                    'authors':[
                        {   'surname': 'Furton', 'fname': 'EJ' },
                        {   'surname': 'Dort', 'fname': 'V' },
                    ],
                    'date': 2000,
                    'source': 'Addiction and compulsive behaviors',
                    'title': 'Proceedings of the 17th Workshop for Bishops',
                    'location': 'Dallas, TX',
                    'num': '17',
                    'organization': 'National Catholic Bioethics Center (US)',
                    'org_location': 'Boston',
                    'pages': '258 p'
            })
        },
        ]

RESPONSE_FORMAT = {
        'type': 'json_object',
        'schema':{
            'type': 'object',
            'properties': {
                'reftype': {'type': 'string', 'enum': ['journal', 'thesis', 'book', 'data', 'webpage', 'software', 'confproc']},
                'authors': {'type': 'array',
                            'items': {
                                        'type': 'object',
                                        'properties': {
                                            'surname': {'type': 'string'},
                                            'fname': {'type': 'string'},
                                            'collab': {'type': 'string'}
                                        }
                                }
                            },
                "full_text": {"type": "integer"},
                "date": {"type": "integer"},
                "title": {"type": "string"},
                "chapter": {"type": "string"},
                "edition": {"type": "string"},
                "source": {"type": "string"},
                "vol": {"type": "integer"},
                "num": {"type": "integer"},
                "pages": {"type": "string"},
                "fpage": {"type": "string"},
                "lpage": {"type": "string"},
                "doi": {"type": "string"},
                "degree": {"type": "string"},
                "organization": {"type": "string"},
                "location": {"type": "string"},
                "org_location": {"type": "string"},
                "num_pages": {"type": "integer"},
                "uri": {"type": "string"},
                "access_id": {"type": "string"},
                "access_date": {"type": "string"},
                "version": {"type": "string"},
            },
        }
        }