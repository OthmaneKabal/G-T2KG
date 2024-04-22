import json
import sys
sys.path.append('../../utilities')
import utilities as u
import argparse
class Mergetriplets:
    def __init__(self,hyponyms_path, openie_path, output_path):
        self.hyponyms_path = hyponyms_path
        self.openie_path = openie_path
        self.output_path = output_path
        self.hyponyms_triplets = self.get_hyp_triplets()
        self.openie_triplets = self.get_oie_triplets()
        self.results = []

    
    def get_hyp_triplets(self):
        return u.read_json_file(self.hyponyms_path)
    def get_oie_triplets(self):
        return self.delete_duplicate(u.read_json_file(self.openie_path))
    def mergeAndsave(self):
        self.results = self.hyponyms_triplets + self.openie_triplets
        u.save_to_json(self.output_path, self.results)
        
    def delete_duplicate(self,data):
        unique_entries = {}
        for entry in data:
            key = (entry['sentence'], entry['subject'], entry['predicate'], entry['object'])
            if key not in unique_entries or unique_entries[key]['confidence'] < entry['confidence']:
                unique_entries[key] = entry
        cleaned_data = list(unique_entries.values())
        return cleaned_data

if __name__ == "__main__":
    print("Merge Triplets ...")
    parser = argparse.ArgumentParser(description="OIE Post-Processing: Syntactic Cleaning")
    parser.add_argument("input_file", type=str, help="name of the input file inside the data G-T2KG_input directory")
    args = parser.parse_args()
    openie_path =  "../../outputs/"+args.input_file+"_oie_cleaned_triplets.json"
    hyponyms_path =  "../../outputs/hyponyms_"+args.input_file+".json"
    output_path =  "../../outputs/"+args.input_file+"_All_Triplets.json"
    me = Mergetriplets(hyponyms_path, openie_path, output_path)
    me.mergeAndsave()
    print("Triplets merged successfully")




