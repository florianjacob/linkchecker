"""
             out  -- created Sun Dec 14 21:41:11 1997

This file was automatically generated by the PyLR parser generator.
It defines the tables 'actiontable', 'gototable', and 'prodinfo'.  These 
tables are used to give functionality to a parsing engine.  It also defines
A Parser class called GrammarParser which will use this engine.  It's Usage is 
indicated in GrammarParser's doc-string.
"""
#
# this section contains source code added by the user 
# plus 'import PyLR'
#

import PyLR.Lexers
import PyLR.Parser
import PyLR

#
# the action table ('s', 4) means shift to state 4, 
# ('r', 4) means reduce by production number 4
# other entries are errors.  each row represents a state
# and each column a terminal lookahead symbol (plus EOF)
# these symbols are ['LEX', 'CODE', 'CLASS', 'ID', 'COLON', 'SCOLON', 'OR', 'LPAREN', 'RPAREN', 'GDEL', 'EOF']
#
_actiontable = [
	[('s', 10), ('s', 11), ('s', 12), ('', -1), ('', -1), ('', -1), ('', -1), ('', -1), ('', -1), ('s', 5), ('', -1)],
	[('', -1), ('', -1), ('', -1), ('', -1), ('', -1), ('', -1), ('', -1), ('', -1), ('', -1), ('', -1), ('a', -1)],
	[('', -1), ('', -1), ('', -1), ('', -1), ('', -1), ('', -1), ('', -1), ('', -1), ('', -1), ('', -1), ('r', 1)],
	[('s', 10), ('s', 11), ('s', 12), ('', -1), ('', -1), ('', -1), ('', -1), ('', -1), ('', -1), ('s', 5), ('', -1)],
	[('', -1), ('', -1), ('', -1), ('', -1), ('', -1), ('', -1), ('', -1), ('', -1), ('', -1), ('', -1), ('r', 2)],
	[('', -1), ('', -1), ('', -1), ('s', 15), ('', -1), ('', -1), ('', -1), ('', -1), ('', -1), ('', -1), ('', -1)],
	[('', -1), ('', -1), ('', -1), ('s', 15), ('', -1), ('', -1), ('', -1), ('', -1), ('', -1), ('s', 7), ('', -1)],
	[('', -1), ('', -1), ('', -1), ('', -1), ('', -1), ('', -1), ('', -1), ('', -1), ('', -1), ('', -1), ('r', 3)],
	[('r', 4), ('r', 4), ('r', 4), ('', -1), ('', -1), ('', -1), ('', -1), ('', -1), ('', -1), ('r', 4), ('', -1)],
	[('r', 5), ('r', 5), ('r', 5), ('', -1), ('', -1), ('', -1), ('', -1), ('', -1), ('', -1), ('r', 5), ('', -1)],
	[('r', 6), ('r', 6), ('r', 6), ('', -1), ('', -1), ('', -1), ('', -1), ('', -1), ('', -1), ('r', 6), ('', -1)],
	[('r', 7), ('r', 7), ('r', 7), ('', -1), ('', -1), ('', -1), ('', -1), ('', -1), ('', -1), ('r', 7), ('', -1)],
	[('r', 8), ('r', 8), ('r', 8), ('', -1), ('', -1), ('', -1), ('', -1), ('', -1), ('', -1), ('r', 8), ('', -1)],
	[('', -1), ('', -1), ('', -1), ('r', 9), ('', -1), ('', -1), ('', -1), ('', -1), ('', -1), ('r', 9), ('', -1)],
	[('', -1), ('', -1), ('', -1), ('r', 10), ('', -1), ('', -1), ('', -1), ('', -1), ('', -1), ('r', 10), ('', -1)],
	[('', -1), ('', -1), ('', -1), ('', -1), ('s', 16), ('', -1), ('', -1), ('', -1), ('', -1), ('', -1), ('', -1)],
	[('', -1), ('', -1), ('', -1), ('s', 28), ('', -1), ('r', 17), ('r', 17), ('r', 17), ('', -1), ('', -1), ('', -1)],
	[('', -1), ('', -1), ('', -1), ('', -1), ('', -1), ('s', 18), ('s', 20), ('', -1), ('', -1), ('', -1), ('', -1)],
	[('', -1), ('', -1), ('', -1), ('r', 11), ('', -1), ('', -1), ('', -1), ('', -1), ('', -1), ('r', 11), ('', -1)],
	[('', -1), ('', -1), ('', -1), ('', -1), ('', -1), ('r', 12), ('r', 12), ('', -1), ('', -1), ('', -1), ('', -1)],
	[('', -1), ('', -1), ('', -1), ('s', 28), ('', -1), ('r', 17), ('r', 17), ('r', 17), ('', -1), ('', -1), ('', -1)],
	[('', -1), ('', -1), ('', -1), ('', -1), ('', -1), ('r', 13), ('r', 13), ('', -1), ('', -1), ('', -1), ('', -1)],
	[('', -1), ('', -1), ('', -1), ('', -1), ('', -1), ('r', 14), ('r', 14), ('s', 23), ('', -1), ('', -1), ('', -1)],
	[('', -1), ('', -1), ('', -1), ('s', 24), ('', -1), ('', -1), ('', -1), ('', -1), ('', -1), ('', -1), ('', -1)],
	[('', -1), ('', -1), ('', -1), ('', -1), ('', -1), ('', -1), ('', -1), ('', -1), ('s', 25), ('', -1), ('', -1)],
	[('', -1), ('', -1), ('', -1), ('', -1), ('', -1), ('r', 15), ('r', 15), ('', -1), ('', -1), ('', -1), ('', -1)],
	[('', -1), ('', -1), ('', -1), ('s', 27), ('', -1), ('r', 16), ('r', 16), ('r', 16), ('', -1), ('', -1), ('', -1)],
	[('', -1), ('', -1), ('', -1), ('r', 18), ('', -1), ('r', 18), ('r', 18), ('r', 18), ('', -1), ('', -1), ('', -1)],
	[('', -1), ('', -1), ('', -1), ('r', 19), ('', -1), ('r', 19), ('r', 19), ('r', 19), ('', -1), ('', -1), ('', -1)]
]



#
# the goto table, each row represents a state
# and each column, the nonterminal that was on the lhs of the
# reduction
#
_gototable = [
	[1, 2, 3, 9, None, None, None, None, None, None],
	[None, None, None, None, None, None, None, None, None, None],
	[None, None, None, None, None, None, None, None, None, None],
	[None, 4, None, 8, None, None, None, None, None, None],
	[None, None, None, None, None, None, None, None, None, None],
	[None, None, None, None, 6, 14, None, None, None, None],
	[None, None, None, None, None, 13, None, None, None, None],
	[None, None, None, None, None, None, None, None, None, None],
	[None, None, None, None, None, None, None, None, None, None],
	[None, None, None, None, None, None, None, None, None, None],
	[None, None, None, None, None, None, None, None, None, None],
	[None, None, None, None, None, None, None, None, None, None],
	[None, None, None, None, None, None, None, None, None, None],
	[None, None, None, None, None, None, None, None, None, None],
	[None, None, None, None, None, None, None, None, None, None],
	[None, None, None, None, None, None, None, None, None, None],
	[None, None, None, None, None, None, 17, 19, 22, 26],
	[None, None, None, None, None, None, None, None, None, None],
	[None, None, None, None, None, None, None, None, None, None],
	[None, None, None, None, None, None, None, None, None, None],
	[None, None, None, None, None, None, None, 21, 22, 26],
	[None, None, None, None, None, None, None, None, None, None],
	[None, None, None, None, None, None, None, None, None, None],
	[None, None, None, None, None, None, None, None, None, None],
	[None, None, None, None, None, None, None, None, None, None],
	[None, None, None, None, None, None, None, None, None, None],
	[None, None, None, None, None, None, None, None, None, None],
	[None, None, None, None, None, None, None, None, None, None],
	[None, None, None, None, None, None, None, None, None, None]
]



#
# This is the prodinfo table.  each row represents a production
# the entries are the length of the production, the name of a method 
# in an instance of the GrammarParser class below that gets called 
# when that production occurs, and the index of the lhs in the 
# nonterminals (as in # the gototable)
#
_prodinfo = [
	(1, 'unspecified', 0),       # pspec -> ['gspec']
	(2, 'unspecified', 0),       # pspec -> ['pydefs', 'gspec']
	(3, 'unspecified', 1),       # gspec -> ['GDEL', 'lhsdeflist', 'GDEL']
	(2, 'unspecified', 2),       # pydefs -> ['pydefs', 'pydef']
	(1, 'unspecified', 2),       # pydefs -> ['pydef']
	(1, 'lexdef', 3),            # pydef -> ['LEX']
	(1, 'addcode', 3),           # pydef -> ['CODE']
	(1, 'classname', 3),         # pydef -> ['CLASS']
	(2, 'unspecified', 4),       # lhsdeflist -> ['lhsdeflist', 'lhsdef']
	(1, 'unspecified', 4),       # lhsdeflist -> ['lhsdef']
	(4, 'lhsdef', 5),            # lhsdef -> ['ID', 'COLON', 'rhslist', 'SCOLON']
	(1, 'singletolist', 6),      # rhslist -> ['rhs']
	(3, 'rhslist_OR_rhs', 6),    # rhslist -> ['rhslist', 'OR', 'rhs']
	(1, 'rhs_idlist', 7),        # rhs -> ['rhsidlist']
	(4, 'rhs_idlist_func', 7),   # rhs -> ['rhsidlist', 'LPAREN', 'ID', 'RPAREN']
	(1, 'unspecified', 8),       # rhsidlist -> ['idlist']
	(0, 'rhseps', 8),            # rhsidlist -> []
	(2, 'idl_idlistID', 9),      # idlist -> ['idlist', 'ID']
	(1, 'idlistID', 9),          # idlist -> ['ID']
	]




class GrammarParser (PyLR.Parser.Parser):
    """
    this class was produced automatically by the PyLR parser generator.
    It is meant to be subclassed to produce a parser for the grammar

pspec -> gspec                                         (unspecified)
        | pydefs gspec;                                (unspecified)
gspec -> GDEL lhsdeflist GDEL;                         (unspecified)
pydefs -> pydefs pydef                                 (unspecified)
        | pydef;                                       (unspecified)
pydef -> LEX                                           (lexdef)
        | CODE                                         (addcode)
        | CLASS;                                       (classname)
lhsdeflist -> lhsdeflist lhsdef                        (unspecified)
        | lhsdef;                                      (unspecified)
lhsdef -> ID COLON rhslist SCOLON;                     (lhsdef)
rhslist -> rhs                                         (singletolist)
        | rhslist OR rhs;                              (rhslist_OR_rhs)
rhs -> rhsidlist                                       (rhs_idlist)
        | rhsidlist LPAREN ID RPAREN;                  (rhs_idlist_func)
rhsidlist -> idlist                                    (unspecified)
        | ;                                            (unspecified)
idlist -> idlist ID                                    (idl_idlistID)
        | ID;                                          (idlistID)

    While parsing input, if one of the above productions is recognized,
    a method of your sub-class (whose name is indicated in parens to the 
    right) will be invoked. Names marked 'unspecified' should be ignored. 
    
    usage: 

class MyGrammarParser(GrammarParser):
    # ...define the methods for the productions... 

p = MyGrammarParser(); p.parse(text)
    """

    def __init__(self):
	lexer = PyLR.Lexers.GrammarLex()
	PyLR.Parser.Parser.__init__(self, lexer, _actiontable, _gototable, _prodinfo)
