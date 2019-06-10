import os
from utils import readfiles
import time
import nltk
from utils import sbst


punctuations = [',', '.', ':', ';', '?', '(', ')', '[', ']', '&', '!', '*', '@', '#',
                '$', '%', '<', '>', "''", '``', "'", '{', '}']


class IndexTable:

    def __init__(self):
        self.table = {}
        self.permuterm_index_table = None

    def insert_pair(self, word, docID):
        IDlist = self.table.get(word, 'null')
        if IDlist != 'null':
            if IDlist[0].get(word, 'null') != 'null':
                IDlist[0][word] += 1
            else:
                IDlist[0][word] = 1
                IDlist[1] += 1
        else:
            self.table[word] = [{docID: 1}, 1]

    def get_docIDs(self, word):
        IDlist = self.table.get(word, 'null')
        if IDlist == 'null':
            return []
        else:
            return IDlist[0].keys()

    def get_docIDs_with_TF(self, word):
        IDlist = self.table.get(word, 'null')
        if IDlist == 'null':
            return []
        else:
            return IDlist[0]

    def get_IDF(self, word):
        IDlist = self.table.get(word, 'null')
        if IDlist == 'null':
            return 0
        else:
            return IDlist[1]

    def create_Permuterm_index(self):
        print('Begin creating Permuterm index.')
        t = time.time()
        self.permuterm_index_table = sbst()
        for item in self.table.items():
            word = item[0] + '$'
            for i in range(len(word)):
                self.permuterm_index_table.add([word[i:] + word[:i],item[0]])
        print(time.time() - t)
        print('Finished creating Permuterm index. Elasped time: ', time.time() - t, 's')

    def find_regex_words(self, _prefix):
        print('Begin wildcard query.')
        t = time.time()

        prefix = _prefix + '$'
        prefix = prefix[prefix.rindex('*')+1:] + prefix[:prefix.index('*')]
        candidates = []
        for i in self.permuterm_index_table.forward_from(prefix):
            if not i[0].startswith(prefix): break
            candidates.append(i)
        prefix = _prefix.split('*')
        candidates_filterd = []
        for _candidate in candidates:
            seed = False
            candidate =_candidate[1]
            for pre in prefix:
                try:
                    candidate = candidate[candidate.index(pre)+len(pre):]
                except:
                    seed = True
                    break
            if not seed:
                candidates_filterd.append(_candidate[1])

        print('Finished wildcard query. Elasped time: ', time.time() - t, 's')

        return candidates_filterd


class StaticObjects:

    def __init__(self):
        self.documents = ''
        self.document_words = ''
        self.indextable = ''


def process(dir_name):
    t = time.time()
    print('Begin loading and build index.')
    objects = StaticObjects()
    objects.documents = readfiles(dir_name)
    objects.document_words = tokenize(objects.documents)
    objects.indextable = IndexTable()

    for words in objects.document_words:
        for word in words[1]:
            objects.indextable.insert_pair(word, words[0])
    # print(objects.indextable.table)
    print('Finished loading and build index. Elasped time: ', time.time() - t, 's')
    return objects


def tokenize(documents, engine='nltk'):
    document_words = []
    for _doc in documents:
        if engine == 'nltk':
            doc = nltk.word_tokenize(_doc[1])
        doc_filtered = [word for word in doc if word not in punctuations]
        document_words.append([_doc[0], doc_filtered])
    return document_words


if __name__ == '__main__':
    t = time.time()
    object = process('/Users/alan/Desktop/Reuters')
    object.indextable.create_Permuterm_index()
    object.indextable.find_regex_words('b*g*n')
    t = time.time() - t
    print(t)

