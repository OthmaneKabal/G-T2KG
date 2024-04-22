import warnings
warnings.filterwarnings("ignore")
import Entities_Mapper as em
import json
import PredicateMapper as pm
import re
class Mapping:
    def __init__(self, input_path, verbs_map_path, embd_verbs_path, output_path):
        self.input_path = input_path
        self.output_path = output_path
        self.verbs_map_path = verbs_map_path
        self.embd_verbs_path = embd_verbs_path
        self.mapping_result = [] ## store the result



    def is_passive(self, s , p , o ):
        # Unpack the triple into subject, predicate, and object
        subject = s
        predicate = p
        obj = o
        
        # Define patterns for identifying passive voice
        passive_patterns = [
            # re.compile(r"\b(?:am|is|are|was|were|been|being)\b", re.IGNORECASE),
            re.compile(r"\b(?:-by)\b", re.IGNORECASE),
        ]
        
        # Check if any passive voice pattern is present in the predicate
        is_passive = any(pattern.search(predicate) for pattern in passive_patterns)
        
        # Determine the voice based on the analysis
        if is_passive:
            return True
        else:
            return False

    def convert_to_active(self,s,p,o):
      # Unpack the triple into subject, predicate, and object
        subject = s
        predicate = p
        obj = o
        
        # subject, predicate, obj = passive_triple
        predicate_without_by = re.sub(r"\b(?:-by)\b", "", predicate, flags=re.IGNORECASE).strip()
        
        active_triple = (obj,predicate_without_by, subject)
        return active_triple

    def apply(self):
        entities_mapper = em.EntitiesMapper(self.input_path, self.output_path )
        entities_mapper.run()
        predicate_mapper = pm.PredicateMapper(self.input_path, self.verbs_map_path,  self.embd_verbs_path)
        # predicate_mapper.predicate_mapping(0.7)
        for element in entities_mapper.input_triples:
            subject = element["subject"]
            predicate = element["predicate"]
            object = element["object"]
            # if predicate in predicate_mapper.mapped_predicate.keys():
            predicate = predicate_mapper.direct_mapping(predicate)
            if subject in entities_mapper.label2cskg_entity.keys():
                subject = entities_mapper.label2cskg_entity[subject]
            if object in entities_mapper.label2cskg_entity.keys():
                 object = entities_mapper.label2cskg_entity[object]

            ## verify if active or passive and convert to active
            if self.is_passive(subject, predicate, object):
                subject, predicate, object = self.convert_to_active(subject, predicate, object)
            ## lemma of predicates
            # predicate = self.lemmatize_predicate(predicate)
            
            self.mapping_result.append(
                {
                        'sentence': element['sentence'],
                        'subject': subject,
                        'predicate': predicate,
                        'object': object,
                        'confidence': element['confidence'],
                        'first_validation': element['first_validation']
                    }
                
            )
            for element in self.mapping_result:
                element["subject"] = self.supprimer_ponctuation(element["subject"])
                element["object"] = self.supprimer_ponctuation(element["object"])
                element['first_validation'] = self.supprimer_ponctuation(element["first_validation"])
            self.handle_duplicates()
            # self.handle_duplicates()

    
    
    ### avec la semilarité des predicats !!!
    def apply_sim_pred(self):
        entities_mapper = em.EntitiesMapper(self.input_path, self.output_path )
        entities_mapper.run()
        predicate_mapper = pm.PredicateMapper(self.input_path, self.verbs_map_path,  self.embd_verbs_path)
        predicate_mapper.similarity_predicate_mapping(0.7)
        for element in entities_mapper.input_triples:
            subject = element["subject"]
            predicate = element["predicate"]
            object = element["object"]
            if predicate in predicate_mapper.mapped_predicate.keys():
                predicate = predicate_mapper.mapped_predicate[predicate]
            if subject in entities_mapper.label2cskg_entity.keys():
                subject = entities_mapper.label2cskg_entity[subject]
            if object in entities_mapper.label2cskg_entity.keys():
                 object = entities_mapper.label2cskg_entity[object]

            ## verify if active or passive and convert to active
            if self.is_passive(subject, predicate, object):
                subject, predicate, object = self.convert_to_active(subject, predicate, object)
            ## lemma of predicates
            # predicate = self.lemmatize_predicate(predicate)
            
            self.mapping_result.append(
                {
                        'sentence': element['sentence'],
                        'subject': subject,
                        'predicate': predicate,
                        'object': object,
                        'confidence': element['confidence'],
                        'first_validation': element["first_validation"]
                        
                    }
                
            )
        for element in self.mapping_result:
            element["subject"] = self.supprimer_ponctuation(element["subject"])
            element["object"] = self.supprimer_ponctuation(element["object"])
            element['first_validation'] = self.supprimer_ponctuation(element["first_validation"])
        self.handle_duplicates()
            
        
    def supprimer_ponctuation(self, phrase):
        # Définition des caractères de ponctuation à supprimer
        ponctuations = '!"#$%&\()*+,-./:;<=>?@[\\]^_{|}~'
        # Filtrer les caractères pour ne garder que ceux qui ne sont pas des ponctuations
        phrase_sans_ponctuation = ''.join(caractere for caractere in phrase if caractere not in ponctuations)
        return phrase_sans_ponctuation 
        
    def handle_duplicates(self):
        # Create a dictionary to store unique sentences with their confidence
        unique_entries = {}
        for entry in self.mapping_result:
            key = (entry['subject'], entry['predicate'], entry['object'])
            if key in unique_entries:
                # Vérifie si la phrase est déjà présente pour éviter la duplication
                if entry['sentence'] not in unique_entries[key]['sentence']:
                    unique_entries[key]['sentence'] += f" | {entry['sentence']}"
                if entry['first_validation'] == 'True':
                    unique_entries[key]['first_validation'] = 'True'
            else:
                unique_entries[key] = entry
        self.mapping_result = list(unique_entries.values())
        return list(unique_entries.values())
       
    def write_to_json(self):
        with open(self.output_path, 'w', encoding='utf-8') as jsonfile:
            json.dump(self.mapping_result, jsonfile, ensure_ascii=False, indent=2)
    def save_results(self):
        pass


if __name__ == "__main__":
    print("Mapping ...")
    parser = argparse.ArgumentParser(description="Post-Processing: entities and predicates mapping ")
    parser.add_argument("input_file", type=str, help="name of the input file inside the data G-T2KG_input directory")
    args = parser.parse_args()
    input_path = "../../outputs/"+args.input_file+"_validated_Triplets.json"
    output_path = "../../outputs/"+args.input_file+"_KG.json"
    verbs_map_path = "../../../resources/CSKG_VerbNet_verb_map.csv"
    embd_path = '../../../resources/predicate_embeddings.json'
    mapping = Mapping(input_path,verbs_map_path, embd_path ,output_path)
    mapping.apply()
    mapping.write_to_json()