import tkinter as tk
from tkinter import ttk
from operator import attrgetter
import pandas as pd
import time
import pygame
from pygame.locals import *
import sys
import random

#Definiciones para la ventana del mapa
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 700

def ejercicioA(ciudad):
   # df Contiene la informacion de las ciudades y distancias
   path = 'datos.xlsx'
   df = pd.read_excel(path)
   # dfCoor Contiene las coordenadas de cada ciudad en nuestro mapa propio
   pathCoor = 'coordenadas.xlsx'
   dfCoor = pd.read_excel(pathCoor)  

   #Inicializacion de variables
   recorrido = []
   distancias = []
   i=0

   df = df.set_index('Distancias en kilómetros')  # Columna índice
   
   ciudadInicial = ciudad
   recorrido.append(ciudadInicial) 
   print(ciudadInicial)            
   getRecorrido(ciudadInicial, i, recorrido, distancias, df)
   print("Recorrido: ", recorrido)
   dibujo(recorrido, dfCoor, SCREEN_WIDTH, SCREEN_HEIGHT)

def ejercicioB():
   # df Contiene la informacion de las ciudades y distancias
   path = 'datos.xlsx'
   df = pd.read_excel(path)
   # dfCoor Contiene las coordenadas de cada ciudad en nuestro mapa propio
   pathCoor = 'coordenadas.xlsx'
   dfCoor = pd.read_excel(pathCoor) 

   #Inicializacion de variables
   i=0

   df = df.set_index('Distancias en kilómetros')  # Columna indice

   #Obtenemos el recorrido con menor distancia
   def getMinRecorrido(df):
      print("El problema del viajante")
      recorridoMinimo = []
      #Iteramos todos los posibles recorridos
      for col in df.columns:
         recorrido = [col]
         distancias = []
         getRecorrido(col,i,recorrido,distancias, df)
         #Asignamos el recorrido al recorrido minimo si es mas corto que el anterior
         if len(recorridoMinimo) == 0 or recorrido[-1] < recorridoMinimo[-1]:
            recorridoMinimo = recorrido
      return recorridoMinimo

   recorridoMinimo = getMinRecorrido(df)
   print("Recorrido: ", recorridoMinimo)
   dibujo(recorridoMinimo,dfCoor, SCREEN_WIDTH, SCREEN_HEIGHT)
   
def ejercicioC(respElit, inCiclos):
   # df Contiene la informacion de las ciudades y distancias
   path = 'datos.xlsx'
   global df
   df = pd.read_excel(path)
   # dfCoor Contiene las coordenadas de cada ciudad en nuestro mapa propio
   pathCoor = 'coordenadasAG.xlsx'
   dfCoor = pd.read_excel(pathCoor)
   pathCoor = 'coordenadasAG1.xlsx'
   dfCoor1 = pd.read_excel(pathCoor)

   "Método de Selección: Ruleta. Método de Crossover: CROSSOVER CICLICO. Método de Mutación: invertida."
   pCrossover = 0.75
   pMutacion = 0.05
   cantIndividuos = 50
   cantGenes = 24
   ciclos = int(inCiclos)
   tamanoElite = 10

   #Etapa 1: Generación de la población inicial
   def getPoblacionInicial():
      #Creamos la coleccion de cromosomas
      cromosomas = []
      #Inicializa cada cromosoma generado de la poblacion con sus propiedades y lo guarda en nuestra coleccion final de cromosomas iniciales
      for individuo in generarPoblacionInicial():
         cromosomas.append(Cromosoma(individuo))
      return cromosomas
   def generarPoblacionInicial():
      #Crea una poblacion de 50 individuos donde cada uno es un cromosoma generado
      return [generarCromosomaInicial() for _ in range(cantIndividuos)]
   def generarCromosomaInicial():
      #Genera un cromosoma con bits del 1 al 24 en posiciones aleatorias
      return random.sample(range(1,25),24)

   class Cromosoma:
      def __init__(self,bits=None):
         global df
         #Inicializamos el cromosoma calculando y asignando sus propiedades, en el caso que estemos 
         # creando un cromosoma máximo inicial lo inicializamos con bits = None, 
         # con el objetivo de solamente analizar su funcion objetivo (distancia) en las comparaciones.
         if(bits != None):
            self.bits = bits
            self.distancia = self.calcularDistancia()
            self.ftn = 0
         else:
            self.distancia = 0
      
      def calcularFitness(self,sumaX):
         if(sumaX!=0):
            self.ftn = 1 - (self.distancia/sumaX) #A menor distancia, mayor fitness
         else:
            self.ftn = 0

      def calcularDistancia(self):
         global df
         dist = 0.0
         ciudadAnt = None
         #Calcular distancia entre las ciudades cuyos numeros estan en bits y lo devuelve
         for ciudad in self.bits:
            if (ciudadAnt != None and ciudad != None): #Si ya tenemos una ciudad con la que calcular distancia
               dist = dist + df.iloc[ciudadAnt-1][ciudad] #Sumamos la distancia entre la ciudad anterior y la actual
            ciudadAnt = ciudad #Seteamos como anterior la ciudad actual
         
         dist = dist + df.iloc[ciudadAnt-1][self.bits[0]] #Sumamos la distancia entre la ultima ciudad y la ciudad de inicio (volvemos a la ciudad de inicio)
         return dist 

   class Poblacion:
      def __init__(self,cromosomas):
         self.cromosomas = cromosomas
         self.sumaFtn = 0
         self.sumaX = 0
         self.cromMinDistanciaCiclo = Cromosoma() #Inicializamos el cromosoma maximo del ciclo un cromosoma con objetivo 0
      
      #Etapa 2: Guardado de datos
      def calcularYSetearDatos(self):
         for cromosoma in self.cromosomas:
            #Calculo de la distancia minima
            if(self.cromMinDistanciaCiclo.distancia == 0 or cromosoma.distancia < self.cromMinDistanciaCiclo.distancia):
               self.cromMinDistanciaCiclo = cromosoma
            #Calculo de la suma de valores de las funciones objetivo
            self.sumaX += cromosoma.distancia
         #Calculo del fitness de cada cromosoma
         for cromosoma in self.cromosomas:
            cromosoma.calcularFitness(self.sumaX)

      #Etapa 3: Seleccion   
      def seleccionTorneo(self, elitismo):
         individuos = cantIndividuos
         if(elitismo): 
            individuos -= tamanoElite
         #Creamos la colección de pares
         pares = []
         #Iteramos en la cantidad de pares que tendremos
         for _ in range(int(individuos/2)):
            ganadores = []
            for _ in range(2):
               peleador1 = self.cromosomas[random.randint(0,(cantIndividuos-1))]
               while True:
                  peleador2 = self.cromosomas[random.randint(0,(cantIndividuos-1))]
                  if peleador2 != peleador1:
                     break
               if peleador1.ftn > peleador2.ftn:
                  ganadores.append(peleador1)
               else:
                  ganadores.append(peleador2)
            pares.append(ganadores)
         return pares 

      def seleccionRuleta(self, elitismo):
         individuos = cantIndividuos
         if(elitismo): 
            individuos -= tamanoElite
         #Creamos la colección de pares
         pares = []
         #Iteramos en la cantidad de pares que tendremos
         for i in range(int(individuos/2)):
            #Agregamos un par vacio a la colección de pares
            pares.append([])
            #Agregamos los 2 cromosomas al par los cuales los elegimos de nuestros cromosomas segun el peso que ejerza el valor del fitness de cada uno.
            for _ in range(2):
               sumFitness = sum(crom.ftn for crom in self.cromosomas)  # suma todas las funciones fitness para sacar un numero entre 0 y dicha suma
               pick = random.uniform(0, sumFitness)
               current = 0
               # cada cromosoma tiene un rango dependiendo su funcion fitness, cuando el numero random este dentro del rango de un
               # cromosoma especifico devolvera ese cromosoma
               for crom in self.cromosomas:
                  current += crom.ftn
                  if current > pick:
                     pares[i].append(crom)
                     break
         return pares

      def getListafitness(self):
         #Inicializamos la coleccion de los valores fitness
         listafitness = []
         #Agregamos el fitness de cada cromosoma a la coleccion
         for cromosoma in self.cromosomas:
            listafitness.append(cromosoma.ftn)
         return listafitness

      #Etapa 4: Crossover y mutación
      def aplicarCrossoverMutacion(self,pares):
         sigPoblacion = []       
         for par in pares:
            if (self.evaluarCrossoverOMutacion(pCrossover)):
               for i in range(2):
                  index = 0 #Tiene el indice del numABuscar para poder meterlo en los hijos
                  numABuscar = int(par[i].bits[0]) #El numero que tenemos que buscar en padre1
                  hijo = [None]*cantGenes #Inicializado para luego poder llenarlo (cuando encontremos un numero ya ingresado)             

                  #Vamos llenando el hijo hasta encontrar un numero que ya metimos
                  while numABuscar not in hijo:
                     hijo[index] = numABuscar #Guardamos el numero a buscar en el hijo en la posicion de su indice en padre1
                     numABuscar = int(par[abs(i-1)].bits[index]) #Obtenemos el numero que esta abajo del que acabamos de agregar al hijo
                     index = par[i].bits.index(numABuscar) #Obtenemos el index del numero que acabamos de obtener

                  #Llenamos las posiciones faltantes
                  for j in range(cantGenes):
                     if hijo[j] is None:
                        hijo[j] = par[abs(i-1)].bits[j]
                           
                  if(self.evaluarCrossoverOMutacion(pMutacion)):
                     pto1Mutacion = random.randint(0,23)
                     pto2Mutacion = random.randint(0,23)
                     aux = hijo[pto1Mutacion]
                     hijo[pto1Mutacion] = hijo[pto2Mutacion]
                     hijo[pto2Mutacion] = aux

                  cromosoma = Cromosoma(hijo)
                  
                  sigPoblacion.append(cromosoma)
            else:
               for i in range(2):
                  hijo = par[abs(i-1)].bits

                  if(self.evaluarCrossoverOMutacion(pMutacion)):
                     pto1Mutacion = random.randint(0,23)
                     pto2Mutacion = random.randint(0,23)
                     aux = hijo[pto1Mutacion]
                     hijo[pto1Mutacion] = hijo[pto2Mutacion]
                     hijo[pto2Mutacion] = aux

                  cromosoma = Cromosoma(hijo)
                  
                  sigPoblacion.append(cromosoma)
         return sigPoblacion                        

      def evaluarCrossoverOMutacion(self,probabilidadTrue):
         #Recibe una probabilidad para realizar algo y devuelve True si se debe realizar o False si no (usado para decidir crossover y mutacion)
         return (random.choices([0,1],[1-probabilidadTrue,probabilidadTrue])[0] == 1)

      #Helpers
      def aplicarElitismo(self,tamanoElite):
         cromosomasElite = []
         poblacionTemp = self.cromosomas[:]
         for _ in range(tamanoElite):
            unMaximo = max(poblacionTemp,key=attrgetter('ftn')) #Sacamos el cromosoma con mayor fitness
            #Lo eliminamos de los cromosomas de la pobl actual y a la vez lo asignamos a la lista de elite (pop elimina el objeto y a su vez lo devuelve)
            cromosomasElite.append(poblacionTemp.pop(poblacionTemp.index(unMaximo))) 
         return cromosomasElite
      
      def getListaFtn(self):
         listaFtn = []
         for cromosoma in self.cromosomas:
            listaFtn.append(cromosoma.ftn)
         return listaFtn

   def empezar(respElit):
      global poblacion,cromMinDistanciaCorrida
      #Inicializaciones
      
      cromMinDistanciaCorrida = Cromosoma() #Inicializamos el cromosoma maximo como un cromosoma con distancia 0
      elitismo = respElit
      poblacion = Poblacion(getPoblacionInicial())

      print("Comenzando algoritmo con "+str(ciclos)+" ciclos solicitados")

      for i in range(ciclos):
         print()
         sigCromosomas = [] #Lista de cromosomas siguientes (utilizados cuando se activa elitismo)
         poblacion.calcularYSetearDatos() 

         #Actualizacion del cromosoma con menor distancia de la corrida
         if(cromMinDistanciaCorrida.distancia == 0 or poblacion.cromMinDistanciaCiclo.distancia < cromMinDistanciaCorrida.distancia):
            cromMinDistanciaCorrida = poblacion.cromMinDistanciaCiclo

         if(elitismo):
            #Sacamos los cromosomas con mejor fitness
            sigCromosomas = poblacion.aplicarElitismo(tamanoElite)

         pares = poblacion.seleccionRuleta(elitismo)

         #Final del ciclo actual
         finCiclo(i+1) 

         poblacion = Poblacion(poblacion.aplicarCrossoverMutacion(pares))
         poblacion.cromosomas += sigCromosomas #Si hay elitismo, sigCromosomas va a tener cromosomas y aca se agregan, sino va a estar vacio y no se va a agregar nada 

   #Etapa 5: Mensaje final con los datos de la generacion
   def finCiclo(numCiclo):
      #Muestra los datos finales de la generacion que acaba de finalizar
      print("CICLO "+str(numCiclo)+" COMPLETADO. Datos del mismo:")
      print("DISTANCIA --> DISTANCIA MINIMA = "+str(poblacion.cromMinDistanciaCiclo.distancia))
      print("CROMOSOMA MINIMO --> "+str(poblacion.cromMinDistanciaCiclo.bits))

      if(numCiclo == ciclos):
         print("Algoritmo finalizado: se cumplieron los ciclos solicitados")
         print("Recorrido minimo de toda la corrida: "+str(cromMinDistanciaCorrida.bits))
         print("Distancia del cromosoma con recorrido minimo de toda la corrida: "+str(cromMinDistanciaCorrida.distancia))
         dibujo(cromMinDistanciaCorrida, dfCoor, dfCoor1)

   #Helpers
   def dibujo(recorrido, dfCoor, dfCoor1):
      pygame.init()
      # creamos la ventana y le indicamos un titulo:
      screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
      pygame.display.set_caption("Problema del viajante")

      color = pygame.Color(70,80,150)
      screen.fill(color=(255,255,255))

      # cargamos el fondo y redimencionamos
      fondo = pygame.image.load("mapa.jpg").convert()
      fondo = pygame.transform.scale(fondo, (600,700))
      
      # Indicamos la posicion de las "Surface" sobre la ventana
      screen.blit(fondo, (0, 0))
      
      # se muestran lo cambios en pantalla
      pygame.display.flip()

      fuente = pygame.font.Font(None, 25)
      texto1 = fuente.render("Ciudad Inicial:", 0, (0, 0, 0))
      screen.blit(texto1,(600,15))
      texto1 = fuente.render(str(dfCoor.loc[2, recorrido.bits[0]]), 0, (0, 0, 0))
      screen.blit(texto1,(730,15))
      texto1 = fuente.render("Logitud de Trayecto:", 0, (0, 0, 0))
      screen.blit(texto1,(600,40))
      texto1 = fuente.render(str(recorrido.distancia), 0, (0, 0, 0))
      screen.blit(texto1,(780,40))
      texto1 = fuente.render("Kms", 0, (0, 0, 0))
      screen.blit(texto1,(850,40))
      texto1 = fuente.render("Recorrido:", 0, (0, 0, 0))
      screen.blit(texto1,(600,70))
      # el bucle principal
      while True:
         alt=90
         # Prevenir posibles entradas del teclado y mouse para que no crashee
         for event in pygame.event.get():
            if event.type == pygame.QUIT:
               sys.exit()
         
         for i in range(len(recorrido.bits)-1):
            #Dibujamos la linea de una coordenada a otra.      
            pygame.draw.line(screen,color,(dfCoor1.loc[0, recorrido.bits[i]],dfCoor1.loc[1, recorrido.bits[i]]),(dfCoor1.loc[0, recorrido.bits[i+1]],dfCoor1.loc[1, recorrido.bits[i+1]]),2)
         
         for i in range(len(recorrido.bits)):
            #Escribe la lista de ciudades
            texto1 = fuente.render(str(dfCoor.loc[2, recorrido.bits[i]]), 0, (0, 0, 0))
            screen.blit(texto1,(600,alt))
            alt=alt+20
         
         pygame.display.update()
         time.sleep(1)
   
   empezar(respElit)

#Helpers
def dibujo(recorrido, dfCoor, SCREEN_WIDTH, SCREEN_HEIGHT):
      pygame.init()
      # Creamos la ventana y le indicamos un titulo:
      screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
      pygame.display.set_caption("Problema del viajante - Grupo 5")

      color = pygame.Color(70,80,150)
      screen.fill(color=(255,255,255))

      # Cargamos el fondo y redimencionamos
      fondo = pygame.image.load("mapa.jpg").convert()
      fondo = pygame.transform.scale(fondo, (600,700))
      
      # Indicamos la posicion de las "Surface" sobre la ventana
      screen.blit(fondo, (0, 0))
      
      # se muestran lo cambios en pantalla
      pygame.display.flip()

      fuente = pygame.font.Font(None, 25)
      texto1 = fuente.render("Ciudad Inicial:", 0, (0, 0, 0))
      screen.blit(texto1,(600,15))
      texto1 = fuente.render(recorrido[0], 0, (0, 0, 0))
      screen.blit(texto1,(730,15))
      texto1 = fuente.render("Longitud de Trayecto:", 0, (0, 0, 0))
      screen.blit(texto1,(600,40))
      trayecto=str(recorrido[len(recorrido)-1])
      texto1 = fuente.render(trayecto, 0, (0, 0, 0))
      screen.blit(texto1,(785,40))
      texto1 = fuente.render("Kms", 0, (0, 0, 0))
      screen.blit(texto1,(850,40))
      texto1 = fuente.render("Recorrido:", 0, (0, 0, 0))
      screen.blit(texto1,(600,70))

      # Bucle para dibujar todos los caminos y nombres de ciudades
      while True:
         alt=90
         # Prevenir posibles entradas del teclado y mouse para que no crashee
         for event in pygame.event.get():
            if event.type == pygame.QUIT:
               sys.exit()
         for i in range(len(recorrido)-2):
            #Dibujamos la linea de una coordenada a otra.
            pygame.draw.line(screen,color,(dfCoor.loc[0, recorrido[i]],dfCoor.loc[1, recorrido[i]]),(dfCoor.loc[0, recorrido[i+1]],dfCoor.loc[1, recorrido[i+1]]),2)
            #Escribe la lista de ciudades
            texto1 = fuente.render(recorrido[i], 0, (0, 0, 0))
            screen.blit(texto1,(600,alt))
            alt=alt+20  
         pygame.display.update()
         time.sleep(1)

def getRecorrido(ciudadInicial,i,recorrido,distancias,df):
      if i==0:           
         df = df.drop(ciudadInicial)   # Iniciamos el recorrido en la ciudad inicial
         i = 1
      if (len(recorrido)==len(df.columns)):  # Terminamos el recorrido nuevamente en la ciudad inicial 
         recorrido.append(ciudadInicial) 
         recorrido.append(sum(distancias))    
         return recorrido
      else:
         for col in df.columns:
            if recorrido[len(recorrido)-1] == col: # Busca columna de la ultima ciudad añadida
               masCercana = df[col].idxmin()  # Devuelve la ciudad mas cercana (distancia mas chica)
               distancias.append(df[col][masCercana]) # Agregamos la distancia hasta esta ciudad
               recorrido.append(masCercana) # Agregamos la ciudad al recorrido
               if (len(recorrido)==len(df.columns)): # Este bloque es para agregar la distancia al volver a la ciudad de inicio
                  for colu in df.columns:
                        if colu == ciudadInicial:
                           distFinal = df[colu][masCercana]
                           distancias.append(distFinal)
               df = df.drop([masCercana]) # Removemos la ciudad mas cercana de las ciudades a visitar
               getRecorrido(ciudadInicial,i,recorrido, distancias, df) #Empezamos recursividad hasta recorrer todas las ciudades                        
               break

def ventanaEjercicioC():
   ventanaEjercicioC = tk.Toplevel(app)
   ventanaEjercicioC.geometry('500x250')
   ciclos = tk.StringVar()
   entry = tk.Entry(ventanaEjercicioC, textvariable=ciclos)
   entry.place(x=50, y=50)
   button1 = tk.Button(ventanaEjercicioC, text="Con Elitismo", command=lambda : ejercicioC(1,ciclos.get()))
   button2 = tk.Button(ventanaEjercicioC, text="Sin Elitismo", command= lambda: ejercicioC(0,ciclos.get()))
   label = tk.Label(ventanaEjercicioC, text="Ingrese cantidad de ciclos")
   label.pack(padx=100, ipadx=250, pady=10)
   entry.pack(padx=100, ipadx=250, pady=20)
   button1.pack(padx=100, ipadx=250, pady=20)
   button2.pack(padx=100, ipadx=250, pady=20)

def ventanaEjercicioA():
   ventanaA = tk.Toplevel(app)
   ventanaA.geometry('500x250')
   combo = ttk.Combobox(ventanaA, state="readonly")
   combo["values"] = ["Cdad. de Bs. As.", "Córdoba", "Corrientes", "Formosa", "La Plata", "La Rioja", "Mendoza" ,"Neuquén", "Paraná", "Posadas", "Rawson", "Resistencia", "Río Gallegos", "S.F.d.V.d. Catamarca", "S.M. de Tucumán", "S.S. de Jujuy", "Salta", "San Juan", "San Luis","Santa Fe", "Santa Rosa", "Sgo. Del Estero", "Ushuaia", "Viedma"]
   combo.place(x=50, y=50)
   button1 = tk.Button(ventanaA, text="Aceptar", command= lambda: ejercicioA(combo.get()))
   label = tk.Label(ventanaA, text="Ingrese ciudad inicial")
   label.pack(padx=100, ipadx=250, pady=10)
   combo.pack(padx=100, ipadx=250, pady=20)
   button1.pack(padx=100, ipadx=250, pady=20)

app = tk.Tk()
app.geometry('500x250')
app.title("Problema del viajante - Grupo 5")
button1 = tk.Button(app, text="Ejercicio A", command=ventanaEjercicioA)
button2 = tk.Button(app, text="Ejercicio B", command=ejercicioB)
button3 = tk.Button(app, text="Ejercicio C: Algoritmo Genetico", command=ventanaEjercicioC)
button1.pack(padx=100, ipadx=250, pady=20)
button2.pack(padx=100, ipadx=250, pady=20)
button3.pack(padx=100, ipadx=250, pady=20)
app.mainloop()
