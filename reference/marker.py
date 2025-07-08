from model_ai.generic_llama import GenericLlama

from reference.config import MESSAGES, RESPONSE_FORMAT


def mark_reference(reference_text):
    reference_marker = GenericLlama(MESSAGES, RESPONSE_FORMAT)
    output = reference_marker.run(reference_text)
    # output['choices'][0]['message']['content']
    for item in output["choices"]:
        yield item["message"]["content"]


def mark_references(reference_block):
    for ref_row in reference_block.split("\n"):
        ref_row = ref_row.strip()
        if ref_row:
            choices = mark_reference(ref_row)
            yield {
                "reference": ref_row,
                "choices": list(choices)
            }

