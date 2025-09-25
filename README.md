# ADN CLI - Automatización de Documentos y Notas

**ADN CLI** es un framework CLI profesional para automatizar la creación de documentos de extracción y notas estructuradas a partir de archivos PDF, así como la conversión de archivos CSV a documentos Markdown individuales con metadatos estructurados.

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## Características principales

- **Procesamiento automático de PDFs**: Genera archivos de extracción con metadatos estructurados
- **Conversión CSV a Markdown**: Transforma archivos CSV en documentos Markdown individuales con YAML front-matter
- **Gestión inteligente de directorios**: Crea automáticamente carpetas de salida y estructura de directorios
- **Sistema de templates flexible**: Personaliza el formato de salida usando Jinja2
- **Configuración cross-platform**: Funciona en Windows, macOS y Linux
- **CLI intuitiva**: Interfaz de línea de comandos rica con colores y ayuda detallada
- **Procesamiento por lotes**: Procesa múltiples archivos simultáneamente con opciones de directorio personalizadas
- **Validación robusta**: Sistema completo de validación y manejo de errores
- **Encoding automático**: Detecta automáticamente diferentes codificaciones de archivos
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

### 4. Especificar directorio de salida

```bash
# El CLI crea automáticamente la carpeta si no existe
adn create --all --output-dir C:\mis_extracciones
adn create documento.pdf --output-dir ./resultados
```

### 5. Convertir CSV a archivos Markdown

```bash
# Convertir archivo CSV a archivos .md numerados
adn csv-to-md convert datos.csv

# Especificar directorio de salida
adn csv-to-md convert datos.csv --output-dir ./markdown_files

# Validar CSV antes de procesar
adn csv-to-md validate datos.csv
```

---

## Uso

### Comandos principales

#### Crear archivos de extracción

```bash
# Archivo individual
adn create documento.pdf

# Archivo individual con directorio de salida personalizado
adn create documento.pdf --output-dir C:\mis_documentos

# Todos los PDFs del directorio actual
adn create --all

# Todos los PDFs con directorio de salida específico (crea la carpeta automáticamente)
adn create --all --output-dir C:\extracciones

# Con opciones personalizadas
adn create documento.pdf --template custom --output-dir ./extracciones

# Forzar sobrescritura de archivos existentes
adn create --all --output-dir C:\resultados --force

# Usando patrones glob
adn create glob "*.pdf" --template academico --output-dir ./salida

# Usando subcomandos específicos
adn create file documento.pdf --output-dir C:\archivos
adn create all --output-dir C:\todos_los_pdfs
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

#### Conversión CSV a Markdown

```bash
# Convertir CSV a archivos Markdown individuales
adn csv-to-md convert datos.csv

# Especificar directorio de salida
adn csv-to-md convert datos.csv --output-dir ./documentos

# Iniciar numeración desde un número específico
adn csv-to-md convert datos.csv --start-number 10

# Forzar sobrescritura de archivos existentes
adn csv-to-md convert datos.csv --force

# Validar estructura del CSV antes de procesar
adn csv-to-md validate datos.csv
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
adn --verbose create --all

# Suprimir salida no esencial
adn --quiet create documento.pdf

# Ver ayuda
adn --help
adn create --help
adn config --help

# Ver versión
adn --version
```

### Opciones comunes del comando create

| Opción | Alias | Descripción |
|--------|-------|-------------|
| `--output-dir` | `-o` | Directorio donde guardar archivos (se crea automáticamente) |
| `--template` | `-t` | Template personalizado a usar |
| `--force` | `-f` | Sobrescribir archivos existentes |
| `--all` | | Procesar todos los PDFs del directorio |
| `--pattern` | `-p` | Patrón de archivos (por defecto: `*.pdf`) |
| `--skip-processed` | | Omitir archivos ya procesados (por defecto: true) |

---

## Gestión de directorios de salida

### Creación automática de carpetas

ADN CLI **crea automáticamente** los directorios de salida si no existen:

```bash
# Crea C:\documentos si no existe
adn create --all --output-dir C:\documentos

# Crea toda la estructura de carpetas padre
adn create documento.pdf --output-dir C:\proyectos\2025\analisis\resultados

# Funciona con rutas relativas
adn create --all --output-dir ./extracciones/febrero
```

### Comportamiento por defecto

- **Sin `--output-dir`**: Los archivos se guardan junto al PDF original
- **Con `--output-dir`**: Se usa el directorio especificado (se crea si no existe)
- **Carpetas padre**: Se crean automáticamente todas las carpetas necesarias
- **Permisos**: Respeta los permisos del sistema operativo

### Ejemplos prácticos

```bash
# Organización por fecha
adn create --all --output-dir "C:\extracciones\2025\enero"

# Separar por tipo de documento
adn create informes*.pdf --output-dir C:\trabajo\informes
adn create facturas*.pdf --output-dir C:\trabajo\facturas

# Estructura para proyectos
adn create --all --output-dir C:\proyectos\cliente-a\documentos
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
adn create --all --template academico --output-dir C:\investigacion\analisis
```

### Gestión de documentos corporativos

```bash
# Configurar para documentos corporativos
adn config set default_template "corporativo"
adn config set preserve_structure true

# Procesar documentos manteniendo estructura
adn create glob "**/*.pdf" --output-dir C:\empresa\procesados

# Procesar por departamentos
adn create --all --output-dir C:\empresa\rrhh --template corporativo
adn create --all --output-dir C:\empresa\finanzas --template financiero
```

### Notas personales

```bash
# Template simple para notas
adn config set output_suffix "_notas"
adn create documento.pdf --template simple --output-dir C:\mis_notas

# Organizar por fecha
adn create --all --output-dir "C:\notas\$(Get-Date -Format 'yyyy-MM')"

# Procesar libros y documentos de estudio
adn create --all --output-dir C:\estudio\extracciones --template academico
```

---

## Conversión CSV a Markdown

ADN CLI incluye una funcionalidad completa para convertir archivos CSV a archivos Markdown individuales con metadatos estructurados.

### Formato de CSV requerido

El archivo CSV debe contener las siguientes columnas obligatorias:

```csv
source,doi,title,abstract
"Journal of Computer Science","10.1234/jcs.2023.001","Machine Learning Applications","Este artículo explora..."
"IEEE Transactions","10.1109/tai.2023.002","Neural Networks for NLP","Una revisión comprehensive..."
```

**Columnas requeridas:**
- `source`: Fuente de la información
- `doi`: Identificador único del documento
- `title`: Título del artículo/documento
- `abstract`: Resumen del contenido

### Formato de salida

Cada registro del CSV genera un archivo `.md` con numeración secuencial (`001.md`, `002.md`, etc.) y el siguiente formato:

```yaml
---
source: Journal of Computer Science
doi: 10.1234/jcs.2023.001
title: Machine Learning Applications in Healthcare
abstract: Este artículo explora las aplicaciones del aprendizaje automático...
estado:
  - procesado
tags:
  - documento
  - investigacion
---
```

### Comandos disponibles

#### Validar archivo CSV

```bash
# Verificar que el CSV tenga las columnas requeridas
adn csv-to-md validate datos.csv

# Ejemplo de salida:
# ✓ Archivo CSV válido
# Archivo: datos.csv
# Columnas encontradas: abstract, doi, source, title
# Número de registros: 25
```

#### Convertir CSV a Markdown

```bash
# Conversión básica (usa directorio actual)
adn csv-to-md convert papers.csv

# Especificar directorio de salida
adn csv-to-md convert papers.csv --output-dir ./markdown_docs

# Iniciar numeración desde número específico
adn csv-to-md convert papers.csv --start-number 50

# Forzar sobrescritura de archivos existentes
adn csv-to-md convert papers.csv --force

# Combinando opciones
adn csv-to-md convert papers.csv --output-dir ./docs --start-number 1 --force
```

### Opciones del comando convert

| Opción | Alias | Descripción | Por defecto |
|--------|-------|-------------|-------------|
| `--output-dir` | `-o` | Directorio de salida para archivos Markdown | Directorio actual |
| `--start-number` | `-s` | Número inicial para la nomenclatura de archivos | 1 |
| `--force` | `-f` | Sobrescribir archivos existentes | No |

### Manejo de datos faltantes

El sistema maneja correctamente los datos faltantes:

```csv
source,doi,title,abstract
"Complete Journal","10.1234/complete","Complete Article","Full abstract here"
"Missing DOI Journal",,"Article Without DOI","Abstract without DOI"
,,"Missing Everything",
```

Los campos vacíos aparecen como valores vacíos en el YAML front-matter:

```yaml
---
source: Missing DOI Journal
doi: 
title: Article Without DOI
abstract: Abstract without DOI
estado:
  - procesado
tags:
  - documento
  - investigacion
---
```

### Características técnicas

- **Encoding automático**: Detecta automáticamente UTF-8, Latin-1, CP1252
- **Validación robusta**: Verifica columnas requeridas antes de procesar
- **Manejo de errores**: Mensajes claros para archivos inválidos o faltantes
- **Nomenclatura secuencial**: Archivos numerados con formato de 3 dígitos
- **Progreso visual**: Barra de progreso durante el procesamiento
- **Compatibilidad**: Funciona con diferentes formatos de CSV

### Casos de uso

#### Biblioteca de investigación

```bash
# Procesar base de datos de papers académicos
adn csv-to-md convert academic_papers.csv --output-dir ./biblioteca

# Resultado: 001.md, 002.md, 003.md...
# Cada archivo contiene metadatos estructurados listos para gestores de referencias
```

#### Documentación corporativa

```bash
# Convertir catálogo de documentos corporativos  
adn csv-to-md convert documentos_empresa.csv --output-dir ./docs_empresa --start-number 100

# Resultado: 100.md, 101.md, 102.md...
# Metadatos listos para sistemas de gestión documental
```

#### Gestión de conocimiento

```bash
# Procesar base de conocimiento en lotes
adn csv-to-md convert kb_articles.csv --output-dir ./knowledge_base

# Validar antes de procesar archivos grandes
adn csv-to-md validate large_dataset.csv
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