"""19.veljače 2016."""
from pj import *

class SET(enum.Enum):
    RIJEČ='abc'
    SKUP='SKUP'
    IME='S123'
    ISPISI='ISPISI'
    PLUSJ='+='
    MINUSJ='-='
    MINUS='-'
    UPITNIK='?'
    OTV='['
    ZATV=']'

def set_lex(kod):
    lex=Tokenizer(kod)
    for znak in iter(lex.čitaj,''):
        if znak.isspace():lex.token(E.PRAZNO)
        elif znak=='+':
            t=lex.čitaj()
            if t=='=': yield lex.token(SET.PLUSJ)
            else: yield lex.greška()
        elif znak=='-':
            t=lex.čitaj()
            if t=='=': yield lex.token(SET.MINUSJ)
            else:
                lex.vrati()
                yield lex.token(SET.MINUS)
        elif znak.isalpha():
            lex.zvijezda(str.isalpha)
            if lex.sadržaj.isupper() and lex.sadržaj not in ['SKUP','ISPISI']:
                lex.zvijezda(str.isdigit)
                yield lex.token(SET.IME)
            elif lex.sadržaj.islower() and lex.sadržaj not in ['skup','ispisi']:
                yield lex.token(SET.RIJEČ)
            else:
                yield lex.token(ključna_riječ(SET,lex.sadržaj,False) or lex.greška())
        else:
            yield lex.token(operator(SET,lex.sadržaj) or lex.greška())

class SETParser(Parser):
    def start(self):
        naredbe=[]
        while not self >> E.KRAJ:
            naredbe.append(self.naredba())
        return Program(naredbe)
    def naredba(self):
        if self >> SET.SKUP: rezultat=self.deklaracija()
        elif self >> SET.ISPISI: rezultat=self.ispis()
        elif self >> SET.IME: rezultat=self.operacija(self.zadnji)
        else: self.greška()
        return rezultat
    def deklaracija(self):
        ime=self.pročitaj(SET.IME)
        return Deklaracija(ime)
    def ispis(self):
        slovo1,slovo2='a','z'
        ime=self.pročitaj(SET.IME)
        if self >> SET.OTV:
            slovo1=self.pročitaj(SET.RIJEČ)
            slovo1=slovo1.sadržaj
            self.pročitaj(SET.MINUS)
            slovo2=self.pročitaj(SET.RIJEČ)
            slovo2=slovo2.sadržaj
            self.pročitaj(SET.ZATV)
            if len(slovo1)!=1 or len(slovo2)!=1:
                self.greška()
        return Ispis(ime,slovo1,slovo2)
    def operacija(self,ime):
        if self >> SET.PLUSJ:
            riječ=self.pročitaj(SET.RIJEČ)
            return Dodaj(ime,riječ)
        elif self >> SET.MINUSJ:
            riječ=self.pročitaj(SET.RIJEČ)
            return Izbaci(ime,riječ)
        elif self >> SET.UPITNIK:
            riječ=self.pročitaj(SET.RIJEČ)
            return Provjeri(ime,riječ)
        else: self.greška()

def pogledaj(memorija,skup):
    if skup.sadržaj in memorija: return memorija[skup.sadržaj]
    else: skup.problem('Nedeklariran skup')
    
class Program(AST('naredbe')):
    def izvrši(self):
        memorija={}
        izlazi=[]
        for naredba in self.naredbe:
            izlazi.append(naredba.izvrši(memorija))
        return izlazi
    
class Deklaracija(AST('ime')):
    def izvrši(self,memorija):
        if self.ime.sadržaj in memorija:
            self.ime.redeklaracija()
        memorija[self.ime.sadržaj]=set()

class Ispis(AST('ime od do')):
    def izvrši(self,memorija):
        s=pogledaj(memorija,self.ime)
        for rijec in s:
            if rijec[0]<=self.do and rijec[0]>=self.od:
                print(rijec)

class Dodaj(AST('ime rijec')):
    def izvrši(self,memorija):
        s=pogledaj(memorija,self.ime)
        s|={self.rijec.sadržaj}

class Izbaci(AST('ime rijec')):
    def izvrši(self,memorija):
        s=pogledaj(memorija,self.ime)
        if self.rijec.sadržaj in s: s-={self.rijec.sadržaj}
        else: self.rijec.problem('Riječ ne postoji u skupu')

class Provjeri(AST('ime rijec')):
    def izvrši(self,memorija):
        s=pogledaj(memorija,self.ime)
        return self.rijec.sadržaj in s
if __name__ == '__main__':
    print(*set_lex('''
        SKUP A1
        SKUP B1
        A1+=maja
        B1+=pero B1+=ivo B1+=tea 
        ispisi B1
        ispisi B1 [i-p]
        A1 ? andro
    '''))
    print(SETParser.parsiraj(set_lex('''
        SKUP A1
        SKUP B1
        A1+=maja
        B1+=pero B1+=ivo B1+=tea 
        ispisi B1
        ispisi B1 [i-p]
        A1 ? andro
        A1+= andro
        ispisi A1
        A1-=maja
        ispisi A1
    ''')).izvrši())
