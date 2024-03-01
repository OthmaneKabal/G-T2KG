#!/usr/bin/env python
# coding: utf-8
import json
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from tqdm import tqdm
import PredicateMapper_utilities
from nltk.stem import WordNetLemmatizer

class PredicateMapper:
    def __init__(self, triples_path,verbs_path, embd_path):
        self.predicate_embd = PredicateMapper_utilities.load_embeddings(embd_path)
        self.verb_map = PredicateMapper_utilities.loadVerbMap(verbs_path)
        self.input_triples = PredicateMapper_utilities.read_json_file(triples_path)
        self.mapped_predicate = {}

    
    
    
    def similarity_mapping(self, predicate):
       
        model = SentenceTransformer('paraphrase-multilingual-mpnet-base-v2')
        embd_predicate = model.encode(predicate, convert_to_tensor=True)
        embd_predicate = np.array(embd_predicate).reshape(1, -1)    
        max_similarity = float('-inf')
        max_element = None
        for k, v in self.predicate_embd.items():
            embd_verb = np.array(v).reshape(1, -1)
            similarity = cosine_similarity(embd_predicate, embd_verb)[0, 0]
    
            if similarity > max_similarity:
                max_similarity = similarity
                max_element = {k: similarity}
    
        # print(max_element)
        return max_element
    


    def check_last_word_preposition(self, predicate):
    # Liste des prépositions en anglais (à compléter si nécessaire)
        prepositions = ["aboard", "about", "above", "across", "after", "against", "along", "amid", "among", "around", 
                        "as", "at", "before", "behind", "below", "beneath", "beside", "between", "beyond", "by", 
                        "concerning", "considering", "despite", "down", "during", "except", "for", "from", "in", 
                        "inside", "into", "like", "near", "of", "off", "on", "onto", "out", "outside", "over", 
                        "past", "regarding", "round", "since", "through", "throughout", "to", "toward", "under", 
                        "underneath", "until", "unto", "up", "upon", "with", "within", "without"]
    
        words = predicate.split()
        last_word = words[-1].lower()  # Convertir en minuscules pour la comparaison en anglais
    
        if last_word in prepositions:
            # Le dernier mot est une préposition
            sentence_without_preposition = ' '.join(words[:-1])
            return (self.lemmatize_predicate(sentence_without_preposition), last_word)
        else:
            # Le dernier mot n'est pas une préposition
            return (self.lemmatize_predicate(predicate),None)




    
    def lemmatize_predicate(self,p):
        lemmatizer = WordNetLemmatizer()
        lemmatized_verb = lemmatizer.lemmatize(p, pos='v')
        return lemmatized_verb
        
##  verify if a given predicate like text-text (is-a, part-of, ....)
    def detecte_pattern(self,predicate):
        # Séparation du texte par "-"
        parties = predicate.split("-")
        
        # Vérification si le texte a exactement deux parties et si les deux parties sont du texte
        if len(parties) == 2 and all(partie.strip().isalpha() for partie in parties):
            return True
        else:
            return False
    
    ## return the dic of mapped predicate
        # threshold: the predicate mapping threshold
        # option: keep or  delete for unmpapped predicate
            ## keep: keep the as them (not mention them in the dict mapping)
            ## delete: in the mapping dict add a message that indicate thist triple should be deleted ("invalid triple")
   
    
    def direct_mapping(self,predicate):
         predicate_elts =  predicate.split()
         ## ne pas mapper be dans le cas d' AUX
         if len(predicate_elts) == 1 and predicate_elts[0] == 'be':
             return "is-a"
         p_mapped = []
         for p_elt in predicate_elts:
             if p_elt in self.verb_map.keys():
                 if p_elt != "be":
                     p_mapped.append(self.verb_map[p_elt])
                     if self.detecte_pattern(self.verb_map[p_elt]):
                         return self.verb_map[p_elt]
                 else:
                     p_mapped.append(p_elt)
             else:    
                 p_mapped.append(p_elt)
         p_mapped = [self.lemmatize_predicate(p) for p in p_mapped]
         return "-".join(p_mapped)       

    def similarity_predicate_mapping(self, threshold, option = "keep"):
        for triple in tqdm(self.input_triples, desc="predicate mapping"):
            predicate =  triple["predicate"]
            predicate_ = self.check_last_word_preposition(predicate)
            # predicate_[0] = self.lemmatize_predicate(predicate_[0])
            if predicate_:
                if predicate_[0] in self.verb_map.keys(): 
                    pp = ""
                    if predicate_[1]:
                        pp = "-"+ predicate_[1]
                    if self.detecte_pattern(self.verb_map[predicate_[0]]):
                        self.mapped_predicate[predicate] = self.lemmatize_predicate(self.verb_map[predicate_[0]])
                    else:
                        self.mapped_predicate[predicate] = self.lemmatize_predicate(self.verb_map[predicate_[0]]) + pp
                    # print("direct mapping:  ", predicate,"-->" ,self.verb_map[predicate_[0]] + pp )
                else:
                    max_sim_verb = self.similarity_mapping(predicate_[0])
                    # print(max_sim_verb)
                    if list(max_sim_verb.values())[0] >= threshold:
                        pp = ""
                        if predicate_[1]:
                            pp = "-"+ predicate_[1]

                        if self.detecte_pattern(self.verb_map[list(max_sim_verb.keys())[0]]):
                            self.mapped_predicate[predicate] =  self.lemmatize_predicate(self.verb_map[list(max_sim_verb.keys())[0]])
                        else:
                            self.mapped_predicate[predicate] =  self.lemmatize_predicate(self.verb_map[list(max_sim_verb.keys())[0]]) + pp
                        # print("sim:",max_sim_verb,"\n")
                        # print("similarity mapping:  ", predicate,"-->", self.verb_map[list(max_sim_verb.keys())[0]] + pp )
                    else:
                        ### keep or delete ! 
                        if option == "delete":
                            self.mapped_predicate[predicate] = "invalid triple"
                        if option == "keep":
                            pass
                        else:
                            print("invalid option !")
                            break  
