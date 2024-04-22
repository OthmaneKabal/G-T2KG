import json
import sys
sys.path.append('../utilities')
import utilities as u
from openai import OpenAI
import os
from tqdm import tqdm

class Triplets_validator:
   
    def __init__(self, input_path, output_path, gpt_key):
        ## input_path:  triplets file path
        ## output_path: directory for outputs
        ##gpt_key: openai key
        self.input_triplets = u.read_json_file(input_path)
        self.output_path = output_path
        self.openai_key = gpt_key
        self.client = OpenAI(api_key= self.openai_key)
        self.results = []
#         _ = load_dotenv(find_dotenv())
#         openai.api_key  = os.getenv(gpt_key)
    
    



    def chat_gpt(self, prompt):
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature = 0
        )
        
        return response.choices[0].message.content.strip()
    
    
    ## retourne le prompt pour la validation avec la phrase
    def Triple_sentence_prompt(self,data_elt):
        sentence = data_elt ["sentence"]
        subject = data_elt["subject"]
        predicate = data_elt["predicate"]
        objet = data_elt["object"]
        affirmation = subject + " "+ predicate +" " + objet
#         print(affirmation)
#         prompt = "Given the detailed sentence:\n" + sentence + "\n does the following affirmation accurately capture the essence contained within the detailed sentence?\n "+ "Affirmation:\n" + affirmation
        prompt = (
                    'Given the detailed sentence:\n  "'
                    f'{sentence} "\n'
                    "Does the following affirmation accurately capture the essence contained within the detailed sentence?\n"
                    'Affirmation:\n "'
                    f'{affirmation}"'
                    """
                    \nResponse:
-True
-False
Please select "True" if you agree that the affirmation accurately part of the essence of the detailed sentence.
Select "False" if you believe it does not.
                    """
                    )
        return prompt
    
    def Triple_sentence_validation(self, data_elt):
        prompt = self.Triple_sentence_prompt(data_elt)
        is_valid = self.chat_gpt(prompt)
        return is_valid
    def apply(self):
        for triple in tqdm(self.input_triplets, desc=" triplets validation", unit="triple"):
#             print(self.Triple_sentence_prompt(triple))
            first_validation = self.Triple_sentence_validation(triple)
            self.results.append({
            "sentence": triple ["sentence"],
            "subject" : triple["subject"],
            "predicate" : triple["predicate"],
            "object" : triple["object"],
            "confidence": triple["confidence"],
            "first_validation": first_validation    
            })
        u.save_to_json(output_path, self.results)
        return self.results

if __name__ == "__main__":
    print("Triplets Validation ...")
    parser = argparse.ArgumentParser(description="GPT-validation")
    parser.add_argument("input_file", type=str, help="name of the input file inside the data G-T2KG_input directory")
    parser.add_argument("--gpt_key", type=str, help="The OpenAI key to customize the GPT-4")
    args = parser.parse_args()
    input_path =  "../outputs/"+args.input_file+"_All_Triplets.json"
    output_path = "../outputs/"+args.input_file+"_validated_Triplets.json"
    api_key = args.gpt_key
    tv = Triplets_validator(input_path, output_path, api_key)
    res = tv.apply()
    print("Validation Done.")
