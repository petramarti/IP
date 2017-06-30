"""31.siječnja 2014"""
from pj import *

class POLJA(enum.Enum):
    TOČKAZAREZ=';'
    OTV='['
    ZATV=']'
    PRIDRUŽI='='
    CHAR='char'
    INT='int'
    FLOAT='float'
    BOOL='bool'
    IME='polje'
    BROJ=123
    PRINT='print'

def polja_lex(kôd):
    lex=Tokenizer(kôd)
    for znak in iter(lex.čitaj, ''):
        if znak.isspace(): lex.token(E.PRAZNO)
        elif znak.isalpha():
            lex.zvijezda(str.isalnum)
            yield lex.token(ključna_riječ(POLJA,lex.sadržaj,False) or POLJA.IME)
##            if lex.sadržaj=="char" : yield lex.token(POLJA.CHAR)
##            elif lex.sadržaj=="int": yield lex.token(POLJA.INT)
##            elif lex.sadržaj=="float": yield lex.token(POLJA.FLOAT)
##            elif lex.sadržaj=="bool": yield lex.token(POLJA.BOOL)
##            elif lex.sadržaj=="print": yield lex.token(POLJA.PRINT)
##            else: yield lex.token(POLJA.IME)
        elif znak.isdigit():
            lex.zvijezda(str.isdigit)
            yield lex.token(POLJA.BROJ)
        else:
            yield lex.token(operator(POLJA,znak) or lex.greška())

### Beskontekstna gramatika
# start ->  deklaracija naredbe
# naredbe -> ''|naredba naredbe
# naredba -> deklaracija | ispis | pridruživanje TOČKAZAREZ
# deklaracija -> tip IME (''|OTV BROJ ZATV)
# tip -> CHAR|INT|FLOAT|BOOL
# pridruživanje -> IME (''|OTV BROJ ZATV) PRIDRUŽI BROJ
# ispis -> PRINT IME (''| BROJ BROJ)

### Apstraktna stabla
# Skripta: naredbe
# Deklaracija: tip, ime, polje - deklarira varijablu određenog tip, imena i pamti je li polje ili ne
# Pridruživanje: ime, mjesto, vrijednost - mjesto je -1 po defaultu
# Ispis: ime, od, do - od i do su -1 po defaultu

class POLJAParser(Parser):
    def deklaracija(self):
        tip=self.zadnji
        ime=self.pročitaj(POLJA.IME)
        polje=0
        if self >> POLJA.OTV:
            self.pročitaj(POLJA.BROJ)
            self.pročitaj(POLJA.ZATV)
            polje=1
        return Deklaracija(tip,ime,polje)
    def ispis(self):
        ime=self.pročitaj(POLJA.IME)
        od=do=-1
        if self >> POLJA.BROJ:
            od=self.zadnji
            do=self.pročitaj(POLJA.BROJ)
        return Ispis(ime,od,do)
    def pridruživanje():
        ime=self.zadnji
        mjesto=-1
        if self >> POLJA.OTV:
            mjesto=self.pročitaj(POLJA.BROJ)
            self.pročitaj(POLJA.ZATV)
        self.pročitaj(POLJA.PRIDRUŽIVANJE)
        vrijednost=self.pročitaj(POLJA.BROJ)
        return Pridruživanje(ime,mjesto,vrijednost)
    def naredba(self):
        if self >> POLJA.PRINT: rezultat=self.ispis()
        elif self >> POLJA.CHAR: rezultat=self.deklaracija()
        elif self >> POLJA.INT: rezultat=self.deklaracija()
        elif self >> POLJA.FLOAT: rezultat=self.deklaracija()
        elif self >> POLJA.BOOL: rezultat=self.deklaracija()
        elif self >> POLJA.IME: rezultat=self.pridruživanje()
        self.pročitaj(POLJA.TOČKAZAREZ)
        return rezultat
    def start(self):
        naredbe=[self.naredba()]
        while not self >> E.KRAJ: naredbe.append(self.naredba())
        return Skripta(naredbe)

class Skripta(AST('naredbe')):
    def razriješi(self):
        varijable = {}
        for naredba in self.naredbe: naredba.razriješi(varijable)
        return varijable
class Deklaracija(AST('tip ime polje')):
    def razriješi(self,varijable):
        if self.ime in varijable:
            self.ime.nedeklaracija('postojeća varijabla')
        else:
            var=varijable[self.ime]={"tip":tip, "polje":polje}
class Ispis(AST('ime od do')):
    def razriješi(self,varijable):
        p=varijable["ispisane"]=[]
        if self.ime not in varijable:
            self.ime.nedeklaracija('nepostojeća varijabla')
        if od==-1 and do==-1:
            if varijable[self.ime]["polje"]: p.append

if __name__ == '__main__':
    print(*polja_lex('int polje[123]; char s;'))
