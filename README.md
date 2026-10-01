# Gestor de tareas: Taller AI-Native Software Engineer

Gestor de tareas multiusuario en Python, desarrollado como solución al taller práctico **AI-Native Software Engineer**. Parte de un programa con errores funcionales y de seguridad, que se analizó, corrigió y validó usando un asistente de IA (Claude) dentro de un proceso de ingeniería:

```text
comprende → proporciona contexto → solicita → verifica → prueba → corrige → documenta
```

## Funcionalidades

- Crear, listar, completar y eliminar tareas.
- Cada tarea pertenece a un usuario: nadie puede ver ni modificar las tareas de otro.
- Validación de usuario, título e índice, con mensajes de error claros.
- El menú no se cierra ante entradas incorrectas (texto en lugar de número, índices fuera de rango, Ctrl+D).
- Solo biblioteca estándar; sin bases de datos ni frameworks.

## Archivos

| Archivo | Descripción |
|---|---|
| `task_manager.py` | **Versión final.** Lógica (`TaskManager`) e interfaz de consola (`run_cli`). |
| `test_task_manager.py` | 39 pruebas automáticas con pytest. |
| `task_manager_ai_native.py` | Primera propuesta de la IA, antes de la revisión humana (conservada como evidencia). |
| `task_manager_original.py` | Código original con errores (conservado como evidencia). |
| `Documento_de_evidencias.docx` | Análisis, prompts, evidencias, comparación y reflexión. |

> Las pruebas importan el módulo `task_manager`, por lo que solo funcionan con la versión final.

## Requisitos

- Python 3.9 o superior
- pytest (solo para las pruebas)

```bash
pip install pytest
```

## Uso

```bash
python task_manager.py
```

Menú:

```text
1. Crear  2. Listar  3. Completar  4. Eliminar  5. Salir
```

Los números de tarea empiezan en 1 y son propios de cada usuario. Al eliminar una tarea, los números de las siguientes se recorren.

### Uso como biblioteca

```python
from task_manager import TaskManager

tm = TaskManager()
tm.register_user("ana")
tm.create_task("ana", "Informe trimestral")
tm.complete_task("ana", 1)
print(tm.list_tasks("ana"))   # [{'title': 'Informe trimestral', 'done': True}]
```

Errores posibles (todos heredan de `TaskError`):

| Excepción | Cuándo ocurre |
|---|---|
| `InvalidInputError` | Usuario, título o índice con formato inválido. |
| `UserNotFoundError` | El usuario no está registrado. |
| `TaskNotFoundError` | El número de tarea no existe para ese usuario. |

## Pruebas

```bash
python -m pytest -v
```

Resultado esperado: `39 passed`. Las pruebas cubren:

- Crear, listar, completar y eliminar.
- Restricción por usuario e intentos de modificar tareas ajenas.
- Índice inválido (`0`, `-1`, `99`, `abc`, `1.5`, `True`).
- Usuario inexistente.
- Entradas incorrectas (título vacío, solo espacios o de más de 100 caracteres).
- Menú interactivo con entradas simuladas, incluido el fin de entrada.

## Problemas corregidos respecto al original

| Problema original | Solución |
|---|---|
| El listado mostraba tareas de todos los usuarios | Tareas almacenadas por usuario |
| Se podían completar o eliminar tareas ajenas | Cada operación solo accede a la lista del usuario que la pide |
| `IndexError` con índice inexistente | `TaskNotFoundError` con mensaje claro |
| El índice `-1` operaba sobre la última tarea | Solo se aceptan números de 1 a n |
| `ValueError` con texto no numérico | `InvalidInputError` |
| Usuarios y títulos vacíos o sin límite | Validación y normalización |
| Estado global y lógica mezclada con `print`/`input` | Clase `TaskManager` separada de `run_cli` |
| Sin pruebas | Suite de 39 pruebas |

## Decisiones del desarrollador

Marcadas en el código con `# DECISIÓN DEL DESARROLLADOR`:

- Numeración de tareas por usuario, en lugar de índices globales.
- Función independiente `validate_index`, que rechaza `bool` y negativos.
- Normalización del nombre de usuario (sin espacios sobrantes y en minúsculas).
- `list_tasks` devuelve copias para no exponer el estado interno.
- Cierre limpio del menú ante Ctrl+D / Ctrl+C.

## Limitaciones

- No hay autenticación: el sistema confía en el nombre de usuario ingresado.
- Los datos viven solo en memoria y se pierden al cerrar el programa.
