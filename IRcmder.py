import cmd
import sys
from InvertedIndexTable import process

class IRcmder(cmd.Cmd):
    intro = 'Welcome to the Information Retrival System.\nType help or ? to list commands.\n'

    def do_build(self, args):
        self.object = process(args)

    def do_create_Permuterm_index(self, args):
        self.object.indextable.create_Permuterm_index()

    def do_wildcard_query(self, args):
        if not self.object.permuterm_index_table:
            self.object.indextable.create_Permuterm_index()
        ret = self.object.indextable.find_regex_words(args)
        print(ret)

    def do_search_by_TFIDF(self, args):

        ret = self.object.indextable.compute_TFIDF(args)
        print(ret)

    def do_quit(self, args):
        print('Goodbye.')
        sys.exit()

    def emptyline(self):
        pass

    def default(self, line):
        print('Unrecognized command.\nNo such symbol : %s' % line)

    def help_build(self):
        print('Path to Reuters.')


if __name__ == '__main__':

    print("Information Retrival System, version 1.0.0-release\n"
          "Copyright 2019 @ Alan Shaw from ZJU. Course final project for IR.\n"
          "These shell commands are defined internally.  Type `help' to see this list.\n"
          "Type `help name' to find out more about the function `name'.\n")

    IRcmder.prompt = 'IR-Cmder > '
    IRcmder().cmdloop()

