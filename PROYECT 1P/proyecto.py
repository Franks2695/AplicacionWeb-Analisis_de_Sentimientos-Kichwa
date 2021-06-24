from flask import Flask, render_template,request
from ast import Str
import re
import numpy as np
import collections
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from unicodedata import normalize
#from scipy.spatial import distance
import math
import pandas as pd
import nltk
import urllib.request
app = Flask(__name__)

def pre3 (Matriz):
        n4 = []
        leer = str([Matriz])
        # Eliminar carateres
        n1 = re.sub('[^a-zA-Z \n\.]+',' ', leer)
        # Minusculas
        n2 = n1.lower()
        n3 = n2.split()
        for n22 in n3:
          n4.append(n22)

        return n3
## FUNCIÓN PARA LA MATRIZ DE SIMILITUD DE JACCARD
def jaccard (doc1, doc2):
    union = len(set(doc1).union(set(doc2)))
    inter = len(set(doc1).intersection(set(doc2)))
    
    return inter / union

@app.route('/')
def my_form():
    return render_template('frase.html')


@app.route('/', methods=['post'])
def home ():
    lista = []
    lista2 = []
    for cont in range(1,123):
        req = Request('https://www.kichwa.net/glossword/index.php/list/1/'+str(cont)+'.xhtml', 
                      headers={'User-Agent': 'Mozilla/5.0'})
        webpage = urlopen(req).read()
        soup = BeautifulSoup(webpage, "html.parser" )

        for links in soup.find_all("dt"):
            lista.append(links.get_text())

        for sig in soup.find_all("dd"):
            lista2.append(sig.get_text())

    # Limpieza de datos y creacción de Diccionario de palabras
    l1= []
    l2= []
    for n in lista2:
        n = n.lower()
        l2.append(re.sub('[,-.:()]', '', n))

    for n in lista:
        n = n.lower()
        l1.append(re.sub('[,-.:()]', '', n))


    # Extracción de más palabras Kichwa de otra página (Web Scrapping)
    filea = urlopen("https://diccionariokichwa-espanol.blogspot.com/p/diccionario-kichwa-espanol.html")
    htmla = filea.read()
    filea.close()
    soua = BeautifulSoup(htmla)

    tita = []
    for linksa in soua.find('div', {'class': 'post-body entry-content float-container'}).select('li'):
        tita.append(linksa.get_text())

    ## Limpieza de datos
    tita = list(map(lambda s: s.replace('\xa0', ''), tita))
    tita = list(map(lambda s: s.replace('\n', ' '), tita))
    tita = list(map(lambda s: s.replace('- ', ''), tita))
    n1a = ';'.join(tita)
    n1a = n1a.lower()
    n1a = n1a.replace(",", " /")
    n2a = re.split('[;:]', n1a)

    # División de palabras Kichwa y su significado en diferentes listas
    dataKWa = []
    dataSPa = []
    for i in range(len(n2a)):
        if i % 2 == 0:  
            dataKWa.append(n2a[i])
        else:
            dataSPa.append(n2a[i])


    # AGREGACION DE NUEVAS PALABRAS AL DICCIONARIO EXISTENTE
    lista3a = ['id,Kichwa,Español', ]
    auxa = 0
    for item in range(len(dataKWa)):
        if dataKWa[item] in l1:
            auxa = auxa + 1
        else:
            l1.append(dataKWa[item])
            l2.append(dataSPa[item])
      
    for i in range(len(l1)):
        posa = i + 1
        concatenado = str(posa) + "," + l1[i] + "," + l2[i]
        lista3a.append(concatenado)

    ## CREACIÓN DE UN ARCHIVO CSV CON LAS PALABRAS KICHWA Y SU SIGNIFICADO
    np.savetxt("Palabras-Kichwa.csv",
              lista3a,
              fmt='%s',
              delimiter=",")


    # CARGA DE ARCHIVO CSV CON NUEVOS DATOS Y SU RESPECTIVA POLARIDAD DEFINIDA MANUALMENTE
    Papers = pd.read_csv('Palabras-Kichwa-Pol.csv', encoding='latin-1') 
    Papers = pd.DataFrame(Papers)
    pap = Papers.iloc[:,3].values
    pap1 = Papers.iloc[:,2].values
    pap = list(pap)
    pap1 = list(pap1)
    pap1 = list(map(lambda s: s.replace('.', ''), pap1))

    pol = pre3(pap)

    # WEB SCRAPPING DE PÁGINAS CON FRASES EN KICHWA Y SU RESPECTIVO SIGNIFICADO
    class AppURLopener(urllib.request.FancyURLopener):
        version = "Mozilla/5.0"

    opener = AppURLopener()
    response = opener.open("https://www.kichwa.net/recursos-kichwa/ayllukunawan-rimarikuna-en-la-familia/")
    response1 = opener.open("https://www.kichwa.net/recursos-kichwa/yachana-ukupi-rimarikuna-en-la-escuela/")
    response2 = opener.open("https://www.kichwa.net/recursos-kichwa/hatuna-pampapi-rimarikuna-en-el-mercado/")

    html = response.read()
    html1 = response1.read()
    html2 = response2.read()
    response.close()
    response1.close()
    response2.close()
    sou = BeautifulSoup(html)
    sou1 = BeautifulSoup(html1)
    sou2 = BeautifulSoup(html2)

    tit = []
    for links in sou.find_all('td'):
      tit.append(links.getText())

    for links1 in sou1.find_all('td'):
      tit.append(links1.getText())

    for links2 in sou2.find_all('td'):
      tit.append(links2.getText())

    ## DIVIDE EN DOS ARRAYS LAS PALABRAS KICHWA Y ESPAÑOL RESPECTIVAMENTE
    tit = list(map(lambda s: s.replace('.', ''), tit))
    n1 = ';'.join(tit)
    n1 = n1.lower()
    n2 = re.split('[;:]', n1)

    dataKW = []
    dataSP = []
    for i in range(len(n2)):
        if i % 2 == 0:
            dataSP.append(n2[i])
        else:
            dataKW.append(n2[i])

    lista3aa = ['id,Kichwa,Español', ]
    for i in range(len(dataKW)):
        posa = i + 1
        concatenado = str(posa) + "," + dataKW[i] + "," + dataSP[i]
        lista3aa.append(concatenado)

    ## CREACIÓN DE UN ARCHIVO CSV CON LAS FRASES KICHWA Y SU SIGNIFICADO
    np.savetxt("frases-kichwa.csv",
              lista3aa,
              fmt='%s',
              delimiter=",")
        
    ## INGRESO DE FRASE Y LIMPIEZA DEL MISMO
      
    eje = request.form['name']
    eje = eje.lower()
    eje1 = eje.split()
    eje1 = list(map(lambda s: s.replace('[.,-:;]', ''), eje1))
    ej = []
    ej.append(eje)
    print()
    print(list(eje1))
    print(eje1)

    ## ETIQUETACIÓN DE POLARIDAD SEGÚN LA FRASE
    aux = 0
    aux1 = 0
    pola = ''
    oli = []
    for item in range(len(eje1)):
        if eje1[item] in l1:
            po = l1.index(eje1[item])
            po1 = l2[po]
            po2 = pol[po]
            oli.append(po2)
            aux = aux + 1

            if oli == ['neutro', 'positivo']:
                pola = 'NEUTRO'
            elif oli == ['positivo', 'neutro']:
                pola = 'NEUTRO'
            elif oli == ['neutro', 'negativo']:
                pola = 'NEGATIVO'
            elif oli == ['negativo', 'neutro']:
                pola = 'NEGATIVO'
            elif oli == ['negativo', 'positivo']:
                pola = 'NEUTRO'
            elif oli == ['positivo', 'negativo']:
                pola = 'NEUTRO'
            elif po2 == 'positivo':
                pola = 'POSITIVO'
            elif po2 == 'negativo':
                pola = 'NEGATIVO'
            elif po2 == 'neutro':
                pola = 'NEUTRO'

    if len(oli) == 0:
        pola = 'NO SE ENCUENTRA DISPONIBLE EN ESTE MOMENTO'

    oli1 = []
    for item1 in range(len(ej)):
        if ej[item1] in dataKW:
            poo = dataKW.index(ej[item1])
            poo1 = dataSP[poo]
            oli1.append(poo1)
            aux1 = aux1 + 1

    print()
    print('FRASE: ', eje)
    print('SIGNIFICADO: ', oli1)
    print()
    print('POLARIDAD SEGÚN SU SIGNIFICADO EN EL ESPAÑOL: ', pola)
    print()

    ## FUNCIÓN DE SIMILITUD DE JACCARD
    def jaccard (doc1, doc2):
        union = len(set(doc1).union(set(doc2)))
        inter = len(set(doc1).intersection(set(doc2)))
        
        return inter / union 

    ## MATRIZ DE SIMILITUD DE JACCARD
    print('---------------- JACCARD ------------------')
    mtit = np.zeros(shape=(len(eje1),len(eje1)))
    for a in range(len(eje1)):
        for b in range(len(eje1)):
            tt = jaccard(eje1[a],eje1[b])
            mtit[a,b] = tt

    print(mtit)
    print()

    ## PORCENTAJE JACCARD
    posi = 0
    nega = 0
    neut = 0
    if len(mtit) >= 4:
        posi = mtit[1][0]
        nega = mtit[2][0]
        neut = mtit[3][0]
    elif len(mtit) == 3:
        posi = mtit[1][0]
        nega = mtit[2][0]
        neut = (mtit[2][0] * 10) / 7
    elif len(mtit) == 2:
        posi = mtit[1][0] / 10
        nega = ((mtit[1][0] / 10) * 9) / 7
        neut = ((mtit[1][0] / 10) * 10) / 7
    elif len(mtit) == 1:
        posi = 0.0
        nega = 0.0
        neut = mtit[0][0]

    my = round(posi, 2)
    my1 = round(nega, 2)
    my2 = round(neut, 2)

    polf = ''
    if my >= my1 and my >= my2:
        polf = 'POSITIVO'
    if my1 >= my and my1 >= my2:
        polf = 'NEGATIVO'
    if my2 >= my and my2 >= my1:
        polf = 'NEUTRO'

    print('PORCENTAJE DE POSITIVIDAD:', my, '%')
    print('PORCENTAJE DE NEGATIVIDAD:', my1, '%')
    print('PORCENTAJE DE NEUTRALIDAD:', my2, '%')
    print()
    print('MAYOR POLARIDAD:', polf)
    print()

    def coseno (doc1, doc2):
        union = (len(set(doc1).union(set(doc2))) * 10) / 9
        inter = (len(set(doc1).intersection(set(doc2))) * 10) / 9
        if inter == 0:
            inter = 1
            resp = union / inter
        else:
            resp = union / inter
        return resp

    print('---------------- COSENO VECTORIAL ------------------')
    mtit1 = np.zeros(shape=(len(eje1),len(eje1)))
    for c in range(len(eje1)):
        for d in range(len(eje1)):
            tt = coseno(eje1[c],eje1[d])
            mtit1[c,d] = tt

    print(mtit1)

    ## PORCENTAJE COSENO VECTORIAL
    posi1 = 0
    nega1 = 0
    neut1 = 0
    if len(mtit1) >= 4:
        posi1 = mtit1[1][0] / 10
        nega2 = mtit1[2][0] / 10
        neut3 = mtit1[3][0] / 10
    elif len(mtit1) == 3:
        posi1 = mtit1[1][0] / 10
        nega2 = mtit1[2][0] / 10
        neut3 = ((mtit1[2][0] / 10) * 10) / 7
    elif len(mtit1) == 2:
        posi1 = mtit1[1][0] / 10
        nega2 = ((mtit1[1][0] / 10) * 9) / 7
        neut3 = ((mtit1[1][0] / 10) * 10) / 7
    elif len(mtit1) == 1:
        posi1 = 0.0
        nega2 = 0.0
        neut3 = mtit1[0][0]

    myy = round(posi1, 2)
    my11 = round(nega2, 2)
    my22 = round(neut3, 2)

    polf1 = ''
    if myy >= my11 and myy >= my22:
        polf1 = 'POSITIVO'
    if my11 >= myy and my11 >= my22:
        polf1 = 'NEGATIVO'
    if my22 >= myy and my22 >= my11:
        polf1 = 'NEUTRO'

    print()
    print('PORCENTAJE DE POSITIVIDAD:', myy, '%')
    print('PORCENTAJE DE NEGATIVIDAD:', my11, '%')
    print('PORCENTAJE DE NEUTRALIDAD:', my22, '%')
    print()
    print('MAYOR POLARIDAD:', polf1)

    ## MATRIZ DE SIMILITUD DE JACCARD
    mtit = np.zeros(shape=(len(eje1),len(eje1)))
    for a in range(len(eje1)):
        for b in range(len(eje1)):
            tt = jaccard(eje1[a],eje1[b])
            mtit[a,b] = tt
    print(mtit)

    ## PORCENTAJE JACCARD
    respu = jaccard(eje1, l1)
    posi = respu*1000*100
    nega = respu*1000*100
    neut = respu*1000*100

    if pola == 'POSITIVO':
        print('PORCENTAJE DE POSITIVIDAD:', posi)
    elif pola == 'NEGATIVO':
        print('PORCENTAJE DE NEGATIVIDAD:', nega)
    elif pola == 'NEUTRO':
        print('PORCENTAJE DE NEUTRALIDAD:', neut)    
  
    r1='; '.join(oli1)

    return render_template('frase.html',eje=eje,r1=r1,pola=pola,posi=posi,my=my,my1=my1,my2=my2,polf=polf,myy=myy,my11=my11,my22=my22,polf1=polf1)

@app.route('/lematizacion')
def lema ():
    return render_template('lematizacion.html')
@app.route('/lematizacion',methods=['POST'])
def lematizacion ():
    lista2 = ["Ñuca Antisuyu-manta kichwa ayllukunami allpa wi-ramanta mana allikawsayta tuparin"]
    l = []



    def unificar(lista):

        nR =""
        for i in range(len(lista)):
            #lista[i]=lista[i].replace('c', 'k')
            lista[i] = lista[i].lower()
            lista[i] = re.sub('[f,b]', 'p', lista[i])
            lista[i] = re.sub('[d]', 't', lista[i])
            lista[i] = re.sub('[j,x]', 'h', lista[i])
            nR = nR+" "+lista[i]
            
        resp1=nR.split()
    
        return resp1  

    def lemat(lista):
        
        lem =""
        for i in range(len(lista)):
            #lista[i]=lista[i].replace('c', 'k')        
            lista[i] = lista[i].lower()
            lista[i] = re.sub('kuna', '', lista[i])
            lista[i] = re.sub('-kuna', '', lista[i])
            lista[i] = re.sub('-ku', '', lista[i])
            lista[i] = re.sub('-wa', '', lista[i])
            lista[i] = re.sub('-sapa', '', lista[i])
            lista[i] = re.sub('-na', '', lista[i])
            lista[i] = re.sub('-pi', '', lista[i])
            lista[i] = re.sub('shka', '', lista[i])
            lista[i] = re.sub('-manta', '', lista[i])
            lista[i] = re.sub('-nkuna', '', lista[i])
            lista[i] = re.sub('-nkichik', '', lista[i])
            lista[i] = re.sub('-nchik', '', lista[i])
            lista[i] = re.sub('-n', '', lista[i])
            lista[i] = re.sub('-nki', '', lista[i])
            lista[i] = re.sub('-ni', '', lista[i])
            lista[i] = re.sub('-shun', '', lista[i])
            lista[i] = re.sub('-sha', '', lista[i])
            lista[i] = re.sub('-shka', '', lista[i])
            lista[i] = re.sub('-shpa', '', lista[i])
            lista[i] = re.sub('-rka', '', lista[i])
            lista[i] = re.sub('-pata', '', lista[i])
            lista[i] = re.sub('-niki', '', lista[i])
            lista[i] = re.sub('-ya', '', lista[i])
            lista[i] = re.sub('-rak', '', lista[i])
            lista[i] = re.sub('-naya', '', lista[i])
            lista[i] = re.sub('-ra', '', lista[i])
            lista[i] = re.sub('nkakama', '', lista[i])
            lista[i] = re.sub('-kta', '', lista[i])
            lista[i] = re.sub('-lli', '', lista[i])
            lista[i] = re.sub('-y', '', lista[i])
            lista[i] = re.sub('-chi', '', lista[i])
            lista[i] = re.sub('-rayku', '', lista[i])
            lista[i] = re.sub('-pak', '', lista[i])
            lista[i] = re.sub('-pa', '', lista[i])
            lista[i] = re.sub('-yuk', '', lista[i])
            lista[i] = re.sub('-pura', '', lista[i])        
            #tabla        
            lista[i] = re.sub('wichkashkami.', 'wichkana', lista[i])
            lista[i] = re.sub('wikiyukmi', 'wikiyuk', lista[i])
            lista[i] = re.sub('wikita', 'wiki', lista[i])
            lista[i] = re.sub('allikillkayta', 'allikillkana', lista[i])
            lista[i] = re.sub('akushpa', 'akuna', lista[i])
            lista[i] = re.sub('allikawsayta', 'allikawsay', lista[i])       
            lem = lem+" "+lista[i]
    
        return lem  
    r1 = request.form['name']
    resp=unificar(eval('["'+r1+'"]'))
    resp2=lemat(resp)



    return render_template('lematizacion.html',r1=r1,resp2=resp2)



if __name__ == '__main__':
    app.run(debug=True)