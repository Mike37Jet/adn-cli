# Guía de Instalación - ADN CLI

## Precondiciones

### Requisito: Python instalado

ADN CLI requiere **Python 3.8 o superior**. Antes de instalar, asegúrate de tener Python configurado correctamente.

#### Verificar Python existente

```bash
# Verificar versión de Python
python --version

# Verificar que pip funciona
pip --version
```

#### Instalación recomendada de Python (Windows)

Si tienes problemas con pip o múltiples versiones de Python:

1. **Desinstalar versiones existentes:**
   - Ve a **Configuración > Aplicaciones**
   - Busca "Python" y desinstala todas las versiones
   - Elimina también cualquier instalación manual

2. **Instalar desde Microsoft Store (RECOMENDADO):**
   - Abre **Microsoft Store**
   - Busca "Python 3.11" o la versión más reciente
   - Instala la versión oficial de Python Software Foundation
   - Esta instalación incluye pip y se configura automáticamente

3. **Verificar instalación:**
   ```bash
   python --version
   pip --version
   ```

4. **Configurar PATH para scripts de Python:**
   - Después de instalar Python desde Microsoft Store, asegúrate de agregar el directorio de scripts al PATH
   - Ve a **Configuración > Sistema > Acerca de > Configuración avanzada del sistema**
   - Haz clic en **Variables de entorno**
   - En **Variables del usuario**, busca **Path** y haz clic en **Editar**
   - Agrega esta ruta (ajustando según tu usuario y versión de Python):
   ```
   C:\Users\[TU_USUARIO]\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.XX_[ID_ALEATORIO]\LocalCache\local-packages\PythonXXX\Scripts
   ```
   - **Ejemplo para Python 3.13:**
   ```
   C:\Users\migue\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\LocalCache\local-packages\Python313\Scripts
   ```
   - Haz clic en **Aceptar** para guardar
   - **Reinicia PowerShell** para que los cambios surtan efecto

## Métodos Disponibles AHORA

### Opción 1: Desde código fuente (RECOMENDADO)

**Si ya tienes el proyecto descargado:**
```bash
# Entrar al directorio del proyecto
cd adn-cli

# Instalar en modo desarrollo
pip install -e .

# Verificar instalación
adn --version
```

### Opción 2: Desde repositorio Git

```bash
# Clonar e instalar directamente
git clone https://github.com/Mike37Jet/adn-cli.git
cd adn-cli
pip install -e .
```

### Opción 3: Para desarrollo (con herramientas extra)

```bash
# Si quieres contribuir al proyecto
git clone https://github.com/Mike37Jet/adn-cli.git
cd adn-cli
pip install -e ".[dev]"
```

## Instalación manual (Si tienes archivos dist/)

### Si generaste archivos de distribución localmente:

**Archivo Wheel:**
```bash
# Solo si existe el archivo
pip install adn_cli-1.0.0-py3-none-any.whl
```

**Archivo Source:**
```bash
# Solo si existe el archivo  
pip install adn_cli-1.0.0.tar.gz
```

**Nota:** Estos archivos se generan con `python -m build` o los scripts incluidos

## Verificación

Después de instalar, verifica que funciona:

```bash
# Ver versión
adn --version

# Ver ayuda
adn --help

# Inicializar configuración
adn config init

# Ver comandos disponibles
adn list-files --help
```

## Actualización

Para actualizar a una nueva versión:

```bash
# Si instalaste desde código fuente
cd adn-cli
git pull
pip install -e .

# Si instalaste desde wheel/tar.gz local
pip install --upgrade adn_cli-[nueva-version]-py3-none-any.whl
```

## Desinstalación

```bash
pip uninstall adn-cli
```

## Requisitos del sistema

- **Python**: 3.8 o superior
- **Sistema operativo**: Windows, macOS, Linux
- **Dependencias**: Se instalan automáticamente con pip

## Solución de problemas

### Comando `adn` no encontrado

```bash
# Verifica la instalación
pip list | grep adn

# Si instalaste desde código fuente, reinstala
cd adn-cli
pip install -e .
```

### El comando `adn` está instalado pero no se encuentra (Windows)

Si ves un mensaje como "WARNING: The script adn.exe is installed in '...' which is not on PATH":

```powershell
# Agregar el directorio de scripts de Python al PATH (sesión actual)
$env:PATH += ";C:\Users\[TU_USUARIO]\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.XX_[ID_ALEATORIO]\LocalCache\local-packages\PythonXXX\Scripts"

# Ejemplo para Python 3.13:
$env:PATH += ";C:\Users\migue\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\LocalCache\local-packages\Python313\Scripts"

# Verificar que funciona
adn --version
```

**Nota:** Reemplaza `[TU_USUARIO]` con tu nombre de usuario, `3.XX` con tu versión de Python (ej: 3.11, 3.12, 3.13), `[ID_ALEATORIO]` con el identificador único que aparece en tu sistema, y `PythonXXX` con el número correspondiente (ej: Python311, Python312, Python313).

### Errores de permisos

```bash
# Instalar para el usuario actual solamente
pip install --user -e .
```

### Conflictos de dependencias

```bash
# Crear entorno virtual limpio
python -m venv adn_env
adn_env\Scripts\activate     # Windows
# o
source adn_env/bin/activate  # Linux/Mac

# Instalar en el ambiente limpio
pip install -e .
```