# ADN CLI - Automatización de Documentos y Notas

**ADN CLI** es un framework CLI profesional para automatizar la creación de documentos de extracción y notas estructuradas a partir de archivos PDF.

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## Características principales

- **Procesamiento automático de PDFs**: Genera archivos de extracción con metadatos estructurados
- **Sistema de templates flexible**: Personaliza el formato de salida usando Jinja2
- **Configuración cross-platform**: Funciona en Windows, macOS y Linux
- **CLI intuitiva**: Interfaz de línea de comandos rica con colores y ayuda detallada
- **Procesamiento por lotes**: Procesa múltiples PDFs simultáneamente
- **Validación robusta**: Sistema completo de validación y manejo de errores
- **Logging profesional**: Sistema de logs con rotación automática
- **Extensible**: Arquitectura modular y personalizable

---

## Instalación

### Via pip (Recomendado)

```bash
pip install adn-cli
```

### Instalación desde el código fuente

```bash
# Clonar el repositorio
git clone https://github.com/usuario/adn-cli.git
cd adn-cli

# Instalar en modo desarrollo
pip install -e .

# O usar el instalador automático
python install.py all
```

### Verificar instalación

```bash
adn --help
```

---

## Inicio rápido

### 1. Inicializar configuración

```bash
adn config init
```

### 2. Procesar un archivo PDF

```bash
adn create archivo.pdf
```

### 3. Procesar todos los PDFs en un directorio

```bash
adn create --all
```

---

## Uso

### Comandos principales

#### Crear archivos de extracción

```bash
# Archivo individual
adn create documento.pdf

# Todos los PDFs del directorio actual
adn create --all

# Con opciones personalizadas
adn create documento.pdf --template custom --output-dir ./extracciones

# Usando patrones glob
adn create glob "*.pdf" --template academico
```

#### Gestión de configuración

```bash
# Inicializar configuración
adn config init

# Mostrar configuración actual
adn config show

# Establecer valores
adn config set default_template "academico"
adn config set output_suffix "_resumen"

# Obtener valores específicos
adn config get default_template

# Restablecer configuración por defecto
adn config reset

# Editar templates
adn config template --name academico

# Ver información del sistema
adn config path
```

#### Utilidades

```bash
# Ver estado de procesamiento
adn status

# Listar PDFs en directorio
adn list-files /ruta/a/pdfs

# Limpiar archivos temporales
adn clean

# Ver versión
adn version
```

### Opciones globales

```bash
# Activar logging detallado
adn --verbose comando

# Suprimir salida no esencial
adn --quiet comando

# Ver ayuda
adn --help
adn comando --help
```

---

## Sistema de templates

### Template por defecto

El template por defecto genera metadatos simples:

```yaml
---
annotation-target: nombre_archivo.pdf
---
```

### Crear templates personalizados

```bash
# Crear nuevo template
adn config template --name academico

# Editar template existente
adn config template --name default
```

### Variables disponibles

Los templates usan Jinja2 y tienen acceso a:

- `nombre_archivo`: Nombre del PDF sin extensión
- `nombre_completo`: Nombre completo del archivo PDF
- `fecha_actual`: Objeto datetime actual
- `version_adn`: Versión de ADN CLI
- `tamaño_archivo`: Tamaño del archivo en bytes

### Ejemplo de template personalizado

```markdown
# {{ nombre_archivo }} - Análisis

**Archivo**: {{ nombre_completo }}  
**Fecha**: {{ fecha_actual.strftime("%d/%m/%Y") }}  
**Procesado con**: ADN CLI v{{ version_adn }}

## Resumen

[Espacio para resumen ejecutivo]

## Puntos clave

- [ ] Punto 1
- [ ] Punto 2
- [ ] Punto 3

## Referencias

[Lista de referencias]

---
annotation-target: {{ nombre_completo }}
generated: {{ fecha_actual.isoformat() }}
---
```

---

## Configuración

### Archivo de configuración

La configuración se almacena en:
- **Windows**: `%APPDATA%\adn-cli\config.yaml`
- **macOS/Linux**: `~/.adn/config.yaml`

### Parámetros configurables

| Parámetro | Valor por defecto | Descripción |
|-----------|-------------------|-------------|
| `default_template` | `default` | Template por defecto |
| `output_suffix` | `_extraccion` | Sufijo para archivos de salida |
| `default_output_dir` | `.` | Directorio de salida por defecto |
| `log_level` | `INFO` | Nivel de logging |
| `auto_open_generated` | `false` | Abrir archivos generados |
| `preserve_structure` | `true` | Preservar estructura de directorios |
| `date_format` | `%d/%m/%Y %H:%M` | Formato de fechas |
| `encoding` | `utf-8` | Codificación de archivos |
| `max_filename_length` | `100` | Longitud máxima de nombres |

### Configuración avanzada

```yaml
# config.yaml personalizado
default_template: "academico"
output_suffix: "_notas"
default_output_dir: "./extracciones"
log_level: "DEBUG"
auto_open_generated: true
date_format: "%Y-%m-%d %H:%M:%S"
```

---

## Casos de uso

### Investigación académica

```bash
# Configurar para trabajo académico
adn config set default_template "academico"
adn config set output_suffix "_analisis"

# Procesar papers de investigación
adn create --all --template academico
```

### Gestión de documentos corporativos

```bash
# Configurar para documentos corporativos
adn config set default_template "corporativo"
adn config set preserve_structure true

# Procesar documentos manteniendo estructura
adn create glob "**/*.pdf" --output-dir ./procesados
```

### Notas personales

```bash
# Template simple para notas
adn config set output_suffix "_notas"
adn create documento.pdf --template simple
```

---

## Testing

### Ejecutar tests

```bash
# Tests completos
python -m pytest

# Con cobertura
python -m pytest --cov=adn --cov-report=html

# Tests específicos
python -m pytest tests/test_cli.py -v
```

### Estructura de tests

```
tests/
├── __init__.py
├── conftest.py          # Fixtures compartidas
├── test_cli.py          # Tests de CLI
├── test_config.py       # Tests de configuración
├── test_create.py       # Tests de creación
├── test_file_handler.py # Tests de manejo de archivos
├── test_template.py     # Tests de templates
└── test_utils.py        # Tests de utilidades
```

### Ejecutar tests de calidad

```bash
# Formateo de código
black adn/ tests/

# Organización de imports
isort adn/ tests/

# Análisis estático
flake8 adn/ --max-line-length=88
mypy adn/

# Pre-commit hooks
pre-commit run --all-files
```

### Cobertura de tests

El proyecto mantiene >90% de cobertura de código:

- Tests unitarios completos
- Tests de integración
- Tests de CLI end-to-end
- Validación de configuración
- Manejo de errores

---

## Roadmap

### Versión 1.1.0
- [ ] Soporte para más formatos (DOCX, TXT)
- [ ] API REST opcional
- [ ] Templates con lógica condicional
- [ ] Integración con servicios cloud

### Versión 1.2.0
- [ ] Plugin system
- [ ] Extracción automática de texto con OCR
- [ ] Análisis de contenido con IA
- [ ] Interfaz web opcional

### Versión 2.0.0
- [ ] Arquitectura distribuida
- [ ] Base de datos integrada
- [ ] Colaboración multi-usuario
- [ ] Análisis avanzado de documentos

---

## Licencia

Este proyecto está licenciado bajo la Licencia MIT. Ver el archivo [LICENSE](LICENSE) para más detalles.

### Copyright

Copyright (c) 2025 ADN CLI Contributors

### Contribuciones

Las contribuciones son bienvenidas. Por favor lee [CONTRIBUTING.md](CONTRIBUTING.md) para detalles sobre nuestro código de conducta y el proceso para enviar pull requests.

---

**¿Te gusta ADN CLI?** ¡Dale una estrella en GitHub!