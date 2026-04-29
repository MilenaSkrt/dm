from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import Optional
import sys
import io
import traceback
import time
import threading
import math  # разрешаем math

router = APIRouter(prefix="/sandbox", tags=["sandbox"])


class CodeExecutionRequest(BaseModel):
    code: str = Field(..., description="Python код для выполнения", min_length=1, max_length=5000)
    stdin: Optional[str] = Field(None, description="Входные данные для программы")
    timeout: Optional[int] = Field(5, description="Таймаут выполнения в секундах", ge=1, le=10)


class ExecutionResult(BaseModel):
    success: bool
    output: str
    error: Optional[str] = None
    execution_time: float


def execute_code_with_timeout(code: str, input_data: str, timeout: int):
    """Выполнение кода с таймаутом в отдельном потоке"""
    result = {
        "success": False,
        "output": "",
        "error": None
    }

    def target():
        try:
            # Сохраняем оригинальные потоки
            old_stdout = sys.stdout
            old_stderr = sys.stderr
            old_stdin = sys.stdin

            # Создаем буферы для захвата вывода
            stdout_capture = io.StringIO()
            stderr_capture = io.StringIO()

            # Перенаправляем вывод
            sys.stdout = stdout_capture
            sys.stderr = stderr_capture

            # Разрешенные модули для импорта
            allowed_modules = {
                'math': math,
                'random': __import__('random'),
                'time': __import__('time'),
                'datetime': __import__('datetime'),
                'collections': __import__('collections'),
                'itertools': __import__('itertools'),
                'functools': __import__('functools'),
                'string': __import__('string'),
            }

            # Настраиваем безопасный импорт
            def safe_import(name, *args, **kwargs):
                if name in allowed_modules:
                    return allowed_modules[name]
                raise ImportError(f"Модуль '{name}' не разрешен в песочнице")

            # Настраиваем безопасное пространство имен
            safe_builtins = {
                'print': print,
                'range': range,
                'len': len,
                'str': str,
                'int': int,
                'float': float,
                'bool': bool,
                'list': list,
                'dict': dict,
                'tuple': tuple,
                'set': set,
                'abs': abs,
                'max': max,
                'min': min,
                'sum': sum,
                'sorted': sorted,
                'enumerate': enumerate,
                'zip': zip,
                'map': map,
                'filter': filter,
                'any': any,
                'all': all,
                'round': round,
                'pow': pow,
                'divmod': divmod,
                'isinstance': isinstance,
                'type': type,
                'help': lambda *args, **kwargs: "Справка отключена в песочнице",
                '__import__': safe_import,
                '__name__': '__sandbox__',
            }

            # Настройка input
            input_lines = (input_data or "").split('\n')
            input_index = 0

            def safe_input(prompt=""):
                nonlocal input_index
                if prompt:
                    safe_builtins['print'](prompt, end='')
                if input_index < len(input_lines) and input_lines[input_index].strip():
                    result = input_lines[input_index]
                    input_index += 1
                    return result
                elif input_index < len(input_lines):
                    input_index += 1
                    return ""
                return ""

            safe_builtins['input'] = safe_input

            # Глобальное пространство
            safe_globals = {
                '__builtins__': safe_builtins,
                '__name__': '__sandbox__',
            }

            # Добавляем разрешенные модули в глобальное пространство
            for mod_name, mod in allowed_modules.items():
                safe_globals[mod_name] = mod

            # Выполняем код
            exec(code, safe_globals)

            # Получаем вывод
            output = stdout_capture.getvalue()
            error = stderr_capture.getvalue()

            result["output"] = output + error if output or error else ""
            result["success"] = True

            # Восстанавливаем потоки
            sys.stdout = old_stdout
            sys.stderr = old_stderr
            sys.stdin = old_stdin

        except Exception as e:
            error_msg = traceback.format_exc()
            result["error"] = error_msg
            result["success"] = False

    # Запускаем в отдельном потоке
    thread = threading.Thread(target=target)
    thread.daemon = True
    thread.start()
    thread.join(timeout)

    if thread.is_alive():
        result["error"] = f"Превышен таймаут выполнения ({timeout} секунд)"
        result["success"] = False
        result["output"] = ""

    return result


@router.post("/run", response_model=ExecutionResult)
async def run_python_code(request: CodeExecutionRequest):
    """
    Безопасное выполнение Python кода
    """
    # Проверка на опасный код
    dangerous_patterns = [
        '__import__', 'eval', 'exec', 'compile',
        'open', 'file', '__builtins__', 'globals', 'locals',
        '__subclasses__', '__class__', '__bases__',
        'os.', 'subprocess', 'socket', 'requests',
        'importlib', '__code__', '__func__', 'breakpoint',
        '__loader__', '__spec__', '__getattribute__',
        'system', 'popen', 'kill', 'exit'
    ]

    code_lower = request.code.lower()
    for pattern in dangerous_patterns:
        if pattern in code_lower:
            return ExecutionResult(
                success=False,
                output="",
                error=f"🛡️ Безопасность: код содержит запрещенный паттерн '{pattern}'",
                execution_time=0.0
            )

    # Ограничение длины
    if len(request.code) > 5000:
        return ExecutionResult(
            success=False,
            output="",
            error="❌ Код слишком длинный (максимум 5000 символов)",
            execution_time=0.0
        )

    start_time = time.time()

    # Выполняем код
    result = execute_code_with_timeout(
        request.code,
        request.stdin or "",
        request.timeout
    )

    execution_time = time.time() - start_time

    if result["success"]:
        output = result["output"]
        if not output:
            output = "✅ Код выполнен успешно (нет вывода)"

        return ExecutionResult(
            success=True,
            output=output,
            error=None,
            execution_time=round(execution_time, 3)
        )
    else:
        error_msg = result["error"] or "Неизвестная ошибка"
        # Очищаем ошибку от лишних деталей
        lines = error_msg.split('\n')
        clean_error = '\n'.join(lines[:10])  # Только первые 10 строк
        return ExecutionResult(
            success=False,
            output="",
            error=clean_error,
            execution_time=round(execution_time, 3)
        )


@router.get("/health")
async def health_check():
    """Проверка статуса"""
    return {"status": "healthy", "mode": "python sandbox"}


@router.get("/templates")
async def get_templates():
    """Возвращает примеры кода"""
    return {
        "templates": {
            "golden": {
                "name": "Метод золотого сечения",
                "code": '''import math

def f(x):
    return (x - 2)**2 + 1

def golden_section_search(a, b, eps=0.001):
    phi = (1 + math.sqrt(5)) / 2
    iterations = 0

    print("Поиск минимума f(x) = (x-2)^2 + 1")
    print("Интервал: [{}, {}]".format(a, b))

    while abs(b - a) > eps:
        iterations += 1
        x1 = b - (b - a) / phi
        x2 = a + (b - a) / phi

        if f(x1) < f(x2):
            b = x2
        else:
            a = x1

        print("Итерация {}: [{:.4f}, {:.4f}]".format(iterations, a, b))

    min_x = (a + b) / 2
    print("\\nРезультат:")
    print("Минимум в x = {:.6f}".format(min_x))
    print("f(x) = {:.6f}".format(f(min_x)))
    return min_x

golden_section_search(0, 5)'''
            },
            "gradient": {
                "name": "Градиентный спуск",
                "code": '''def f(x):
    return x**2 - 4*x + 4

def gradient(x):
    return 2*x - 4

def gradient_descent(start_x, learning_rate=0.1, iterations=20):
    x = start_x
    print("Градиентный спуск для f(x) = x^2 - 4x + 4")
    print("Начальная точка: {}".format(x))

    for i in range(iterations):
        grad = gradient(x)
        x = x - learning_rate * grad
        print("Шаг {}: x = {:.6f}, f(x) = {:.6f}".format(i+1, x, f(x)))

        if abs(grad) < 0.0001:
            print("Сходимость достигнута!")
            break

    print("\\nМинимум в x = {:.6f}".format(x))
    print("f(x) = {:.6f}".format(f(x)))
    return x

gradient_descent(5.0, 0.1)'''
            }
        }
    }