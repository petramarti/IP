"""Zad 31.siječnja 2011."""
from pj import *
import pprint

class LIST(enum.Enum):
    LISTA = 'LISTA'
    PRAZNA = 'PRAZNA'
    UBACI = 'UBACI'
    IZBACI = 'IZBACI'
    DOHVATI = 'DOHVATI'
    KOLIKO = 'KOLIKO'
    IME = 'L'
    BROJ = 123
    MINUSBROJ= -123

def lista_lex(kôd):
    lex=Tokenizer(kôd)
    for znak in iter(lex.čitaj, ''):
        if znak.isspace(): lex.token(E.PRAZNO)
        elif znak.isdigit():
            lex.zvijezda(str.isdigit)
            yield lex.token(LIST.BROJ)
        elif znak.isalpha():
            if znak=='L':
                ime=lex.čitaj()
                if ime.isdigit():
                    if ime!='0':
                        yield lex.token(LIST.IME)
                    else: lex.greška('Očekivana znamenka veća od 0')
                elif ime.isalpha():
                    lex.zvijezda(str.isalpha)
                    yield lex.token(ključna_riječ(LIST,lex.sadržaj,False) or E.GREŠKA)
                else: yield lex.greška()
            else:
                lex.zvijezda(str.isalpha)
                yield lex.token(ključna_riječ(LIST,lex.sadržaj,False) or E.GREŠKA)
        elif znak=='-':
            if lex.čitaj().isdigit():
                lex.zvijezda(str.isdigit)
                yield lex.token(LIST.MINUSBROJ)
            else: yield lex.greška('očekivana znamenka nakon minusa')
        else: yield lex.greška()

###Beskontekstna gramatika
# start -> naredba naredbe
# deklaracija -> DEKLARACIJA IME
# naredbe -> '' | naredba naredbe
# naredba -> deklaracija | prazna | ubaci | izbaci | dohvati | koliko
# prazna -> PRAZNA IME
# ubaci -> UBACI IME (BROJ | MINUSBROJ) BROJ
# izbaci -> IZBACI IME BROJ
# dohvati -> DOHVATI IME BROJ
# koliko -> KOLIKO IME

###Apstraktna stabla
# svaka naredba - jedno apstraktno stablo
# Skripta: naredbe - niz naredbi, počinje deklaracijom
# Deklaracija: ime - stvara listu imena ime
# Prazna: ime - provjerava je li lista ime prazna
# Ubaci: ime, element, mjesto - ubacuje element na mjesto u listi ime
# Izbaci: ime, mjesto - izbacuje element na mjestu mjesto u listiime
# Dohvati: ime, mjesto - dohvaća element na mjestu u listi ime
# Koliko: ime - vraća broj elemenata u listi ime

class LISTAParser(Parser):
    def start(self):
        naredbe= []
        while not self >> E.KRAJ:
            naredbe.append(self.naredba())
        return Skripta(naredbe)
    def naredba(self):
        if self >> LIST.LISTA:
            rezultat=self.deklaracija()
        elif self >> LIST.PRAZNA: rezultat=self.prazna()
        elif self >> LIST.UBACI: rezultat=self.ubaci()
        elif self >> LIST.IZBACI: rezultat=self.izbaci()
        elif self >> LIST.DOHVATI: rezultat=self.dohvati()
        elif self >> LIST.KOLIKO: rezultat=self.koliko()
        return rezultat
    def deklaracija(self):
        ime=self.pročitaj(LIST.IME)
        return Deklaracija(ime)
    def prazna(self):
        ime=self.pročitaj(LIST.IME)
        return Prazna(ime)
    def ubaci(self):
        ime=self.pročitaj(LIST.IME)
        element=self.pročitaj(LIST.BROJ)
        mjesto=self.pročitaj(LIST.BROJ)
        return Ubaci(ime,element,mjesto)
    def izbaci(self):
        ime=self.pročitaj(LIST.IME)
        mjesto=self.pročitaj(LIST.BROJ)
        return Izbaci(ime,mjesto)
    def dohvati(self):
        ime=self.pročitaj(LIST.IME)
        mjesto=self.pročitaj(LIST.BROJ)
        return Dohvati(ime,mjesto)
    def koliko(self):
        ime=self.pročitaj(LIST.IME)
        return Koliko(ime)
class Skripta(AST('naredbe')):
    """Niz naredbi"""
    def razriješi(self):
        liste={}
        izlazi=[]
        for naredba in self.naredbe:
            izlazi.append(naredba.razriješi(liste))
        return liste,izlazi
class Deklaracija(AST('ime')):
    def razriješi(self,liste):
        #ako lista već postoji, prijavi grešku redeklaracije
        if self.ime.sadržaj in liste:
            self.ime.redeklaracija()
        #(inače) deklariraj praznu listu
        liste[self.ime.sadržaj]=[]
class Prazna(AST('ime')):
    def razriješi(self,liste):
        if self.ime.sadržaj in liste:
            return not liste[self.ime.sadržaj]
        else: self.ime.nedeklaracija('nema liste')
class Ubaci(AST('ime element mjesto')):
    def razriješi(self,liste):
        if self.ime.sadržaj in liste:
            li=liste[self.ime.sadržaj]
            v=int(self.element.sadržaj)
            i=int(self.mjesto.sadržaj)
            if i<=len(self.ime.sadržaj):
                liste[self.ime.sadržaj].insert(i,v)
            else: self.mjesto.nedeklaracija('u listi nema tog mjesta')
        else: self.ime.nedeklaracija('nema liste')
class Izbaci(AST('ime mjesto')):
    def razriješi(self,liste):
        if self.ime.sadržaj in liste:
            li=liste[self.ime.sadržaj]
            if int(self.mjesto.sadržaj)<len(li):
                del li[int(self.mjesto.sadržaj)]
            else: self.mjesto.nedeklaracija('u listi nema tog mjesta')
        else: self.ime.nedeklaracija('nema liste')
class Dohvati(AST('ime mjesto')):
    def razriješi(self,liste):
        if self.ime.sadržaj in liste:
            li=liste[self.ime.sadržaj]
            if int(self.mjesto.sadržaj)<len(li):
                return li[int(self.mjesto.sadržaj)]
            else: self.mjesto.nedeklaracija('u listi nema tog mjesta')
        else: self.ime.nedeklaracija('nema liste')            
class Koliko(AST('ime')):
    def razriješi(self,liste):
        if self.ime.sadržaj in liste:
            return len(liste[self.ime.sadržaj])
        else: self.ime.nedeklaracija('nema liste')            
    
if __name__ == '__main__':
    skripta = LISTAParser.parsiraj(lista_lex('''
            LISTA L1
            UBACI L1 12 0
            dohvati L1 0
            lista L2
            UBACI L1 34 1
            prazna L2
            UBACI L2 36 0
            prazna L2
            UBACI L1 56 2
            izbaci L1 1
            koliko L1
    '''))
    pprint.pprint(skripta.razriješi())
    print(*lista_lex('lista L1 prazna ubaci -2345 izbaci L9 dohvati 3 koliko L1'))
    
