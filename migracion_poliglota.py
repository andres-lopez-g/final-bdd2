"""
Sistema de Migración de Persistencia Políglota
==============================================
Autor: Andrés
Descripción: Script para migrar datos desde PostgreSQL (base de datos relacional)
            hacia Neo4j (base de datos de grafos). Implementa el patrón de 
            persistencia políglota para aprovechar las fortalezas de ambos sistemas.

Arquitectura:
- PostgreSQL: Almacena datos estructurados y transaccionales
- Neo4j: Modela relaciones complejas como grafos para consultas eficientes

Funcionalidades:
- Migración de usuarios como nodos :Persona
- Migración de publicaciones como nodos :Post
- Creación de relaciones :AMIGO_DE entre personas
- Creación de relaciones :PUBLICO entre personas y sus publicaciones
"""

import psycopg2
from neo4j import GraphDatabase
import json
import sys

# Intentar importar PyQt5 para interfaz gráfica (opcional)
try:
    from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QMessageBox
    GUI_DISPONIBLE = True
except ImportError:
    GUI_DISPONIBLE = False

# =============================================
# CONFIGURACIÓN INICIAL
# =============================================

# Cargar configuración desde archivo JSON
with open('configuracion.json', 'r', encoding='utf-8') as archivo:
    configuracion = json.load(archivo)

# Extraer parámetros de conexión
CONFIG_POSTGRESQL = configuracion['postgresql']
CONFIG_NEO4J = configuracion['neo4j']

# Cargar mapeo de migración desde JSON
try:
    with open('mapeo_migracion.json', 'r', encoding='utf-8') as archivo_mapeo:
        MAPEO_MIGRACION = json.load(archivo_mapeo)
except FileNotFoundError:
    print("⚠️  Archivo mapeo_migracion.json no encontrado, usando migración manual")
    MAPEO_MIGRACION = None

# Configuración predeterminada: no limpiar Neo4j al iniciar
if 'borrar_al_iniciar' not in CONFIG_NEO4J:
    CONFIG_NEO4J['borrar_al_iniciar'] = False


# =============================================
# CLASE PRINCIPAL: MIGRADOR POLÍGLOTA
# =============================================

class MigradorPoliglota:
    """
    Clase encargada de migrar datos entre bases de datos de diferentes paradigmas.
    Maneja conexiones a PostgreSQL (relacional) y Neo4j (grafos).
    """
    
    def __init__(self):
        """
        Constructor: Inicializa las conexiones a ambas bases de datos.
        Si está configurado, limpia Neo4j antes de comenzar.
        """
        try:
            # Conectar a PostgreSQL
            self.conexion_postgres = psycopg2.connect(**CONFIG_POSTGRESQL)
            
            # Conectar a Neo4j
            self.driver_neo4j = GraphDatabase.driver(
                CONFIG_NEO4J['direccion_uri'], 
                auth=(CONFIG_NEO4J['usuario'], CONFIG_NEO4J['clave'])
            )
            
            # Limpiar Neo4j si está configurado
            if CONFIG_NEO4J.get('borrar_al_iniciar', False):
                self.limpiar_neo4j()
                
        except Exception as error:
            print(f"Error al conectar a las bases de datos: {error}")
            sys.exit(1)

    def limpiar_neo4j(self):
        """
        Elimina todos los nodos y relaciones en Neo4j.
        PRECAUCIÓN: Esta operación es irreversible.
        """
        with self.driver_neo4j.session() as sesion:
            # DETACH DELETE elimina nodos y todas sus relaciones
            sesion.run("MATCH (n) DETACH DELETE n")
            print("✓ Neo4j limpiado completamente")

    def obtener_datos_postgresql(self, consulta):
        """
        Ejecuta una consulta SQL en PostgreSQL y retorna los resultados.
        
        Args:
            consulta (str): Consulta SQL a ejecutar
            
        Returns:
            list: Lista de tuplas con los resultados
        """
        with self.conexion_postgres.cursor() as cursor:
            cursor.execute(consulta)
            return cursor.fetchall()

    def crear_nodos_neo4j(self, transaccion, consulta_cypher, registros, etiqueta):
        """
        Crea nodos en Neo4j a partir de registros de PostgreSQL.
        
        Args:
            transaccion: Transacción activa de Neo4j
            consulta_cypher (str): Consulta Cypher para crear nodos
            registros (list): Lista de diccionarios con datos de nodos
            etiqueta (str): Etiqueta del nodo (ej: 'Persona', 'Post')
        """
        for registro in registros:
            # Ejecutar consulta Cypher para cada registro
            transaccion.run(consulta_cypher, **registro)
        print(f"✓ Nodos :{etiqueta} creados exitosamente ({len(registros)} registros)")

    def crear_relaciones_neo4j(self, transaccion, consulta_cypher, registros, tipo_relacion):
        """
        Crea relaciones entre nodos existentes en Neo4j.
        
        Args:
            transaccion: Transacción activa de Neo4j
            consulta_cypher (str): Consulta Cypher para crear relaciones
            registros (list): Lista de diccionarios con datos de relaciones
            tipo_relacion (str): Tipo de relación (ej: 'AMIGO_DE', 'PUBLICO')
        """
        for registro in registros:
            # Ejecutar consulta Cypher para cada relación
            transaccion.run(consulta_cypher, **registro)
        print(f"✓ Relaciones :{tipo_relacion} creadas exitosamente ({len(registros)} registros)")

    def ejecutar_migracion(self):
        """
        Método principal que orquesta toda la migración de datos.
        Si existe mapeo_migracion.json, usa migración automática.
        Si no existe, usa migración manual tradicional.
        
        Returns:
            str: Mensaje de confirmación de migración exitosa
        """
        print("\n=== Iniciando Migración de Datos ===\n")
        
        # Verificar si usar migración automática o manual
        if MAPEO_MIGRACION:
            return self.ejecutar_migracion_automatica()
        else:
            return self.ejecutar_migracion_manual()
    
    def ejecutar_migracion_automatica(self):
        """
        Ejecuta migración usando configuración JSON para automatizar el proceso.
        Lee entidades y relaciones del archivo mapeo_migracion.json
        """
        print("🤖 Usando migración automática desde mapeo_migracion.json\n")
        
        opciones = MAPEO_MIGRACION.get('opciones', {})
        
        with self.driver_neo4j.session() as sesion:
            
            # Limpiar Neo4j si está configurado
            if opciones.get('limpiar_neo4j_antes', False):
                print("Limpiando Neo4j...")
                sesion.run("MATCH (n) DETACH DELETE n")
                print("✓ Neo4j limpiado\n")
            
            # =============================================
            # MIGRAR ENTIDADES
            # =============================================
            print("FASE 1: Migrando entidades...")
            
            for entidad in MAPEO_MIGRACION['entidades']:
                nombre = entidad['nombre']
                etiqueta = entidad['etiqueta_neo4j']
                
                print(f"\n  → Migrando {nombre} como :{etiqueta}")
                
                # Obtener datos de PostgreSQL
                datos = self.obtener_datos_postgresql(entidad['consulta_sql'])
                
                if not datos:
                    print(f"    ⚠️  No hay datos para {nombre}")
                    continue
                
                # Convertir datos usando mapeo de campos
                mapeo = entidad['mapeo_campos']
                campos_sql = list(mapeo.keys())
                
                datos_dict = []
                for fila in datos:
                    registro = {}
                    for i, campo_sql in enumerate(campos_sql):
                        campo_neo4j = mapeo[campo_sql]
                        registro[campo_neo4j] = fila[i]
                    datos_dict.append(registro)
                
                # Generar consulta Cypher dinámica CORREGIDA
                campos_neo4j = list(mapeo.values())
                id_campo = campos_neo4j[0]  # Primer campo como ID (debe ser único)
                
                # Separar el ID de los demás campos para SET
                campos_set = [f"n.{campo} = ${campo}" for campo in campos_neo4j]
                
                consulta = f"""
                    MERGE (n:{etiqueta} {{{id_campo}: ${id_campo}}})
                    SET {', '.join(campos_set)}
                """
                
                if opciones.get('modo_debug', False):
                    print(f"    Consulta Cypher: {consulta}")
                
                # Ejecutar creación de nodos
                sesion.execute_write(
                    self.crear_nodos_neo4j,
                    consulta,
                    datos_dict,
                    etiqueta
                )
            
            # =============================================
            # MIGRAR RELACIONES
            # =============================================
            print("\nFASE 2: Migrando relaciones...")
            
            for relacion in MAPEO_MIGRACION['relaciones']:
                nombre = relacion['nombre']
                tipo = relacion['tipo_relacion']
                
                print(f"\n  → Creando relaciones :{tipo}")
                
                # Obtener datos de relaciones
                datos = self.obtener_datos_postgresql(relacion['consulta_sql'])
                
                if not datos:
                    print(f"    ⚠️  No hay relaciones para {nombre}")
                    continue
                
                # Convertir a diccionarios
                datos_dict = [
                    {
                        'id_origen': fila[0],
                        'id_destino': fila[1]
                    }
                    for fila in datos
                ]
                
                # Generar consulta Cypher para relaciones
                # Obtener el campo ID de cada nodo
                nodo_origen_config = next(e for e in MAPEO_MIGRACION['entidades'] 
                                         if e['etiqueta_neo4j'] == relacion['nodo_origen'])
                nodo_destino_config = next(e for e in MAPEO_MIGRACION['entidades'] 
                                          if e['etiqueta_neo4j'] == relacion['nodo_destino'])
                
                campo_id_origen = list(nodo_origen_config['mapeo_campos'].values())[0]
                campo_id_destino = list(nodo_destino_config['mapeo_campos'].values())[0]
                
                consulta = f"""
                    MATCH (origen:{relacion['nodo_origen']} {{{campo_id_origen}: $id_origen}})
                    MATCH (destino:{relacion['nodo_destino']} {{{campo_id_destino}: $id_destino}})
                    MERGE (origen)-[:{tipo}]->(destino)
                """
                
                if opciones.get('modo_debug', False):
                    print(f"    Consulta Cypher: {consulta}")
                
                # Ejecutar creación de relaciones
                sesion.execute_write(
                    self.crear_relaciones_neo4j,
                    consulta,
                    datos_dict,
                    tipo
                )
            
            # Crear índices si está configurado
            if opciones.get('crear_indices', False):
                print("\nFASE 3: Creando índices...")
                for entidad in MAPEO_MIGRACION['entidades']:
                    etiqueta = entidad['etiqueta_neo4j']
                    id_campo = list(entidad['mapeo_campos'].values())[0]
                    
                    try:
                        consulta_indice = f"CREATE INDEX IF NOT EXISTS FOR (n:{etiqueta}) ON (n.{id_campo})"
                        sesion.run(consulta_indice)
                        print(f"  ✓ Índice creado para {etiqueta}.{id_campo}")
                    except Exception as e:
                        print(f"  ⚠️  Error al crear índice: {e}")
            
            # Mostrar estadísticas
            print("\nFASE 4: Estadísticas de migración...")
            for entidad in MAPEO_MIGRACION['entidades']:
                etiqueta = entidad['etiqueta_neo4j']
                resultado = sesion.run(f"MATCH (n:{etiqueta}) RETURN count(n) as total")
                total = resultado.single()['total']
                print(f"  ✓ Nodos :{etiqueta}: {total}")
            
            print()
            for relacion in MAPEO_MIGRACION['relaciones']:
                tipo = relacion['tipo_relacion']
                resultado = sesion.run(f"MATCH ()-[r:{tipo}]->() RETURN count(r) as total")
                total = resultado.single()['total']
                print(f"  ✓ Relaciones :{tipo}: {total}")
        
        print("\n=== ✓ Migración Automática Completada ===")
        return "Migración automática completada exitosamente"
    
    def ejecutar_migracion_manual(self):
        """
        Método manual tradicional de migración.
        Ejecuta el proceso en 4 fases predefinidas:
        1. Migrar usuarios como nodos :Persona
        2. Migrar publicaciones como nodos :Post
        3. Crear relaciones :AMIGO_DE entre usuarios
        4. Crear relaciones :PUBLICO entre usuarios y publicaciones
        
        Returns:
            str: Mensaje de confirmación de migración exitosa
        """
        print("📝 Usando migración manual (modo tradicional)\n")
        
        with self.driver_neo4j.session() as sesion:
            
            # =============================================
            # FASE 1: MIGRAR USUARIOS
            # =============================================
            print("FASE 1: Migrando usuarios...")
            
            # Obtener todos los usuarios de PostgreSQL
            usuarios = self.obtener_datos_postgresql(
                "SELECT id_usuario as id, nombre, email FROM usuarios"
            )
            
            # Convertir tuplas a diccionarios para Neo4j
            usuarios_dict = [
                {"id": usuario[0], "nombre": usuario[1], "email": usuario[2]} 
                for usuario in usuarios
            ]
            
            # Consulta Cypher: MERGE evita duplicados
            consulta_usuarios = """
                MERGE (persona:Persona {id_sql: $id}) 
                SET persona.nombre = $nombre, persona.email = $email
            """
            
            # Ejecutar creación de nodos en una transacción
            sesion.execute_write(
                self.crear_nodos_neo4j, 
                consulta_usuarios, 
                usuarios_dict, 
                "Persona"
            )

            # =============================================
            # FASE 2: MIGRAR PUBLICACIONES
            # =============================================
            print("\nFASE 2: Migrando publicaciones...")
            
            # Obtener todas las publicaciones de PostgreSQL
            publicaciones = self.obtener_datos_postgresql(
                "SELECT id_publicacion as id, texto_contenido as texto FROM publicaciones"
            )
            
            # Convertir a diccionarios
            publicaciones_dict = [
                {"id": post[0], "texto": post[1]} 
                for post in publicaciones
            ]
            
            # Consulta Cypher para crear nodos Post
            consulta_posts = """
                MERGE (post:Post {id_sql: $id}) 
                SET post.texto = $texto
            """
            
            sesion.execute_write(
                self.crear_nodos_neo4j, 
                consulta_posts, 
                publicaciones_dict, 
                "Post"
            )

            # =============================================
            # FASE 3: MIGRAR AMISTADES
            # =============================================
            print("\nFASE 3: Migrando amistades...")
            
            # Obtener solo amistades aceptadas
            amistades = self.obtener_datos_postgresql(
                """SELECT usuario_solicitante_id as id1, usuario_receptor_id as id2 
                   FROM amistades WHERE estado = 'ACEPTADA'"""
            )
            
            # Convertir a diccionarios
            amistades_dict = [
                {"id1": amistad[0], "id2": amistad[1]} 
                for amistad in amistades
            ]
            
            # Consulta Cypher para crear relaciones bidireccionales
            consulta_amistad = """
                MATCH (persona1:Persona {id_sql: $id1})
                MATCH (persona2:Persona {id_sql: $id2})
                MERGE (persona1)-[:AMIGO_DE]->(persona2)
            """
            
            sesion.execute_write(
                self.crear_relaciones_neo4j, 
                consulta_amistad, 
                amistades_dict, 
                "AMIGO_DE"
            )

            # =============================================
            # FASE 4: MIGRAR RELACIONES AUTOR-PUBLICACIÓN
            # =============================================
            print("\nFASE 4: Creando relaciones autor-publicación...")
            
            # Obtener relaciones entre autores y publicaciones
            publicaciones_autor = self.obtener_datos_postgresql(
                "SELECT autor_id as autor, id_publicacion as post FROM publicaciones"
            )
            
            # Convertir a diccionarios
            publicaciones_autor_dict = [
                {"autor": pub[0], "post": pub[1]} 
                for pub in publicaciones_autor
            ]
            
            # Consulta Cypher para crear relación PUBLICO
            consulta_publico = """
                MATCH (persona:Persona {id_sql: $autor})
                MATCH (post:Post {id_sql: $post})
                MERGE (persona)-[:PUBLICO]->(post)
            """
            
            sesion.execute_write(
                self.crear_relaciones_neo4j, 
                consulta_publico, 
                publicaciones_autor_dict, 
                "PUBLICO"
            )

        print("\n=== ✓ Migración Completada Exitosamente ===")
        return "Migración completada exitosamente"

    def cerrar_conexiones(self):
        """
        Cierra todas las conexiones abiertas a las bases de datos.
        Debe llamarse al finalizar para liberar recursos.
        """
        if self.conexion_postgres:
            self.conexion_postgres.close()
        if self.driver_neo4j:
            self.driver_neo4j.close()
        print("✓ Conexiones cerradas correctamente")


# =============================================
# INTERFAZ GRÁFICA (OPCIONAL - REQUIERE PyQt5)
# =============================================

if GUI_DISPONIBLE:
    class AplicacionGUI(QWidget):
        """
        Interfaz gráfica simple para ejecutar la migración con un botón.
        Solo disponible si PyQt5 está instalado.
        """
        
        def __init__(self):
            super().__init__()
            self.migrador = None
            self.inicializar_interfaz()

        def inicializar_interfaz(self):
            """Configura los elementos de la interfaz gráfica."""
            self.setWindowTitle('Migración Políglota PostgreSQL → Neo4j')
            
            # Layout vertical
            layout = QVBoxLayout()
            
            # Etiqueta informativa
            etiqueta = QLabel('Presiona el botón para migrar datos de PostgreSQL a Neo4j')
            layout.addWidget(etiqueta)
            
            # Botón de migración
            boton_migrar = QPushButton('🚀 Iniciar Migración')
            boton_migrar.clicked.connect(self.ejecutar_migracion)
            layout.addWidget(boton_migrar)
            
            self.setLayout(layout)

        def ejecutar_migracion(self):
            """Maneja el evento de clic del botón de migración."""
            try:
                # Crear instancia del migrador
                self.migrador = MigradorPoliglota()
                
                # Ejecutar migración
                resultado = self.migrador.ejecutar_migracion()
                
                # Cerrar conexiones
                self.migrador.cerrar_conexiones()
                
                # Mostrar mensaje de éxito
                QMessageBox.information(self, 'Éxito', resultado)
                
            except Exception as error:
                # Mostrar mensaje de error
                QMessageBox.critical(self, 'Error', str(error))
                
            finally:
                # Asegurar cierre de conexiones
                if self.migrador:
                    self.migrador.cerrar_conexiones()


# =============================================
# PUNTO DE ENTRADA DEL PROGRAMA
# =============================================

if __name__ == "__main__":
    # Si PyQt5 está disponible, usar interfaz gráfica
    if GUI_DISPONIBLE:
        aplicacion = QApplication(sys.argv)
        ventana = AplicacionGUI()
        ventana.show()
        sys.exit(aplicacion.exec_())
    
    # Si no hay GUI, ejecutar en modo consola
    else:
        migrador = None
        try:
            # Crear migrador y ejecutar
            migrador = MigradorPoliglota()
            resultado = migrador.ejecutar_migracion()
            print(f"\n{resultado}")
            
        except Exception as error:
            print(f"Error durante la migración: {error}")
            
        finally:
            # Cerrar conexiones siempre
            if migrador:
                migrador.cerrar_conexiones()
