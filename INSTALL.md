# Guía de Instalación - ADN CLI

## 🚀 Instalación en otra PC

### Opción 1: Archivo Wheel (Recomendado)

1. **Copia el archivo** `adn_cli-1.0.0-py3-none-any.whl` desde la carpeta `dist/`
2. **En la otra PC, ejecuta:**
   ```bash
   pip install adn_cli-1.0.0-py3-none-any.whl
   ```
3. **Verifica la instalación:**
   ```bash
   adn --version
   ```

### Opción 2: Archivo Source

1. **Copia el archivo** `adn_cli-1.0.0.tar.gz` desde la carpeta `dist/`
2. **En la otra PC, ejecuta:**
   ```bash
   pip install adn_cli-1.0.0.tar.gz
   ```

### Opción 3: Desde repositorio Git

```bash
git clone https://github.com/username/adn-cli.git
cd adn-cli
pip install -e .
```

### Opción 4: Instalación completa con dependencias de desarrollo

```bash
git clone https://github.com/username/adn-cli.git
cd adn-cli
pip install -e ".[dev]"
```

## ✅ Verificación

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

## 🔄 Actualización

Para actualizar a una nueva versión:

```bash
# Si instalaste desde wheel/tar.gz
pip install --upgrade adn_cli-[nueva-version]-py3-none-any.whl

# Si instalaste desde código fuente
cd adn-cli
git pull
pip install -e .
```

## 🗑️ Desinstalación

```bash
pip uninstall adn-cli
```

## 📋 Requisitos del sistema

- **Python**: 3.8 o superior
- **Sistema operativo**: Windows, macOS, Linux
- **Dependencias**: Se instalan automáticamente con pip

## 🐛 Solución de problemas

### Comando `adn` no encontrado

```bash
# Verifica la instalación
pip list | grep adn-cli

# Reinstala si es necesario
pip uninstall adn-cli
pip install adn_cli-1.0.0-py3-none-any.whl
```

### Errores de permisos

```bash
# Instalar para el usuario actual solamente
pip install --user adn_cli-1.0.0-py3-none-any.whl
```

### Conflictos de dependencias

```bash
# Crear entorno virtual limpio
python -m venv adn_env
source adn_env/bin/activate  # Linux/Mac
# o
adn_env\Scripts\activate     # Windows

pip install adn_cli-1.0.0-py3-none-any.whl
```