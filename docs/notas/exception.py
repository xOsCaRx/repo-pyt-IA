
'''
EXCEPCIONES

Definición: Eventos que ocurren durante la ejecución de un programa que interrumpen el flujo normal de las instrucciones. 
            Pueden ser errores de sintaxis, errores de tiempo de ejecución, errores lógicos, etc.

try     : bloque de código que se ejecuta y puede generar una excepción
except  : capturar la excepción y manejarla
raise   : lanzar una excepción
finally : bloque de código que se ejecuta siempre, haya o no una excepción. 
          Acá podría cerrar conexiones/archivos, liberar recursos, etc.
else    : bloque de código que se ejecuta si no hubo ninguna excepción en el bloque try

SINTAXIS

try:
    # Código que puede generar una excepción
except ErrorType1:
    # Código para manejar la excepción ErrorType1
except ErrorType2:
    # Código para manejar la excepción ErrorType2
else:
    # Código que se ejecuta si no hubo ninguna excepción
finally:
    # Código que se ejecuta siempre, haya o no una excepción


'''
#-------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------
try:
    x = 10
    y = 0
    resultado = x / y
except ZeroDivisionError:
    print("Error: División por cero.")

#-------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------

try:
    numero = int("hola")
except ValueError:
    print("Error: No se puede convertir a entero. Debe ingresar un número válido.")

#-------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------

try:
    txt = "Hola"
    numero = 22
    frase = txt + numero
except TypeError:
    print("Error: No se puede concatenar un string con un número. Los tipos de datos deben ser compatibles para la operación.")

#-------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------

try:
    frutas = ["manzana", "plátano", "naranja"]
    print(frutas[5])
except IndexError:
    print("Error: Índice fuera de rango. La lista tiene menos elementos de los que se intentan acceder.")

#-------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------

try:
    estudiante = {"nombre": "Juan", "apellido": "Perez"}
    print(estudiante["edad"])
except KeyError:
    print("Error: Clave no encontrada en el diccionario. La clave 'edad' no existe en el diccionario 'estudiante'.")    

#-------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------

def dividir():
    try:
        num1 = int(input("Ingrese el primer número: "))
        num2 = int(input("Ingrese el segundo número: "))
        resultado = num1 / num2
        print(f"El resultado de la división es: {resultado}")
    except ValueError:
        print("Error: Debe ingresar un número válido.")
    except ZeroDivisionError:
        print("Error: No se puede dividir por cero.")
    except Exception as e:
        print(f"Error inesperado: {e}") 
    finally:
        print("¡Gracias por usar la calculadora!")

dividir()

#-------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------

try:
    bebida = ["agua", "jugo", "bebida"]
    bebida_deseada = input("Ingrese la bebida que desea: ")
    if bebida_deseada not in bebida:
        raise ValueError("Esta bebida no está disponible.")
    else:
        print(f"Se ha seleccionado la bebida: {bebida_deseada}")
except ValueError as e:
    print(f"Error: {e}")
    
#-------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------