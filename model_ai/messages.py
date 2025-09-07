import json

DOI_AND_SECTION_MESSAGES = [
            {   'role': 'system',
                'content': 'You are an assistant who distinguishes ONLY the DOI and the Section of an initial fragment of an article with output in JSON'
            },
            {   'role': 'user',
                'content': """
                                Indización automatizada de Revistas
                                DOI: 10.4025/abm.v4i8.55
                                <table border='1'>
                                <tr>
                                <th colspan="3">Edgar Durán<br>Ingeniero (Universidade Federal do Ceará – UFC)<br>Profesor del Instituto de ingeniería – IFCE<br>E-mail: isac.freitas@ifce.edu.br</th>
                                </tr>
                                <tr>
                                <td>Recibido: 22-01-2025</td>
                                <td>Aceptado: 17-05-2022</td>
                                </tr>
                                </table>
                            """
            },
            {   'role': 'assistant',
                'content': json.dumps(
                                        {
                                            "doi": "10.4025/abm.v4i8.55",
                                            "section": "",
                                        }
                )
            },
            {   'role': 'user',
                'content': """
                                10.3456/jc.4545.740
                                SECCION A
                                Estrategias de gamificación para mejorar la motivación en plataformas de aprendizaje virtual: un estudio de caso en universidades de México
                                Estratégias de gamificação para melhorar a motivação em plataformas de aprendizagem virtual: um estudo de caso em universidades do México
                                Laura Fernández Ramos* 0000-0003-2456-8721
                                Carlos Méndez Sotelo** 0000-0001-9987-3342
                                * Doctora en Sociología. Máster en Estudios de Género. Licenciada en Ciencias Políticas. Profesora titular en la Facultad de Ciencias Sociales de la Universidad de Granada, España. Coordinadora del grupo de investigación Sociedad y Cambio Social. Líneas de investigación: igualdad de género, políticas públicas y análisis de movimientos sociales. Correo electrónico: lfernandez@ugr.es
                                ** Ingeniero en Informática. Máster en Ciencia de Datos. Consultor en analítica digital en la empresa TecnoSoft Iberia. Colaborador en proyectos de innovación educativa. Líneas de investigación: inteligencia artificial aplicada, minería de datos y visualización de información. Correo electrónico: cmendez@tecnosoft.es
                            """
            },
            {   'role': 'assistant',
                'content': json.dumps(
                                        {
                                            "doi": "10.3456/jc.4545.740",
                                            "section": "SECCION A",
                                        }
                )
            },
]

DOI_AND_SECTION_FORMAT = {
        'type': 'json_object',
        'schema':{
            'type': 'object',
                'properties': {
                    'doi': {'type': 'string'},
                    'section': {'type': 'string'}
                }
            },
            'required':['doi', 'section'],
        }

AUTHOR_MESSAGES = [
            {   'role': 'system',
                'content': 'You are an assistant who distinguishes all the Authors of an initial fragment of an article with output in JSON'
            },
            {   'role': 'user',
                'content': """
                                Indización automatizada de Revistas
                                DOI: 10.4025/abm.v4i8.55
                                <table border='1'>
                                <tr>
                                <th colspan="3">Edgar Durán<br>Ingeniero (Universidade Federal do Ceará – UFC)<br>Profesor del Instituto de ingeniería – IFCE<br>E-mail: isac.freitas@ifce.edu.br</th>
                                </tr>
                                <tr>
                                <td>Recibido: 22-01-2025</td>
                                <td>Aceptado: 17-05-2022</td>
                                </tr>
                                </table>
                            """
            },
            {   'role': 'assistant',
                'content': json.dumps({
                        'authors':  [
                                        {
                                            "name": "Edgar",
                                            "surname": "Durán",
                                            "orcid": "",
                                            "aff": "1",
                                            "char": "*"
                                        }
                                    ]
                })
            },
            {   'role': 'user',
                'content': """
                                10.3456/jc.4545.740
                                SECCION A
                                Estrategias de gamificación para mejorar la motivación en plataformas de aprendizaje virtual: un estudio de caso en universidades de México
                                Estratégias de gamificação para melhorar a motivação em plataformas de aprendizagem virtual: um estudo de caso em universidades do México
                                Laura Fernández Ramos* 0000-0003-2456-8721
                                Carlos Méndez Sotelo** 0000-0001-9987-3342
                                * Doctora en Sociología. Máster en Estudios de Género. Licenciada en Ciencias Políticas. Profesora titular en la Facultad de Ciencias Sociales de la Universidad de Granada, España. Coordinadora del grupo de investigación Sociedad y Cambio Social. Líneas de investigación: igualdad de género, políticas públicas y análisis de movimientos sociales. Correo electrónico: lfernandez@ugr.es
                                ** Ingeniero en Informática. Máster en Ciencia de Datos. Consultor en analítica digital en la empresa TecnoSoft Iberia. Colaborador en proyectos de innovación educativa. Líneas de investigación: inteligencia artificial aplicada, minería de datos y visualización de información. Correo electrónico: cmendez@tecnosoft.es
                            """
            },
            {   'role': 'assistant',
                'content': json.dumps({
                        'authors':  [
                                        {
                                            "name": "Laura",
                                            "surname": "Fernández Ramos",
                                            "orcid": "0000-0003-2456-8721",
                                            "aff": "1",
                                            "char": "*"
                                        },
                                        {
                                            "name": "Carlos",
                                            "surname": "Méndez Sotelo",
                                            "orcid": "0000-0001-9987-3342",
                                            "aff": "2",
                                            "char": "**"
                                        }
                                    ]
                })
            }
]

AUTHOR_RESPONSE_FORMAT = {
        'type': 'json_object',
        'schema':{
            'type': 'object',
            'properties': {
                'authors': {'type': 'array',
                            'items': {
                                        'type': 'object',
                                        'properties': {
                                            'name': {'type': 'string'},
                                            'surname': {'type': 'string'},
                                            'orcid': {'type': 'string'},
                                            'aff': {'type': 'integer'},
                                            'char': {'type': 'string'}
                                        },
                                        'required': ['name', 'surname', 'orcid', 'aff', 'char']
                                }
                            },
            },
            'required':['authors']
        }
    }

TITLE_MESSAGES = [
            {   'role': 'system',
                'content': """
                                You are an assistant who distinguishes all Titles and their languages of an initial fragment of an article with output in JSON
                                Use 2-letter language codes (en, pt, es, etc).
                                """
            },
            {   'role': 'user',
                'content': """
                                Indización automatizada de Revistas
                                DOI: 10.4025/abm.v4i8.55
                                <table border='1'>
                                <tr>
                                <th colspan="3">Edgar Durán<br>Ingeniero (Universidade Federal do Ceará – UFC)<br>Profesor del Instituto de ingeniería – IFCE<br>E-mail: isac.freitas@ifce.edu.br</th>
                                </tr>
                                <tr>
                                <td>Recibido: 22-01-2025</td>
                                <td>Aceptado: 17-05-2022</td>
                                </tr>
                                </table>
                            """
            },
            {   'role': 'assistant',
                'content': json.dumps({
                        'art_titles':  [
                                        {
                                            "title": "Indización automatizada de Revistas",
                                            "language": "es",
                                        }
                                    ]
                })
            },
            {   'role': 'user',
                'content': """
                                10.3456/jc.4545.740
                                SECCION A
                                Estrategias de gamificación para mejorar la motivación en plataformas de aprendizaje virtual: un estudio de caso en universidades de México
                                Estratégias de gamificação para melhorar a motivação em plataformas de aprendizagem virtual: um estudo de caso em universidades do México
                                Laura Fernández Ramos* 0000-0003-2456-8721
                                Carlos Méndez Sotelo** 0000-0001-9987-3342
                                * Doctora en Sociología. Máster en Estudios de Género. Licenciada en Ciencias Políticas. Profesora titular en la Facultad de Ciencias Sociales de la Universidad de Granada, España. Coordinadora del grupo de investigación Sociedad y Cambio Social. Líneas de investigación: igualdad de género, políticas públicas y análisis de movimientos sociales. Correo electrónico: lfernandez@ugr.es
                                ** Ingeniero en Informática. Máster en Ciencia de Datos. Consultor en analítica digital en la empresa TecnoSoft Iberia. Colaborador en proyectos de innovación educativa. Líneas de investigación: inteligencia artificial aplicada, minería de datos y visualización de información. Correo electrónico: cmendez@tecnosoft.es
                            """
            },
            {   'role': 'assistant',
                'content': json.dumps({
                        'art_titles':  [
                                        {
                                            "title": "Estrategias de gamificación para mejorar la motivación en plataformas de aprendizaje virtual: un estudio de caso en universidades de México",
                                            "language": "es",
                                        },
                                        {
                                            "title": "Estratégias de gamificação para melhorar a motivação em plataformas de aprendizagem virtual: um estudo de caso em universidades do México",
                                            "language": "pt",
                                        }
                                    ]
                })
            },
]

TITLE_RESPONSE_FORMAT = {
        'type': 'json_object',
        'schema':{
            'type': 'object',
            'properties': {
                'art_titles': {'type': 'array',
                            'items': {
                                        'type': 'object',
                                        'properties': {
                                            'title': {'type': 'string'},
                                            'language': {'type': 'char(2)'},
                                        },
                                        'required':['title', 'language']
                                }
                            },
            },
            'required':['art_titles']
        }
    }

AFFILIATION_MESSAGES = [
            {   'role': 'system',
                'content': """You are an assistant who distinguishes all the metadata of Author''s Affiliations of an initial fragment of an article with output in JSON
                                Rules:
                                - Each distinct institution must be assigned a distinct "char(s)" symbol.
                                - Reuse the same "char" only if the affiliation is exactly the same institution.
                                - Use the following pattern for "char": *, **, ***, ****, etc.
                                - The "aff" field is a unique identifier (1, 2, 3...) for each distinct institution.
                                - Always include the original affiliation text in "text_aff".
                """
            },
            {   'role': 'user',
                'content': """
                                Indización automatizada de Revistas
                                DOI: 10.4025/abm.v4i8.55
                                <table border='1'>
                                <tr>
                                <th colspan="3">Edgar Durán<br>Ingeniero (Universidade Federal do Ceará – UFC)<br>Profesor del Instituto de ingeniería – IFCE<br>E-mail: isac.freitas@ifce.edu.br</th>
                                </tr>
                                <tr>
                                <td>Recibido: 22-01-2025</td>
                                <td>Aceptado: 17-05-2022</td>
                                </tr>
                                </table>
                            """
            },
            {   'role': 'assistant',
                'content': json.dumps({
                        'affiliations':  [
                                        {
                                            "aff": "1",
                                            "char": "*",
                                            "orgname": "Universidade Federal do Ceará",
                                            "orgdiv1": "Instituto de ingeniería",
                                            "orgdiv2": "",
                                            "postal": "string",
                                            "city": "",
                                            "state": "",
                                            "code_country": "",
                                            "name_country": "",
                                            "text_aff": "Ingeniero (Universidade Federal do Ceará – UFC)<br>Profesor del Instituto de ingeniería – IFCE"
                                        }
                                    ]
                })
            },
            {   'role': 'user',
                'content': """
                                10.3456/jc.4545.740
                                SECCION A
                                Estrategias de gamificación para mejorar la motivación en plataformas de aprendizaje virtual: un estudio de caso en universidades de México
                                Estratégias de gamificação para melhorar a motivação em plataformas de aprendizagem virtual: um estudo de caso em universidades do México
                                Laura Fernández Ramos* 0000-0003-2456-8721
                                Carlos Méndez Sotelo** 0000-0001-9987-3342
                                * Doctora en Sociología. Máster en Estudios de Género. Licenciada en Ciencias Políticas. Profesora titular en la Facultad de Ciencias Sociales de la Universidad de Granada, España. Coordinadora del grupo de investigación Sociedad y Cambio Social. Líneas de investigación: igualdad de género, políticas públicas y análisis de movimientos sociales. Correo electrónico: lfernandez@ugr.es
                                ** Ingeniero en Informática. Máster en Ciencia de Datos. Consultor en analítica digital en la empresa TecnoSoft Iberia. Colaborador en proyectos de innovación educativa. Líneas de investigación: inteligencia artificial aplicada, minería de datos y visualización de información. Correo electrónico: cmendez@tecnosoft.es
                            """
            },
            {   'role': 'assistant',
                'content': json.dumps({
                        'affiliations':  [
                                        {
                                            "aff": "1",
                                            "char": "*",
                                            "orgname": "Universidad de Granada",
                                            "orgdiv1": "Facultad de Ciencias Sociales",
                                            "orgdiv2": "",
                                            "postal": "",
                                            "city": "",
                                            "state": "",
                                            "code_country": "es",
                                            "name_country": "España",
                                            "text_aff": "Doctora en Sociología. Máster en Estudios de Género. Licenciada en Ciencias Políticas. Profesora titular en la Facultad de Ciencias Sociales de la Universidad de Granada, España. Coordinadora del grupo de investigación Sociedad y Cambio Social. Líneas de investigación: igualdad de género, políticas públicas y análisis de movimientos sociales"
                                        },
                                        {
                                            "aff": "2",
                                            "char": "**",
                                            "orgname": "TecnoSoft Iberia",
                                            "orgdiv1": "",
                                            "orgdiv2": "",
                                            "postal": "",
                                            "city": "",
                                            "state": "",
                                            "code_country": "",
                                            "name_country": "",
                                            "text_aff": "Ingeniero en Informática. Máster en Ciencia de Datos. Consultor en analítica digital en la empresa TecnoSoft Iberia. Colaborador en proyectos de innovación educativa. Líneas de investigación: inteligencia artificial aplicada, minería de datos y visualización de información"
                                        }
                                    ]
                })
            }
]

AFFILIATION_RESPONSE_FORMAT = {
        'type': 'json_object',
        'schema':{
            'type': 'object',
            'properties': {
                'affiliations': {'type': 'array',
                            'items': {
                                        'type': 'object',
                                        'properties': {
                                            'aff': {'type': 'integer'},
                                            'char': {'type': 'string'},
                                            'orgname': {'type': 'string'},
                                            'orgdiv1': {'type': 'string'},
                                            'orgdiv2': {'type': 'string'},
                                            'postal': {'type': 'string'},
                                            'city': {'type': 'string'},
                                            'state': {'type': 'string'},
                                            'code_country': {'type': 'string'},
                                            'name_country': {'type': 'string'},
                                            'text_aff': {'type': 'text'}
                                        },
                                        "required": [
                                            "aff", "char", "orgname", "orgdiv1", "orgdiv2",
                                            "postal", "city", "state", "code_country",
                                            "name_country", "text_aff"
                                        ]
                                }
                            },
            },
            'required': ['affiliations']
        }
    }

ALL_FIRST_BLOCK = """
    ### Instruction:
    From the provided Text, extract the specified metadata as shown in the Example.

    Specifications:
        language: Use 2-letter codes
        orgname: Name of Organization, University, Intitution or similar
        orgdiv1: Name of Departament, Division or similar
        orgdiv2: Name of Subdepartament, Subdivision or similar
        name_country: Complete name of Country
        code_country: Use 2-letter codes for Country
        state: State or province abbreviation in capital letters
        char: Characters that link the author with their affiliation
        section: If you don't specify a section, choose the word adjacent to the DOI
        text_aff: Full text block of affiliation data
        orgdiv1, orgdiv2: No street names or neighborhoods

    Notes: 
        - The text may contain bracket-style tags or markup.
        - Return the result in JSON format.
        - Return ONLY the JSON result. No explanations, notes, or formatting outside the JSON.
        - Only one JSON object must be returned.
        - If multiple values exist (e.g. multiple "section" labels), pick the most relevant or the first one.
        - Do NOT return multiple JSON objects.
        - Include all fields in object JSON even if they are empty.

    Example:
    {{
        "doi": "DOI",
        "section": "Section",
        "titles": [
            {{
            "title": "Title 1",
            "language": "Language 1"
            }},
            {{
            "title": "Title 2",
            "language": "Language 2"
            }}
        ],
        "authors": [
            {{
            "name": "First Name",
            "surname": "Last Name",
            "orcid": "ORCID",
            "aff": 1,
            "char": "*"
            }},
            {{
            "name": "First Name 2",
            "surname": "Last Name 2",
            "orcid": "ORCID",
            "aff": 2,
            "char": "**"
            }}
        ],
        "affiliations": [
            {{
            "aff": 1,
            "char": "*",
            "orgname": "Organization Name 1",
            "orgdiv1": "Department or Division 1",
            "orgdiv2": "Subdepartment or Subdivision 1",
            "postal": "Postal Code 1",
            "city": "City 1",
            "state": "ST",
            "code_country": "co",
            "name_country": "Country 1",
            "text_aff": "Block of Text Affiliation 1"
            }},
            {{
            "aff": 2,
            "char": "**",
            "orgname": "Organization Name 2",
            "orgdiv1": "Department or Division 2",
            "orgdiv2": "Subdepartment or Subdivision 2",
            "postal": "Postal Code 2",
            "city": "City 2",
            "state": "ST",
            "code_country": "co",
            "name_country": "Country 2",
            "text_aff": "Block of Text Affiliation 2"
            }}
        ]
    }}

    ### Text:
    {text}

    ### Response:
"""


instruction = """
            From the provided Text, extract the metadata and return it as a single JSON object. 

            RULES:
            1. Output MUST be ONLY one valid JSON object (no markdown, no notes).
            2. Always include ALL fields in the JSON, even if they are empty.
            3. Use arrays for "titles", "authors", and "affiliations".
            4. If there are multiple options, choose the first or most relevant.
            5. Do NOT invent data; leave empty strings if unknown.
            6. orgdiv1/orgdiv2 must be departments or divisions (no street names).
            7. language must use 2-letter codes.
            8. country must include full name and 2-letter code.
            9. section: if not specified, use the word next to the DOI.
            10. Keep "char" consistent between authors and affiliations.

            OUTPUT FORMAT (strictly follow this):
            {
            "doi": "string",
            "section": "string",
            "titles": [
                {"title": "string", "language": "xx"}
            ],
            "authors": [
                {"name": "string", "surname": "string", "orcid": "string", "aff": number, "char": "string"}
            ],
            "affiliations": [
                {
                "aff": number,
                "char": "string",
                "orgname": "string",
                "orgdiv1": "string",
                "orgdiv2": "string",
                "postal": "string",
                "city": "string",
                "state": "string",
                "code_country": "xx",
                "name_country": "string",
                "text_aff": "string"
                }
            ]
            }

            EXAMPLE:
            {
            "doi": "10.1234/example.doi",
            "section": "Article",
            "titles": [
                {"title": "Example Title in English", "language": "en"},
                {"title": "Ejemplo de título en Español", "language": "es"}
            ],
            "authors": [
                {"name": "Alice", "surname": "Smith", "orcid": "0000-0001-2345-6789", "aff": 1, "char": "*"},
                {"name": "Bob", "surname": "Johnson", "orcid": "", "aff": 2, "char": "**"}
            ],
            "affiliations": [
                {
                "aff": 1,
                "char": "*",
                "orgname": "University of Example",
                "orgdiv1": "Department of Biology",
                "orgdiv2": "",
                "postal": "12345",
                "city": "Example City",
                "state": "EX",
                "code_country": "us",
                "name_country": "United States",
                "text_aff": "Department of Biology, University of Example, 12345 Example City, EX, United States"
                },
                {
                "aff": 2,
                "char": "**",
                "orgname": "Institute of Testing",
                "orgdiv1": "Division of Chemistry",
                "orgdiv2": "",
                "postal": "54321",
                "city": "Testville",
                "state": "TS",
                "code_country": "uk",
                "name_country": "United Kingdom",
                "text_aff": "Division of Chemistry, Institute of Testing, 54321 Testville, TS, United Kingdom"
                }
            ]
            }
        """