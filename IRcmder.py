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
        try:
            self.k = int(args)
        except Exception as e:
            print(e)
        
    def do_phrase_query(self, args):
        try:
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
        except Exception as e:
            print(e)

    def do_build(self, args):
        try:
            self.object = process(args)
            self.object.indextable.index_compression()
        except Exception as e:
            print(e)

    def do_create_Permuterm_index(self, args):
        try:
            self.object.indextable.create_Permuterm_index()
        except Exception as e:
            print(e)

    def do_wildcard_query(self, args):
        try:
            if not self.object.indextable.permuterm_index_table:
                self.object.indextable.create_Permuterm_index()
            ret = self.object.indextable.find_regex_words(args)
            print('searched words: ', ret)
            ret = self.object.indextable.compute_TFIDF(' '.join(ret))
            print('Top-%d rankings:' % self.k)
            for index, i in enumerate(ret):
                if index > self.k: break
                print(i)
        except Exception as e:
            print(e)
            
    def do_search_by_TFIDF(self, args):
        try:
            ret = self.object.indextable.compute_TFIDF(args)
            print('Top-%d rankings:' % self.k)
            for index, i in enumerate(ret):
                if index > self.k: break
                print(i)
            # build Reuters
            # search_by_TFIDF approximately
        except Exception as e:
            print(e)

    #布尔查询
    def do_boolean_query(self, args):
        try:
            expression = args.replace('(',' ( ').replace(')',' ) ').split()
            doc_list = sorted(self.object.documents.keys())
            ret = self.object.indextable.boolean_query(expression, doc_list)
            if ret == []:
                print('Not found.')
                if len(expression) == 1:
                    self.object.indextable.correction(expression[0])
            else:
                print(ret)
        except Exception as e:
            print(e)                
                
    #模糊查询
    def do_fuzzy_query(self,args):
        try:
#             if not self.object.indextable.permuterm_index_table:
#                 self.object.indextable.create_Permuterm_index()
            candidate,ret = self.object.indextable.fuzzy_query(args)
            if candidate == ret:
                print(candidate)
            else:
                scores = self.object.indextable.compute_TFIDF(candidate)
                print('Found '+str(len(scores))+' documents that matched query')
                rank = 0
                for score in scores:
                    if rank <=20:
                        print('doc name:'+str(score[0])+'.html score '+str(score[1]))
                        rank = rank+1
                    else:
                        break
        except Exception as e:
            print(e)                    
                    
    #同义词查询
    def do_synonym_query(self,args):
        try:
            self.object.indextable.synonym_query(args)
        except Exception as e:
            print(e)            
        
    #索引打印
    def do_index_print(self, args):
        try:
            self.object.indextable.index_print(args)
        except Exception as e:
            print(e)            

    def do_quit(self, args):
        try:
            print('Goodbye.')
            sys.exit()
        except Exception as e:
            print(e)            

    def emptyline(self):
        pass

    def default(self, line):
        print('Unrecognized command.\nNo such symbol : %s' % line)

    def help_build(self):
        print('Path to Reuters.')

    def help_boolean_query(self):
        print('Support operator:AND OR NOT.\nMaximum expression length: 3.')

    def help_fuzzy_query(self):
        print('Support fuzzy query of one word')
        print('You can input like this: fuzzy_query approxmtely')

    def help_synonym_query(self):
        print('Support synonym query of one word')
        print('You can input like this: synonym_query absolutely')


    def help_index_print(self):
        print('Print index in VB code.\n')
        
if __name__ == '__main__':

    print("Information Retrival System, version 1.0.0-release\n"
          "Copyright 2019 @ Alan Shaw from ZJU. Course final project for IR.\n"
          "These shell commands are defined internally.  Type `help' to see this list.\n"
          "Type `help name' to find out more about the function `name'.\n")

    IRcmder.prompt = 'IR-Cmder > '
    IRcmder().cmdloop()

