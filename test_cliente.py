# Script para realizar pruebas unitarias
# Fecha creación: 27-10-2026
from unittest.mock import patch, Mock
import pytest
import cliente
from src.consumir_gemini import enviar_peticion

#====================================================================================
# FIXTURE -> Permite reiniciar la variable costo_total_sesion a cero en cada ejecución del script
# Fecha creación: 27-10-2026
#====================================================================================

@pytest.fixture(autouse=True)
def reiniciar_costo_total():
    cliente.costo_total_sesion = 0
    yield

#====================================================================================
# ENVIAR_PETICION -> Sección para testing de credencial inválida, limite de uso y petición con éxito
# Fecha creación: 27-10-2026
#====================================================================================
def test_enviar_peticion_credencial_invalida():
    respuesta_falsa = Mock(status_code=401)

    with patch("src.consumir_gemini.requests.post", return_value=respuesta_falsa):
        with pytest.raises(ValueError):
            enviar_peticion("https://ejemplo.invalid", {"pregunta":"test"})


def test_enviar_peticion_limite_de_uso():
    respuesta_falsa = Mock(status_code=429)

    with patch("src.consumir_gemini.requests.post", return_value=respuesta_falsa):
        with pytest.raises(TimeoutError):
            enviar_peticion("https://ejemplo.invalid", {"pregunta":"test"})

def test_enviar_peticion_exito():
    respuesta_falsa = Mock(status_code=200)
    respuesta_falsa.json.return_value = {"texto" : "respuesta simulada"}

    with patch("src.consumir_gemini.requests.post", return_value=respuesta_falsa):
        resultado = enviar_peticion("https://ejemplo.invalid", {"pregunta":"test"})

    assert resultado == {"texto" : "respuesta simulada"}

#====================================================================================
# CON_REINTENTO -> Sección para testing de agota reintentos, y error con ValueError
# Fecha creación: 27-10-2026
#====================================================================================

def test_con_reintento_agota_intentos():
    def siempre_falla():
        raise TimeoutError("simulado")

    with patch("cliente.time.sleep"):
        with pytest.raises(TimeoutError):
            cliente.con_reintento(siempre_falla, intentos=3)

def test_con_reintento_no_reintenta_value_error():
    operacion = Mock(side_effect=ValueError("simulado"))
    
    with patch("cliente.time.sleep") as dormir:
        with pytest.raises(ValueError):
            cliente.con_reintento(operacion)
            
    operacion.assert_called_once()
    dormir.assert_not_called()            

#====================================================================================
# REGISTRAR_COSTO -> Sección para testing de costo acumulado
# Fecha creación: 27-10-2026
#====================================================================================

def test_registrar_costo_acumula():
    respuesta_falsa = {"usageMetadata": {"totalTokenCount": 1000}}
    costo = cliente.registrar_costo(respuesta_falsa)

    assert costo == cliente.COSTO_POR_1000_TOKENS
    assert cliente.costo_total_sesion == cliente.COSTO_POR_1000_TOKENS

#====================================================================================
# CONSULTAR_MODELO -> Sección para testing de conversión de Error de timeout a runtime
# Fecha creación: 27-10-2026
#====================================================================================

def test_consultar_modelo_convierte_error():
    error_simulado = TimeoutError("simulado")

    with patch("cliente.con_reintento", side_effect=error_simulado):
        with pytest.raises(RuntimeError):
            cliente.consultar_modelo("pregunta de prueba")