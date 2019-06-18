# -*- coding: utf-8 -*-
import os
from utils import readfiles
from utils import vector_encode, vector_decode, boolean_op, vb_decode, vb_encode, print_vb_code
import time
import nltk
from utils import sbst
import math
from collections import Counter
import operator
import numpy as np

punctuations = [',', '.', ':', ';', '?', '(', ')', '[', ']', '&', '!', '*', '@', '#',
                '$', '%', '<', '>', "''", '``', "'", '{', '}']

class CompressTable:

    def __init__(self, compress_doc_id, compress_doc_fre, compress_word):
        self.compress_doc_id = compress_doc_id
        self.compress_doc_fre = compress_doc_fre
        self.compress_word = compress_word

    def keys(self):
        return self.compress_word

    def get(self, word, default=None):
        for i in range(len(self.compress_word)):
            if self.compress_word[i] == word:
                # 解码
                docIDs = vb_decode(self.compress_doc_id[i])
                docFres = vb_decode(self.compress_doc_fre[i])
                # 求ID
                for j in range(1, len(docIDs)):
                    docIDs[j] = docIDs[j] - docIDs[j - 1]
                tep_list = []
                dic = {}
                for j in range(len(docIDs)):
                    dic[docIDs[j]] = docFres[j]
                tep_list.append(dic)
                tep_list.append(len(dic))
                return tep_list
        return default

    def __getitem__(self, word, default=None):
        for i in range(len(self.compress_word)):
            if self.compress_word[i] == word:
                # 解码
                docIDs = vb_decode(self.compress_doc_id[i])
                docFres = vb_decode(self.compress_doc_fre[i])
                # 求ID
                for j in range(1, len(docIDs)):
                    docIDs[j] = docIDs[j] - docIDs[j - 1]
                tep_list = []
                dic = {}
                for j in range(len(docIDs)):
                    dic[docIDs[j]] = docFres[j]
                tep_list.append(dic)
                tep_list.append(len(dic))
                return tep_list

class IndexTable:

    def __init__(self, document_words):
        self.tep_table = {}
        self.table = None
        self.tep_table_2 = {}
        self.table_2 = None
        self.document_words = document_words
        self.permuterm_index_table = False
        self.length = 0
        self.length_2 = 0
        self.compress_doc_id = []
        self.compress_doc_fre = []
        self.compress_word = []

    def insert_pair(self, word, docID):
        IDlist = self.tep_table.get(word, 'null')
        if IDlist != 'null':
            if IDlist[0].get(docID, 'null') != 'null':
                IDlist[0][docID] += 1
            else:
                IDlist[0][docID] = 1
                IDlist[1] += 1
        else:
            self.tep_table[word] = [{docID: 1}, 1]
            self.length += 1

    def insert_pair_2(self, word, docID):
        IDlist = self.tep_table_2.get(word, 'null')
        if IDlist != 'null':
            if IDlist.get(docID, 'null') != 'null':
                IDlist[docID] += 1
            else:
                IDlist[docID] = 1
        else:
            self.tep_table_2[word] = {docID: 1}
            self.length_2 += 1

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
        for item in self.table.keys():
            word = item + '$'
            for i in range(len(word)):
                self.permuterm_index_table.add([word[i:] + word[:i],item])
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

    def compute_TFIDF(self, sentence, engine='nltk'):
        if engine == 'nltk':
            sentence = nltk.word_tokenize(sentence)
            # sentence = [word for word in sentence if word not in punctuations]
        scores = {}
        sentence = Counter(sentence)
        for piece in sentence.items():
            doc_list = self.table[piece[0]]
            weight = (1 + math.log10(piece[1])) * math.log10(self.length / doc_list[1])
            for doc in doc_list[0].items():
                if scores.get(doc[0], 'null') != 'null':
                    scores[doc[0]] += (1 + math.log10(doc[1])) * math.log10(self.length / doc_list[1]) * weight
                else:
                    scores[doc[0]] = (1 + math.log10(doc[1])) * math.log10(self.length / doc_list[1]) * weight
        for i in scores.items():
            scores[i[0]] = scores[i[0]] / len(self.document_words[i[0]])
        scores = sorted(scores.items(), key=operator.itemgetter(1), reverse=True)
        return scores

    def compute_TFIDF_with_docID(self, sentence, docID, engine='nltk'):
        if engine == 'nltk':
            sentence = nltk.word_tokenize(sentence)
            # sentence = [word for word in sentence if word not in punctuations]
        score = 0
        sentence = Counter(sentence)
        for piece in sentence.items():
            doc_list = self.table[piece[0]]
            weight = (1 + math.log10(piece[1])) * math.log10(self.length / doc_list[1])
            ret = doc_list[0].get(docID, 'none')
            if ret != 'none':
                score += (1 + math.log10(ret)) * math.log10(self.length / doc_list[1]) * weight
            score = score / len(self.document_words[docID])
        return score

    #布尔检索(表达式长度最大为3)
    def boolean_query(self, expression, doc_list):
        ret = []
        if len(expression) == 1:
            if expression[0] not in ['AND', 'OR', 'NOT']:
                IDlist = self.table.get(expression[0], [{},0])[0]
                ret.extend(sorted(IDlist.keys()))
            else:
                print('Invalid boolean expression.')
        elif len(expression) == 2 and expression[0] == 'NOT':
            IDlist = self.table.get(expression[1], [{},0])[0]
            for id in doc_list:
                if id not in IDlist:
                    ret.append(id)
        elif len(expression) == 3:
            IDlist1 = self.table.get(expression[0], [{},0])[0]
            IDlist2 = self.table.get(expression[2], [{},0])[0]
            if expression[1] == 'AND':
                for id in doc_list:
                    if (id in IDlist1) and (id in IDlist2):
                        ret.append(id)
            elif expression[1] == 'OR':
                for id in doc_list:
                    if (id in IDlist1) or (id in IDlist2):
                        ret.append(id)
            else:
                return 'Invalid boolean expression./n'
        else:
            return 'Invalid boolean expression.'
        return ret

    # 索引压缩(VB编码)
    def index_compression(self):
        words = list(self.tep_table)
        docIDs = []
        docFres = []
        compress_word = []
        compress_doc_id = []
        compress_doc_fre = []
        for word in words:
            docIDs.append(list(self.tep_table[word][0]))
        for i in range(len(docIDs)):
            temp = []
            docIDs[i].sort()
            for j in range(len(docIDs[i])):
                temp.append(self.tep_table[words[i]][0][docIDs[i][j]])
            docFres.append(temp)
        for i in range(len(docIDs)):    # 求间距
            for j in range(1, len(docIDs[i])):
                    docIDs[i][len(docIDs[i]) - j] = docIDs[i][len(docIDs[i]) - j] + docIDs[i][len(docIDs[i]) - j - 1]
        for i in range(len(docIDs)):    # 编码
            compress_doc_id.append(vb_encode(docIDs[i]))
            compress_doc_fre.append(vb_encode(docFres[i]))
        compress_word = words
        self.tep_table = {}
        self.table = CompressTable(compress_doc_id, compress_doc_fre, compress_word)
        #如果有table_2
        words = list(self.tep_table_2)
        docIDs = []
        docFres = []
        compress_word = []
        compress_doc_id = []
        compress_doc_fre = []
        for word in words:
            docIDs.append(list(self.tep_table[word]))
        for i in range(len(docIDs)):
            temp = []
            docIDs[i].sort()
            for j in range(len(docIDs[i])):
                temp.append(self.tep_table[words[i]][docIDs[i][j]])
            docFres.append(temp)
        for i in range(len(docIDs)):    # 求间距
            for j in range(1, len(docIDs[i])):
                    docIDs[i][len(docIDs[i]) - j] = docIDs[i][len(docIDs[i]) - j] + docIDs[i][len(docIDs[i]) - j - 1]
        for i in range(len(docIDs)):    # 编码
            compress_doc_id.append(vb_encode(docIDs[i]))
            compress_doc_fre.append(vb_encode(docFres[i]))
        compress_word = words
        self.tep_table = {}
        self.table = CompressTable(compress_doc_id, compress_doc_fre, compress_word)
    
    #索引打印
    def index_print(self, word):
        for i in range(len(self.table.compress_word)):
            if self.table.compress_word[i] == word:
                print(self.table.compress_doc_id[i])
                print_vb_code(self.table.compress_doc_id[i])
                
    #布尔检索(表达式长度最大为3)
    def boolean_query(self, expression, doc_list):
        ret = []
        if len(expression) == 1:
            if expression[0] not in ['AND', 'OR', 'NOT']:
                IDlist = self.table.get(expression[0], [{},0])[0]
                ret.extend(sorted(IDlist.keys()))
            else:
                print('Invalid boolean expression.')
        elif len(expression) == 2 and expression[0] == 'NOT':
            IDlist = self.table.get(expression[1], [{},0])[0]
            for id in doc_list:
                if id not in IDlist:
                    ret.append(id)
        elif len(expression) == 3:
            IDlist1 = self.table.get(expression[0], [{},0])[0]
            IDlist2 = self.table.get(expression[2], [{},0])[0]
            if expression[1] == 'AND':
                for id in doc_list:
                    if (id in IDlist1) and (id in IDlist2):
                        ret.append(id)
            elif expression[1] == 'OR':
                for id in doc_list:
                    if (id in IDlist1) or (id in IDlist2):
                        ret.append(id)
            else:
                return 'Invalid boolean expression./n'
        else:
            return 'Invalid boolean expression.'
        return ret

    # 布尔检索(表达式长度最大为3)
    def boolean_query(self, words, doc_list):
        priority = {'AND': 1, 'OR': 1, 'NOT': 2, '(': 0}
        stack = []
        op = []
        ret = []
        for i in range(0, len(words)):
            if words[i] == 'AND' or words[i] == 'OR' or words[i] == 'NOT':
                # print op
                while (len(op) > 0) and priority[op[len(op) - 1]] >= priority[words[i]]:
                    stack = self.boolean_op(op.pop(), stack)
                op.append(words[i])
            elif words[i] == '(':
                op.append('(')
            elif words[i] == ')':
                while len(op) > 0 and op[len(op) - 1] != '(':
                    stack = boolean_op(op.pop(), stack)
                op.pop()
            else:
                vec = vector_encode(self.table.get(words[i], [{},0])[0], doc_list)
                stack.append(vec)				

        while len(op) > 0:
            stack = boolean_op(op.pop(), stack)
        if len(stack) > 1:
            return 'Invalid boolean expression.'
        res = stack[0]
        ret = vector_decode(res, doc_list)
        return ret

    def correction(self, word):
        print('correcting...')
        t = time.time()
        candidates = []
        for key in self.table.keys():
            if abs(len(word)-len(key)) < 3 and Levenshtein_Distance(word, key) < 3:
                candidates.append(key)
        if len(candidates):
            print('You may want to search:')
            print(' '.join(candidates))
        print(time.time() - t)

    def phrase_query(self, args, engine='nltk'):
        if engine == 'nltk':
            sentence = nltk.word_tokenize(args)
        docs = []
        for i in range(len(sentence)-1):
            ret = self.table_2.get(sentence[i]+' '+sentence[i+1], 'none')
            if ret == 'none': return []
            docs.append(set(ret[0].keys()))
        docs = set.intersection(*docs)
        docs_filterd = []
        for doc in docs:
            for i in range(len(self.document_words[doc])):
                seed = False
                if i == sentence[0]:
                    for index, token in enumerate(sentence):
                        if token != self.document_words[doc][i + index]:
                            seed = True
                            break
                if seed == False:
                    docs_filterd.append(doc)

        return docs_filterd


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
    objects.indextable = IndexTable(objects.document_words)

    for words in objects.document_words.items():
        for word in words[1]:
            objects.indextable.insert_pair(word, words[0])
        for i in range(len(words[1]) - 1):
            objects.indextable.insert_pair_2(words[1][i] + ' ' + words[1][i+1], words[0])
    # print(objects.indextable.table)
    print('Finished loading and build index. Elasped time: ', time.time() - t, 's')
    return objects


def tokenize(documents, engine='nltk'):
    document_words = {}
    for _doc in documents.items():
        if engine == 'nltk':
            doc = nltk.word_tokenize(_doc[1])
        # doc_filtered = [word for word in doc if word not in punctuations]
        document_words[_doc[0]] = doc
    return document_words

def Levenshtein_Distance(str1,str2):
    m = len(str1)
    n = len(str2)
    M = np.zeros((m+1, n+1))
    flag = 0
    for i in range(m+1):
        M[i][0] = i
    for j in range(n+1):
        M[0][j] = j
    for i in range(1, m+1):
        flag = 1
        for j in range(1, n+1):
            if str1[i-1] == str2[j-1]:
                M[i][j] = min(M[i-1][j]+1, M[i][j-1]+1, M[i-1][j-1])
            else:
                M[i][j] = min(M[i-1][j]+1, M[i][j-1]+1, M[i-1][j-1]+1)
            if M[i][j] < 3:
                flag = 0
        if flag == 1:
            return 10
    return int(M[m][n])

if __name__ == '__main__':
    t = time.time()
    object = process('C:/Users/Night/Desktop/Reuters_test')
    # object.indextable.create_Permuterm_index()
    # object.indextable.find_regex_words('b*g*n')
    # object.indextable.index_compression()
    # object.indextable.index_recovery()
    print(object.indextable.compute_TFIDF('we are'))
    t = time.time() - t
    print(t)

