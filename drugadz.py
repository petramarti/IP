"""Druga zadaca"""
from pj import *

class XHTML(enum.Enum):
    TEXT = 'obican_tekst'
    OTV = '<'
    ZATV = '>'
    KOSA = '/'
    NAVODNICI= '"'
    HTML = 'html'
    HEAD = 'head'
    BODY = 'body'
    ULISTA = 'ul'
    OLISTA = 'ol'
    ELEMENT ='li'
    TYPE ='type'
    BR='br'
    JEDNAKO='='

def xhtml_lex(kôd):
    lex = Tokenizer(kôd)
    for znak in iter(lex.čitaj, ''):
        if znak.isspace(): lex.token(E.PRAZNO)
        elif znak.isalnum():
            lex.zvijezda(identifikator)
            #yield lex.token(ključna_riječ(XHTML, lex.sadržaj,False) or XHTML.TEXT)
            #ne znam zašto ovo ne radi...
            if(lex.sadržaj=="ol"): yield lex.token(XHTML.OLISTA)
            elif(lex.sadržaj=="ul"): yield lex.token(XHTML.ULISTA)
            elif(lex.sadržaj=="li"): yield lex.token(XHTML.ELEMENT)
            elif(lex.sadržaj=="html"): yield lex.token(XHTML.HTML)
            elif(lex.sadržaj=="head"): yield lex.token(XHTML.HEAD)
            elif(lex.sadržaj=="body"): yield lex.token(XHTML.BODY)
            elif(lex.sadržaj=="type"): yield lex.token(XHTML.TYPE)
            elif(lex.sadržaj=="br"): yield lex.token(XHTML.BR)
            else: yield lex.token(XHTML.TEXT)
        elif znak=='/':
            yield lex.token(XHTML.KOSA)
        elif znak=='"':
            yield lex.token(XHTML.NAVODNICI)
        else:
            yield lex.token(operator(XHTML, znak) or lex.greška())

### Beskontekstna gramatika
# start -> unutar(HTML, zaglavlja)
# zaglavlja -> header body
# header -> unutar(HEAD,podatci)
# podatci -> podatak podatci
# podatak -> '' | TEXT
# body ->unutar(BODY,sadrzaj)
# sadrzaj ->podatci | lista sadrzaj
# lista -> ulista | olista
# ulista -> unutar(ULISTA, element)
# olista ->unutar(OLISTA, element)
# element ->unutar(ELEMENT, sadrzaj)
#
# gdje je unutar(tag, sadržaj) pokrata za
# OTV tag ZATV sadržaj OTV KOSA tag ZATV

### Apstraktna sintaksna stabla:
# Dokument: header, body - <html> sadrzaj </html>
# Header: podatci - <head> sadrzaj </head>
# Body: sadržaj - <body> sadrzaj </body>
# ULista: elementi,bullet - <ul><li> prvi element </li><li> drugi element</li>...</ul>
# OLista: elementi,bullet - <ol><li> prvi element </li><li> drugi element</li>...</ol>
# Element: sadržaj
# Podatak: riječi
class Dokument(AST('header body')):
    def izvrši(self):
        self.header.izvrši()
        self.body.izvrši()
class Header(AST('podatci')):
    def izvrši(self):
        depth=0
        for podatak in self.podatci:
            podatak.izvrši(depth)
class Body(AST('sadrzaj')):
    def izvrši(self):
        depth=0
        for podatak in self.sadrzaj:
            podatak.izvrši(depth)
        # prazan redak na kraju dokumenta
        # da bude urednije kad ih se više izvršava
        print("\n")
class Br(AST('')):
    def izvrši(self,depth):
        print("\n",end="")
class ULista(AST('elementi bullet')):
    def izvrši(self,depth):
        symbols=[chr(9679),chr(9675),chr(9632),""]
        s=symbols[['disc','circle','square','none'].index(self.bullet)]
        for element in self.elementi:
            element.izvrši(s+" ",depth+1)
class OLista(AST('elementi bullet')):
    def izvrši(self,depth):
        i=self.bullet
        for element in self.elementi:
            element.izvrši(i+". ",depth+1)
            i=chr(ord(i)+1)
class Element(AST('sadrzaj')):
    def izvrši(self,sign,depth):
        for podatak in self.sadrzaj:
            
            if podatak ** Podatak:
                print("\t"*depth,end="")
                print(sign,end="")
            podatak.izvrši(depth)
class Podatak(AST('rijeci')):
    def izvrši(self,depth):
        for rijec in self.rijeci:
            print(rijec.sadržaj,end=" ")
        print("\n",end="")
class XHTMLParser(Parser):
    def start(self):
        self.pročitaj(XHTML.OTV)
        self.pročitaj(XHTML.HTML)
        self.pročitaj(XHTML.ZATV)
        h_data=self.header()
        b_data=self.body()
        self.pročitaj(XHTML.OTV)
        self.pročitaj(XHTML.KOSA)
        self.pročitaj(XHTML.HTML)
        self.pročitaj(XHTML.ZATV)
        return(Dokument(h_data,b_data))
    def header(self):
        self.pročitaj(XHTML.OTV)
        self.pročitaj(XHTML.HEAD)
        self.pročitaj(XHTML.ZATV)
        ##moze li se u tekstu nalaziti <, >, / ?
        ##< i > ne mogu, / moze -> u pravom HTML-u
        podatci=[]
        while 1:
            if self >> XHTML.OTV:
                if self >> XHTML.BR:
                    podatci.append(self.br())
                else: break
            elif self >>XHTML.ZATV: self.greška()
            else: podatci.append(self.podatak())
        self.pročitaj(XHTML.KOSA)
        self.pročitaj(XHTML.HEAD)
        self.pročitaj(XHTML.ZATV)
        return Header(podatci)
    
    def body(self):
        self.pročitaj(XHTML.OTV)
        self.pročitaj(XHTML.BODY)
        self.pročitaj(XHTML.ZATV)
        ##ne smije se pojaviti >, ali ako se pojavi <
        ##treba provjeriti što je iza
        ##nista, lista, ili kraj body-a
        sadrzaj=[]
        while 1:
            if self >> XHTML.OTV:
                if self >> XHTML.ULISTA:
                    sadrzaj.append(self.ulista())
                elif self >> XHTML.OLISTA:
                    sadrzaj.append(self.olista())
                elif self >> XHTML.BR:
                    sadrzaj.append(self.br())
                elif self >> XHTML.KOSA:
                    break;
                else: self.greška()
            elif self >> XHTML.ZATV:
                self.greška()
            else:
                sadrzaj.append(self.podatak())
        self.pročitaj(XHTML.BODY)
        self.pročitaj(XHTML.ZATV)
        return Body(sadrzaj)
    def br(self):
        self.pročitaj(XHTML.KOSA)
        self.pročitaj(XHTML.ZATV)
        return Br()
    def ulista(self):
        bullet='disc'
        if self >> XHTML.TYPE:
            self.pročitaj(XHTML.JEDNAKO)
            self.pročitaj(XHTML.NAVODNICI)
            bullet=self.pročitaj(XHTML.TEXT).sadržaj
            if bullet not in ['disc','circle','square','none']:
                self.greška()
            self.pročitaj(XHTML.NAVODNICI)
        self.pročitaj(XHTML.ZATV)
        elementi=[]
        while 1:
            if self >> XHTML.OTV:
                if self >> XHTML.ELEMENT:
                    elementi.append(self.element())
                elif self >> XHTML.KOSA:
                    break
            elif self >> XHTML.ZATV:
                self.greška()
            else:
                self.greška()
        self.pročitaj(XHTML.ULISTA)
        self.pročitaj(XHTML.ZATV)
        return ULista(elementi,bullet)
    def olista(self):
        bullet='1'
        if self >> XHTML.TYPE:
            self.pročitaj(XHTML.JEDNAKO)
            self.pročitaj(XHTML.NAVODNICI)
            bullet=self.pročitaj(XHTML.TEXT).sadržaj
            if bullet not in "1Aa":
                self.greška()
            self.pročitaj(XHTML.NAVODNICI)
        self.pročitaj(XHTML.ZATV)
        elementi=[]
        while 1:
            if self >> XHTML.OTV:
                if self >> XHTML.ELEMENT:
                    elementi.append(self.element())
                elif self >> XHTML.KOSA:
                    break
            elif self >> XHTML.ZATV:
                self.greška()
            else:
                self.greška()
        self.pročitaj(XHTML.OLISTA)
        self.pročitaj(XHTML.ZATV)
        return OLista(elementi,bullet)
    def element(self):
        self.pročitaj(XHTML.ZATV)
        sadrzaj=[]
        while 1:
            #ako pročitamo <, ili je kraj li elementa, ili je nova lista
            if self >> XHTML.OTV:
                #nova lista
                if self >> XHTML.ULISTA:
                    sadrzaj.append(self.ulista())
                elif self >> XHTML.OLISTA:
                    sadrzaj.append(self.olista())
                #kraj li elementa
                elif self >> XHTML.KOSA:
                    break;
            elif self >> XHTML.ZATV:
                self.greška()
            else:
                sadrzaj.append(self.podatak())
        self.pročitaj(XHTML.ELEMENT)
        self.pročitaj(XHTML.ZATV)
        return Element(sadrzaj)
    def podatak(self):
        riječi=[]
        while not self >> XHTML.OTV:
            riječi.append(self.pročitaj(XHTML.TEXT))
        self.vrati()
        return Podatak(riječi)
    

if __name__ == '__main__':
    XHTMLParser.parsiraj(xhtml_lex('''
       <html>
        <head></head>
        <body>
            <ul type="circle">
               <li>Prvi element</li>
               <li>Drugi element</li>
            </ul>
            <br/>
            <ol type="A">
                <li>Treci element</li>
                <li>Četvrti</li>
                <li>Peti</li>
            </ol>
       </body>
       </html>
    ''')).izvrši()
    XHTMLParser.parsiraj(xhtml_lex('''
        <html>
        <head>Nesto pise u headeru <br/> jos nesto u novom redu</head>
        <body>
            Neki tekst u bodyu
            <ul type="square">
                <li>Prvi element</li>
                <li>Drugi element</li>
                <li>
                    <ol>
                        <li>Treci element</li>
                        <li>Cetvrti element</li>
                    </ol>
                </li>
                <li>Novi element</li>
                <li>
                    <ul>
                        <li>Jos elemenata</li>
                        <li>
                            <ol>
                                <li>Uređeni element jedan</li>
                                <li>Uređeni element dva</li>
                                <li>
                                    <ul type="none">
                                        <li>Cetvrto gnijezdo</li>
                                    </ul>
                                </li>
                                <li>Uređeni element 3</li>
                            </ol>
                        </li>
                    </ul>
                </li>
            </ul>
            Jos teksta
            <ol>
                <li>Još malo listi</li>
            </ol>
        </body>
        </html>
    ''')).izvrši()
    print("Ovdje će biti greška jer imamo li element izvan ul ili ol elementa")
    XHTMLParser.parsiraj(xhtml_lex('''
        <html>
        <head></head>
        <body>
            <ol>
                <li>Prvi element</li>
                <li>Drugi element</li>
                <li>
                    <ul>
                        <li>Prvi element ugnjezdene liste</li>
                        <li>jos u gnijezdu</li>
                    </ul>
                </li>
            </ol>
            <li>Element izvan liste</li>
        </body>
        </html>
    ''')).izvrši()
    
