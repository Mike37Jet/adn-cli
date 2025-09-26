# 📦 Guía de Distribución ADN CLI

Esta guía explica todas las formas de distribuir ADN CLI a otros usuarios.

## 🚀 Métodos de Distribución Disponibles

### 1. PyPI (Python Package Index) - 🥇 RECOMENDADO

**Para usuarios finales:**
```bash
pip install adn-cli
```

**Para publicar (desarrolladores):**
```bash
python publish_pypi.py
```

**Ventajas:**
- ✅ Instalación con una línea
- ✅ Actualizaciones automáticas
- ✅ Distribución global
- ✅ Manejo de dependencias

---

### 2. Ejecutables Standalone - 💻 FÁCIL PARA USUARIOS

**Para crear ejecutables:**
```bash
python build_executable.py
```

**Para usuarios finales:**
- Windows: Descargar `adn-cli.exe` y ejecutar
- Linux/macOS: Descargar `adn-cli`, hacer `chmod +x` y ejecutar

**Ventajas:**
- ✅ No requiere Python
- ✅ Un solo archivo
- ✅ Funciona inmediatamente
- ✅ Ideal para usuarios no técnicos

---

### 3. Instalación con Una Línea - ⚡ MUY RÁPIDO

**Windows (PowerShell):**
```powershell
iwr -useb https://raw.githubusercontent.com/Mike37Jet/adn-cli/main/install.ps1 | iex
```

**Linux/macOS:**
```bash
curl -sSL https://raw.githubusercontent.com/Mike37Jet/adn-cli/main/install.sh | bash
```

**Ventajas:**
- ✅ Instalación automática completa
- ✅ Detecta Python automáticamente
- ✅ Maneja errores común

---

### 4. GitHub Releases - 📦 PROFESIONAL

El workflow `.github/workflows/release.yml` automatiza:
- ✅ Construcción automática de ejecutables
- ✅ Releases con archivos descargables
- ✅ Versionado automático
- ✅ Distribución multi-plataforma

---

### 5. Instalador Local - 🔧 OFFLINE

**Para crear:**
Copia `install_simple.py` a otra PC y ejecuta:
```bash
python install_simple.py
```

**Ventajas:**
- ✅ Funciona sin internet
- ✅ Instalación guiada
- ✅ Detección automática de problemas

---

## 📋 Checklist de Distribución

### Antes de Distribuir:

- [ ] **Actualizar versión** en `pyproject.toml`
- [ ] **Ejecutar tests** con `python -m pytest`
- [ ] **Verificar que funciona** con `adn --version`
- [ ] **Limpiar archivos temporales** (ya hecho con tu limpieza)
- [ ] **Actualizar CHANGELOG.md** con cambios
- [ ] **Commit y tag** de la versión

### Para Distribución Completa:

```bash
# 1. Crear ejecutables
python build_executable.py

# 2. Publicar en PyPI
python publish_pypi.py

# 3. Crear release en GitHub
git tag v1.0.0
git push origin v1.0.0
```

---

## 🎯 Recomendaciones por Usuario

### Para Desarrolladores Python:
```bash
pip install adn-cli
```

### Para Usuarios No Técnicos:
1. Descargar ejecutable desde GitHub Releases
2. O usar script de una línea

### Para Equipos Corporativos:
1. Publicar en PyPI interno
2. O distribuir ejecutables via red corporativa

### Para Testing:
1. TestPyPI primero
2. Luego PyPI oficial

---

## 🔧 Scripts Incluidos

| Script | Propósito |
|--------|-----------|
| `install_simple.py` | Instalador local automático |
| `build_executable.py` | Crear .exe y binarios |
| `publish_pypi.py` | Publicar en PyPI |
| `install.sh` | Instalador Unix con una línea |
| `install.ps1` | Instalador Windows con una línea |

---

## 🚀 Próximos Pasos Recomendados

1. **Publicar en PyPI**: La forma más profesional
2. **Crear GitHub Release**: Con ejecutables descargables
3. **Actualizar README**: Con instrucciones de instalación
4. **Crear documentación**: Para usuarios finales

---

## 💡 Tips Importantes

- **Versioning**: Usa semantic versioning (1.0.0, 1.0.1, etc.)
- **Testing**: Siempre prueba en TestPyPI antes de PyPI
- **Seguridad**: Usa tokens de API en lugar de contraseñas
- **Automatización**: Los workflows de GitHub facilitan todo
- **Documentación**: Usuarios necesitan instrucciones claras

¡Tu proyecto está listo para distribución profesional! 🎉