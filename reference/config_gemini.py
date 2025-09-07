def create_prompt_reference(references):

    prompt_reference = f"""
    You are an assistant who distinguishes all the components of all citations in an article with output in JSON

    Rules:
    - If a DOI is present in the citation, it must be included in the doi field, and the uri field must be None. If there is no DOI, then a valid persistent URL (e.g., from a repository or publisher) must be provided in the uri field instead. One of these fields — doi or uri — must always be populated. Never leave both empty.
    - For references of type journal, the field pages must not be included, even if they appear in the original citation. Instead, the page range should be provided only in the fields fpage and lpage.
    - Consider that in book-type references, the source field generally refers to the title of the book, so do not use the title field in this case, only source.

    Specifications of JSON:

    {{
        "type": "json_object",
        "schema":{{
            "type": "object",
            "properties": {{
                "full_text": {{"type": "string"}},
                "reftype": {{"type": "string", "enum": ["journal", "thesis", "book", "data", "webpage", "software", "confproc"]}},
                "authors": {{"type": "array",
                            "items": {{
                                        "type": "object",
                                        "properties": {{
                                            "surname": {{"type": "string"}},
                                            "fname": {{"type": "string"}},
                                            "collab": {{"type": "string"}}
                                        }}
                                }}
                            }},
                "date": {{"type": "integer"}},
                "title": {{"type": "string"}},
                "chapter": {{"type": "string"}},
                "edition": {{"type": "string"}},
                "source": {{"type": "string"}},
                "vol": {{"type": "integer"}},
                "num": {{"type": "integer"}},
                "pages": {{"type": "string"}},
                "fpage": {{"type": "string"}},
                "lpage": {{"type": "string"}},
                "doi": {{"type": "string"}},
                "degree": {{"type": "string"}},
                "organization": {{"type": "string"}},
                "location": {{"type": "string"}},
                "org_location": {{"type": "string"}},
                "num_pages": {{"type": "integer"}},
                "uri": {{"type": "string"}},
                "access_id": {{"type": "string"}},
                "access_date": {{"type": "string"}},
                "version": {{"type": "string"}},
            }}
        }}
    }}

    Example:

    Bachman, S., J. Moat, A. W. Hill, J. de la Torre and B. Scott. 2011. Supporting Red List threat assessments with GeoCAT: geospatial conservation assessment tool. ZooKeys 150: 117-126. DOI: https://doi.org/10.3897/zookeys.150.2109

    Brunel, J. F. 1987. Sur le genre Phyllanthus L. et quelques genres voisins de la Tribu des Phyllantheae Dumort. (Euphorbiaceae, Phyllantheae) en Afrique intertropicale et à Madagascar. Thèse de doctorat de l’Université L. Pasteur. Strasbourg, France. 760 pp.

    Hernández-López, L. 1995. The endemic flora of Jalisco, Mexico: Centers of endemism and implications for conservation. Tesis de maestría. Universidad de Wisconsin. Madison, USA. 74 pp.

    Jones DL. The role of physical activity on the need for revision total knee arthroplasty in individuals with osteoarthritis of the knee [dissertation]. [Pittsburgh (PA)]: University of Pittsburgh; 2001. 436 p.

    Schimper, A. F. W. 1903. Plant geography upon a physiological basis. Clarendon Press. Oxford, UK. 839 pp.

    Correa, M. D., C. Galdames and M. Stapf. 2004. Catálogo de Plantas Vasculares de Panamá. Smithsonian Tropical Research Institute. Ciudad de Panamá, Panamá. 599 pp.

    Hernández-López, L. 2019. Las especies endémicas de plantas en el estado de Jalisco: su distribución y conservación. Comisión Nacional para el Conocimiento y Uso de la Biodiversidad (CONABIO). Cd. Mx., México. https://doi.org/10.15468/ktvqds (consultado diciembre de 2019).

    Lucas Leão; Perobelli, Fernando Salgueiro; Ribeiro, Hilton Manoel Dias, 2024, Data for: Ação Coletiva Institucional e Consórcio Públicos Intermunicipais no Brasil, DOI: 10.48331/scielodata.5Z4TMP, SciELO Data, V1, UNF:6:Neyjad4du3rFprhupCXizA== [fileUNF]. Disponível em: https://doi.org/10.48331/scielodata
    
    INAFED. 2010. Enciclopedia de los Municipios y Delegaciones de México: Jalisco. Instituto Nacional para el Federalismo y el Desarrollo Municipal. http://www.inafed.gob.mx/ work/enciclopedia/EMM21puebla/index.html (consultado diciembre de 2018).

    COB - Comitê Olímpico Brasileiro. Desafio para o corpo. Disponível em: http://www.cob.org.br/esportes/esporte.asp?id=39. (Acesso em 10 abr 2010)
    
    Nikon Corporation. 1991-2006. NIS- Elements, version 2.33. Tokio, Japón.

    Hamric, Ann B.; Spross, Judith A.; Hanson, Charlene M. Advanced practice nursing: an integrative approach. 3rd ed. St. Louis (MO): Elsevier Saunders; c2005. 979 p.

    Calkins BM, Mendeloff AI. The epidemiology of idiopathic inflammatory bowel disease. In: Kirsner JB, Shorter RG, eds. Inflammatory bowel disease, 4th ed. Baltimore: Williams & Wilkins. 1995:31-68.

    Furton EJ, Dort V, editors. Addiction and compulsive behaviors. Proceedings of the 17th Workshop for Bishops; 1999; Dallas, TX. Boston: National Catholic Bioethics Center (US); 2000. 258 p.
    
    Response:

    [
    {{
                        "full_text": "Bachman, S., J. Moat, A. W. Hill, J. de la Torre and B. Scott. 2011. Supporting Red List threat assessments with GeoCAT: geospatial conservation assessment tool. ZooKeys 150: 117-126. DOI: https://doi.org/10.3897/zookeys.150.2109",
                        "reftype": "journal",
                        "authors":  [
                            {{   "surname": "Bachman", "fname": "S." }},
                            {{   "surname": "Moat", "fname": "J." }},
                            {{   "surname": "Hill", "fname": "A. W." }},
                            {{   "surname": "de la Torre", "fname": "J." }},
                            {{   "surname": "Scott", "fname": "B." }},
                        ],
                        "date": 2011,
                        "title": "Supporting Red List threat assessments with GeoCAT: geospatial conservation assessment tool",
                        "source": "ZooKeys",
                        "vol": "150",
                        "num": None,
                        "fpage": "117",
                        "lpage": "126",
                        "doi": "10.3897/zookeys.150.2109",
                }},
    {{
                        "full_text": "Brunel, J. F. 1987. Sur le genre Phyllanthus L. et quelques genres voisins de la Tribu des Phyllantheae Dumort. (Euphorbiaceae, Phyllantheae) en Afrique intertropicale et à Madagascar. Thèse de doctorat de l’Université L. Pasteur. Strasbourg, France. 760 pp.",
                        "reftype": "Thesis",
                        "authors":  [
                            {{   "surname": "Brunel", "fname": "J. F." }},
                        ],
                        "date": 1987,
                        "source": "Sur le genre Phyllanthus L. et quelques genres voisins de la Tribu des Phyllantheae Dumort. (Euphorbiaceae, Phyllantheae) en Afrique intertropicale et à Madagascar",
                        "degree": "doctorat",
                        "organization": "l’Université L. Pasteur",
                        "location": "Strasbourg, France",
                        "num_pages": 760
                }},
    {{
                        "full_text": "Hernández-López, L. 1995. The endemic flora of Jalisco, Mexico: Centers of endemism and implications for conservation. Tesis de maestría. Universidad de Wisconsin. Madison, USA. 74 pp.",
                        "reftype": "Thesis",
                        "authors":  [
                            {{   "surname": "Hernández-López", "fname": "L." }},
                        ],
                        "date": 1995,
                        "source": "The endemic flora of Jalisco, Mexico: Centers of endemism and implications for conservation",
                        "degree": "maestría",
                        "organization": "Universidad de Wisconsin",
                        "location": "Madison, USA",
                        "num_pages": 74
                }},
    {{
                        "full_text": "Jones DL. The role of physical activity on the need for revision total knee arthroplasty in individuals with osteoarthritis of the knee [dissertation]. [Pittsburgh (PA)]: University of Pittsburgh; 2001. 436 p.",
                        "reftype": "Thesis",
                        "authors":  [
                            {{   "surname": "Jones", "fname": "DL" }},
                        ],
                        "date": 2001,
                        "source": "The role of physical activity on the need for revision total knee arthroplasty in individuals with osteoarthritis of the knee [dissertation]",
                        "organization": "University of Pittsburgh",
                        "location": "[Pittsburgh (PA)]",
                        "num_pages": 436 p
                }},
    {{
                    "full_text": "Schimper, A. F. W. 1903. Plant geography upon a physiological basis. Clarendon Press. Oxford, UK. 839 pp.",
                    "reftype": "book",
                    "authors":[
                        {{   "surname": "Schimper", "fname": "A. F. W." }},
                    ],
                    "date": 1903,
                    "source": "Plant geography upon a physiological basis",
                    "organization": "Clarendon Press",
                    "location": "Oxford, UK"
                    "num_pages": 839
                }},
    {{
                    "full_text": "Correa, M. D., C. Galdames and M. Stapf. 2004. Catálogo de Plantas Vasculares de Panamá. Smithsonian Tropical Research Institute. Ciudad de Panamá, Panamá. 599 pp.",
                    "reftype": "book",
                    "authors":[
                        {{   "surname": "Correa", "fname": "M. D." }},
                        {{   "surname": "Galdames", "fname": "C." }},
                        {{   "surname": "Stapf", "fname": "M." }},
                    ],
                    "date": 2004,
                    "source": "Catálogo de Plantas Vasculares de Panamá",
                    "organization": "Smithsonian Tropical Research Institute",
                    "location": "Ciudad de Panamá, Panamá",
                    "num_pages": 599
                }},
    {{
                    "full_text": "Hernández-López, L. 2019. Las especies endémicas de plantas en el estado de Jalisco: su distribución y conservación. Comisión Nacional para el Conocimiento y Uso de la Biodiversidad (CONABIO). Cd. Mx., México. https://doi.org/10.15468/ktvqds (consultado diciembre de 2019).",
                    "reftype": "data",
                    "authors":[
                        {{   "surname": "Hernández-López", "fname": "L." }},
                    ],
                    "date": 2019,
                    "title": "Las especies endémicas de plantas en el estado de Jalisco: su distribución y conservación",
                    "source": "Comisión Nacional para el Conocimiento y Uso de la Biodiversidad (CONABIO)",
                    "location": "Cd. Mx. México",
                    "doi": "https://doi.org/10.15468/ktvqds ",
                    "access_date": "diciembre de 2019"
                }},
    {{
                    "full_text": "Lucas Leão; Perobelli, Fernando Salgueiro; Ribeiro, Hilton Manoel Dias, 2024, Data for: Ação Coletiva Institucional e Consórcio Públicos Intermunicipais no Brasil, DOI: 10.48331/scielodata.5Z4TMP, SciELO Data, V1, UNF:6:Neyjad4du3rFprhupCXizA== [fileUNF]. Disponível em: https://doi.org/10.48331/scielodata",
                    "reftype": "data",
                    "authors":[
                        {{   "surname": "Leão", "fname": "Lucas" }},
                        {{   "surname": "Perobelli", "fname": "Fernando Salgueiro" }},
                        {{   "surname": "Ribeiro", "fname": "Hilton Manoel Dias" }}
                    ],
                    "date": 2024,
                    "version": "V1",
                    "title": "Data for: Ação Coletiva Institucional e Consórcio Públicos Intermunicipais no Brasil",
                    "source": "SciELO Data",
                    "doi": "https://doi.org/10.48331/scielodata",
                    "access_id": "UNF:6:Neyjad4du3rFprhupCXizA== [fileUNF]",
                    "access_date": "diciembre de 2019"
                }},
    {{
                    "full_text": "INAFED. 2010. Enciclopedia de los Municipios y Delegaciones de México: Jalisco. Instituto Nacional para el Federalismo y el Desarrollo Municipal. http://www.inafed.gob.mx/ work/enciclopedia/EMM21puebla/index.html (consultado diciembre de 2018).",
                    "reftype": "webpage",
                    "authors":[
                        {{   "collab": "INAFED" }},
                    ],
                    "date": 2010,
                    "source": "Enciclopedia de los Municipios y Delegaciones de México: Jalisco",
                    "organization": "Instituto Nacional para el Federalismo y el Desarrollo Municipal",
                    "uri": "http://www.inafed.gob.mx/ work/enciclopedia/EMM21puebla/index.html",
                    "access_date": "diciembre de 2018"
                }},
    {{
                    "full_text": "COB - Comitê Olímpico Brasileiro. Desafio para o corpo. Disponível em: http://www.cob.org.br/esportes/esporte.asp?id=39. (Acesso em 10 abr 2010)",
                    "reftype": "webpage",
                    "authors":[
                        {{   "collab": "COB -Comitê Olímpico Brasileiro" }},
                    ],
                    "date": 2010,
                    "source": "Desafio para o corpo",
                    "uri": "http://www.cob.org.br/esportes/esporte.asp?id=39",
                    "access_date": "10 abr 2010"
                }},
    {{
                    "full_text": "Nikon Corporation. 1991-2006. NIS- Elements, version 2.33. Tokio, Japón.",
                    "reftype": "software",
                    "authors":[
                        {{   "collab": "Nikon Corporation" }},
                    ],
                    "date": 2006,
                    "source": "NIS- Elements",
                    "version": "2.33",
                    "city": "Tokio",
                    "country": "Japón",
                }},
    {{
                    "full_text": "Hamric, Ann B.; Spross, Judith A.; Hanson, Charlene M. Advanced practice nursing: an integrative approach. 3rd ed. St. Louis (MO): Elsevier Saunders; c2005. 979 p.",
                    "reftype": "book",
                    "authors":[
                        {{   "surname": "Hamric", "fname": "Ann B." }},
                        {{   "surname": "Spross", "fname": "Judith A." }},
                        {{   "surname": "Hanson", "fname": "Charlene M." }},
                    ],
                    "date": c2005,
                    "source": "Advanced practice nursing: an integrative approach",
                    "edition: "3rd ed"
                    "organization": "Elsevier Saunders",
                    "location": "St. Louis (MO)",
                    "num_pages": 979 p
                }},
    {{
                    "full_text": "Calkins BM, Mendeloff AI. The epidemiology of idiopathic inflammatory bowel disease. In: Kirsner JB, Shorter RG, eds. Inflammatory bowel disease, 4th ed. Baltimore: Williams & Wilkins. 1995:31-68.",
                    "reftype": "book",
                    "authors":[
                        {{   "surname": "Calkins", "fname": "BM" }},
                        {{   "surname": "Mendeloff", "fname": "AI" }},
                    ],
                    "editors":[
                        {{   "surname": "Kirsner", "fname": "JB" }},
                        {{   "surname": "Shorter", "fname": "RG" }},
                    ],
                    "date": 1995,
                    "source": "Inflammatory bowel disease",
                    "chapter": "The epidemiology of idiopathic inflammatory bowel disease.",
                    "edition: "4th"
                    "organization": "Williams & Wilkins",
                    "location": "Baltimore",
                    "fpage": 31,
                    "lpage": 68
                }},
    {{
                    "full_text": "Furton EJ, Dort V, editors. Addiction and compulsive behaviors. Proceedings of the 17th Workshop for Bishops; 1999; Dallas, TX. Boston: National Catholic Bioethics Center (US); 2000. 258 p.",
                    "reftype": "confproc",
                    "authors":[
                        {{   "surname": "Furton", "fname": "EJ" }},
                        {{   "surname": "Dort", "fname": "V" }},
                    ],
                    "date": 2000,
                    "source": "Addiction and compulsive behaviors",
                    "title": "Proceedings of the 17th Workshop for Bishops",
                    "location": "Dallas, TX",
                    "num": "17",
                    "organization": "National Catholic Bioethics Center (US)",
                    "org_location": "Boston",
                    "pages": "258 p"
                }}
    ]

    Citations:

    {references}
    """

    return prompt_reference