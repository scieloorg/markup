from huggingface_hub import login
from huggingface_hub import hf_hub_download

HF_TOKEN = 'INTRODUCE_TOKEN'

login(token=HF_TOKEN)

repo_id = 'hugging-quants/Llama-3.2-3B-Instruct-Q4_K_M-GGUF'
filename = 'llama-3.2-3b-instruct-q4_k_m.gguf'
local_dir = 'llama-3.2'

downloaded_file = hf_hub_download(repo_id=repo_id, filename=filename, local_dir=local_dir)
