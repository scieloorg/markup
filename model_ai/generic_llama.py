from config.settings.base import LLAMA_MODEL_DIR, MODEL_LLAMA
from llama_cpp import Llama
import os
import google.generativeai as genai

class GenericLlama:

  def __init__(self, messages=None, response_format=None, max_tokens=4000, temperature=0.1, top_p=0.1, type='chat'): 
    self.llm = Llama(model_path = os.path.join(LLAMA_MODEL_DIR, MODEL_LLAMA), n_threads=2, n_ctx=5000)
    self.messages = messages
    self.response_format = response_format
    self.max_tokens = max_tokens
    self.temperature = temperature
    self.top_p = top_p
    self.type = type

  def run(self, user_input):
    if self.type == 'chat':
      input = self.messages.copy()
      input.append({
        'role': 'user',
        'content': user_input
      })
      return self.llm.create_chat_completion(messages=input, response_format=self.response_format, max_tokens=self.max_tokens, temperature=self.temperature, top_p=self.top_p)
    if self.type == 'prompt':
      #USO DE GEMINI
      #genai.configure(api_key='')
      #model = genai.GenerativeModel('models/gemini-2.0-flash')
      #return model.generate_content(user_input).text
      return self.llm(user_input, max_tokens=2000, temperature=self.temperature, stop=["###"])