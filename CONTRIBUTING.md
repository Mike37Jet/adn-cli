# Guía de contribución para ADN CLI

¡Gracias por tu interés en contribuir a ADN CLI! Esta guía te ayudará a empezar.

## Cómo empezar

### 1. Fork del repositorio

```bash
# Fork el repositorio en GitHub, luego clona tu fork
git clone https://github.com/tu-usuario/adn-cli.git
cd adn-cli
```

### 2. Configurar entorno de desarrollo

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# Instalar dependencias de desarrollo
pip install -e .[dev]

# O usar el instalador automático
python install.py dev
```

### 3. Configurar pre-commit hooks

```bash
pre-commit install
```

### 4. Ejecutar tests

```bash
# Tests básicos
pytest

# Tests con cobertura
pytest --cov=adn --cov-report=html
```

### 5. Verificar calidad de código

```bash
# Formatear código
black adn/ tests/

# Organizar imports
isort adn/ tests/

# Verificar lint
flake8 adn/
mypy adn/
```

---

## Tipos de contribución

### Reportar bugs

1. Busca primero si el bug ya existe en Issues
2. Si no existe, crea un nuevo issue con:
   - Descripción clara del problema
   - Pasos para reproducir
   - Comportamiento esperado vs actual
   - Información del sistema (OS, Python version, etc.)

### Sugerir mejoras

1. Revisa primero las issues existentes y el roadmap
2. Abre una nueva issue con:
   - Descripción clara de la mejora
   - Justificación del beneficio
   - Propuesta de implementación (opcional)

### Contribuir código

1. Asigna o crea una issue relacionada
2. Crea una rama desde main: `git checkout -b feature/nombre-feature`
3. Realiza tus cambios siguiendo los estándares de código
4. Añade tests para nuevas funcionalidades
5. Ejecuta todos los tests y verificaciones de calidad
6. Haz commit siguiendo las convenciones
7. Envía un Pull Request

---

## Estándares de código

### Formateo y estilo

- **Black**: Formateo automático de código
- **isort**: Organización de imports
- **Flake8**: Análisis estático básico
- **MyPy**: Verificación de tipos

### Configuración de herramientas

#### Black
```toml
# pyproject.toml
[tool.black]
line-length = 88
target-version = ['py38']
include = '\.pyi?$'
```

#### isort
```toml
# pyproject.toml
[tool.isort]
profile = "black"
multi_line_output = 3
line_length = 88
```

#### Flake8
```ini
# .flake8
[flake8]
max-line-length = 88
extend-ignore = E203, W503
```

### Convenciones de código

#### Nomenclatura

- **Variables y funciones**: `snake_case`
- **Clases**: `PascalCase`
- **Constantes**: `UPPER_SNAKE_CASE`
- **Archivos y módulos**: `snake_case`

#### Documentación

```python
def process_pdf(file_path: Path, template: str = "default") -> Path:
    """
    Procesar un archivo PDF y generar archivo de extracción.
    
    Args:
        file_path: Ruta del archivo PDF a procesar
        template: Nombre del template a utilizar
        
    Returns:
        Path: Ruta del archivo de extracción generado
        
    Raises:
        FileNotFoundError: Si el archivo PDF no existe
        TemplateError: Si el template especificado no es válido
    """
```

#### Type hints

```python
from typing import Optional, Dict, Any, List
from pathlib import Path

def get_config_value(
    key: str, 
    default: Optional[Any] = None
) -> Any:
    """Obtener valor de configuración con type hints."""
```

### Estructura de commits

#### Formato de commits

```
tipo(scope): descripción breve

Descripción más detallada si es necesaria.

- Cambio específico 1
- Cambio específico 2

Fixes #123
```

#### Tipos de commit

- `feat`: Nueva funcionalidad
- `fix`: Corrección de bug
- `docs`: Cambios en documentación
- `style`: Cambios de formato (no afectan funcionalidad)
- `refactor`: Refactorización de código
- `test`: Añadir o modificar tests
- `chore`: Tareas de mantenimiento

#### Ejemplos

```bash
feat(create): añadir soporte para procesamiento por lotes

Implementa la funcionalidad para procesar múltiples PDFs
simultáneamente con barra de progreso.

- Añade comando create --batch
- Implementa ThreadPoolExecutor para paralelización
- Añade progress bar con Rich

Closes #45
```

```bash
fix(config): corregir validación de templates personalizados

Fixes #67
```

### Tests

#### Estructura de tests

```python
import pytest
from pathlib import Path
from adn.commands.create import create_file

class TestCreateCommand:
    """Tests para el comando create."""
    
    def test_create_file_success(self, temp_pdf, temp_dir):
        """Test creación exitosa de archivo de extracción."""
        # Arrange
        output_file = temp_dir / "test_extraccion.md"
        
        # Act
        result = create_file(temp_pdf, output_dir=temp_dir)
        
        # Assert
        assert output_file.exists()
        assert "annotation-target" in output_file.read_text()
    
    def test_create_file_missing_pdf(self, temp_dir):
        """Test manejo de archivo PDF inexistente."""
        # Arrange
        missing_pdf = temp_dir / "missing.pdf"
        
        # Act & Assert
        with pytest.raises(FileNotFoundError):
            create_file(missing_pdf)
```

#### Fixtures compartidas

```python
# tests/conftest.py
import pytest
from pathlib import Path
import tempfile

@pytest.fixture
def temp_dir():
    """Directorio temporal para tests."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)

@pytest.fixture  
def temp_pdf(temp_dir):
    """Archivo PDF temporal para tests."""
    pdf_file = temp_dir / "test.pdf"
    pdf_file.write_bytes(b"%PDF-1.4 fake pdf content")
    return pdf_file
```

---

## Convenciones

### Estructura del proyecto

```
adn-cli/
├── adn/                 # Código fuente principal
│   ├── __init__.py
│   ├── cli.py          # CLI principal
│   ├── commands/       # Comandos del CLI
│   ├── utils/          # Utilidades compartidas
│   └── templates/      # Templates por defecto
├── tests/              # Tests
├── docs/               # Documentación
├── scripts/            # Scripts de desarrollo
├── pyproject.toml      # Configuración del proyecto
├── README.md
├── CONTRIBUTING.md
└── LICENSE
```

### Manejo de errores

```python
from adn.utils.exceptions import ADNError, ConfigError

class TemplateNotFoundError(ADNError):
    """Error cuando no se encuentra un template."""
    pass

def load_template(name: str) -> str:
    """Cargar template con manejo de errores apropiado."""
    try:
        # Lógica de carga
        return template_content
    except FileNotFoundError:
        raise TemplateNotFoundError(f"Template '{name}' no encontrado")
    except Exception as e:
        logger.exception(f"Error cargando template {name}")
        raise ConfigError(f"Error en configuración: {e}")
```

### Logging

```python
from adn.utils.logger import get_logger

logger = get_logger(__name__)

def process_files(files: List[Path]) -> None:
    """Procesar archivos con logging apropiado."""
    logger.info(f"Procesando {len(files)} archivos")
    
    for file_path in files:
        try:
            logger.debug(f"Procesando {file_path}")
            # Lógica de procesamiento
            logger.info(f"Procesado exitosamente: {file_path}")
        except Exception as e:
            logger.error(f"Error procesando {file_path}: {e}")
            raise
```

### Configuración

```python
from adn.utils.config import ConfigManager

def get_user_preference(key: str, default: Any = None) -> Any:
    """Obtener preferencia con fallback a configuración."""
    config = ConfigManager()
    return config.get_config_value(key, default)
```

---

¡Gracias por contribuir a ADN CLI!