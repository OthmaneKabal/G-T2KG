## imports
from nltk import Tree
import re
import stanza
import spacy
import json
from tqdm import tqdm
import copy
from nltk import word_tokenize, pos_tag
from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer
import GptHead as gh
import argparse
from multiprocessing import Pool, cpu_count

## read data -----> utilities
def read_json_file(file_path):
    """
    Read a JSON file and return its contents as a Python dictionary.

    :param file_path: The path to the JSON file.
    :type file_path: str
    :return: A dictionary representing the JSON data.
    :rtype: dict
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        print(f"File not found: {file_path}")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON in file {file_path}: {e}")
    except Exception as e:
        print(f"An error occurred while reading the file {file_path}: {e}")

## for read the general stopwords by domain ;) 
def get_general_words(file_path):
    """
    Read lines from a text file and return them as a list of strings.

    Parameters:
    - file_path (str): The path to the text file.

    Returns:
    - list of str: A list containing the lines from the file.
    """
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
        strip_lines = [line.strip() for line in lines]
        return strip_lines
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
        return []
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

###post_traitment utilities
class ConstituentNode:
    def __init__(self, label, children=None):
        self.label = label
        self.children = children or []


def first_most_deepNP(node):
  ### return le NP le plus profond
    if node is not None:
        if node.label == "NP":
            # Retrieve the subtree with the root "NP"
            result = tree_to_string(node)

            # Initialize the variable to store the recursively found NP child subtree
            np_child_subtree = None

            # Check if the NP node has a direct child that is also an NP node
            for child in node.children:
                if child.label == "NP":
                    # Retrieve the subtree of the NP child recursively
                    np_child_subtree = first_most_deepNP(child)

            # Return the NP child subtree if it exists, otherwise return the current subtree
            return np_child_subtree if np_child_subtree is not None else result

        # If the node is not "NP", continue the traversal
        for child in node.children:
            result = first_most_deepNP(child)
            if result is not None:
                return result



def tree_to_string(node, level=0):
  # return a tree as a string 

    if not node.children:  # Check if the node is a leaf
        return " " * level + f"{node.label}"

    result = " " * level + f"({node.label}"
    for child in node.children:
        result += tree_to_string(child, level + 1)
    result += " " * level + ")"
    return result

def build_tree_from_string(s):
    if s:
      return Tree.fromstring(s)
    else:
      return

def get_text_from_tree(tree):
  if tree:
    leaves = tree.leaves()
    return " ".join(leaves)
##############################################################################################################################################

## verify if the subject and the object do not exceed cerntain lenght
def valid_lenght(string, max_nb_words):
    words = string.split()
    return len(words) <= max_nb_words

## !!!!!!
def lemmatize_and_lowercase(sentence,nlp):
    # Analysez la phrase avec spaCy
    doc = nlp(sentence)
    # Lemmatisez chaque mot et convertissez-le en minuscules
    lemmatized_tokens = [token.lemma_.lower() for token in doc]
    # Rejoignez les mots lemmatisés pour former la phrase résultante
    lemmatized_sentence = ' '.join(lemmatized_tokens)
    return lemmatized_sentence

def lemmatize_Nouns_and_lowercase(sentence, nlp):
    # Analysez la phrase avec spaCy
    doc = nlp(sentence)
    # Lemmatisez chaque mot qui est un nom (Noun) et convertissez-le en minuscules
    lemmatized_tokens = [token.lemma_.lower() if token.pos_ == 'NOUN' else token.text.lower() for token in doc]
    # Rejoignez les mots lemmatisés pour former la phrase résultante
    lemmatized_sentence = ' '.join(lemmatized_tokens)
    print(lemmatized_sentence)
    return lemmatized_sentence


## delete adj  & adv for predicate
def delete_adj_adv(s,nlp):
    doc = nlp(s)
    cleaned_s = ' '.join(token.text for token in doc if token.pos_ not in ['ADJ', 'ADV'])
    # predicate_stpW_removal(cleaned_predicate)
    return cleaned_s

## delete first "to" (predicate)
def delete_first_TO(s):
    if not s:
        return
    tokens = s.split()
    if tokens[0] == "to":
        return (" ".join(tokens[1:])).strip()

def get_wordnet_pos(treebank_tag):
    """Converts treebank tags to WordNet tags."""
    if treebank_tag.startswith('J'):
        return wordnet.ADJ
    elif treebank_tag.startswith('V'):
        return wordnet.VERB
    elif treebank_tag.startswith('N'):
        return wordnet.NOUN
    elif treebank_tag.startswith('R'):
        return wordnet.ADV
    else:
        return None

def lemmatize_predicate(predicate):
    tokens = word_tokenize(predicate)
    tagged_tokens = pos_tag(tokens)
    lemmatizer = WordNetLemmatizer()
    lemmatized_tokens = []
    
    for word, tag in tagged_tokens:
        wn_tag = get_wordnet_pos(tag)
        if wn_tag is None:
            # If no WordNet POS tag is found, lemmatize as a noun by default.
            lemma = lemmatizer.lemmatize(word)
        else:
            lemma = lemmatizer.lemmatize(word, wn_tag)
        lemmatized_tokens.append(lemma)
    
    return ' '.join(lemmatized_tokens)

def lemmatize_onlyNouns_and_lowercase_stanza(sentence,nlp_stanza):
  
    doc = nlp_stanza(sentence)
    Nouns_lemmatizer = WordNetLemmatizer()
    # Lemmatiser chaque mot qui est un nom (Noun) et convertissez-le en minuscules
    lemmatized_tokens = [Nouns_lemmatizer.lemmatize(word.text.lower(),"n") if word.pos == 'NOUN' else word.text.lower() for sent in doc.sentences for word in sent.words]
    
    # Rejoignez les mots lemmatisés pour former la phrase résultante
    lemmatized_sentence = ' '.join(lemmatized_tokens)
    
    return lemmatized_sentence


# # #### leamm_wordnet
# def get_wordnet_pos(treebank_tag):
#     """Converts treebank POS tags to WordNet POS tags."""
#     if treebank_tag.startswith('N'):
#         return wordnet.NOUN
#     return None

# def lemmatize_onlyNouns_and_lowercase_wordNet(sentence):
#     tokens = word_tokenize(sentence)
#     tagged_tokens = pos_tag(tokens)
    
#     Nouns_lemmatizer = WordNetLemmatizer()
#     lemmatized_Nouns = [Nouns_lemmatizer.lemmatize(word.lower(), pos=get_wordnet_pos(pos_tag)) if get_wordnet_pos(pos_tag) else word.lower() for word, pos_tag in tagged_tokens]
    
#     lemmatized_sentence = ' '.join(lemmatized_Nouns)
    
#     return lemmatized_sentence




def detect_negation(text):
    # Detects the presence of negation in a given English text.

    # Args:
    # - text (str): The input text in English.

    # Returns:
    # - bool: True if negation is detected, False otherwise.

    negation_words = ["not", "no", "never", "none", "nobody", "nowhere", "nothing", "neither","nor", "hardly", "scarcely", "barely",
                      "doesn't", "isn't", "wasn't", "hasn't", "can't",
                      "won't", "couldn't", "wouldn't", "shouldn't", "didn't", "doesn't", "won't", "can't", "isn't", "haven't", "aren't"]

    # Convert the text to lowercase for case-insensitive comparison
    text_lower = text.lower()

    # Check if any negation word is present in the text
    for word in negation_words:
        if word in text_lower:
            return True
    # If no negation word is found, return False
        return False


## return the first word of a string (used for predicate rectification)
def get_first_word(string):
    words = string.split()
    if words:
        return words[0]
    else:
        return None
        
## pour extraire les noms qui suivent directement la "Head"
def extract_noun_follow_head_direct(input_sentence,nlp_spacy):
    doc = nlp_spacy(input_sentence)
    parts = []
    # Ajouter les noms successifs au début de la phrase
    for token in doc:
        if token.pos_ == "NOUN":
            parts.append(token.text)
        else:
            break
    result = " ".join(parts)
    return result

## Extrare jusqu'a le root  +  les nons qui suivent directement le Root
def only_head_Noun(sentence, nlp_spacy):
    doc = nlp_spacy(sentence)
    # Recherchez le nœud racine de l'arbre de dépendances
    root = next(token for token in doc if token.head == token)

    # Extraire la partie principale de la phrase jusqu'au nœud racine
    main_part_1 = sentence[:root.idx + len(root.text)]
    main_part_2 = sentence[root.idx + len(root.text):].strip()
    print(main_part_2)

    main_part_2 = extract_noun_follow_head_direct(main_part_2,nlp)
    main_part = main_part_1 +" "+ main_part_2
    return main_part



def is_verb_with_stanza(word,nlp_stanza):
    doc = nlp_stanza(word)
    for sentence in doc.sentences:
        for word in sentence.words:
            if word.upos == 'VERB':
                return True
    return False


# Fonction  pour extraire tous les NPs
def extract_all_nps(tree):
    nps = []  # Liste pour stocker tous les groupes nominaux trouvés

    def recurse(node):
        if node.label == 'NP':  # Si le nœud est un groupe nominal
            nps.append(node)  # Ajoutez ce nœud à la liste des NPs
        for child in node.children:  # Parcourir les enfants du nœud récursivement
            recurse(child)

    recurse(tree)  # Commencer la recherche récursive
    return nps

##options:["SBAR",("PP"or "PP-of")]
## SBAR: supprimer SBAR; PP: supprimer: PP, PP-of: supprimer PP sauf ceux  qui contiennent "of"
def get_NP_Head(node, word, options = ["SBAR","PP-of", "VP","S"],brother = None, nlp_stanza = None):
    current_np = None
    current_brother = None
    # if not nlp_stanza:
    #     nlp_stanza = stanza.Pipeline(lang='en', processors='tokenize,pos,constituency,depparse,lemma')
    if node is not None:
        # if node.label == "NN" and len(node.leaf_labels()) == 1 and word in node.leaf_labels():
        #   return node, None
        # if node.label == "NNP" and word in node.leaf_labels():
          # return node, None
        if is_verb_with_stanza(word, nlp_stanza):
              nps = extract_all_nps(node)
              NP = None
              for np in nps:
                  if word not in np.leaf_labels() and node.leaf_labels().index(word) > node.leaf_labels().index(np.leaf_labels()[-1]):
                      NP = np
              return NP,None
        if node.label == "NP" and word in node.leaf_labels():
            if is_verb_with_stanza(word, nlp_stanza):
              nps = extract_all_nps(node)
              NP = None
              for np in nps:
                  if word not in np.leaf_labels() and node.leaf_labels().index(word) > node.leaf_labels().index(np.leaf_labels()[-1]):
                      NP = np
              return NP,None
            # current_np = tree_to_string(node)
            current_np = node
            if brother:
              current_brother =  brother
              # current_brother =  tree_to_string(brother)
              for option in options:
                if option =="PP-of" and brother.label == "PP":
                  if brother.leaf_labels()[0] != "of":
                    current_brother = None
                else:
                  if brother.label == option:
                    current_brother = None

        for num_cild,child in enumerate(node.children):
            if num_cild >= len(node.children)-1:
                brother = None
            else:
                brother = node.children[num_cild+1]

            result,bro = get_NP_Head(child,word,options,brother, nlp_stanza)
            if result is not None:
                current_np = result
                current_brother = bro
        return current_np, current_brother
        
## stanford
def get_root_word_stanford(sentence, nlp_stanford):
    doc = nlp_stanford(sentence)
    return next((word.text for sent in doc.sentences for word in sent.words if word.deprel == "root"), None)
### spacy
def get_root_word(sentence,nlp_spacy):
    doc = nlp_spacy(sentence)
    # Recherchez le nœud racine de l'arbre de dépendances
    root = next(token for token in doc if token.head == token)
    return root.text

def is_word_count_less_than(sentence, l):
    """
    Check if the number of words in a sentence is less than a given length.

    Parameters:
    sentence (str): The sentence to check.
    l (int): The length to compare the word count against.

    Returns:
    bool: True if the number of words is less than l, False otherwise.
    """
    # Split the sentence into words
    words = sentence.split()
    
    # Count the words and compare with l
    return len(words) < l
#-------------------------------clean by syntactic rules -----------------------------
# This function encapsulates all treatment for extracting NP if it exists (option)
## sentence: la phrase (sujet ou l'objet ) pour laquelle on extrait le NP
## NP method, choisir la methode ou le critere pour extraire le NP il y'a trois methodes possible:
    ### NP+head:
          ####options:["SBAR",("PP"or "PP-of")]
              ## SBAR: supprimer SBAR; PP: supprimer: PP, PP-of: supprimer PP sauf ceux  qui contiennent "of"
    ### only_head:
    ###  first_most_DeepNP:
def Extract_NP(sentence, nlp_stanza, nlp_spacy, NP_method = "NP+Head", option = ["SBAR","PP-of", "VP","S"], root_method = None, gpt_key = None):
    doc = nlp_stanza(sentence)
    constituency_tree = doc.sentences[0].constituency
    final_result = None
    if NP_method == "first_most_DeepNP":
      extracted_Np = first_most_deepNP(constituency_tree)
      tree_obj = build_tree_from_string(extracted_Np)
      final_result = get_text_from_tree(tree_obj)
    elif NP_method =="only_head":
      final_result = only_head_Noun(sentence, nlp_spacy)
    elif NP_method =="NP+Head":
      #root_word = get_root_word(sentence, nlp_spacy)
      if root_method == "gpt" and gpt_key :
          gpt_head = gh.GptHead(gpt_key)
          root_word = gpt_head.get_gpt_head(sentence)
          if len(root_word.split())> 1:
              root_word = get_root_word_stanford(sentence,nlp_stanza)
      elif root_method == "stanza":
          root_word = get_root_word_stanford(sentence,nlp_stanza)
      else: 
          print("invalid root method !")
          return
      if  constituency_tree.get_root_labels(constituency_tree.children)[0] == "NN" and len(constituency_tree.leaf_labels()) == 1:
          NP_head, brother_tree = constituency_tree, None
          
      elif constituency_tree.get_root_labels(constituency_tree.children)[0] == "NNP" and len(constituency_tree.leaf_labels()) == 1:
          NP_head, brother_tree = constituency_tree, None
      else:
          NP_head, brother_tree = get_NP_Head(constituency_tree,root_word,option, None,nlp_stanza)
        
      if NP_head:
        NP_head =  tree_to_string(NP_head)
        
        NP_tree_obj = build_tree_from_string(NP_head)
        extracted_Np = get_text_from_tree(NP_tree_obj)
        extracted_brother =""
        if brother_tree:
          brother_tree = tree_to_string(brother_tree)
          brother_tree_obj = build_tree_from_string(brother_tree)
          extracted_brother = get_text_from_tree(brother_tree_obj)
        if extracted_brother:
            final_result = extracted_Np + " " + extracted_brother
        else:
            final_result = extracted_Np 
    return final_result

##------------------------------------------------------
### verifie si une phrase donnée commance par "ADP" si oui on supprime ce dernier
## exemple: in the brain and Electroencephalogram => the brain and Electroencephalogram
def firstWord_is_ADP(sentence, nlp_spacy):
   first_word = get_first_word(sentence)
   doc = nlp_spacy(first_word)
   if doc[0].pos_ == 'ADP':
     mots = sentence.split()
     return  ' '.join(mots[1:])
   else:
      return sentence


# ### verify if the sentence contains NP or NN or NNP
def is_contains_NP(sentence, nlp_stenza):
  doc = nlp_stenza(sentence)
  tree = doc.sentences[0].constituency
  Counter = tree.get_constituent_counts(tree.children)
  # print(Counter)
  if 'NP' in Counter or 'NN' in tree.get_root_labels(tree.children) or 'NNP' in tree.get_root_labels(tree.children):
      return True
  else:
      return False

# def is_contains_NP(sentence, nlp_stenza):
#   doc = nlp_stenza(sentence)
#   tree = doc.sentences[0].constituency
#   Counter = tree.get_constituent_counts(tree.children)
#   return 'NP' or 'NNP' or "NN" in Counter


def is_general(triple, general_words_path):
    s,p,o = triple
    ## 
    general_words = get_general_words(general_words_path)
    if s in general_words or o in general_words:
        return True
    else:
        return False
    

def remove_adj_stopwords(sentence):
    adj_stopwords = [
        'able', 'available', 'brief', 'certain',"this","me","you","it"
        'different', 'due', 'enough', 'especially', 'few', 'fifth','It'
        'former', 'his', 'howbeit', 'immediate', 'important', 'inc',
        'its', 'last', 'latter', 'least', 'less', 'likely', 'little',
        'many', 'more', 'most', 'much', 'my', 'necessary',
        'new', 'next', 'non', 'old', 'other', 'our', 'ours', 'own',
        'particular', 'past', 'possible', 'present', 'proud', 'recent',
        'same', 'several', 'significant', 'similar', 'such', 'sup', 'sure',
        'a',"an", 'the', "treeb", "rbek", "en", "that", "those", 'some',"these",
        "often", "approximately", "and", "their", "we", "our","us", "effective", "can","may",
        "should","need", "either", "then", 'good', 'accurately', 'corresponding',"explicitly", "along", "major"
    ]
    

    words = sentence.split()
    filtered_words = [word for word in words if word.lower() not in adj_stopwords]
    result_sentence = ' '.join(filtered_words)
    return result_sentence

def duplicated_triples(triples):
    pass


def not_empty_triple(triple):
    if not triple:
        return False
    s,p,o = triple
    return s and p and o


def remove_abbreviations(sentence):
    # Using a regular expression to remove anything within parentheses
    sentence = re.sub(r'\([^)]*\)', '', sentence)
    # Also remove any prefix ending with an open parenthesis at the end of the string
    sentence = re.sub(r'\s*\([^)]*$', '', sentence)
    return sentence.strip()


general_terms = [ 'method',
                     'paper',
                     'approach',
                     'novel work',
                     'two main step',
                     'introduction',
                     'paper introduction',
                     'aim',
                     "it",
                     'study',
                     'result',
                     'experiment',
                     'thing',
                     'two score',
                ]
######################################################################Post processing class #################################################################
# class TriplesPostProcessing:
#     def __init__(self, data_path, output_path, root_method, gpt_key = None):
#         self.data_path = data_path
#         self.output_path = output_path
#         self.input_triples = self.get_triples(data_path)##input triples before processing
#         print("\n",data_path,"\n")
#         print(data_path)
#         self.cleaned_triples = [] ## output triples
#         self.nlp_spacy = spacy.load("en_core_web_sm")
#         self.nlp_stanza = stanza.Pipeline(lang='en', processors='tokenize,pos,constituency,depparse,lemma')
#         self.root_method = root_method
#         self.gpt_key = gpt_key
#     def get_triples(self,input_data):
#         data = read_json_file(input_data)
#         return data
#     @classmethod
#     def json_to_tuple(cls, json_element):
#         return tuple([json_element['subject'],
#                      json_element['predicate'],
#                      json_element['object']])
    
#     ## predicate rectification
#     def predicate_rectifier(self,t):
#         sujet, predicate, objet = t
#         #### to lower
#         sujet = sujet.lower()
#         predicate = predicate.lower()
#         objet = objet.lower()
#         # Liste des prépositions à vérifier
#         prepositions = ['by', 'at', 'in', 'to', 'for', 'of', 'on','with']
    
#         # Vérifier si l'objet commence par l'une des prépositions
#         for preposition in prepositions:
#             if get_first_word(objet) == preposition:
#                 # Ajouter l'objet à la fin du prédicat
#                 predicate += ' ' + preposition
#                 # Supprimer la préposition de l'objet
#                 objet = objet[len(preposition):].strip()
#                 #nlp = spacy.load("en_core_web_sm")
#         fw = get_first_word(objet)
#         if not fw:
#             return
#         doc = self.nlp_spacy(fw)
#         if  doc[0].pos_ =='VERB':
#             predicate += ' ' + fw
#             # Supprimer la préposition de l'objet
#             objet = objet[len(fw):].strip()
#             # break  # Sortir de la boucle après la première correspondance
    
#         # Retourner le tuple modifié
#         return sujet, predicate, objet

#     @classmethod
#     def triple_cleaning(cls, triple, NP_method = "NP+Head", option = ["SBAR","PP-of", "VP","S"] ):
#         if not_empty_triple(triple):
#           s = remove_adj_stopwords(triple[0])
#           o = remove_adj_stopwords(triple[2])
#           if not s or not o:
#               return
#           triple = (s,triple[1],o)
#           temp = cls.predicate_rectifier(triple)
#           if temp:
#               s, p, o = temp
#               ## delete stop words using defined list
#               p = remove_adj_stopwords(p)
#               ## delete all adjectives and adverbs
#               p = delete_adj_adv(p,cls.nlp_spacy)
#               p = lemmatize_predicate(p)
#               # p = delete_first_TO(p)
#               ## if is_passive(p):
#               ## inverse_triple()
#           else:
#               return
#           if not p:
#               return
#           if detect_negation(p):
#             return
#           s = remove_abbreviations(s)
#           o = remove_abbreviations(o)
#           s = firstWord_is_ADP(s, cls.nlp_spacy)
#           if not s or not o:
#               return
#           if is_contains_NP(s, cls.nlp_stanza ) and is_contains_NP(o, cls.nlp_stanza) :
#             s = lemmatize_onlyNouns_and_lowercase_stanza(s,cls.nlp_stanza )
#             o = lemmatize_onlyNouns_and_lowercase_stanza(o,cls.nlp_stanza )
#             # s = lemmatize_onlyNouns_and_lowercase_wordNet(s)
#             # o = lemmatize_onlyNouns_and_lowercase_wordNet(o)
              

              
#             NP_subject = Extract_NP(s, cls.nlp_stanza, cls.nlp_spacy, NP_method , option, cls.root_method, cls.gpt_key)
#             NP_object = Extract_NP(o, cls.nlp_stanza, cls.nlp_spacy, NP_method , option, cls.root_method, cls.gpt_key)
    
#             if NP_subject in general_terms or NP_object in general_terms:
#                 return
#             if NP_subject and NP_object:
#                 ## verify_max_len()
#                 if is_word_count_less_than(NP_subject,6) and is_word_count_less_than(NP_subject,6): 
#                     return NP_subject, p, NP_object
#                 else:
#                     return
#             else:
#                 return 
#             # else:
#             #     return
#           else:
#             return
#         else:
#            return

    # def clean_triples(self):
    #     for triple in tqdm(self.input_triples, desc="Cleaning triples", unit="triple"):
    #         try:
    #             t = self.json_to_tuple(triple)
    #             cleaned_t = self.triple_cleaning(t)
    #             if cleaned_t:
    #                 self.cleaned_triples.append(
    #                     {
    #                         'sentence': triple['sentence'],
    #                         'subject': cleaned_t[0],
    #                         'predicate': cleaned_t[1],
    #                         'object': cleaned_t[2],
    #                         'confidence': triple['confidence']
                            
    #                     }
                    
    #                 )
    #         except Exception as e:
    #             print(f"Error processing triple {triple}: {e}")
                
    # @classmethod
    # def clean_single_triple(cls, triple):
    #     try:
    #         t = cls.json_to_tuple(triple)
    #         cleaned_t = cls.triple_cleaning(t)
    #         if cleaned_t:
    #             return {
    #                 'sentence': triple['sentence'],
    #                 'subject': cleaned_t[0],
    #                 'predicate': cleaned_t[1],
    #                 'object': cleaned_t[2],
    #                 'confidence': triple['confidence']
    #             }
    #     except Exception as e:
    #         print(f"Error processing triple {triple}: {e}")
    #     return None

    # def clean_triples(self):
    #     # Creating a pool of workers, by default the same as the number of CPU cores
    #     with Pool(processes=cpu_count()) as pool:
    #         # Map the clean_single_triple function to each item in the input_triples
    #         # Use tqdm to create a progress bar around the map function
    #         results = list(tqdm(pool.imap(self.clean_single_triple, self.input_triples),
    #                             total=len(self.input_triples),
    #                             desc="Cleaning triples",
    #                             unit="triple"))
    #     print(len(filter(None, results)))
    #     # Filter out None results and extend cleaned_triples list
    #     self.cleaned_triples.extend(filter(None, results))


class TriplesPostProcessing:
    nlp_spacy = spacy.load("en_core_web_sm")
    nlp_stanza = stanza.Pipeline(lang='en', processors='tokenize,pos,constituency,depparse,lemma')

    def __init__(self, data_path, output_path, root_method, gpt_key = None):
        self.data_path = data_path
        self.output_path = output_path
        self.input_triples = self.get_triples(data_path)##input triples before processing
        print("\n",data_path,"\n")
        print(data_path)
        self.cleaned_triples = [] ## output triples
        # self.nlp_spacy = spacy.load("en_core_web_sm")
        # self.nlp_stanza = stanza.Pipeline(lang='en', processors='tokenize,pos,constituency,depparse,lemma')
        self.root_method = root_method
        self.gpt_key = gpt_key
    def get_triples(self,input_data):
        data = read_json_file(input_data)
        return data
        
    def json_to_tuple(self, json_element):
        return tuple([json_element['subject'],
                     json_element['predicate'],
                     json_element['object']])
    
    ## predicate rectification
    def predicate_rectifier(self,t):
        sujet, predicate, objet = t
        #### to lower
        sujet = sujet.lower()
        predicate = predicate.lower()
        objet = objet.lower()
        # Liste des prépositions à vérifier
        prepositions = ['by', 'at', 'in', 'to', 'for', 'of', 'on','with']
    
        # Vérifier si l'objet commence par l'une des prépositions
        for preposition in prepositions:
            if get_first_word(objet) == preposition:
                # Ajouter l'objet à la fin du prédicat
                predicate += ' ' + preposition
                # Supprimer la préposition de l'objet
                objet = objet[len(preposition):].strip()
                #nlp = spacy.load("en_core_web_sm")
        fw = get_first_word(objet)
        if not fw:
            return
        doc = self.nlp_spacy(fw)
        if  doc[0].pos_ =='VERB':
            predicate += ' ' + fw
            # Supprimer la préposition de l'objet
            objet = objet[len(fw):].strip()
            # break  # Sortir de la boucle après la première correspondance
    
        # Retourner le tuple modifié
        return sujet, predicate, objet

    def triple_cleaning(self, triple, NP_method = "NP+Head", option = ["SBAR","PP-of", "VP","S"] ):
        if not_empty_triple(triple):
          s = remove_adj_stopwords(triple[0])
          o = remove_adj_stopwords(triple[2])
          if not s or not o:
              return
          triple = (s,triple[1],o)
          temp = self.predicate_rectifier(triple)
          if temp:
              s, p, o = temp
              ## delete stop words using defined list
              p = remove_adj_stopwords(p)
              ## delete all adjectives and adverbs
              p = delete_adj_adv(p,self.nlp_spacy)
              p = lemmatize_predicate(p)
              # p = delete_first_TO(p)
              ## if is_passive(p):
              ## inverse_triple()
          else:
              return
          if not p:
              return
          if detect_negation(p):
            return
          s = remove_abbreviations(s)
          o = remove_abbreviations(o)
          s = firstWord_is_ADP(s, self.nlp_spacy)
          if not s or not o:
              return
          if is_contains_NP(s, self.nlp_stanza ) and is_contains_NP(o,self.nlp_stanza) :
            s = lemmatize_onlyNouns_and_lowercase_stanza(s,self.nlp_stanza )
            o = lemmatize_onlyNouns_and_lowercase_stanza(o,self.nlp_stanza )
            # s = lemmatize_onlyNouns_and_lowercase_wordNet(s)
            # o = lemmatize_onlyNouns_and_lowercase_wordNet(o)
              

              
            NP_subject = Extract_NP(s, self.nlp_stanza, self.nlp_spacy, NP_method , option, self.root_method, self.gpt_key)
            NP_object = Extract_NP(o, self.nlp_stanza, self.nlp_spacy, NP_method , option, self.root_method, self.gpt_key)
    
            if NP_subject in general_terms or NP_object in general_terms:
                return
            if NP_subject and NP_object:
                ## verify_max_len()
                if is_word_count_less_than(NP_subject,6) and is_word_count_less_than(NP_subject,6): 
                    return NP_subject, p, NP_object
                else:
                    return
            else:
                return 
            # else:
            #     return
          else:
            return
        else:
           return

    # def clean_triples(self):
    #     for triple in tqdm(self.input_triples, desc="Cleaning triples", unit="triple"):
    #         try:
    #             t = self.json_to_tuple(triple)
    #             cleaned_t = self.triple_cleaning(t)
    #             if cleaned_t:
    #                 self.cleaned_triples.append(
    #                     {
    #                         'sentence': triple['sentence'],
    #                         'subject': cleaned_t[0],
    #                         'predicate': cleaned_t[1],
    #                         'object': cleaned_t[2],
    #                         'confidence': triple['confidence']
                            
    #                     }
                    
    #                 )
    #         except Exception as e:
    #             print(f"Error processing triple {triple}: {e}")
                
    def clean_single_triple(self, triple):
        try:
            t = self.json_to_tuple(triple)
            cleaned_t = self.triple_cleaning(t)
            if cleaned_t:
                return {
                    'sentence': triple['sentence'],
                    'subject': cleaned_t[0],
                    'predicate': cleaned_t[1],
                    'object': cleaned_t[2],
                    'confidence': triple['confidence']
                }
        except Exception as e:
            print(f"Error processing triple {triple}: {e}")
        return None
    
    
    def clean_triples(self):
        # Creating a pool of workers, by default the same as the number of CPU cores
        with Pool(processes= 15) as pool:
            # Map the clean_single_triple function to each item in the input_triples
            # Use tqdm to create a progress bar around the map function
            results = list(tqdm(pool.imap(self.clean_single_triple, self.input_triples),
                                total=len(self.input_triples),
                                desc="Cleaning triples",
                                unit="triple"))
        # Filter out None results and extend cleaned_triples list
        self.cleaned_triples.extend(filter(None, results))


    def write_to_json(self):
        with open(self.output_path, 'w', encoding='utf-8') as jsonfile:
            json.dump(self.cleaned_triples, jsonfile, ensure_ascii=False, indent=2)
            
    def run(self):
        self.clean_triples()
        # print("number of triples before cleaning": len(self.clean_triples))
        self.write_to_json()

if __name__ == "__main__":
    print("Syntactic Cleaning ...")
    parser = argparse.ArgumentParser(description="OIE Post-Processing: Syntactic Cleaning")
    parser.add_argument("input_file", type=str, help="name of the input file inside the data G-T2KG_input directory")
    parser.add_argument("--root_option", type=str, help="the option for extracting the head of NP (stanza or gpt) ")
    parser.add_argument("--gpt_key", type=str, nargs='?', default=None, help="the option for extracting the head of NP (stanza or gpt). Default is None if not specified.")
    args = parser.parse_args()
    input_file = "../../outputs/"+args.input_file+"_oie_triplets.json"
    output_file =  "../../outputs/"+args.input_file+"_oie_cleaned_triplets.json"
    root_option =  args.root_option
    gpt_key = args.gpt_key
    tpp = TriplesPostProcessing(input_file, output_file, root_method = root_option, gpt_key = gpt_key)
    tpp.run()
    print("Done")
