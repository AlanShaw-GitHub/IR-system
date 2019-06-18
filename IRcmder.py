# -*- coding: utf-8 -*-
import cmd
import sys
from InvertedIndexTable import process
import operator

class IRcmder(cmd.Cmd):
    intro = 'Welcome to the Information Retrival System.\nType help or ? to list commands.\n'

    def __init__(self):
        super(IRcmder, self).__init__()
        self.k = 10

    def do_change_k(self, args):
        self.k = int(args)

    def do_phrase_query(self, args):
        ret = self.object.indextable.phrase_query(args)
        scores = {}
        for i in ret:
            scores[i] = self.object.indextable.compute_TFIDF_with_docID(args, i)
        scores = sorted(scores.items(), key=operator.itemgetter(1), reverse=True)
        for index, i in enumerate(scores):
            if index > self.k: break
            print(i)
        # build ../Reuters
        # phrase_query information technology

    def do_build(self, args):
        self.object = process(args)
        self.object.indextable.index_compression()

    def do_create_Permuterm_index(self, args):
        self.object.indextable.create_Permuterm_index()

    def do_wildcard_query(self, args):
        if not self.object.indextable.permuterm_index_table:
            self.object.indextable.create_Permuterm_index()
        ret = self.object.indextable.find_regex_words(args)
        print('searched words: ', ret)
        ret = self.object.indextable.compute_TFIDF(' '.join(ret))
        print('Top-%d rankings:' % self.k)
        for index, i in enumerate(ret):
            if index > self.k: break
            print(i)

    def do_search_by_TFIDF(self, args):
        ret = self.object.indextable.compute_TFIDF(args)
        print('Top-%d rankings:' % self.k)
        for index, i in enumerate(ret):
            if index > self.k: break
            print(i)
        # build Reuters
        # search_by_TFIDF approximately


    #布尔查询
    def do_boolean_query(self, args):
        expression = args.replace('(',' ( ').replace(')',' ) ').split()
        doc_list = sorted(self.object.documents.keys())
        ret = self.object.indextable.boolean_query(expression, doc_list)
        if ret == []:
            print('Not found.')
            if len(expression) == 1:
                self.object.indextable.correction(expression[0])
        else:
            print(ret)
    
    #索引打印
    def do_index_print(self, args):
        self.object.indextable.index_print(args)

    def do_quit(self, args):
        print('Goodbye.')
        sys.exit()

    def emptyline(self):
        pass

    def default(self, line):
        print('Unrecognized command.\nNo such symbol : %s' % line)

    def help_build(self):
        print('Path to Reuters.')

    def help_boolean_query(self):
        print('Support operator:AND OR NOT.\nMaximum expression length: 3.')

    def help_index_print(self):
        print('Print index in VB code.\n')
        
if __name__ == '__main__':

    print("Information Retrival System, version 1.0.0-release\n"
          "Copyright 2019 @ Alan Shaw from ZJU. Course final project for IR.\n"
          "These shell commands are defined internally.  Type `help' to see this list.\n"
          "Type `help name' to find out more about the function `name'.\n")

    IRcmder.prompt = 'IR-Cmder > '
    IRcmder().cmdloop()

