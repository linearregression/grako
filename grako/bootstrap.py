from grammar import * #@UnusedWildImport
from parsing import * #@UnusedWildImport

__all__ = ['GrakoGrammar', 'GrakoParserGenerator']

class GrakoGrammarBase(Grammar):

    def _void_(self):
        self._token('()', 'void')

    def _token_(self):
        p = self._pos
        try:
            self._token("'")
            self._pattern(r"(?:[^'\\]|\\')*", 'token')
            self._token("'")
            return
        except FailedCut as e:
            raise e.nested
        except FailedParse:
            pass
        self._goto(p)
        try:
            self._token('"')
            self._pattern(r'(?:[^"\\]|\\")*', 'token')
            self._token('"')
            return
        except FailedCut as e:
            raise e.nested
        except FailedParse:
            pass
        self._goto(p)
        raise FailedParse(self._buffer, '<"> or' + "<'>")

    def _word_(self):
        self._pattern(r'[A-Za-z0-9_]+', 'word')

    def _call_(self):
        self._call('word', 'call')

    def _pattern_(self):
        self._token('?/')
        self._pattern(r'(.*?)(?=/\?)', 'pattern')
        self._token('/?')

    def _cut_(self):
        self._token('!', 'cut')

    def _subexp_(self):
        self._token('(')
        self._call('expre', 'exp')
        self._token(')')

    def _optional_(self):
        self._token('[')
        self._call('expre', 'optional')
        self._token(']')

    def _plus_(self):
        if not self._try('-', 'symbol'):
            self._token('+', 'symbol')

    def _repeat_(self):
        self._token('{')
        self._call('expre', 'repeat')
        self._token('}')
        try:
            self._call('plus', 'plus')
        except FailedParse:
            pass

    def _special_(self):
        self._token('?(')
        self._pattern(r'(.*)\)?', 'special')

    def _atom_(self):
        p = self._pos
        try:
            self._call('void', 'atom')
            return
        except FailedCut as e:
            raise e.nested
        except FailedParse:
            pass
        self._goto(p)
        try:
            self._call('cut', 'atom')
            return
        except FailedCut as e:
            raise e.nested
        except FailedParse:
            pass
        self._goto(p)
        try:
            self._call('token', 'atom')
            return
        except FailedCut as e:
            raise e.nested
        except FailedParse:
            pass
        self._goto(p)
        try:
            self._call('call', 'atom')
            return
        except FailedCut as e:
            raise e.nested
        except FailedParse:
            pass
        self._goto(p)
        try:
            self._call('pattern', 'atom')
            return
        except FailedCut as e:
            raise e.nested
        except FailedParse:
            pass
        self._goto(p)
        raise FailedParse(self._buffer, 'atom')


    def _term_(self):
        p = self._pos
        try:
            self._call('atom', 'term')
            return
        except FailedCut as e:
            raise e.nested
        except FailedParse:
            pass
        self._goto(p)
        try:
            self._call('subexp', 'term')
            return
        except FailedCut as e:
            raise e.nested
        except FailedParse:
            pass
        self._goto(p)
        try:
            self._call('repeat', 'term')
            return
        except FailedCut as e:
            raise e.nested
        except FailedParse:
            pass
        self._goto(p)
        try:
            self._call('optional', 'term')
            return
        except FailedCut as e:
            raise e.nested
        except FailedParse:
            pass
        self._goto(p)
        try:
            self._call('special', 'term')
            return
        except FailedCut as e:
            raise e.nested
        except FailedParse:
            pass
        self._goto(p)
        raise FailedParse(self._buffer, 'term')

    def _named_(self):
        self._call('word', 'name')
        self._token(':')
        try:
            self._call('term', 'value')
            return
        except FailedParse as e:
            raise FailedCut(self._buffer, e)

    def _element_(self):
        p = self._pos
        try:
            self._call('named', 'named')
            return
        except FailedCut as e:
            raise e.nested
        except FailedParse:
            pass
        self._goto(p)
        try:
            self._call('term', 'element')
            return
        except FailedCut as e:
            raise e.nested
        except FailedParse:
            pass
        self._goto(p)
        raise FailedParse(self._buffer, 'element')

    def _sequence_(self):
#        p = self._pos
#        try:
#            self._call('element', 'sequence')
#        except FailedParse:
#            self._goto(p)
#            raise
        while True:
            p = self._pos
            try:
                if not self._try('!'):
                    self._try(',')
                    self._call('element', 'sequence')
                else:
                    try:
                        # insert cut node here
                        self._call('sequence', 'sequence')
                    except FailedParse as e:
                        raise FailedCut(self._buffer, e)
            except FailedCut:
                self._goto(p)
                raise
            except FailedParse:
                self._goto(p)
                break


    def _choice_(self):
        self._call('sequence', 'options')
        while True:
            p = self._pos
            try:
                self._token('|')
                self._call('sequence', 'options')
            except FailedCut as e:
                self._goto(p)
                raise e.nested
            except FailedParse:
                self._goto(p)
                break

    def _expre_(self):
        self._call('choice', 'expre')

    def _rule_(self):
        self._call('word', 'name')
        self._token('=')
        self._call('expre', 'rhs')
        if not self._try(';'):
            self._token('.')

    def _grammar_(self):
        self._call('rule', 'rules')
        while True:
            p = self._pos
            try:
                self._call('rule', 'rules')
            except FailedParse:
                self._goto(p)
                break
        self._next_token()
        self._eof()


class AbstractGrakoGrammar(GrakoGrammarBase):
    def token(self, ast):
        return ast

    def word(self, ast):
        return ast

    def pattern(self, ast):
        return ast

    def cut(self, ast):
        return ast

    def subexp(self, ast):
        return ast

    def optional(self, ast):
        return ast

    def repeat(self, ast):
        return ast

    def special(self, ast):
        return ast

    def atom(self, ast):
        return ast


    def term(self, ast):
        return ast.term

    def named(self, ast):
        return ast

    def element(self, ast):
        return ast

    def sequence(self, ast):
        return ast

    def choice(self, ast):
        return ast

    def expre(self, ast):
        return ast

    def rule(self, ast):
        return ast

    def grammar(self, ast):
        return ast


class GrakoGrammar(AbstractGrakoGrammar):
    @staticmethod
    def _simplify(x):
        if isinstance(x, list) and len(x) == 1:
            return GrakoGrammar._simplify(x[0])
        return x

    def token(self, ast):
        return ast

    def word(self, ast):
        return ast

    def call(self, ast):
        return ast

    def pattern(self, ast):
        return ast

    def cut(self, ast):
        return ast

    def subexp(self, ast):
        return self._simplify(ast.exp)

    def optional(self, ast):
        return ast

    def plus(self, ast):
        return ast

    def repeat(self, ast):
        return ast

    def special(self, ast):
        return ast

    def atom(self, ast):
        return self._simplify(ast.atom[0])

    def term(self, ast):
        return self._simplify(ast.term[0])

    def named(self, ast):
        return ast

    def element(self, ast):
        if 'named' in ast:
            return ast
        return ast.element

    def sequence(self, ast):
        return self._simplify(ast.sequence)

    def choice(self, ast):
        if len(ast.options) == 1:
            return ast.options
        return ast

    def expre(self, ast):
        return self._simplify(ast.expre)

    def rule(self, ast):
        return ast

    def grammar(self, ast):
        return ast


class GrakoParserGenerator(AbstractGrakoGrammar):
    def token(self, ast):
        return TokenParser(ast.token)

    def word(self, ast):
        return ast.word

    def call(self, ast):
        return RuleRefParser(ast.call)

    def pattern(self, ast):
        return PatternParser(ast.pattern)

    def cut(self, ast):
        return CutParser()

    def subexp(self, ast):
        return GroupParser(ast.exp)

    def optional(self, ast):
        return OptionalParser(ast.optional)

    def plus(self, ast):
        return ast

    def repeat(self, ast):
        if ast.plus:
            return RepeatOneParser(ast.repeat)
        return RepeatParser(ast.repeat)

    def special(self, ast):
        return SpecialParser(ast.special)

    def atom(self, ast):
        return ast.atom

    def term(self, ast):
        return ast.term

    def named(self, ast):
        return NamedParser(ast.name, ast.value)

    def element(self, ast):
        return ast.element

    def sequence(self, ast):
        if isinstance(ast.sequence, list):
            if len(ast.sequence) == 1:
                return ast.sequence[0]
            return SequenceParser(ast.sequence)
        return ast.sequence

    def choice(self, ast):
        if isinstance(ast.options, list):
            return ChoiceParser(ast.options)
        return ast.options

    def expre(self, ast):
        return ast.expre

    def rule(self, ast):
        return RuleParser(ast.name, ast.rhs)

    def grammar(self, ast):
        return GrammarParser('grammar', ast.rules)

