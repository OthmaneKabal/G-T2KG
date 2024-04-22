import re
import json
import argparse

class TripletExtractionConverter:
    def __init__(self, data_path, output_path):
        self.data_path = data_path
        self.output_path = output_path
        self.triples_data = []
        
    def extract_triplets(self):
        with open(self.data_path, 'r') as file:
            data = file.read()
        sentences_and_triplets = re.split(r'\n\n', data)
       
#         triplets_data = []
        for sentence_and_triplet in sentences_and_triplets:
            lines = sentence_and_triplet.strip().split('\n')
            sentence = lines[0]
            triplets = lines[1:]
            for triplet in triplets:
                confidence, triplet_data = triplet.split(': ', 1)
                subject, predicate, obj = re.search(r'\((.*?); (.*?); (.*?)\)', triplet_data).groups()
                self.triples_data.append({
                    'sentence': sentence,
                    'subject': subject,
                    'predicate': predicate,
                    'object': obj,
                    'confidence': float(confidence)
                })
                
    def write_to_json(self):
        with open(self.output_path, 'w', encoding='utf-8') as jsonfile:
            json.dump(self.triples_data, jsonfile, ensure_ascii=False, indent=2)
    
    def run(self):
        self.extract_triplets()
        self.write_to_json()
if __name__ == "__main__":
	print("output OIE6 converting ...")
	parser = argparse.ArgumentParser(description="Hyponymy Relations Extractraction")
	parser.add_argument("input_file", type=str, help="name of the input file inside the data G-T2KG_input directory")
	args = parser.parse_args()
	input_file_path = "../outputs/"+args.input_file+"_oie_triplets.txt.oie" ## test_oie_triplets.txt.oie
	output_json_file_path = "../outputs/"+args.input_file+"_oie_triplets.json"
	tec = TripletExtractionConverter(input_file_path,output_json_file_path)
	tec.run()
	print("OIe output succesfully converted ! ")
	
