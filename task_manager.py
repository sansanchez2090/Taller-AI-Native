"""Gestor de tareas multiusuario (versión final, AI-Native).

Cada tarea pertenece a un usuario y solo ese usuario puede consultarla,
completarla o eliminarla. Sin dependencias externas.

Limitación conocida: el sistema identifica al usuario por su nombre, sin
contraseña (no hay autenticación; queda fuera del alcance del taller).
"""

MAX_TITLE_LENGTH = 100
MAX_USER_LENGTH = 30


class TaskError(Exception):
    """Error base del gestor de tareas."""


class InvalidInputError(TaskError):
    """La entrada del usuario no es válida."""


class UserNotFoundError(TaskError):
    """El usuario no está registrado."""


class TaskNotFoundError(TaskError):
    """La tarea solicitada no existe para ese usuario."""


# ---------------------------------------------------------------- validación
def normalize_user(name):
    """Devuelve el nombre de usuario normalizado o lanza InvalidInputError."""
    if not isinstance(name, str):
        raise InvalidInputError("El nombre de usuario debe ser texto.")
    # DECISIÓN DEL DESARROLLADOR: se normaliza (strip + minúsculas) para que
    # " Ana" y "ana" sean el mismo usuario y nadie pueda confundir identidades
    # con diferencias de espacios o mayúsculas. La IA no lo había contemplado.
    name = name.strip().lower()
    if not name:
        raise InvalidInputError("El nombre de usuario no puede estar vacío.")
    if len(name) > MAX_USER_LENGTH:
        raise InvalidInputError(
            f"El nombre de usuario no puede superar {MAX_USER_LENGTH} caracteres."
        )
    return name


def validate_title(title):
    """Devuelve el título limpio o lanza InvalidInputError."""
    if not isinstance(title, str):
        raise InvalidInputError("El título debe ser texto.")
    title = " ".join(title.split())  # quita espacios sobrantes
    if not title:
        raise InvalidInputError("El título no puede estar vacío.")
    if len(title) > MAX_TITLE_LENGTH:
        raise InvalidInputError(
            f"El título no puede superar {MAX_TITLE_LENGTH} caracteres."
        )
    return title


# DECISIÓN DEL DESARROLLADOR:
# Se utiliza una función independiente para validar el índice. Así la regla
# (entero, base 1, dentro del rango de LAS TAREAS DEL USUARIO) vive en un solo
# lugar y se prueba aparte. Además se rechaza bool (True == 1 en Python) y los
# índices negativos, que en una lista accederían al final sin error.
def validate_index(raw_index, total):
    """Convierte el índice (base 1) a posición de lista (base 0)."""
    if isinstance(raw_index, bool):
        raise InvalidInputError("El índice debe ser un número entero.")
    if isinstance(raw_index, int):
        index = raw_index
    elif isinstance(raw_index, str):
        try:
            index = int(raw_index.strip())
        except ValueError:
            raise InvalidInputError("El índice debe ser un número entero.") from None
    else:
        raise InvalidInputError("El índice debe ser un número entero.")
    if total == 0:
        raise TaskNotFoundError("No tienes tareas registradas.")
    if not 1 <= index <= total:
        raise TaskNotFoundError(
            f"No existe la tarea {index}. Tienes {total} tarea(s)."
        )
    return index - 1


# ------------------------------------------------------------------- lógica
class TaskManager:
    """Almacena las tareas separadas por usuario (en memoria)."""

    def __init__(self):
        # La separación por usuario es estructural: una operación solo recibe
        # la lista del usuario que la pide, por lo que no puede tocar la de otro.
        self._tasks = {}

    def register_user(self, user):
        name = normalize_user(user)
        self._tasks.setdefault(name, [])
        return name

    def _tasks_of(self, user):
        name = normalize_user(user)
        if name not in self._tasks:
            raise UserNotFoundError(f"El usuario '{name}' no existe.")
        return self._tasks[name]

    def create_task(self, user, title):
        tasks = self._tasks_of(user)
        tasks.append({"title": validate_title(title), "done": False})
        return len(tasks)

    def list_tasks(self, user):
        # DECISIÓN DEL DESARROLLADOR: se devuelven copias (la propuesta de la IA
        # devolvía las listas internas) para que nadie altere el estado desde fuera.
        return [dict(task) for task in self._tasks_of(user)]

    def complete_task(self, user, index):
        tasks = self._tasks_of(user)
        tasks[validate_index(index, len(tasks))]["done"] = True

    def delete_task(self, user, index):
        tasks = self._tasks_of(user)
        return tasks.pop(validate_index(index, len(tasks)))["title"]


# ---------------------------------------------------------------------- CLI
def format_tasks(tasks):
    if not tasks:
        return "No tienes tareas."
    return "\n".join(
        f"{i}. [{'x' if t['done'] else ' '}] {t['title']}"
        for i, t in enumerate(tasks, start=1)
    )


def run_cli(manager=None, input_fn=input, print_fn=print):
    """Menú interactivo. No termina ante entradas incorrectas."""
    manager = manager or TaskManager()
    try:
        user = None
        while user is None:
            try:
                user = manager.register_user(input_fn("Usuario: "))
            except InvalidInputError as error:
                print_fn(f"Error: {error}")

        while True:
            print_fn("1. Crear  2. Listar  3. Completar  4. Eliminar  5. Salir")
            option = input_fn("Opción: ").strip()
            try:
                if option == "1":
                    manager.create_task(user, input_fn("Título: "))
                    print_fn("Tarea creada.")
                elif option == "2":
                    print_fn(format_tasks(manager.list_tasks(user)))
                elif option == "3":
                    manager.complete_task(user, input_fn("Número de tarea: "))
                    print_fn("Tarea completada.")
                elif option == "4":
                    manager.delete_task(user, input_fn("Número de tarea: "))
                    print_fn("Tarea eliminada.")
                elif option == "5":
                    print_fn("Hasta luego.")
                    break
                else:
                    print_fn("Opción no válida. Elija un número del 1 al 5.")
            except TaskError as error:
                print_fn(f"Error: {error}")
    except (EOFError, KeyboardInterrupt):
        # DECISIÓN DEL DESARROLLADOR: Ctrl+D / Ctrl+C cierran el menú sin traceback.
        print_fn("\nEntrada finalizada. Hasta luego.")


if __name__ == "__main__":
    run_cli()
