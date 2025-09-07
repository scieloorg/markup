from config.settings.base import LLAMA_MODEL_DIR, MODEL_LLAMA
from llama_cpp import Llama
import os
from model_ai import messages

class functionsLlama:

    def getFirstMetadata(text):
        print(messages.ALL_FIRST_BLOCK.format(text=text))
        return messages.ALL_FIRST_BLOCK.format(text=text)

    def getDoiAndSection():
        return messages.DOI_AND_SECTION_MESSAGES, messages.DOI_AND_SECTION_FORMAT

    def getTitles():
        return messages.TITLE_MESSAGES, messages.TITLE_RESPONSE_FORMAT

    def getAuthorConfig():
        return messages.AUTHOR_MESSAGES, messages.AUTHOR_RESPONSE_FORMAT
    
    def getAffiliations():
        return messages.AFFILIATION_MESSAGES, messages.AFFILIATION_RESPONSE_FORMAT