MESSAGES = [
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
            'content': 'Hernández-López, L. 1995. The endemic flora of Jalisco, Mexico: Centers of endemism and implications for conservation. Tesis de maestría. Universidad de Wisconsin. Madison, USA. 74 pp.'
        },
        {   'role': 'assistant',
            'content': {
                    'reftype': 'Thesis',
                    'authors':  [
                        {   'surname': 'Hernández-López', 'fname': 'L.' },
                    ],
                    'date': 1995,
                    'title': 'The endemic flora of Jalisco, Mexico: Centers of endemism and implications for conservation',
                    'degree': 'maestría',
                    'organization': 'Universidad de Wisconsin',
                    'city': 'Madison',
                    'country': 'USA',
                    'num_pages': 74
            },
        },
        {
            'role': 'user',
            'content': 'Schimper, A. F. W. 1903. Plant geography upon a physiological basis. Clarendon Press. Oxford, UK. 839 pp.'
        },
        {
            'role': 'assistant',
            'content': {
                'reftype': 'book',
                'authors':[
                    {   'surname': 'Schimper', 'fname': 'A. F. W.' },
                ],
                'date': 1903,
                'title': 'Plant geography upon a physiological basis',
                'organization': 'Clarendon Press',
                'city': 'Oxford',
                'country': 'UK',
                'num_pages': 839
            }
        },
        {
            'role': 'user',
            'content': 'Correa, M. D., C. Galdames and M. Stapf. 2004. Catálogo de Plantas Vasculares de Panamá. Smithsonian Tropical Research Institute. Ciudad de Panamá, Panamá. 599 pp.'
        },
        {
            'role': 'assistant',
            'content': {
                'reftype': 'book',
                'authors':[
                    {   'surname': 'Correa', 'fname': 'M. D.' },
                    {   'surname': 'Galdames', 'fname': 'C.' },
                    {   'surname': 'Stapf', 'fname': 'M.' },
                ],
                'date': 2004,
                'title': 'Catálogo de Plantas Vasculares de Panamá',
                'organization': 'Smithsonian Tropical Research Institute',
                'city': 'Ciudad de Panamá',
                'country': 'Panamá',
                'num_pages': 599
            }
        },
        {
            'role': 'user',
            'content': 'Hernández-López, L. 2019. Las especies endémicas de plantas en el estado de Jalisco: su distribución y conservación. Comisión Nacional para el Conocimiento y Uso de la Biodiversidad (CONABIO). Cd. Mx., México. https://doi.org/10.15468/ktvqds (consultado diciembre de 2019).'
        },
        {
            'role': 'assistant',
            'content': {
                'reftype': 'data',
                'authors':[
                    {   'surname': 'Hernández-López', 'fname': 'L.' },
                ],
                'date': 2019,
                'title': 'Las especies endémicas de plantas en el estado de Jalisco: su distribución y conservación',
                'organization': 'Comisión Nacional para el Conocimiento y Uso de la Biodiversidad (CONABIO)',
                'city': 'Cd. Mx.',
                'country': 'México',
                'doi': '10.15468/ktvqds',
                'access_date': 'diciembre de 2019'
            }
        },
        {
            'role': 'user',
            'content': 'INAFED. 2010. Enciclopedia de los Municipios y Delegaciones de México: Jalisco. Instituto Nacional para el Federalismo y el Desarrollo Municipal. http://www.inafed.gob.mx/ work/enciclopedia/EMM21puebla/index.html (consultado diciembre de 2018).'
        },
        {
            'role': 'assistant',
            'content': {
                'reftype': 'webpage',
                'authors':[
                    {   'collab': 'INAFED' },
                ],
                'date': 2010,
                'title': 'Enciclopedia de los Municipios y Delegaciones de México: Jalisco',
                'organization': 'Instituto Nacional para el Federalismo y el Desarrollo Municipal',
                'uri': 'http://www.inafed.gob.mx/ work/enciclopedia/EMM21puebla/index.html',
                'access_date': 'diciembre de 2018'
            }
        },
        {
            'role': 'user',
            'content': 'Nikon Corporation. 1991-2006. NIS- Elements, version 2.33. Tokio, Japón.'
        },
        {
            'role': 'assistant',
            'content': {
                'reftype': 'software',
                'authors':[
                    {   'collab': 'Nikon Corporation' },
                ],
                'date': 2006,
                'source': 'NIS- Elements',
                'version': '2.33',
                'city': 'Tokio',
                'country': 'Japón',
            }
        },
        ]

RESPONSE_FORMAT = {
        'type': 'json_object',
        'schema':{
            'type': 'object',
            'properties': {
                'reftype': {'type': 'string', 'enum': ['journal', 'thesis', 'book', 'data', 'webpage', 'software']},
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
                'uri': {'type': 'string'},
                'access_date': {'type': 'string'},
                'version': {'type': 'string'},
            },
            'required':{
                'journal': ['reftype', 'authors', 'date', 'title', 'source', 'vol', 'num', 'pages', 'doi'],
                'thesis': ['reftype', 'authors', 'date', 'title', 'degree', 'organization', 'city', 'country', 'num_pages'],
                'book': ['reftype', 'authors', 'date', 'title', 'organization', 'city', 'country', 'num_pages'],
                'data': ['reftype', 'authors', 'date', 'title', 'organization', 'city', 'country', 'num_pages', 'doi', 'access_date'],
                'webpage': ['reftype', 'authors', 'date', 'title', 'organization', 'uri', 'access_date'],
                'software': ['reftype', 'authors', 'date', 'source', 'version', 'city', 'country']
            }
        }
        }