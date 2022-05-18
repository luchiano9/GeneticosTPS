import random
import xlsxwriter
import os
import pandas as pd
import matplotlib.pyplot as plt
from operator import attrgetter

probCrossover = 0.75
probMutacion = 0.05
cantIndividuos = 10
cantGenes = 30
ciclos = 200
coef = pow(2,30) - 1
cantidadCromosomasElitimos = 2
nombreExcel = "tp1Geneticos.xlsx"

#Paso 1: Generar la poblacion inicial
def poblacionInicial():
    #Creamos la coleccion de cromosomas
    cromosomas = []
    #Inicializa cada cromosoma generado de la poblacion con sus propiedades y lo guarda en nuestra coleccion final de cromosomas iniciales
    for individuo in generarUnaPoblacion():
        cromosomas.append(Cromosoma(individuo))
    return cromosomas
def generarUnaPoblacion():
    #Devuelve una coleccion de cromosomas cada uno con todos sus genes generados aleatoriamente
    return [generarUnCromosoma() for i in range(cantIndividuos)]
def generarUnCromosoma():
    #Devuelve un cromosoma con todos sus genes generados aleatoriamente
    return [random.randint(0, 1) for i in range(cantGenes)]

class Cromosoma:
    def __init__(self,individuo = None):
        #Inicializamos el cromosoma calculando y asignando sus propiedades, en el caso que estemos creando un cromosoma máximo inicial lo inicializamos con individuo = None, con el objetivo de solamente analizar su funcion objetivo en las comparaciones.
        if (individuo != None):
            self.individuo = individuo
            #Pasamos el valor binario del cromosoma a decimal
            self.valorDecimal = (int(self.generarBinario(),2)) #int(string,2=base binario)
            self.fObj = self.calculoFuncionObjetivo()
            self.fitness = 0
        else:
            self.fObj = 0

    def calculoFuncionObjetivo(self):
        #Evalua el valor decimal del cromosoma en la funcion objetivo
        return ((self.valorDecimal/coef) ** 2)

    def calcularFitness(self,sumafObj):
        self.fitness = (self.fObj/sumafObj)

    def generarBinario(self):
        #Concatena en un string todos los genes del cromosoma
        binario = ""
        for gen in self.individuo:
            binario += str(gen)
        return binario

class Poblacion:
    def __init__(self,cromosomas):
        self.cromosomas = cromosomas
        self.cromosomaMaximo = Cromosoma() #Inicializamos el cromosoma maximo del ciclo un cromosoma con valor de su funcion objetivo = 0 
        self.minimoObjetivo = 1
        self.sumafObj = 0
        self.promedioObj = 0

    #Paso 2: Calculo y Guardado de datos de los cromosomas
    def calcularYSetearDatos(self):
        for cromosoma in self.cromosomas:
            #Calculo del cromosoma máximo
            if(cromosoma.fObj > self.cromosomaMaximo.fObj):
                self.cromosomaMaximo = cromosoma
            #Calculo del minimoObjetivo
            if(cromosoma.fObj < self.minimoObjetivo):
                self.minimoObjetivo = cromosoma.fObj
            #Calculo de la suma de valores de las funciones objetivo
            self.sumafObj += cromosoma.fObj
        #Calculo del promedio de valores de la funcion objetivo
        self.promedioObj = (self.sumafObj/cantIndividuos)
        #Calculo del fitness de cada cromosoma
        for cromosoma in self.cromosomas:
            cromosoma.calcularFitness(self.sumafObj)

    #Paso 3: Seleccion por metodo de ruleta
    def seleccionRuleta(self, hayElitismo):
        individuos = cantIndividuos
        if(hayElitismo): 
            individuos -= cantidadCromosomasElitimos
        #Creamos la colección de pares
        pares = []
        #Iteramos en la cantidad de pares que tendremos
        for i in range(int(individuos/2)):
            #Agregamos un par vacio a la colección de pares
            pares.append([])
            #Agregamos los 2 cromosomas al par los cuales los elegimos de nuestros cromosomas segun el peso que ejerza el valor del fitness de cada uno.
            for _ in range(2):
                pares[i].append(random.choices(self.cromosomas,self.getListafitness())[0])
        return pares

    def seleccionTorneo(self):
        pares = []
        for _ in range(int(cantIndividuos/2)):
            peleadores = []
            for _ in range(2):
                peleador1 = self.cromosomas[random.randint(0,9)]
                while True:
                    peleador2 = self.cromosomas[random.randint(0,9)]
                    if peleador2 != peleador1:
                        break
                if peleador1.fitness > peleador2.fitness:
                    peleadores.append(peleador1)
                else:
                    peleadores.append(peleador2)
            pares.append(peleadores)
        return pares

    #Paso 4: Crossover y mutación de la población
    def aplicarCrossoverMutacion(self,pares):
        #En este paso aplicamos crossover y mutacion segun corresponda a cada cromosoma
        #Creamos la siguiente poblacion
        sigPoblacion = []
        #Iteramos dentro de cada par de nuestro array de pares
        for par in pares:
            #Determinamos si hay crossover y asignamos el punto de corte segun el resultado
            if(self.evaluarProcesoEvolutivo(probCrossover)):
                puntoCorte = random.randint(0,cantGenes)
            else:
                puntoCorte = cantGenes
            #Recorremos el par actual
            for i in range(2):
                #Creamos el proximo individuo
                individuo = []
                #Agregamos los genes de un padre hasta el primer punto de corte
                for j in range(puntoCorte):
                    individuo.append(par[i].individuo[j])
                #Agregamos los genes del otro padre desde el punto de corte hasta la cantidad máxima de genes completando el individuo
                for j in range(puntoCorte,cantGenes):
                    individuo.append(par[abs(i-1)].individuo[j])
                #Determinamos si hay mutacion y asignamos el punto a mutar de haberlo
                if(self.evaluarProcesoEvolutivo(probMutacion)):
                    puntoAMutar = random.randint(0,cantGenes-1)
                    #Cambiamos el gen de 0 a 1 o viceversa
                    individuo[puntoAMutar] = abs(individuo[puntoAMutar]-1)
                #Creamos el cromosoma partiendo de nuestro individuo
                cromosoma = Cromosoma(individuo)
                #Agregamos el cromosa creado a la siguiente población
                sigPoblacion.append(cromosoma)
        #Devolvemos la nueva población
        return sigPoblacion

    def evaluarProcesoEvolutivo(self,probNecesaria):
        #Pasamos por parametro la probabilidad necesaria para que ocurra el suceso que queremos (crossover o mutacion en este caso) y retorna True o False segun corresponda realizar el proceso
        return (random.choices([0,1],[1-probNecesaria,probNecesaria])[0] == 1)

    def aplicarElitismo(self,cantidadCromosomasElitimos):
        cromosomasElite = []
        for _ in range(cantidadCromosomasElitimos):
            #Obtenemos el cromosoma con mayor fitness
            indiceCromosomaMaximo = max(self.cromosomas,key=attrgetter('fitness')) 

            #Lo eliminamos de los cromosomas de la poblacion actual y a la vez lo asignamos a la lista de elite
            cromosomasElite.append(self.cromosomas.pop(self.cromosomas.index(indiceCromosomaMaximo))) 
        return cromosomasElite

    def getListafitness(self):
        #Inicializamos la coleccion de los valores fitness
        listafitness = []
        #Agregamos el fitness de cada cromosoma a la coleccion
        for cromosoma in self.cromosomas:
            listafitness.append(cromosoma.fitness)
        return listafitness

def inicio():
    global poblacion, cromosomaMaximoCorrida
    #Inicializamos el excel para las tablas
    inicializarExcel() 
    #Inicializamos el cromosoma maximo como un cromosoma con funcion objetivo = 0
    cromosomaMaximoCorrida = Cromosoma() 
    #Definimos si usamos o no elitismo en esta corrida
    elitismo = False 
    #Creamos la poblacion Inicial
    poblacion = Poblacion(poblacionInicial())
    for i in range(ciclos):
        
        #Calculamos los datos y propiedades de la poblacion
        poblacion.calcularYSetearDatos()
        #Actualizamos el cromosoma maximo de la corrida
        if(poblacion.cromosomaMaximo.fObj > cromosomaMaximoCorrida.fObj):
            cromosomaMaximoCorrida = poblacion.cromosomaMaximo
        if(elitismo):
            #Coleccion de los proximos cromosomas en elitismo
            proximosCromosomas = []
            #Obtenemos los cromosomas con mejor fitness
            proximosCromosomas = poblacion.aplicarElitismo(cantidadCromosomasElitimos)

        #Elegimos los pares, comentar metodo que no se desea usar
        pares = poblacion.seleccionRuleta(elitismo)
        #pares = poblacion.seleccionTorneo()

        #Agregamos los datos de la poblacion al excel
        agregarDatos(i+1)
        #Mostramos por consola los datos del ciclo actual
        datosCiclo(i+1)
        #Aplicamos crossover y mutacion a la población
        poblacion = Poblacion(poblacion.aplicarCrossoverMutacion(pares))
        #Si aplicamos elitimos se agregan los cromosomas de la elite a la poblacion siguiente, sino no se agrega nada
        poblacion.cromosomas += proximosCromosomas
    workbook.close()
    #Grafica los resultados
    agregaGrafico()
    #Abrimos el archivo recien creado
    os.system(nombreExcel) 

#Funciones auxiliares
def agregarDatos(i):
    cont = i
    worksheet.write(cont,0,i)
    worksheet.write(cont,1,poblacion.minimoObjetivo)
    worksheet.write(cont,2,poblacion.cromosomaMaximo.fObj)
    worksheet.write(cont,3,poblacion.cromosomaMaximo.valorDecimal)
    worksheet.write(cont,4,poblacion.cromosomaMaximo.generarBinario())
    worksheet.write(cont,5,poblacion.promedioObj)

def agregaGrafico():
    excel=pd.read_excel(nombreExcel)
    excel.to_csv('tp1Geneticos.csv', index=None, header=True)
    datos=pd.read_csv('tp1Geneticos.csv',header=0)
    _, ax = plt.subplots()
    ax.plot(datos['Mínimo'], label='Mínimo')
    ax.plot(datos['Máximo'], label='Máximo')
    ax.plot(datos['Promedio'], label='Promedio')
    plt.legend(loc='lower right')
    plt.show()

def inicializarExcel():
    global worksheet,chart,workbook
    
    #Eliminamos archivo anterior para evitar errores
    os.popen('del '+nombreExcel) 
    workbook = xlsxwriter.Workbook(nombreExcel)
    worksheet = workbook.add_worksheet()
    chart = workbook.add_chart({'type': 'line'})
    worksheet.conditional_format('F1:F201', {'type': '3_color_scale', "min_color": "#FF0000", "mid_color": "#FFFF00", "max_color": "#008000", "min_value": 0,  "max_value": 1})
    worksheet.write(0,0, 'Ciclo')
    worksheet.write(0,1, 'Mínimo')
    worksheet.write(0,2, 'Máximo')
    worksheet.write(0,3, 'Cromosoma máximo decimal')
    worksheet.write(0,4, 'Cromosoma máximo')
    worksheet.write(0,5, 'Promedio')

def datosCiclo(num):
    print(f"Ciclo {num} completado. Datos:")
    print(f"Maximo funcion objetivo: {poblacion.cromosomaMaximo.fObj} \n Suma funciones objetivo: {poblacion.sumafObj} \n Minimo función objetivo: {poblacion.minimoObjetivo} \n Promedio funcion objetivo: {poblacion.promedioObj} \n Cromosoma Maximo: {poblacion.cromosomaMaximo.individuo}")
    print()
    if(num == ciclos):
        print("Corrida finalizada")
        print(f"Cromosoma maximo de toda la corrida: {cromosomaMaximoCorrida.individuo}")
        print(f"Función objetivo del cromosoma maximo de la corrida: {cromosomaMaximoCorrida.fObj}")

inicio()
