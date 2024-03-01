
from SPARQLWrapper import SPARQLWrapper, JSON
from django.utils.encoding import smart_str
# from sentence_transformers import util
from multiprocessing import Process
from urllib.parse import unquote
from random import shuffle
import networkx as nx
import pandas as pd
import numpy as np
import rdflib
import urllib
import random
import pickle 
# import torch
import json
import time
import csv
import os
import nltk
from nltk.tokenize import word_tokenize
#nltk.download('punkt')
from sentence_transformers import util
from sentence_transformers import SentenceTransformer




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





class EntitiesMapper:
    def __init__(self, data_path, output_path):
        self.data_path = data_path
        self.output_path = output_path
        self.input_triples = self.get_input_triples()
        self.mapping_result = {}
        self.entities = []
        self.all_pairs = []
        self.get_entities_pairs()
        self.e2wikidata = {}
        self.e2dbpedia = {}
        self.e_transformer = {}
        self.e2neighbors = {} ## only for context 
        self.cskg2wikidata = {}
        self.cskg2dbpedia = {}
        self.label2cskg_entity = {}

        
    
    def get_input_triples(self):
        return read_json_file(self.data_path)
    
    def get_entities_pairs(self):
        print("get Entities and pairs")
        for triple in self.input_triples:
            if triple["subject"] not in self.entities:
                self.entities.append(triple["subject"])
            if triple["object"] not in self.entities:
                self.entities.append(triple["object"])

            if tuple([triple["subject"], triple["object"]]) not in self.all_pairs:
                self.all_pairs.append(tuple([triple["subject"], triple["object"]]))
                
    
    def linkThroughWikidata(self):
        print('- \t >> Mapping with wikidata started')
        timepoint = time.time()
        entities_to_explore = list(set(self.entities) - set(self.e2wikidata.keys()))

        if len(entities_to_explore) <= 0:
            return

        # sorting entities
        entities_to_explore = sorted(entities_to_explore, key=lambda x: len(x), reverse=True)
        c = 0

        while c < len(entities_to_explore):
            e = entities_to_explore[c]
## prefix rdfs P ## 
            query = """
                    SELECT DISTINCT ?entity ?altLabel
                    WHERE{
                            {
                                ?entity  <http://www.w3.org/2000/01/rdf-schema#label> \"""" + e +"""\"@en .
                                {?entity wdt:P31+ wd:Q21198 }  UNION 
                                {?entity wdt:P31/wdt:P279* wd:Q21198} UNION
                                {?entity wdt:P279+ wd:Q21198} UNION
                                {?entity  wdt:P361+ wd:Q21198} UNION
                                { ?entity  wdt:P1269+ wd:Q21198} UNION
                                {FILTER NOT EXISTS {?entity <http://schema.org/description> "Wikimedia disambiguation page"@en}}
                                 OPTIONAL {
                                    ?entity <http://www.w3.org/2004/02/skos/core#altLabel> ?altLabel .
                                    FILTER(LANG(?altLabel) = 'en')
                                }
                                

                            }  UNION {
                                ?entity <http://www.w3.org/2004/02/skos/core#altLabel> \"""" + e +"""\"@en .
                                {?entity wdt:P31+ wd:Q21198 }  UNION 
                                {?entity wdt:P31/wdt:P279* wd:Q21198} UNION
                                {?entity wdt:P279+ wd:Q21198} UNION
                                {?entity  wdt:P361+ wd:Q21198} UNION
                                { ?entity  wdt:P1269+ wd:Q21198} 
                                 OPTIONAL {
                                    ?entity <http://www.w3.org/2004/02/skos/core#altLabel> ?altLabel .
                                    FILTER(LANG(?altLabel) = 'en')
                                }
                                SERVICE wikibase:label { bd:serviceParam wikibase:language "en" }

                            }
                        }
                    """

            url = 'https://query.wikidata.org/sparql'
            data = urllib.parse.urlencode({'query': query}).encode()
            headers = {"Accept": "application/sparql-results+json"}

            try:
                req = urllib.request.Request(url, data=data, headers=headers)
                response = urllib.request.urlopen(req)

                if response.status == 200:

                    result = response.read().decode('ascii', errors='ignore')
                    jresponse = json.loads(result)
                    variables = jresponse['head']['vars']
                    for binding in jresponse['results']['bindings']:

                        if 'entity' in binding and e not in self.e2wikidata:
                            if 'http://www.wikidata.org/entity/Q' in binding['entity']['value']:
                                self.e2wikidata[e] = binding['entity']['value']

                        if 'altLabel' in binding:
                            if binding['altLabel']['value'].lower() in entities_to_explore and binding['altLabel']['value'].lower() not in self.e2wikidata:
                                if 'http://www.wikidata.org/entity/Q' in binding['entity']['value']:
                                    self.e2wikidata[binding['altLabel']['value'].lower()] = binding['entity']['value']

                    c += 1
                    if c % 100 == 0:
                        print('\t >> Wikidata Processed', c, 'entities in {:.2f} secs.'.format(time.time() - timepoint))
                        # pickle_out = open("../../resources/e2wikidata.pickle", "wb")
                        # pickle.dump(self.e2wikidata, pickle_out)
                        # pickle_out.flush()
                        # pickle_out.close()

            except urllib.error.HTTPError as err:
                print(err)
                print(err.headers)
                print('sleeping...')
                time.sleep(60)
            except Exception as ex:
                print(ex)

        # pickle_out = open("../../resources/e2wikidata.pickle", "wb")
        # pickle.dump(self.e2wikidata, pickle_out)
        # pickle_out.close()
        print('> Mapped to Wikidata:', len(self.e2wikidata))
        
    def findNeiighbors(self):
    
    		for s,o in self.all_pairs:
    			if s not in self.e2neighbors:
    				self.e2neighbors[s] = []
    			if len(self.e2neighbors[s]) < 20:
    				self.e2neighbors[s] += [o]
    
    			if o not in self.e2neighbors:
    				self.e2neighbors[o] = []
    			if len(self.e2neighbors[o]) < 20:
    				self.e2neighbors[o] += [s]

    def linkThroughDbpedia(self):
        print('- \t >> Mapping with dbpedia started')
        
        entities_to_explore = set(self.entities) - set(self.e2dbpedia.keys())
        if len(entities_to_explore) <= 0:
            return

        self.findNeiighbors()

        c = 0
        timepoint = time.time()
        for e in entities_to_explore:
            if e not in self.e2dbpedia:
                neighbors = self.e2neighbors[e]
                
                #content = [e] + [self.id2e[nid] for nid in neighbors_ids[:20]]
                content = [e] + neighbors
                shuffle(content)
                content = ' '.join(content)
                
                url = 'https://api.dbpedia-spotlight.org/en/annotate'
                data = urllib.parse.urlencode({'text': content})
                headers = {"Accept": "application/json"}
        
                try:
                    req = urllib.request.Request(url + '?' + data, headers=headers)
                    response = urllib.request.urlopen(req)
                    if response.status == 200:
                    
                        result = response.read().decode('ascii', errors='ignore')
                        jresponse = json.loads(result)
                        
                        if 'Resources' in jresponse:
                            for resource in jresponse['Resources']:
                                if resource['@surfaceForm'] == e and float(resource['@similarityScore']) >= 0.8:
                                        self.e2dbpedia[e] = resource['@URI']
                                        break

                except urllib.error.HTTPError as e:
                    print('HTTPError: {}'.format(e.code), 'sleeping...')
                    time.sleep(60)
                except:
                    print('E:', e)
                    pass

                c += 1
                if c % 10000 == 0:
                    print('- \t>> DBpedia Processed', c, 'entities in', (time.time() - timepoint), 'secs')
                    # pickle_out = open("../../resources/e2dbpedia.pickle","wb")
                    # pickle.dump(self.e2dbpedia, pickle_out)
                    # pickle_out.close()

		# pickle_out = open("../../resources/e2dbpedia.pickle","wb")
		# pickle.dump(self.e2dbpedia, pickle_out)
		# pickle_out.close()
		# print('- \t >> Mapped to DBpedia:', len(self.e2dbpedia))

    def mergeEntities(self):
        wikidata2cskg = {}
        dbpedia2cskg = {}

        for (s,o) in self.all_pairs:
            if s in self.e2dbpedia:
                if self.e2dbpedia[s] not in dbpedia2cskg:
                    dbpedia2cskg[self.e2dbpedia[s]] = []
                dbpedia2cskg[self.e2dbpedia[s]] += [s]
            if s in self.e2wikidata:
                if self.e2wikidata[s] not in wikidata2cskg:
                    wikidata2cskg[self.e2wikidata[s]] = []
                wikidata2cskg[self.e2wikidata[s]] += [s]
            if o in self.e2dbpedia:
                if self.e2dbpedia[o] not in dbpedia2cskg:
                    dbpedia2cskg[self.e2dbpedia[o]] = []
                dbpedia2cskg[self.e2dbpedia[o]] += [o]
            if o in self.e2wikidata:
                if self.e2wikidata[o] not in wikidata2cskg:
                    wikidata2cskg[self.e2wikidata[o]] = []
                wikidata2cskg[self.e2wikidata[o]] += [o]

		# merging with dbpedia
        for dbe, cskg_entities_labels in dbpedia2cskg.items():
			
			# check if there exists an entity
            cskg_entity = None
            for label in list(set(cskg_entities_labels)):
                if label in self.label2cskg_entity:
                    cskg_entity = self.label2cskg_entity[label]
                    break

            if cskg_entity == None:
                cskg_entity = max(list(set(cskg_entities_labels)), key=len)
			
            for label in list(set(cskg_entities_labels)):
                self.label2cskg_entity[label] = cskg_entity
            self.cskg2dbpedia[cskg_entity] = dbe


		# merging with wikidata
        for wde, cskg_entities_labels in wikidata2cskg.items():
			
            # check if there exists an entity
            cskg_entity = None
            for label in list(set(cskg_entities_labels)):
                if label in self.label2cskg_entity:
                    cskg_entity = self.label2cskg_entity[label]
                    break

            if cskg_entity == None:
                cskg_entity = max(list(set(cskg_entities_labels)), key=len)

            for label in list(set(cskg_entities_labels)):
                self.label2cskg_entity[label] = cskg_entity
            self.cskg2wikidata[cskg_entity] = wde



    def load(self):

        p_wikidata = Process(target=self.linkThroughWikidata)
        p_dbpedia = Process(target=self.linkThroughDBpediaSpotLight)
        p_dbpedia.start()
        p_wikidata.start() 
        try: p_wikidata.join() 
        except: pass 
        try: p_dbpedia.join()
        except: pass 


    ##################### Mapping using transformers ##############################
# function used by mergeEntitiesEuristic
    def mergeEntitiesEmbeddings(self, model, entities):

        paraphrases = util.paraphrase_mining(model, entities, query_chunk_size=100, corpus_chunk_size=10000, batch_size=256, top_k=5, show_progress_bar=False)

        for paraphrase in paraphrases:
            score, i, j = paraphrase
            ei = entities[i] # entity
            ej = entities[j] # entity 
			# since the results are ordered, the loop is stopped when the similarity is lower than 0.9
            if score < 0.9:
                break

            if ei not in self.label2cskg_entity and ej not in self.label2cskg_entity:
                self.label2cskg_entity[ej] = ei
                self.label2cskg_entity[ei] = ei
                #print(ej, '->', ei, ' : ', score)
            elif ei not in self.label2cskg_entity and ej in self.label2cskg_entity:
                self.label2cskg_entity[ei] = self.label2cskg_entity[ej]
                #print(ei, '->', ej, '->',  self.label2cskg_entity[ej], ' : ', score)
            elif ei in self.label2cskg_entity and ej not in self.label2cskg_entity:
                self.label2cskg_entity[ej] = self.label2cskg_entity[ei]
                #print(ej, '->', ei, '->',  self.label2cskg_entity[ei], ' : ', score)


    def mergeEntitiesEuristic(self):


        try:
            # merge lables with separate embeddings merging previously computed if it exists, otherwise it will be computed in the
            # execution flow of the code
            f = open('../../resources/only_embeddings_label2cskg_entity.pickle', 'rb')
            only_embeddings_label2cskg_entity = pickle.load(f)
            f.close()
            for (ei, ej) in only_embeddings_label2cskg_entity.items():	
				
                if ei not in self.label2cskg_entity and ej not in self.label2cskg_entity:
                    self.label2cskg_entity[ej] = ei
                    self.label2cskg_entity[ei] = ei
                elif ei not in self.label2cskg_entity and ej in self.label2cskg_entity:
                    self.label2cskg_entity[ei] = self.label2cskg_entity[ej]
                elif ei in self.label2cskg_entity and ej not in self.label2cskg_entity:
                    self.label2cskg_entity[ej] = self.label2cskg_entity[ei]
        except FileNotFoundError:

            # sentence-transformers/paraphrase-distilroberta-base-v2
            model = SentenceTransformer('sentence-transformers/paraphrase-distilroberta-base-v2')
            word2entities = {}

            for (s,o) in self.all_pairs:
                stokens = word_tokenize(s)
                otokens = word_tokenize(o)

                for t in stokens:
                    if t not in word2entities:
                        word2entities[t] = set()
                    word2entities[t].add(s)

                for t in otokens:
                    if t not in word2entities:
                        word2entities[t] = set()
                    word2entities[t].add(o)

            wordcount = len(word2entities)
            for word, entities in word2entities.items():
                #print(wordcount, word, len(entities))
                #wordcount -= 1
                if len(entities) > 1:
                    self.mergeEntitiesEmbeddings(model, list(entities))
                #print('\t>> tokens to be checked:', wordcount)

    def run(self):
        print('\t>> Entities to be mapped:', len(self.entities))
        # self.load()
        self.linkThroughWikidata()
        self.linkThroughDbpedia()
        print("-------------------------------------------")
        self.mergeEntities()
        self.mergeEntitiesEuristic()
        ## apply_mapping 


