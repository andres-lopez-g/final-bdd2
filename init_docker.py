"""
Script de inicialización adaptado para Docker
"""
import os
import sys
import time
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import json

# Esperar a que PostgreSQL esté listo
print("Esperando a que PostgreSQL esté listo...")
max_retries = 30
retry_count = 0

while retry_count < max_retries:
    try:
        # Intentar conectar
        conn = psycopg2.connect(
            dbname='postgres',
            user='postgres',
            password='admin',
            host='postgres'
        )
        conn.close()
        print("✓ PostgreSQL está listo!")
        break
    except psycopg2.OperationalError:
        retry_count += 1
        print(f"Intento {retry_count}/{max_retries}...")
        time.sleep(2)

if retry_count == max_retries:
    print("❌ No se pudo conectar a PostgreSQL")
    sys.exit(1)

# Determinar si estamos en Docker
EN_DOCKER = os.getenv('DOCKER_ENV', 'false') == 'true'

# Cargar configuración apropiada
if EN_DOCKER:
    config_file = 'configuracion.docker.json'
else:
    config_file = 'configuracion.json'

DIRECTORIO_SCRIPT = os.path.dirname(os.path.abspath(__file__))
ruta_config = os.path.join(DIRECTORIO_SCRIPT, config_file)

print(f"Usando configuración: {config_file}")

with open(ruta_config, 'r') as archivo:
    configuracion = json.load(archivo)

CONFIG_POSTGRESQL = configuracion['postgresql']

# Leer SQL
ruta_sql = os.path.join(DIRECTORIO_SCRIPT, 'sistema_red_social.sql')
with open(ruta_sql, 'r', encoding='utf-8') as archivo:
    script_sql = archivo.read()

script_sql = script_sql.replace('\\c red_social_db;', '')

# Filtrar comentarios
lineas = script_sql.split('\n')
lineas_limpias = []
for linea in lineas:
    if linea.strip().startswith('--'):
        continue
    lineas_limpias.append(linea)

script_sql = '\n'.join(lineas_limpias)

# Separar comandos
comandos_sql = []
comando_actual = []
dentro_de_funcion = False
contador_delimitadores = 0

for linea in script_sql.split('\n'):
    linea_limpia = linea.strip()
    if not linea_limpia:
        continue

    if '$$' in linea:
        contador_delimitadores += linea.count('$$')
        dentro_de_funcion = (contador_delimitadores % 2 == 1)

    comando_actual.append(linea)

    if linea_limpia.endswith(';') and not dentro_de_funcion:
        comando_completo = '\n'.join(comando_actual).strip()
        if comando_completo and not comando_completo.startswith('DROP DATABASE') and not comando_completo.startswith('CREATE DATABASE'):
            comandos_sql.append(comando_completo)
        comando_actual = []
        contador_delimitadores = 0

print("\n=== Inicializando Base de Datos ===\n")

try:
    conn = psycopg2.connect(
        dbname='postgres',
        user=CONFIG_POSTGRESQL['user'],
        password=CONFIG_POSTGRESQL['password'],
        host=CONFIG_POSTGRESQL['host']
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()

    cursor.execute("SELECT 1 FROM pg_database WHERE datname='red_social_db'")
    existe_bd = cursor.fetchone()

    if not existe_bd:
        print("1. Creando base de datos red_social_db...")
        cursor.execute("CREATE DATABASE red_social_db;")
        print("   ✓ Base de datos creada")
    else:
        print("1. Base de datos red_social_db ya existe")
        print("   ✓ Usando base de datos existente")

    cursor.close()
    conn.close()

except Exception as error:
    print(f"Error: {error}")
    sys.exit(1)

try:
    conn = psycopg2.connect(
        dbname='red_social_db',
        user=CONFIG_POSTGRESQL['user'],
        password=CONFIG_POSTGRESQL['password'],
        host=CONFIG_POSTGRESQL['host']
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()

    print("2. Ejecutando comandos SQL...")
    for comando in comandos_sql:
        try:
            cursor.execute(comando)
            comando_mayusculas = comando.upper()
            if 'CREATE TABLE' in comando_mayusculas:
                nombre_tabla = comando.split('CREATE TABLE')[1].split('(')[0].strip()
                print(f"   ✓ Tabla: {nombre_tabla}")
            elif 'ALTER TABLE' in comando_mayusculas:
                print(f"   ✓ Restricción añadida")
            elif 'INSERT INTO' in comando_mayusculas:
                nombre_tabla = comando.split('INSERT INTO')[1].split('(')[0].strip()
                print(f"   ✓ Datos: {nombre_tabla}")
            elif 'CREATE OR REPLACE PROCEDURE' in comando_mayusculas:
                proc_name = comando.split('PROCEDURE')[1].split('(')[0].strip()
                print(f"   ✓ Procedimiento: {proc_name}")
            elif 'CREATE OR REPLACE VIEW' in comando_mayusculas:
                view_name = comando.split('VIEW')[1].split('AS')[0].strip()
                print(f"   ✓ Vista: {view_name}")
        except Exception as e:
            if 'already exists' in str(e) or 'ya existe' in str(e):
                pass
            elif 'duplicate key' in str(e) or 'clave duplicada' in str(e):
                pass
            else:
                print(f"   ✗ Error: {e}")

    cursor.close()
    conn.close()

    print("\n✓ Base de datos inicializada correctamente")

except Exception as error:
    print(f"Error: {error}")
    sys.exit(1)
