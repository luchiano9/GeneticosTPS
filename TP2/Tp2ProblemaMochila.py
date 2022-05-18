
#Un objeto con su id, volumen, valor y su proporcion
class Objeto:                                               
    def __init__(self,id,volumen,valor):  
        self.id = id
        self.volumen = volumen
        self.valor = valor
        if volumen != 0:
            self.proporcion = self.valor/self.volumen

#Una combinacion tiene una lista de objetos y un valor y volumen total
class Combinacion:
    def __init__(self,listaObjetos):
        self.listaObjetos = listaObjetos
        self.setVolumenValor()

    #Calcular el valor y peso total de la combinacion
    def setVolumenValor(self):    
        self.valor = 0
        self.volumen = 0
        for obj in self.listaObjetos:
            self.valor += obj.valor                  
            self.volumen += obj.volumen

#Una mochila tiene una combinacion, un volumen maximo soportado y su volumen cargado actual
class Mochila:
    def __init__(self,volumenSoportado):
        self.combinacion = None
        self.volumenSoportado = volumenSoportado
        self.volumenCargado = 0
    
    #Definimos el proceso de busqueda a traves de una busqueda exhaustiva
    def busquedaExhaustiva(self, listaObjetos):
        #Obtenemos todos los subconjuntos posibles de objetos
        listaExhaustiva = obtenerSubconjuntos(listaObjetos)

        #Creamos una lista de todas las combinaciones con sus propiedades
        listaCombinaciones = []
        for comb in listaExhaustiva:
            listaCombinaciones.append(Combinacion(comb))

        #Validamos y comparamos para obtener la combinacion con mayor valor y que sea apta
        valorMax = 0
        for comb in listaCombinaciones:
            if(comb.volumen <= self.volumenSoportado and comb.valor > valorMax):
                valorMax = comb.valor
                self.combinacion = comb
    
    #Definimos el proceso de busqueda a traves de una busqueda Greedy
    def algoritmoGreedy(self,listaObjetos):
        #Ordenamos la lista segun su proporcion de valor/volumen
        listaObjetos.sort(key=lambda objeto: objeto.proporcion,reverse = True)

        #Agregamos objetos a la mochila en el orden de su proporcion, se evaluan todos aunque 
        #uno no entre el siguiente podria hacerlo
        combinacion = []
        for obj in listaObjetos:
            if(obj.volumen + self.volumenCargado <= self.volumenSoportado):
                combinacion.append(obj)
                self.volumenCargado += obj.volumen
        self.combinacion = Combinacion(combinacion)

def empezar():    
    resp = int(input("Ejercicio 1 y 2 (1 o 2) o 3 (3)? "))
    #Definimos que ejercicio se quiere evaluar y creamos la mochila y la lista segun el caso
    if(resp == 1 or resp == 2):
        mochila = Mochila(4200)
        listaObjetos = [Objeto(1,150,20),Objeto(2,325,40),Objeto(3,600,50),
        Objeto(4,805,36),Objeto(5,430,25),Objeto(6,1200,64),Objeto(7,770,54),
        Objeto(8,60,18),Objeto(9,930,46),Objeto(10,353,28)]
    else:
        mochila = Mochila(3000)
        listaObjetos = [Objeto(1,1800,72),Objeto(2,600,36),Objeto(3,1200,60)]
    
    mochila.busquedaExhaustiva(listaObjetos)
    mostrarDatos(mochila.combinacion, "EXHAUSTIVA", resp)
    print(" ")
    mochila.algoritmoGreedy(listaObjetos)
    mostrarDatos(mochila.combinacion, "HEURISTICA GREEDY", resp)

#Helpers
#Funcion recursiva que nos permite obtener todos los subconjuntos posibles del problema
def obtenerSubconjuntos(conjunto):
    #Definimos el array donde se guardaran todos los subconjuntos
    subconjuntos=[]
    #Empezamos la recursividad
    if(len(conjunto)>1):
        #Llamamos recursvivamente al metodo pero con un elemento menos que antes, para lograr todas
        #las combinaciones posibles e ir agregando cada elemento solo tambien.
        subconjuntos+=obtenerSubconjuntos(conjunto[1:])
        #Asignamos el elemento a agregar a cada subconjunto en esta iteracion
        elemento=[conjunto[0]]
        #Iteramos sobre una copia exacta del array actual de subconjuntos
        for sub in subconjuntos[:]:
            #Se agrega al array principal de subconjuntos cada subconjunto anterior + el nuevo elemento
            subconjuntos.append(sub+elemento)
        #Se agrega el elemento solo a los subconjuntos
        subconjuntos.append(elemento)
    #Se agrega el caso donde solo hay 1 objeto en el conjunto
    else:
        subconjuntos+=[conjunto]
    return subconjuntos

def mostrarDatos(mejorCombinacion, tipoBusqueda, resp):
    print(f"Mejor combinacion con busqueda {tipoBusqueda}:")
    print(f"Valor total: {mejorCombinacion.valor}")
    print(f"Volumen total: {mejorCombinacion.volumen}")
    print("Lista de objetos en la mochila:")
    if resp == 3:
        for i in range (len(mejorCombinacion.listaObjetos)):
            print(f"""Objeto numero {mejorCombinacion.listaObjetos[i].id} peso: {mejorCombinacion.listaObjetos[i].volumen} valor: {mejorCombinacion.listaObjetos[i].valor} proporcion: {round(mejorCombinacion.listaObjetos[i].proporcion,4)}""")
    if resp == 1 or resp == 2: 
        for i in range (len(mejorCombinacion.listaObjetos)):
            print(f"""Objeto numero {mejorCombinacion.listaObjetos[i].id} volumen: {mejorCombinacion.listaObjetos[i].volumen} valor: {mejorCombinacion.listaObjetos[i].valor} proporcion: {round(mejorCombinacion.listaObjetos[i].proporcion,4)}""")

empezar()