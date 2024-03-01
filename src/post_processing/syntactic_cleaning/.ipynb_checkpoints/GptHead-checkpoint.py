import json
from openai import OpenAI

class GptHead: 
    def __init__(self, openai_key):
        self.openai_key = openai_key
        
    def chat_gpt_request(self, prompt):
            client = OpenAI(api_key = self.openai_key)
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature = 0
            )
            
            return response.choices[0].message.content.strip()
        
    def get_gpt_head(self, sentence):
        prompt = ( 
        'From the next sentence:\n "'
        f'{sentence} "\n'
        """
    extract the head of a noun phrase (NP). The head of a noun phrase (NP) is the word that determines the main lexical category of the entire phrase. It is the central noun that all other modifying words or phrases within the noun phrase ultimately describe."
    the result conain only the extracted Head 
        """
        '\nResponse:'
    )
        
        head = self.chat_gpt_request(prompt)
        return head