from model_ai.generic_llama import GenericLlama
from model_ai.function_llama import functionsLlama

import re


def mark_article(text, metadata):
    if metadata == 'author':
        messages, response_format = functionsLlama.getAuthorConfig()
    if metadata == 'affiliation':
        messages, response_format = functionsLlama.getAffiliations()
    if metadata == 'doi':
        messages, response_format = functionsLlama.getDoiAndSection()
    if metadata == 'title':
        messages, response_format = functionsLlama.getTitles()

    gll = GenericLlama(messages, response_format)
    output = gll.run(text)
    output = output['choices'][0]['message']['content']
    if metadata == 'doi':
        output = re.search(r'\{.*\}', output, re.DOTALL)
    else:
        output = re.search(r'\[.*\]', output, re.DOTALL)
    if output:
        output = output.group(0)
    return output

def mark_references(reference_block):
    for ref_row in reference_block.split("\n"):
        ref_row = ref_row.strip()
        if ref_row:
            choices = mark_reference(ref_row)
            yield {
                "reference": ref_row,
                "choices": list(choices)
            }

