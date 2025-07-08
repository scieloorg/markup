from config.settings.base import LLAMA_MODEL_DIR, MODEL_LLAMA
from llama_cpp import Llama
import os

class functionsLlama:

    def getFirstMetadata(text_first_block):
        instruction = """
        From the provided Text, extract the specified metadata as shown in the Example.

        Specifications:
            language: Use 2-letter codes
            orgname: Name of Organization, University, Intitution or similar
            orgdiv2: Name of Departament, Division or similar
            orgdiv1: Name of Subdepartament, Subdivision or similar
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
        {
            "doi": "DOI",
            "section": "Section",
            "titles": [
                {
                "title": "Title 1",
                "language": "Language 1"
                },
                {
                "title": "Title 2",
                "language": "Language 2"
                }
            ],
            "authors": [
                {
                "name": "First Name",
                "surname": "Last Name",
                "orcid": "ORCID",
                "aff": 1
                },
                {
                "name": "First Name 2",
                "surname": "Last Name 2",
                "orcid": "ORCID",
                "aff": 2
                }
            ],
            "affiliations": [
                {
                "aff": 1,
                "orgname": "Organization Name 1",
                "orgdiv2": "Department or Division 1",
                "orgdiv1": "Subdepartment or Subdivision 1",
                "postal": "Postal Code 1",
                "city": "City 1",
                "country": "Country 1"
                },
                {
                "aff": 2,
                "orgname": "Organization Name 2",
                "orgdiv2": "Department or Division 2",
                "orgdiv1": "Subdepartment or Subdivision 2",
                "postal": "Postal Code 2",
                "city": "City 2",
                "country": "Country 2"
                }
            ]
        }
        """

        prompt = f"""
                    ### Instruction:
                        {instruction}

                    ### Text:
                        {text_first_block}

                    ### Response:
        """

        return prompt