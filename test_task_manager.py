import pytest

from task_manager import (
    InvalidInputError,
    TaskManager,
    TaskNotFoundError,
    UserNotFoundError,
    run_cli,
    validate_index,
)


@pytest.fixture
def tm():
    manager = TaskManager()
    manager.register_user("ana")
    manager.register_user("bob")
    return manager


# ------------------------------------------------------------ casos normales
def test_crear_tarea(tm):
    assert tm.create_task("ana", "Informe") == 1
    assert tm.list_tasks("ana") == [{"title": "Informe", "done": False}]


def test_listar_tareas_en_orden(tm):
    tm.create_task("ana", "A")
    tm.create_task("ana", "B")
    assert [t["title"] for t in tm.list_tasks("ana")] == ["A", "B"]


def test_completar_tarea(tm):
    tm.create_task("ana", "A")
    tm.complete_task("ana", 1)
    assert tm.list_tasks("ana")[0]["done"] is True


def test_eliminar_tarea(tm):
    tm.create_task("ana", "A")
    tm.create_task("ana", "B")
    assert tm.delete_task("ana", 1) == "A"
    assert [t["title"] for t in tm.list_tasks("ana")] == ["B"]


# ------------------------------------------------------ restricción por usuario
def test_usuario_solo_ve_sus_tareas(tm):
    tm.create_task("ana", "Privada de ana")
    tm.create_task("bob", "De bob")
    assert [t["title"] for t in tm.list_tasks("bob")] == ["De bob"]


def test_no_puede_completar_tarea_ajena(tm):
    tm.create_task("ana", "Privada de ana")
    with pytest.raises(TaskNotFoundError):
        tm.complete_task("bob", 1)  # bob no tiene tareas
    assert tm.list_tasks("ana")[0]["done"] is False


def test_no_puede_eliminar_tarea_ajena(tm):
    tm.create_task("ana", "Privada de ana")
    tm.create_task("bob", "De bob")
    tm.delete_task("bob", 1)  # solo borra la de bob
    assert [t["title"] for t in tm.list_tasks("ana")] == ["Privada de ana"]
    assert tm.list_tasks("bob") == []


def test_no_se_puede_modificar_estado_interno_desde_el_listado(tm):
    tm.create_task("ana", "A")
    tm.list_tasks("ana")[0]["done"] = True
    assert tm.list_tasks("ana")[0]["done"] is False


def test_usuario_normalizado_no_permite_suplantacion_por_formato(tm):
    tm.create_task("ana", "A")
    assert tm.list_tasks("  ANA ")[0]["title"] == "A"


# ---------------------------------------------------------- índice inválido
@pytest.mark.parametrize("indice", [0, -1, 2, 99])
def test_indice_fuera_de_rango(tm, indice):
    tm.create_task("ana", "A")
    with pytest.raises(TaskNotFoundError):
        tm.complete_task("ana", indice)
    with pytest.raises(TaskNotFoundError):
        tm.delete_task("ana", indice)


@pytest.mark.parametrize("indice", ["abc", "", "1.5", None, 1.5, True, [1]])
def test_indice_no_entero(tm, indice):
    tm.create_task("ana", "A")
    with pytest.raises(InvalidInputError):
        tm.complete_task("ana", indice)


def test_validate_index_lista_vacia():
    with pytest.raises(TaskNotFoundError):
        validate_index(1, 0)


def test_validate_index_acepta_texto_numerico():
    assert validate_index(" 2 ", 3) == 1


# -------------------------------------------------------- usuario inexistente
@pytest.mark.parametrize(
    "operacion",
    [
        lambda m: m.list_tasks("fantasma"),
        lambda m: m.create_task("fantasma", "x"),
        lambda m: m.complete_task("fantasma", 1),
        lambda m: m.delete_task("fantasma", 1),
    ],
)
def test_usuario_inexistente(tm, operacion):
    with pytest.raises(UserNotFoundError):
        operacion(tm)


# ---------------------------------------------------------- entrada incorrecta
@pytest.mark.parametrize("titulo", ["", "   ", None, 123, "x" * 101])
def test_titulo_invalido(tm, titulo):
    with pytest.raises(InvalidInputError):
        tm.create_task("ana", titulo)
    assert tm.list_tasks("ana") == []


@pytest.mark.parametrize("usuario", ["", "   ", None, 5, "u" * 31])
def test_usuario_invalido_al_registrar(usuario):
    with pytest.raises(InvalidInputError):
        TaskManager().register_user(usuario)


# ------------------------------------------------------------------------ CLI
def ejecutar_cli(entradas):
    salidas = []
    iterador = iter(entradas)

    def entrada(_prompt=""):
        try:
            return next(iterador)
        except StopIteration:
            raise EOFError from None  # simula Ctrl+D / fin de la entrada

    run_cli(TaskManager(), entrada, salidas.append)
    return "\n".join(salidas)


def test_cli_no_se_cae_con_entradas_incorrectas():
    salida = ejecutar_cli(
        ["", "ana", "9", "1", "   ", "3", "abc", "4", "-5", "2", "5"]
    )
    assert "El nombre de usuario no puede estar vacío" in salida
    assert "Opción no válida" in salida
    assert "El título no puede estar vacío" in salida
    assert "El índice debe ser un número entero" in salida
    assert "No tienes tareas registradas" in salida
    assert "Hasta luego." in salida


def test_cli_flujo_completo():
    salida = ejecutar_cli(["ana", "1", "Informe", "3", "1", "2", "4", "1", "2", "5"])
    assert "1. [x] Informe" in salida
    assert "No tienes tareas." in salida


def test_cli_termina_limpio_si_se_acaba_la_entrada():
    salida = ejecutar_cli(["ana"])  # la entrada se acaba en el menú
    assert "Entrada finalizada" in salida
