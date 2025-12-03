"""
Script de Inicialización de Base de Datos PostgreSQL
=====================================================
Autor: Andrés
Descripción: Este script ejecuta un archivo SQL para crear/actualizar la base de datos
            de la red social en PostgreSQL. Maneja la creación de la base de datos,
            tablas, datos de prueba y procedimientos almacenados.

Funcionalidades:
- Conexión a PostgreSQL usando credenciales del archivo de configuración
- Creación automática de la base de datos si no existe
- Ejecución de comandos SQL con manejo de errores
- Procesamiento inteligente de scripts SQL con funciones PL/pgSQL
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import json

# =============================================
# CONFIGURACIÓN INICIAL
# =============================================

import os

# Obtener directorio del script
DIRECTORIO_SCRIPT = os.path.dirname(os.path.abspath(__file__))

# Cargar configuración desde archivo JSON
ruta_config = os.path.join(DIRECTORIO_SCRIPT, 'configuracion.json')
with open(ruta_config, 'r') as archivo:
    configuracion = json.load(archivo)

# Extraer parámetros de conexión a PostgreSQL
CONFIG_POSTGRESQL = configuracion['postgresql']

# =============================================
# LECTURA Y PROCESAMIENTO DEL SCRIPT SQL
# =============================================

# Leer el archivo SQL completo
ruta_sql = os.path.join(DIRECTORIO_SCRIPT, 'sistema_red_social.sql')
with open(ruta_sql, 'r', encoding='utf-8') as archivo:
    script_sql = archivo.read()

# Eliminar el comando de cambio de base de datos (no funciona en psycopg2)
script_sql = script_sql.replace('\\c red_social_db;', '')

# Filtrar líneas de comentarios que comienzan con --
lineas = script_sql.split('\n')
lineas_limpias = []
for linea in lineas:
    # Ignorar líneas que solo contienen comentarios
    if linea.strip().startswith('--'):
        continue
    lineas_limpias.append(linea)

# Reconstruir el script sin comentarios
script_sql = '\n'.join(lineas_limpias)

# =============================================
# SEPARACIÓN DE COMANDOS SQL
# =============================================
# Los comandos SQL se separan por punto y coma (;)
# Pero debemos tener cuidado con funciones PL/pgSQL que usan $$ delimitadores

comandos_sql = []
comando_actual = []
dentro_de_funcion = False  # Flag para detectar bloques de función
contador_delimitadores = 0  # Contador de $$ para saber si estamos dentro o fuera

# Procesar línea por línea
for linea in script_sql.split('\n'):
    linea_limpia = linea.strip()
    
    # Saltar líneas vacías
    if not linea_limpia:
        continue

    # Detectar delimitadores $$ (usados en funciones PL/pgSQL)
    if '$$' in linea:
        contador_delimitadores += linea.count('$$')
        # Si el contador es impar, estamos dentro de una función
        dentro_de_funcion = (contador_delimitadores % 2 == 1)

    # Agregar la línea al comando actual
    comando_actual.append(linea)

    # Si la línea termina en ; y NO estamos dentro de una función
    if linea_limpia.endswith(';') and not dentro_de_funcion:
        # Unir todas las líneas del comando
        comando_completo = '\n'.join(comando_actual).strip()
        
        # Filtrar comandos de creación/eliminación de base de datos
        # (estos se manejan por separado)
        if comando_completo and not comando_completo.startswith('DROP DATABASE') and not comando_completo.startswith('CREATE DATABASE'):
            comandos_sql.append(comando_completo)
        
        # Resetear para el siguiente comando
        comando_actual = []
        contador_delimitadores = 0

print("=== Iniciando Configuración de Base de Datos ===\n")

# =============================================
# FASE 1: CREAR BASE DE DATOS (si no existe)
# =============================================

try:
    # Conectar a la base de datos por defecto 'postgres'
    conexion = psycopg2.connect(
        dbname='postgres',
        user=CONFIG_POSTGRESQL['user'],
        password=CONFIG_POSTGRESQL['password'],
        host=CONFIG_POSTGRESQL['host'],
        port=CONFIG_POSTGRESQL.get('port', 5432)
    )
    # Modo autocommit necesario para crear bases de datos
    conexion.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conexion.cursor()

    # Verificar si la base de datos ya existe
    cursor.execute("SELECT 1 FROM pg_database WHERE datname='red_social_db'")
    existe_bd = cursor.fetchone()

    if not existe_bd:
        print("1. Creando base de datos red_social_db...")
        cursor.execute("CREATE DATABASE red_social_db;")
        print("   ✓ Base de datos creada exitosamente")
    else:
        print("1. Base de datos red_social_db ya existe")
        print("   ✓ Usando base de datos existente")

    # Cerrar conexión inicial
    cursor.close()
    conexion.close()

except Exception as error:
    print(f"Error al crear la base de datos: {error}")
    import traceback
    traceback.print_exc()
    exit(1)

# =============================================
# FASE 2: EJECUTAR COMANDOS SQL EN LA BASE DE DATOS
# =============================================

try:
    # Conectar a la base de datos recién creada
    conexion = psycopg2.connect(
        dbname='red_social_db',
        user=CONFIG_POSTGRESQL['user'],
        password=CONFIG_POSTGRESQL['password'],
        host=CONFIG_POSTGRESQL['host'],
        port=CONFIG_POSTGRESQL.get('port', 5432)
    )
    conexion.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conexion.cursor()

    print("2. Ejecutando comandos SQL en la base de datos...")
    
    # Ejecutar cada comando SQL individualmente
    for indice, comando in enumerate(comandos_sql, 1):
        try:
            cursor.execute(comando)
            
            # Proporcionar feedback específico según el tipo de comando
            comando_mayusculas = comando.upper()
            
            if 'CREATE TABLE' in comando_mayusculas:
                # Extraer nombre de tabla
                nombre_tabla = comando.split('CREATE TABLE')[1].split('(')[0].strip()
                print(f"   ✓ Tabla creada: {nombre_tabla}")
                
            elif 'ALTER TABLE' in comando_mayusculas:
                print(f"   ✓ Restricción añadida correctamente")
                
            elif 'INSERT INTO' in comando_mayusculas:
                # Extraer nombre de tabla
                nombre_tabla = comando.split('INSERT INTO')[1].split('(')[0].strip()
                print(f"   ✓ Datos insertados en: {nombre_tabla}")
                
            elif 'CREATE OR REPLACE PROCEDURE' in comando_mayusculas:
                # Extraer nombre del procedimiento
                nombre_procedimiento = comando.split('PROCEDURE')[1].split('(')[0].strip()
                print(f"   ✓ Procedimiento almacenado creado: {nombre_procedimiento}")
                
            elif 'CREATE OR REPLACE VIEW' in comando_mayusculas:
                # Extraer nombre de la vista
                nombre_vista = comando.split('VIEW')[1].split('AS')[0].strip()
                print(f"   ✓ Vista creada: {nombre_vista}")
                
        except Exception as error:
            # Manejar errores comunes que no son críticos
            mensaje_error = str(error)
            
            if 'already exists' in mensaje_error or 'ya existe' in mensaje_error:
                # El objeto ya existe, continuar sin problema
                pass
            elif 'duplicate key' in mensaje_error or 'clave duplicada' in mensaje_error:
                # Dato duplicado, continuar sin problema
                pass
            else:
                # Error inesperado, mostrar mensaje
                print(f"   ✗ Error en comando {indice}: {error}")

    # Cerrar conexión
    cursor.close()
    conexion.close()

    print("\n✓ Base de datos configurada y lista para usar")

except Exception as error:
    print(f"Error al ejecutar comandos SQL: {error}")
    exit(1)
