# Proyecto de Persistencia Políglota - Red Social

## 📋 Descripción del Proyecto

Sistema completo de red social que implementa **persistencia políglota**, utilizando dos bases de datos complementarias:

- **PostgreSQL**: Base de datos relacional para almacenar datos estructurados (usuarios, publicaciones, amistades)
- **Neo4j**: Base de datos de grafos para modelar y consultar relaciones sociales complejas

## 🗂️ Estructura de Archivos

```
final-andres/
├── configuracion.json              # Credenciales y configuración de conexión
├── sistema_red_social.sql          # Script SQL con estructura y datos de prueba
├── inicializar_bd.py               # Script para crear/actualizar PostgreSQL
├── migracion_poliglota.py          # Script para migrar datos a Neo4j
├── aplicacion_red_social.py        # Aplicación GUI completa (Tkinter)
└── README.md                       # Este archivo
```

## 🚀 Guía de Uso

### Opción 1: Aplicación GUI Completa (Recomendada) ✨

La forma más sencilla de usar el proyecto es ejecutar la aplicación gráfica:

```bash
python aplicacion_red_social.py
```

#### Funcionalidades de la Aplicación:

**Pestaña Usuarios (👤)**
- Registrar nuevos usuarios con nombre, email y país
- Visualizar todos los usuarios registrados
- Los emails deben ser únicos

**Pestaña Publicaciones (📝)**
- Crear publicaciones seleccionando un usuario autor
- Ver todas las publicaciones con fecha, autor y contador de likes
- Contenido de hasta 280 caracteres recomendados

**Pestaña Solicitudes (📨)**
- Enviar solicitudes de amistad entre usuarios
- Ver todas las solicitudes pendientes
- Aceptar o rechazar solicitudes
- Validación automática (no auto-solicitudes, no duplicados)

**Pestaña Amistades (👥)**
- Visualizar todas las amistades confirmadas
- Ver fechas de aceptación
- Explorar la red social completa

**Pestaña Migración (🔄)**
- Migrar todos los datos a Neo4j con un clic
- Ver log detallado del proceso de migración
- Limpiar la base de datos Neo4j si es necesario
- Las migraciones son idempotentes (puedes ejecutarlas múltiples veces)

### Opción 2: Scripts Individuales

Si prefieres ejecutar los procesos por separado:

#### 1. Configurar Credenciales

Edita `configuracion.json` con tus credenciales:

```json
{
    "postgresql": {
        "nombre_bd": "red_social_db",
        "usuario": "tu_usuario",
        "clave": "tu_contraseña",
        "servidor": "localhost"
    },
    "neo4j": {
        "direccion_uri": "bolt://localhost:7687",
        "usuario": "neo4j",
        "clave": "tu_contraseña",
        "borrar_al_iniciar": false
    }
}
```

#### 2. Inicializar Base de Datos PostgreSQL

```bash
python inicializar_bd.py
```

Este script:
- Crea la base de datos `red_social_db` si no existe
- Crea todas las tablas (usuarios, publicaciones, comentarios, amistades)
- Agrega restricciones de integridad referencial
- Inserta datos de prueba (24 usuarios, 20 publicaciones, 25 amistades)
- Crea procedimientos almacenados y vistas
- Es **idempotente**: puedes ejecutarlo múltiples veces sin problemas

#### 3. Migrar Datos a Neo4j

```bash
python migracion_poliglota.py
```

Este script:
- Lee datos de PostgreSQL
- Crea nodos `:Persona` para cada usuario
- Crea nodos `:Post` para cada publicación
- Crea relaciones `:AMIGO_DE` entre usuarios
- Crea relaciones `:PUBLICO` entre usuarios y sus publicaciones
- Usa MERGE para evitar duplicados

## 📦 Requisitos

### Python y Librerías

```bash
# Instalar dependencias
pip install psycopg2-binary neo4j

# Opcional para GUI avanzada en migracion_poliglota.py
pip install PyQt5
```

**Nota**: La aplicación principal (`aplicacion_red_social.py`) usa **Tkinter**, que viene incluido con Python. No requiere instalaciones adicionales.

### Bases de Datos

- **PostgreSQL** (versión 12 o superior)
  - Servicio ejecutándose en puerto 5432 (por defecto)
  - Usuario con permisos para crear bases de datos
  
- **Neo4j** (versión 4.0 o superior)
  - Servicio ejecutándose en puerto 7687 (bolt)
  - Credenciales configuradas

## 🔧 Arquitectura del Sistema

### Modelo de Datos PostgreSQL

```
usuarios
├── id_usuario (PK)
├── nombre
├── email (UNIQUE)
├── fecha_registro
└── pais

publicaciones
├── id_publicacion (PK)
├── texto_contenido
├── fecha_publicacion
├── likes_contador
└── autor_id (FK → usuarios)

amistades
├── id_amistad (PK)
├── fecha_amistad
├── estado (PENDIENTE/ACEPTADA)
├── usuario_solicitante_id (FK → usuarios)
└── usuario_receptor_id (FK → usuarios)
```

### Modelo de Grafos Neo4j

```
(:Persona {id_sql, nombre, email})
(:Post {id_sql, texto})

Relaciones:
(:Persona)-[:AMIGO_DE]->(:Persona)
(:Persona)-[:PUBLICO]->(:Post)
```

## 🎯 Características Técnicas

### Validaciones Implementadas

- ✅ Emails únicos para usuarios
- ✅ No permitir auto-amistades (CHECK constraint)
- ✅ Evitar solicitudes duplicadas (procedimiento almacenado)
- ✅ Validación de campos obligatorios en la GUI
- ✅ Manejo de errores con mensajes descriptivos

### Procedimientos Almacenados

**`crear_amistad(id1, id2)`**
- Valida que los usuarios no sean el mismo
- Verifica si ya existe una amistad (en cualquier dirección)
- Crea solicitud con estado PENDIENTE

### Vistas

**`feed_noticias`**
- Muestra publicaciones con nombre de usuario
- Incluye contador de comentarios
- Ordenadas de más reciente a más antigua

## 🐛 Solución de Problemas

### Error de Conexión a PostgreSQL

```
Error de conexión: could not connect to server
```

**Solución**: Verifica que PostgreSQL esté ejecutándose y que las credenciales en `configuracion.json` sean correctas.

### Error de Conexión a Neo4j

```
Error de conexión: Failed to establish connection
```

**Solución**: 
1. Verifica que Neo4j esté ejecutándose
2. Confirma que el puerto 7687 esté accesible
3. Verifica usuario y contraseña en `configuracion.json`

### La Migración No Muestra Datos

**Solución**: Asegúrate de haber ejecutado `inicializar_bd.py` primero para crear los datos en PostgreSQL.

## 📚 Recursos Adicionales

### Consultas Útiles en Neo4j

```cypher
// Ver todos los usuarios
MATCH (p:Persona) RETURN p

// Ver red de amistades
MATCH (p1:Persona)-[:AMIGO_DE]->(p2:Persona) 
RETURN p1, p2

// Encontrar amigos de amigos
MATCH (p:Persona {nombre: "Ana Garcia"})-[:AMIGO_DE*2]->(amigo) 
RETURN DISTINCT amigo

// Ver publicaciones de un usuario
MATCH (p:Persona)-[:PUBLICO]->(post:Post) 
WHERE p.nombre = "Carlos Perez"
RETURN post
```

## 👨‍💻 Autor

Proyecto desarrollado por **Andrés** como parte del curso de Bases de Datos.

## 📄 Licencia

Proyecto educativo - Uso libre para fines académicos.
