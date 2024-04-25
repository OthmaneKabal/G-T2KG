#!pip install spacy
import re
import spacy
import json
import argparse
class HearstPatterns(object):

    def __init__(self, input_path, output_path , extended=False):

        self.results = []
        self.sentences = self.get_sentences(input_path)
        self.input_path = input_path
        self.output_path = output_path
        self.__adj_stopwords = [
            'able', 'available', 'brief', 'certain',
            'different', 'due', 'enough', 'especially', 'few', 'fifth',
            'former', 'his', 'howbeit', 'immediate', 'important', 'inc',
            'its', 'last', 'latter', 'least', 'less', 'likely', 'little',
            'many', 'ml', 'more', 'most', 'much', 'my', 'necessary',
            'new', 'next', 'non', 'old', 'other', 'our', 'ours', 'own',
            'particular', 'past', 'possible', 'present', 'proud', 'recent',
            'same', 'several', 'significant', 'similar', 'such', 'sup', 'sure',
            'a', 'the', "treeb", "rbek", "en", "that", "those", "some"
        ]

        # now define the Hearst patterns
        # format is <hearst-pattern>, <general-term>
        # so, what this means is that if you apply the first pattern,
        # the first Noun Phrase (NP)
        # is the general one, and the rest are specific NPs
        self.__hearst_patterns = [
            (
                '(NP_\\w+ (, )?such as (NP_\\w+ ?(, )?(and |or )?)+)',
                'first'
            ),
            (
                '(such NP_\\w+ (, )?as (NP_\\w+ ?(, )?(and |or )?)+)',
                'first'
            ),
            (
                '((NP_\\w+ ?(, )?)+(and |or )?other NP_\\w+)',
                'last'
            ),
            (
                '(NP_\\w+ (, )?include (NP_\\w+ ?(, )?(and |or )?)+)',
                'first'
            ),
            (
                '(NP_\\w+ (, )?especially (NP_\\w+ ?(, )?(and |or )?)+)',
                'first'
            ),
        ]

        if extended:
            self.__hearst_patterns.extend([
                (
                    '((NP_\\w+ ?(, )?)+(and |or )?any other NP_\\w+)',
                    'last'
                ),
                (
                    '((NP_\\w+ ?(, )?)+(and |or )?some other NP_\\w+)',
                    'last'
                ),
                (
                    '((NP_\\w+ ?(, )?)+(and |or )?be a NP_\\w+)',
                    'last'
                ),
                (
                    '(NP_\\w+ (, )?like (NP_\\w+ ? (, )?(and |or )?)+)',
                    'first'
                ),
                (
                    'such (NP_\\w+ (, )?as (NP_\\w+ ? (, )?(and |or )?)+)',
                    'first'
                ),
                (
                    '((NP_\\w+ ?(, )?)+(and |or )?like other NP_\\w+)',
                    'last'
                ),
                (
                    '((NP_\\w+ ?(, )?)+(and |or )?one of the NP_\\w+)',
                    'last'
                ),
                (
                    '((NP_\\w+ ?(, )?)+(and |or )?one of these NP_\\w+)',
                    'last'
                ),
                (
                    '((NP_\\w+ ?(, )?)+(and |or )?one of those NP_\\w+)',
                    'last'
                ),
                (
                    'example of (NP_\\w+ (, )?be (NP_\\w+ ? '
                    '(, )?(and |or )?)+)',
                    'first'
                ),
                (
                    '((NP_\\w+ ?(, )?)+(and |or )?be example of NP_\\w+)',
                    'last'
                ),
                (
                    '(NP_\\w+ (, )?for example (, )?'
                    '(NP_\\w+ ?(, )?(and |or )?)+)',
                    'first'
                ),
                (
                    '((NP_\\w+ ?(, )?)+(and |or )?which be call NP_\\w+)',
                    'last'
                ),
                (
                    '((NP_\\w+ ?(, )?)+(and |or )?which be name NP_\\w+)',
                    'last'
                ),
                (
                    '(NP_\\w+ (, )?mainly (NP_\\w+ ? (, )?(and |or )?)+)',
                    'first'
                ),
                (
                    '(NP_\\w+ (, )?mostly (NP_\\w+ ? (, )?(and |or )?)+)',
                    'first'
                ),
                (
                    '(NP_\\w+ (, )?notably (NP_\\w+ ? (, )?(and |or )?)+)',
                    'first'
                ),
                (
                    '(NP_\\w+ (, )?particularly (NP_\\w+ ? '
                    '(, )?(and |or )?)+)',
                    'first'
                ),
                (
                    '(NP_\\w+ (, )?principally (NP_\\w+ ? (, )?(and |or )?)+)',
                    'first'
                ),
                (
                    '(NP_\\w+ (, )?in particular (NP_\\w+ ? '
                    '(, )?(and |or )?)+)',
                    'first'
                ),
                (
                    '(NP_\\w+ (, )?except (NP_\\w+ ? (, )?(and |or )?)+)',
                    'first'
                ),
                (
                    '(NP_\\w+ (, )?other than (NP_\\w+ ? (, )?(and |or )?)+)',
                    'first'
                ),
                (
                    '(NP_\\w+ (, )?e.g. (, )?(NP_\\w+ ? (, )?(and |or )?)+)',
                    'first'
                ),
                (
                    '(NP_\\w+ \\( (e.g.|i.e.) (, )?(NP_\\w+ ? (, )?(and |or )?)+'
                    '(\\. )?\\))',
                    'first'
                ),
                (
                    '(NP_\\w+ (, )?i.e. (, )?(NP_\\w+ ? (, )?(and |or )?)+)',
                    'first'
                ),
                (
                    '((NP_\\w+ ?(, )?)+(and|or)? a kind of NP_\\w+)',
                    'last'
                ),
                (
                    '((NP_\\w+ ?(, )?)+(and|or)? kind of NP_\\w+)',
                    'last'
                ),
                (
                    '((NP_\\w+ ?(, )?)+(and|or)? form of NP_\\w+)',
                    'last'
                ),
                (
                    '((NP_\\w+ ?(, )?)+(and |or )?which look like NP_\\w+)',
                    'last'
                ),
                (
                    '((NP_\\w+ ?(, )?)+(and |or )?which sound like NP_\\w+)',
                    'last'
                ),
                (
                    '(NP_\\w+ (, )?which be similar to (NP_\\w+ ? '
                    '(, )?(and |or )?)+)',
                    'first'
                ),
                (
                    '(NP_\\w+ (, )?example of this be (NP_\\w+ ? '
                    '(, )?(and |or )?)+)',
                    'first'
                ),
                (
                    '(NP_\\w+ (, )?type (NP_\\w+ ? (, )?(and |or )?)+)',
                    'first'
                ),
                (
                    '((NP_\\w+ ?(, )?)+(and |or )? NP_\\w+ type)',
                    'last'
                ),
                (
                    '(NP_\\w+ (, )?whether (NP_\\w+ ? (, )?(and |or )?)+)',
                    'first'
                ),
                (
                    '(compare (NP_\\w+ ?(, )?)+(and |or )?with NP_\\w+)',
                    'last'
                ),
                (
                    '(NP_\\w+ (, )?compare to (NP_\\w+ ? (, )?(and |or )?)+)',
                    'first'
                ),
                (
                    '(NP_\\w+ (, )?among -PRON- (NP_\\w+ ? '
                    '(, )?(and |or )?)+)',
                    'first'
                ),
                (
                    '((NP_\\w+ ?(, )?)+(and |or )?as NP_\\w+)',
                    'last'
                ),
                (
                    '(NP_\\w+ (, )? (NP_\\w+ ? (, )?(and |or )?)+ '
                    'for instance)',
                    'first'
                ),
                (
                    '((NP_\\w+ ?(, )?)+(and|or)? sort of NP_\\w+)',
                    'last'
                ),
                (
                    '(NP_\\w+ (, )?which may include (NP_\\w+ '
                    '?(, )?(and |or )?)+)',
                    'first'
                ),
                (
                    '((NP_\\w+ ?(, )?)+(and|or)? sort of NP_\\w+)',
                    'last'
                ),
            ])

        self.__spacy_nlp = spacy.load("en_core_web_sm")

    def get_sentences(self, file_name):
        
        try:
            with open(file_name, 'r', encoding= 'utf-8') as file:
                lines = file.readlines()
                lines = [l.strip() for l in lines]
                return lines
        except FileNotFoundError:
            print(f"Le fichier '{file_name}' n'a pas été trouvé.")
        except Exception as e:
            print(f"Une erreur s'est produite : {e}")

    
    def chunk(self, rawtext):
        doc = self.__spacy_nlp(rawtext)
        chunks = []
        for sentence in doc.sents:
            sentence_text = sentence.lemma_
            for chunk in sentence.noun_chunks:
                if chunk.lemma_.lower() == "example":
                    start = chunk.start
                    pre_token = sentence[start - 1].lemma_.lower()
                    post_token = sentence[start + 1].lemma_.lower()
                    if start > 0 and\
                            (pre_token == "for" or post_token == "of"):
                        continue
                if chunk.lemma_.lower() == "type":
                    continue
                chunk_arr = []
                replace_arr = []
                # print("chunk:", chunk)
                for token in chunk:
                    if token.lemma_ in self.__adj_stopwords + ["i.e.", "e.g."]:
                        continue
                    chunk_arr.append(token.lemma_)
                    # Remove punctuation and stopword adjectives
                    # (generally quantifiers of plurals)
                    if token.lemma_.isalnum():
                        replace_arr.append(token.lemma_)
                    else:
                        replace_arr.append(''.join(
                            char for char in token.lemma_ if char.isalnum()
                        ))
                if len(chunk_arr) == 0:
                    chunk_arr.append(chunk[-1].lemma_)
                chunk_lemma = ' '.join(chunk_arr)
                # print(chunk_lemma)
                replacement_value = 'NP_' + '_'.join(replace_arr)
                if chunk_lemma:
                    sentence_text = re.sub(r'\b%s\b' % re.escape(chunk_lemma),
                                           r'%s' % replacement_value,
                                           sentence_text)
            chunks.append(sentence_text)
        return chunks

    """
        This is the main entry point for this code.
        It takes as input the rawtext to process and returns a list
        of tuples (specific-term, general-term)
        where each tuple represents a hypernym pair.

    """
    def find_hyponyms(self, rawtext):

        hyponyms = []
        np_tagged_sentences = self.chunk(rawtext)

        for sentence in np_tagged_sentences:
            # two or more NPs next to each other should be merged
            # into a single NP, it's a chunk error

            for (hearst_pattern, parser) in self.__hearst_patterns:
                matches = re.search(hearst_pattern, sentence)
                if matches:
                    match_str = matches.group(0)

                    nps = [a for a in match_str.split() if a.startswith("NP_")]

                    if parser == "first":
                        general = nps[0]
                        specifics = nps[1:]
                    else:
                        general = nps[-1]
                        specifics = nps[:-1]

                    for i in range(len(specifics)):
                        pair = (
                            self.clean_hyponym_term(specifics[i]),
                            self.clean_hyponym_term(general)
                        )
                        # reduce duplicates
                        if pair not in hyponyms:
                            hyponyms.append(pair)

        return hyponyms

    def clean_hyponym_term(self, term):
        # good point to do the stemming or lemmatization
        return term.replace("NP_", "").replace("_", " ")

    def get_triples(self):
        try:
            for sentence in self.sentences:
                hyponyms = self.find_hyponyms(sentence)
                if hyponyms:
                    for hyp in hyponyms:
                        self.results.append({
                            'sentence': sentence,
                            'subject': hyp[0],
                            'predicate': "is-a",
                            'object': hyp[1],
                            'confidence': "-"
                        })
        except Exception as e:
            print(f"An error occurred: {e}")

    
    def write_to_json(self):
        with open(self.output_path, 'w', encoding='utf-8') as jsonfile:
            json.dump(self.results, jsonfile, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    print("Hyponymy Relations Extractraction ...")
    parser = argparse.ArgumentParser(description="Hyponymy Relations Extractraction")
    parser.add_argument("input_file", type=str, help="name of the input file inside the data G-T2KG_input directory")
    args = parser.parse_args()
    input_path = "../outputs/"+args.input_file+"_oie.txt"
    output_path = "../outputs/hyponyms_"+args.input_file+".json"
    HP = HearstPatterns(input_path, output_path)
    HP.get_triples()
    HP.write_to_json()




