"""
Sistema de Gestión de Red Social - Interfaz Moderna con CustomTkinter
=====================================================================
Autor: Andrés
Descripción: Aplicación con interfaz gráfica moderna usando CustomTkinter
            para administrar una red social con persistencia políglota.

Tecnologías:
- CustomTkinter: UI moderna con tema dark/light
- PostgreSQL: Base de datos relacional
- Neo4j: Base de datos de grafos

Características UI:
- Tema dark mode por defecto
- Diseño moderno y limpio
- Animaciones suaves
- Colores personalizados
"""

import sys
import os
import psycopg2
from neo4j import GraphDatabase
import json
import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import networkx as nx
import tkinter as tk

# Configuración de CustomTkinter
ctk.set_appearance_mode("dark")  # Modos: "dark", "light", "system"
ctk.set_default_color_theme("blue")  # Temas: "blue", "green", "dark-blue"


class AplicacionRedSocialModerna:
    """
    Aplicación principal con interfaz moderna usando CustomTkinter.
    """
    
    def __init__(self, ventana_raiz):
        self.ventana = ventana_raiz
        self.ventana.title("Red Social AmigosDB - Panel de Administración")
        self.ventana.geometry("1200x800")
        
        # Variables para almacenar referencias
        self.dict_usuarios = {}
        
        # Inicializar
        self.cargar_configuracion()
        self.conectar_bases_datos()
        self.crear_interfaz_moderna()
        self.actualizar_todos_datos()

    def cargar_configuracion(self):
        """Carga la configuración desde el archivo JSON."""
        directorio = os.path.dirname(os.path.abspath(__file__))
        ruta_config = os.path.join(directorio, 'configuracion.json')
        
        with open(ruta_config, 'r') as archivo:
            config = json.load(archivo)
        
        self.config_postgres = config['postgresql']
        self.config_neo4j = config['neo4j']

    def conectar_bases_datos(self):
        """Establece conexiones con PostgreSQL y Neo4j."""
        try:
            self.conexion_pg = psycopg2.connect(**self.config_postgres)
            self.driver_neo = GraphDatabase.driver(
                self.config_neo4j['direccion_uri'], 
                auth=(self.config_neo4j['usuario'], self.config_neo4j['clave'])
            )
        except Exception as error:
            messagebox.showerror(
                'Error de Conexión', 
                f'No se pudo conectar a las bases de datos:\n{error}'
            )
            sys.exit(1)

    def crear_interfaz_moderna(self):
        """Crea la interfaz moderna con CustomTkinter."""
        
        # Frame principal con padding
        self.frame_principal = ctk.CTkFrame(self.ventana)
        self.frame_principal.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        self.crear_header()
        
        # Tabview (pestañas modernas)
        self.tabview = ctk.CTkTabview(self.frame_principal)
        self.tabview.pack(fill="both", expand=True, pady=(20, 0))
        
        # Crear pestañas
        self.tab_usuarios = self.tabview.add("👤 Usuarios")
        self.tab_publicaciones = self.tabview.add("📝 Publicaciones")
        self.tab_solicitudes = self.tabview.add("📨 Solicitudes")
        self.tab_amistades = self.tabview.add("👥 Amistades")
        self.tab_grafos = self.tabview.add("🕸️ Grafos Neo4j")
        self.tab_migracion = self.tabview.add("🔄 Migración")
        
        # Construir contenido
        self.construir_tab_usuarios()
        self.construir_tab_grafos()
        self.construir_tab_publicaciones()
        self.construir_tab_solicitudes()
        self.construir_tab_amistades()
        self.construir_tab_migracion()

    def crear_header(self):
        """Crea el header de la aplicación."""
        frame_header = ctk.CTkFrame(self.frame_principal, fg_color="transparent")
        frame_header.pack(fill="x", pady=(0, 10))
        
        # Título
        titulo = ctk.CTkLabel(
            frame_header,
            text="🌐 Red Social AmigosDB",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        titulo.pack(side="left")
        
        # Botón de tema
        self.btn_tema = ctk.CTkButton(
            frame_header,
            text="🌙 Tema",
            width=100,
            command=self.cambiar_tema
        )
        self.btn_tema.pack(side="right", padx=5)

    def cambiar_tema(self):
        """Alterna entre tema oscuro y claro."""
        modo_actual = ctk.get_appearance_mode()
        nuevo_modo = "light" if modo_actual == "Dark" else "dark"
        ctk.set_appearance_mode(nuevo_modo)
        
        # Actualizar icono del botón
        icono = "☀️" if nuevo_modo == "light" else "🌙"
        self.btn_tema.configure(text=f"{icono} Tema")

    # ==========================================
    # TAB USUARIOS
    # ==========================================
    
    def construir_tab_usuarios(self):
        """Construye la pestaña de usuarios con diseño moderno."""
        
        # Frame para formulario
        frame_form = ctk.CTkFrame(self.tab_usuarios)
        frame_form.pack(fill="x", padx=20, pady=20)
        
        # Título del formulario
        ctk.CTkLabel(
            frame_form,
            text="Registrar Nuevo Usuario",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=(10, 20))
        
        # Grid para campos
        frame_campos = ctk.CTkFrame(frame_form, fg_color="transparent")
        frame_campos.pack(padx=20, pady=(0, 20))
        
        # Campo Nombre
        ctk.CTkLabel(frame_campos, text="Nombre:", font=ctk.CTkFont(size=14)).grid(
            row=0, column=0, sticky="w", padx=10, pady=10
        )
        self.entrada_nombre = ctk.CTkEntry(
            frame_campos, 
            width=350,
            placeholder_text="Ingresa el nombre completo"
        )
        self.entrada_nombre.grid(row=0, column=1, padx=10, pady=10)
        
        # Campo Email
        ctk.CTkLabel(frame_campos, text="Email:", font=ctk.CTkFont(size=14)).grid(
            row=1, column=0, sticky="w", padx=10, pady=10
        )
        self.entrada_email = ctk.CTkEntry(
            frame_campos,
            width=350,
            placeholder_text="ejemplo@mail.com"
        )
        self.entrada_email.grid(row=1, column=1, padx=10, pady=10)
        
        # Campo País
        ctk.CTkLabel(frame_campos, text="País:", font=ctk.CTkFont(size=14)).grid(
            row=2, column=0, sticky="w", padx=10, pady=10
        )
        self.entrada_pais = ctk.CTkEntry(
            frame_campos,
            width=350,
            placeholder_text="País (opcional)"
        )
        self.entrada_pais.grid(row=2, column=1, padx=10, pady=10)
        
        # Botón de crear
        self.btn_crear_usuario = ctk.CTkButton(
            frame_form,
            text="➕ Crear Usuario",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40,
            command=self.registrar_usuario
        )
        self.btn_crear_usuario.pack(pady=(0, 20))
        
        # Frame para tabla
        frame_tabla = ctk.CTkFrame(self.tab_usuarios)
        frame_tabla.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Título de tabla
        header_tabla = ctk.CTkFrame(frame_tabla)
        header_tabla.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            header_tabla,
            text="Usuarios Registrados",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(side="left")
        
        ctk.CTkButton(
            header_tabla,
            text="🔄 Actualizar",
            width=120,
            command=self.cargar_usuarios
        ).pack(side="right")
        
        # Scrollable frame para usuarios
        self.frame_scroll_usuarios = ctk.CTkScrollableFrame(
            frame_tabla,
            label_text=""
        )
        self.frame_scroll_usuarios.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    # ==========================================
    # TAB PUBLICACIONES
    # ==========================================
    
    def construir_tab_publicaciones(self):
        """Construye la pestaña de publicaciones."""
        
        # Frame formulario
        frame_form = ctk.CTkFrame(self.tab_publicaciones)
        frame_form.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(
            frame_form,
            text="Crear Nueva Publicación",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=(10, 20))
        
        # Usuario
        frame_usuario = ctk.CTkFrame(frame_form, fg_color="transparent")
        frame_usuario.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            frame_usuario, 
            text="Usuario:", 
            font=ctk.CTkFont(size=14)
        ).pack(side="left", padx=(0, 10))
        
        self.combo_autor = ctk.CTkComboBox(
            frame_usuario,
            width=400,
            state="readonly"
        )
        self.combo_autor.pack(side="left")
        
        # Contenido
        frame_contenido = ctk.CTkFrame(frame_form, fg_color="transparent")
        frame_contenido.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            frame_contenido,
            text="Contenido:",
            font=ctk.CTkFont(size=14)
        ).pack(anchor="w")
        
        self.texto_contenido = ctk.CTkTextbox(
            frame_contenido,
            height=100,
            width=500
        )
        self.texto_contenido.pack(fill="x", pady=(5, 0))
        
        # Botón publicar
        ctk.CTkButton(
            frame_form,
            text="📝 Publicar",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40,
            command=self.crear_publicacion
        ).pack(pady=20)
        
        # Frame tabla
        frame_tabla = ctk.CTkFrame(self.tab_publicaciones)
        frame_tabla.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        header_tabla = ctk.CTkFrame(frame_tabla)
        header_tabla.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            header_tabla,
            text="Publicaciones Recientes",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(side="left")
        
        ctk.CTkButton(
            header_tabla,
            text="🔄 Actualizar",
            width=120,
            command=self.cargar_publicaciones
        ).pack(side="right")
        
        self.frame_scroll_publicaciones = ctk.CTkScrollableFrame(frame_tabla)
        self.frame_scroll_publicaciones.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    # ==========================================
    # TAB SOLICITUDES
    # ==========================================
    
    def construir_tab_solicitudes(self):
        """Construye la pestaña de solicitudes."""
        
        # Frame formulario
        frame_form = ctk.CTkFrame(self.tab_solicitudes)
        frame_form.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(
            frame_form,
            text="Enviar Solicitud de Amistad",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=(10, 20))
        
        frame_campos = ctk.CTkFrame(frame_form, fg_color="transparent")
        frame_campos.pack(padx=20, pady=(0, 20))
        
        # De
        ctk.CTkLabel(frame_campos, text="De:", font=ctk.CTkFont(size=14)).grid(
            row=0, column=0, sticky="w", padx=10, pady=10
        )
        self.combo_solicitante = ctk.CTkComboBox(
            frame_campos,
            width=350,
            state="readonly"
        )
        self.combo_solicitante.grid(row=0, column=1, padx=10, pady=10)
        
        # Para
        ctk.CTkLabel(frame_campos, text="Para:", font=ctk.CTkFont(size=14)).grid(
            row=1, column=0, sticky="w", padx=10, pady=10
        )
        self.combo_receptor = ctk.CTkComboBox(
            frame_campos,
            width=350,
            state="readonly"
        )
        self.combo_receptor.grid(row=1, column=1, padx=10, pady=10)
        
        # Botón enviar
        ctk.CTkButton(
            frame_form,
            text="📤 Enviar Solicitud",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40,
            command=self.enviar_solicitud
        ).pack(pady=(0, 20))
        
        # Frame tabla
        frame_tabla = ctk.CTkFrame(self.tab_solicitudes)
        frame_tabla.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        header_tabla = ctk.CTkFrame(frame_tabla)
        header_tabla.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            header_tabla,
            text="Solicitudes Pendientes",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(side="left")
        
        # Botones de acción
        frame_acciones = ctk.CTkFrame(header_tabla, fg_color="transparent")
        frame_acciones.pack(side="right")
        
        ctk.CTkButton(
            frame_acciones,
            text="🔄",
            width=40,
            command=self.cargar_solicitudes
        ).pack(side="right", padx=2)
        
        self.frame_scroll_solicitudes = ctk.CTkScrollableFrame(frame_tabla)
        self.frame_scroll_solicitudes.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    # ==========================================
    # TAB AMISTADES
    # ==========================================
    
    def construir_tab_amistades(self):
        """Construye la pestaña de amistades."""
        
        frame_tabla = ctk.CTkFrame(self.tab_amistades)
        frame_tabla.pack(fill="both", expand=True, padx=20, pady=20)
        
        header_tabla = ctk.CTkFrame(frame_tabla)
        header_tabla.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            header_tabla,
            text="Amistades Aceptadas",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(side="left")
        
        ctk.CTkButton(
            header_tabla,
            text="🔄 Actualizar",
            width=120,
            command=self.cargar_amistades
        ).pack(side="right")
        
        self.frame_scroll_amistades = ctk.CTkScrollableFrame(frame_tabla)
        self.frame_scroll_amistades.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    # ==========================================
    # TAB MIGRACIÓN
    # ==========================================
    
    def construir_tab_migracion(self):
        """Construye la pestaña de migración."""
        
        frame_principal = ctk.CTkFrame(self.tab_migracion)
        frame_principal.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Título
        ctk.CTkLabel(
            frame_principal,
            text="Migración a Neo4j",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=(10, 20))
        
        # Botones
        frame_botones = ctk.CTkFrame(frame_principal, fg_color="transparent")
        frame_botones.pack(pady=10)
        
        ctk.CTkButton(
            frame_botones,
            text="🚀 Migrar a Neo4j",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40,
            width=200,
            command=self.migrar_a_neo4j
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            frame_botones,
            text="🗑️ Limpiar Neo4j",
            font=ctk.CTkFont(size=14),
            height=40,
            width=180,
            fg_color="red",
            hover_color="darkred",
            command=self.limpiar_neo4j
        ).pack(side="left", padx=10)
        
        # Log
        ctk.CTkLabel(
            frame_principal,
            text="Log de Migración:",
            font=ctk.CTkFont(size=14)
        ).pack(anchor="w", padx=10, pady=(20, 5))
        
        self.area_log = ctk.CTkTextbox(
            frame_principal,
            height=500
        )
        self.area_log.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def construir_tab_grafos(self):
        """Construye la pestaña de visualización de grafos Neo4j."""
        
        frame_principal = ctk.CTkFrame(self.tab_grafos)
        frame_principal.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Título
        ctk.CTkLabel(
            frame_principal,
            text="🕸️ Visualización de Grafos de Relaciones",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=(10, 20))
        
        # Controles superiores
        frame_controles = ctk.CTkFrame(frame_principal, fg_color="transparent")
        frame_controles.pack(fill="x", pady=(0, 15))
        
        # Botones de acción
        ctk.CTkButton(
            frame_controles,
            text="🔄 Actualizar Grafo",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40,
            width=180,
            command=self.actualizar_grafo_neo4j
        ).pack(side="left", padx=10)
        
        # Selector de tipo de visualización
        ctk.CTkLabel(
            frame_controles,
            text="Tipo de visualización:",
            font=ctk.CTkFont(size=12)
        ).pack(side="left", padx=(20, 5))
        
        self.tipo_layout = ctk.CTkComboBox(
            frame_controles,
            values=["Spring (Fuerza)", "Circular", "Radial", "Kamada-Kawai"],
            width=180,
            command=self.actualizar_grafo_neo4j
        )
        self.tipo_layout.pack(side="left", padx=5)
        self.tipo_layout.set("Spring (Fuerza)")
        
        # Switch para mostrar etiquetas
        self.mostrar_etiquetas = ctk.CTkSwitch(
            frame_controles,
            text="Mostrar nombres",
            font=ctk.CTkFont(size=12)
        )
        self.mostrar_etiquetas.pack(side="left", padx=20)
        self.mostrar_etiquetas.select()
        
        # Frame para estadísticas
        frame_stats = ctk.CTkFrame(frame_principal)
        frame_stats.pack(fill="x", pady=(0, 15))
        
        self.label_stats = ctk.CTkLabel(
            frame_stats,
            text="📊 Estadísticas: Nodos: 0 | Relaciones: 0",
            font=ctk.CTkFont(size=13)
        )
        self.label_stats.pack(pady=10)
        
        # Frame para el canvas del grafo
        self.frame_canvas = ctk.CTkFrame(frame_principal)
        self.frame_canvas.pack(fill="both", expand=True)
        
        # Inicializar el grafo
        self.actualizar_grafo_neo4j()

    # ==========================================
    # MÉTODOS DE CARGA DE DATOS
    # ==========================================
    
    def actualizar_todos_datos(self):
        """Carga todos los datos iniciales."""
        self.cargar_usuarios()
        self.cargar_publicaciones()
        self.cargar_solicitudes()
        self.cargar_amistades()
        self.cargar_combos_usuarios()

    def cargar_usuarios(self):
        """Carga usuarios en tarjetas modernas."""
        # Limpiar frame
        for widget in self.frame_scroll_usuarios.winfo_children():
            widget.destroy()
        
        cursor = self.conexion_pg.cursor()
        cursor.execute(
            "SELECT id_usuario, nombre, email, pais FROM usuarios ORDER BY id_usuario"
        )
        usuarios = cursor.fetchall()
        
        for id_u, nombre, email, pais in usuarios:
            card = ctk.CTkFrame(self.frame_scroll_usuarios)
            card.pack(fill="x", pady=5, padx=5)
            
            # Info
            frame_info = ctk.CTkFrame(card, fg_color="transparent")
            frame_info.pack(fill="x", padx=15, pady=10)
            
            ctk.CTkLabel(
                frame_info,
                text=f"#{id_u}",
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="gray"
            ).pack(side="left", padx=(0, 10))
            
            ctk.CTkLabel(
                frame_info,
                text=nombre,
                font=ctk.CTkFont(size=14, weight="bold")
            ).pack(side="left")
            
            ctk.CTkLabel(
                frame_info,
                text=f"📧 {email}",
                font=ctk.CTkFont(size=12),
                text_color="gray"
            ).pack(side="left", padx=(20, 0))
            
            if pais:
                ctk.CTkLabel(
                    frame_info,
                    text=f"🌍 {pais}",
                    font=ctk.CTkFont(size=12),
                    text_color="gray"
                ).pack(side="right")
        
        cursor.close()

    def cargar_publicaciones(self):
        """Carga publicaciones en tarjetas."""
        for widget in self.frame_scroll_publicaciones.winfo_children():
            widget.destroy()
        
        cursor = self.conexion_pg.cursor()
        cursor.execute("""
            SELECT p.id_publicacion, u.nombre, p.texto_contenido, 
                   p.fecha_publicacion, p.likes_contador
            FROM publicaciones p
            JOIN usuarios u ON p.autor_id = u.id_usuario
            ORDER BY p.fecha_publicacion DESC
        """)
        publicaciones = cursor.fetchall()
        
        for id_pub, autor, contenido, fecha, likes in publicaciones:
            card = ctk.CTkFrame(self.frame_scroll_publicaciones)
            card.pack(fill="x", pady=8, padx=5)
            
            # Header
            header = ctk.CTkFrame(card, fg_color="transparent")
            header.pack(fill="x", padx=15, pady=(10, 5))
            
            ctk.CTkLabel(
                header,
                text=autor,
                font=ctk.CTkFont(size=14, weight="bold")
            ).pack(side="left")
            
            fecha_str = fecha.strftime('%d/%m/%Y %H:%M') if fecha else ''
            ctk.CTkLabel(
                header,
                text=fecha_str,
                font=ctk.CTkFont(size=11),
                text_color="gray"
            ).pack(side="right")
            
            # Contenido
            ctk.CTkLabel(
                card,
                text=contenido,
                font=ctk.CTkFont(size=13),
                wraplength=700,
                justify="left"
            ).pack(anchor="w", padx=15, pady=(0, 5))
            
            # Footer
            footer = ctk.CTkFrame(card, fg_color="transparent")
            footer.pack(fill="x", padx=15, pady=(0, 10))
            
            ctk.CTkLabel(
                footer,
                text=f"❤️ {likes} likes",
                font=ctk.CTkFont(size=11),
                text_color="gray"
            ).pack(side="left")
        
        cursor.close()

    def cargar_solicitudes(self):
        """Carga solicitudes pendientes."""
        for widget in self.frame_scroll_solicitudes.winfo_children():
            widget.destroy()
        
        cursor = self.conexion_pg.cursor()
        cursor.execute("""
            SELECT a.id_amistad, u1.nombre, u2.nombre, a.fecha_amistad
            FROM amistades a
            JOIN usuarios u1 ON a.usuario_solicitante_id = u1.id_usuario
            JOIN usuarios u2 ON a.usuario_receptor_id = u2.id_usuario
            WHERE a.estado = 'PENDIENTE'
            ORDER BY a.fecha_amistad DESC
        """)
        solicitudes = cursor.fetchall()
        
        if not solicitudes:
            ctk.CTkLabel(
                self.frame_scroll_solicitudes,
                text="No hay solicitudes pendientes",
                font=ctk.CTkFont(size=14),
                text_color="gray"
            ).pack(pady=20)
        
        for id_amistad, de, para, fecha in solicitudes:
            card = ctk.CTkFrame(self.frame_scroll_solicitudes)
            card.pack(fill="x", pady=5, padx=5)
            
            frame_info = ctk.CTkFrame(card, fg_color="transparent")
            frame_info.pack(fill="x", padx=15, pady=10)
            
            ctk.CTkLabel(
                frame_info,
                text=f"{de}  →  {para}",
                font=ctk.CTkFont(size=13)
            ).pack(side="left")
            
            # Botones
            frame_btns = ctk.CTkFrame(frame_info, fg_color="transparent")
            frame_btns.pack(side="right")
            
            ctk.CTkButton(
                frame_btns,
                text="✓",
                width=40,
                fg_color="green",
                hover_color="darkgreen",
                command=lambda id_a=id_amistad: self.aceptar_solicitud(id_a)
            ).pack(side="left", padx=2)
            
            ctk.CTkButton(
                frame_btns,
                text="✗",
                width=40,
                fg_color="red",
                hover_color="darkred",
                command=lambda id_a=id_amistad: self.rechazar_solicitud(id_a)
            ).pack(side="left", padx=2)
        
        cursor.close()

    def cargar_amistades(self):
        """Carga amistades aceptadas."""
        for widget in self.frame_scroll_amistades.winfo_children():
            widget.destroy()
        
        cursor = self.conexion_pg.cursor()
        cursor.execute("""
            SELECT u1.nombre, u2.nombre, a.fecha_amistad
            FROM amistades a
            JOIN usuarios u1 ON a.usuario_solicitante_id = u1.id_usuario
            JOIN usuarios u2 ON a.usuario_receptor_id = u2.id_usuario
            WHERE a.estado = 'ACEPTADA'
            ORDER BY a.fecha_amistad DESC
        """)
        amistades = cursor.fetchall()
        
        for u1, u2, fecha in amistades:
            card = ctk.CTkFrame(self.frame_scroll_amistades)
            card.pack(fill="x", pady=5, padx=5)
            
            frame_info = ctk.CTkFrame(card, fg_color="transparent")
            frame_info.pack(fill="x", padx=15, pady=10)
            
            ctk.CTkLabel(
                frame_info,
                text=f"👥 {u1}  ↔  {u2}",
                font=ctk.CTkFont(size=13)
            ).pack(side="left")
            
            fecha_str = fecha.strftime('%d/%m/%Y') if fecha else ''
            ctk.CTkLabel(
                frame_info,
                text=fecha_str,
                font=ctk.CTkFont(size=11),
                text_color="gray"
            ).pack(side="right")
        
        cursor.close()

    def cargar_combos_usuarios(self):
        """Carga usuarios en los comboboxes."""
        cursor = self.conexion_pg.cursor()
        cursor.execute("SELECT id_usuario, nombre FROM usuarios ORDER BY nombre")
        usuarios = cursor.fetchall()
        
        self.dict_usuarios = {
            f"{nombre} (ID: {id_u})": id_u 
            for id_u, nombre in usuarios
        }
        nombres = list(self.dict_usuarios.keys())
        
        if nombres:
            self.combo_solicitante.configure(values=nombres)
            self.combo_receptor.configure(values=nombres)
            self.combo_autor.configure(values=nombres)
            
            self.combo_solicitante.set(nombres[0])
            self.combo_receptor.set(nombres[0])
            self.combo_autor.set(nombres[0])
        
        cursor.close()

    # ==========================================
    # MÉTODOS DE ACCIÓN
    # ==========================================
    
    def registrar_usuario(self):
        """Crea un nuevo usuario."""
        nombre = self.entrada_nombre.get().strip()
        email = self.entrada_email.get().strip()
        pais = self.entrada_pais.get().strip()
        
        if not nombre or not email:
            messagebox.showwarning('Error', 'Nombre y email son obligatorios')
            return
        
        try:
            cursor = self.conexion_pg.cursor()
            cursor.execute(
                "INSERT INTO usuarios (nombre, email, pais) VALUES (%s, %s, %s)",
                (nombre, email, pais if pais else None)
            )
            self.conexion_pg.commit()
            cursor.close()
            
            messagebox.showinfo('Éxito', f'Usuario "{nombre}" creado correctamente')
            
            self.entrada_nombre.delete(0, "end")
            self.entrada_email.delete(0, "end")
            self.entrada_pais.delete(0, "end")
            
            self.cargar_usuarios()
            self.cargar_combos_usuarios()
            
        except psycopg2.IntegrityError:
            self.conexion_pg.rollback()
            messagebox.showwarning('Error', 'El email ya está registrado')
        except Exception as error:
            self.conexion_pg.rollback()
            messagebox.showerror('Error', f'Error al crear usuario:\n{error}')

    def crear_publicacion(self):
        """Crea una nueva publicación."""
        autor_key = self.combo_autor.get()
        contenido = self.texto_contenido.get("1.0", "end").strip()

        if not autor_key:
            messagebox.showwarning('Error', 'Selecciona un usuario')
            return

        if not contenido:
            messagebox.showwarning('Error', 'El contenido no puede estar vacío')
            return

        id_autor = self.dict_usuarios[autor_key]

        try:
            cursor = self.conexion_pg.cursor()
            cursor.execute(
                "INSERT INTO publicaciones (texto_contenido, autor_id) VALUES (%s, %s)",
                (contenido, id_autor)
            )
            self.conexion_pg.commit()
            cursor.close()

            messagebox.showinfo('Éxito', 'Publicación creada correctamente')
            self.texto_contenido.delete("1.0", "end")
            self.cargar_publicaciones()

        except Exception as error:
            self.conexion_pg.rollback()
            messagebox.showerror('Error', f'Error al crear publicación:\n{error}')

    def enviar_solicitud(self):
        """Envía una solicitud de amistad."""
        solicitante_key = self.combo_solicitante.get()
        receptor_key = self.combo_receptor.get()
        
        if not solicitante_key or not receptor_key:
            messagebox.showwarning('Error', 'Selecciona ambos usuarios')
            return
        
        id_solicitante = self.dict_usuarios[solicitante_key]
        id_receptor = self.dict_usuarios[receptor_key]
        
        if id_solicitante == id_receptor:
            messagebox.showwarning('Error', 'No puedes enviarte una solicitud a ti mismo')
            return
        
        try:
            cursor = self.conexion_pg.cursor()
            cursor.execute("CALL crear_amistad(%s, %s)", (id_solicitante, id_receptor))
            self.conexion_pg.commit()
            cursor.close()
            
            messagebox.showinfo('Éxito', 'Solicitud de amistad enviada')
            self.cargar_solicitudes()
            
        except Exception as error:
            self.conexion_pg.rollback()
            if 'ya existe' in str(error).lower():
                messagebox.showwarning('Aviso', 'Ya existe una solicitud entre estos usuarios')
            else:
                messagebox.showerror('Error', f'Error al enviar solicitud:\n{error}')

    def aceptar_solicitud(self, id_amistad):
        """Acepta una solicitud de amistad."""
        try:
            cursor = self.conexion_pg.cursor()
            cursor.execute(
                "UPDATE amistades SET estado = 'ACEPTADA' WHERE id_amistad = %s",
                (id_amistad,)
            )
            self.conexion_pg.commit()
            cursor.close()
            
            messagebox.showinfo('Éxito', 'Solicitud aceptada')
            self.cargar_solicitudes()
            self.cargar_amistades()
            
        except Exception as error:
            self.conexion_pg.rollback()
            messagebox.showerror('Error', f'Error al aceptar solicitud:\n{error}')

    def rechazar_solicitud(self, id_amistad):
        """Rechaza una solicitud de amistad."""
        if messagebox.askyesno('Confirmar', '¿Estás seguro de rechazar esta solicitud?'):
            try:
                cursor = self.conexion_pg.cursor()
                cursor.execute("DELETE FROM amistades WHERE id_amistad = %s", (id_amistad,))
                self.conexion_pg.commit()
                cursor.close()
                
                messagebox.showinfo('Éxito', 'Solicitud rechazada')
                self.cargar_solicitudes()
                
            except Exception as error:
                self.conexion_pg.rollback()
                messagebox.showerror('Error', f'Error al rechazar solicitud:\n{error}')

    def migrar_a_neo4j(self):
        """Migra datos a Neo4j."""
        self.area_log.delete("1.0", "end")
        self.escribir_log("=== Iniciando Migración a Neo4j ===\n")
        
        try:
            with self.driver_neo.session() as sesion:
                cursor = self.conexion_pg.cursor()
                
                # Usuarios
                self.escribir_log("FASE 1: Migrando usuarios...")
                cursor.execute("SELECT id_usuario, nombre, email FROM usuarios")
                usuarios = cursor.fetchall()
                self.escribir_log(f"  → {len(usuarios)} usuarios encontrados")
                
                for id_u, nombre, email in usuarios:
                    sesion.run(
                        "MERGE (p:Persona {id_sql: $id}) SET p.nombre = $nombre, p.email = $email",
                        id=id_u, nombre=nombre, email=email
                    )
                self.escribir_log("  ✓ Usuarios migrados\n")
                
                # Publicaciones
                self.escribir_log("FASE 2: Migrando publicaciones...")
                cursor.execute("SELECT id_publicacion, texto_contenido FROM publicaciones")
                posts = cursor.fetchall()
                self.escribir_log(f"  → {len(posts)} publicaciones encontradas")
                
                for id_p, texto in posts:
                    sesion.run(
                        "MERGE (p:Post {id_sql: $id}) SET p.texto = $texto",
                        id=id_p, texto=texto
                    )
                self.escribir_log("  ✓ Publicaciones migradas\n")
                
                # Amistades
                self.escribir_log("FASE 3: Migrando amistades...")
                cursor.execute("""
                    SELECT usuario_solicitante_id, usuario_receptor_id 
                    FROM amistades WHERE estado = 'ACEPTADA'
                """)
                amistades = cursor.fetchall()
                self.escribir_log(f"  → {len(amistades)} amistades encontradas")
                
                for id1, id2 in amistades:
                    sesion.run("""
                        MATCH (p1:Persona {id_sql: $id1})
                        MATCH (p2:Persona {id_sql: $id2})
                        MERGE (p1)-[:AMIGO_DE]->(p2)
                    """, id1=id1, id2=id2)
                self.escribir_log("  ✓ Amistades migradas\n")
                
                # Publicaciones
                self.escribir_log("FASE 4: Creando relaciones autor-publicación...")
                cursor.execute("SELECT autor_id, id_publicacion FROM publicaciones")
                publico = cursor.fetchall()
                
                for autor, post in publico:
                    sesion.run("""
                        MATCH (p:Persona {id_sql: $autor})
                        MATCH (post:Post {id_sql: $post})
                        MERGE (p)-[:PUBLICO]->(post)
                    """, autor=autor, post=post)
                self.escribir_log("  ✓ Relaciones creadas\n")
                
                cursor.close()
            
            self.escribir_log("\n✅ Migración completada exitosamente")
            messagebox.showinfo('Éxito', 'Migración a Neo4j completada')
            
        except Exception as error:
            self.escribir_log(f"\n❌ Error: {error}")
            messagebox.showerror('Error', f'Error en la migración:\n{error}')

    def limpiar_neo4j(self):
        """Limpia Neo4j."""
        if messagebox.askyesno('Confirmar', '¿Estás seguro de eliminar TODOS los datos de Neo4j?'):
            try:
                with self.driver_neo.session() as sesion:
                    sesion.run("MATCH (n) DETACH DELETE n")
                
                self.area_log.delete("1.0", "end")
                self.escribir_log("✓ Neo4j limpiado correctamente")
                messagebox.showinfo('Éxito', 'Neo4j limpiado')
                
            except Exception as error:
                messagebox.showerror('Error', f'Error al limpiar Neo4j:\n{error}')

    def actualizar_grafo_neo4j(self, *args):
        """Actualiza y visualiza el grafo de Neo4j."""
        try:
            # Limpiar canvas anterior
            for widget in self.frame_canvas.winfo_children():
                widget.destroy()
            
            # Obtener datos de Neo4j
            with self.driver_neo.session() as sesion:
                # Obtener nodos
                resultado_nodos = sesion.run("""
                    MATCH (p:Persona)
                    RETURN p.id_sql as id, p.nombre as nombre
                """)
                nodos = list(resultado_nodos)
                
                # Obtener relaciones
                resultado_relaciones = sesion.run("""
                    MATCH (p1:Persona)-[:AMIGO_DE]->(p2:Persona)
                    RETURN p1.id_sql as origen, p2.id_sql as destino
                """)
                relaciones = list(resultado_relaciones)
            
            # Si no hay datos
            if len(nodos) == 0:
                ctk.CTkLabel(
                    self.frame_canvas,
                    text="⚠️ No hay datos en Neo4j\n\nPrimero ejecuta la migración en la pestaña 'Migración'",
                    font=ctk.CTkFont(size=16),
                    text_color="gray"
                ).pack(expand=True)
                self.label_stats.configure(text="📊 Estadísticas: Nodos: 0 | Relaciones: 0")
                return
            
            # Crear grafo con NetworkX
            G = nx.Graph()
            
            # Agregar nodos con nombres
            nodos_dict = {}
            for nodo in nodos:
                id_nodo = nodo['id']
                nombre = nodo['nombre']
                G.add_node(id_nodo, nombre=nombre)
                nodos_dict[id_nodo] = nombre
            
            # Agregar aristas (relaciones)
            for rel in relaciones:
                G.add_edge(rel['origen'], rel['destino'])
            
            # Actualizar estadísticas
            num_nodos = G.number_of_nodes()
            num_relaciones = G.number_of_edges()
            self.label_stats.configure(
                text=f"📊 Estadísticas: Nodos: {num_nodos} | Relaciones: {num_relaciones}"
            )
            
            # Crear figura de matplotlib
            fig, ax = plt.subplots(figsize=(10, 8))
            fig.patch.set_facecolor('#2b2b2b')  # Fondo oscuro
            ax.set_facecolor('#2b2b2b')
            
            # Seleccionar layout según tipo
            tipo = self.tipo_layout.get()
            if tipo == "Spring (Fuerza)":
                pos = nx.spring_layout(G, k=0.5, iterations=50)
            elif tipo == "Circular":
                pos = nx.circular_layout(G)
            elif tipo == "Radial":
                pos = nx.shell_layout(G)
            else:  # Kamada-Kawai
                pos = nx.kamada_kawai_layout(G)
            
            # Dibujar el grafo
            # Nodos
            nx.draw_networkx_nodes(
                G, pos, 
                node_color='#1f6aa5',
                node_size=800,
                alpha=0.9,
                ax=ax
            )
            
            # Aristas
            nx.draw_networkx_edges(
                G, pos,
                edge_color='#666666',
                width=2,
                alpha=0.6,
                ax=ax
            )
            
            # Etiquetas (nombres)
            if self.mostrar_etiquetas.get():
                labels = {nodo: data['nombre'] for nodo, data in G.nodes(data=True)}
                nx.draw_networkx_labels(
                    G, pos,
                    labels,
                    font_size=9,
                    font_color='white',
                    font_weight='bold',
                    ax=ax
                )
            
            # Quitar ejes
            ax.axis('off')
            plt.tight_layout()
            
            # Integrar matplotlib en tkinter
            canvas = FigureCanvasTkAgg(fig, master=self.frame_canvas)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
            
        except Exception as error:
            ctk.CTkLabel(
                self.frame_canvas,
                text=f"❌ Error al cargar grafo:\n{error}",
                font=ctk.CTkFont(size=14),
                text_color="red"
            ).pack(expand=True)
            print(f"Error en visualización: {error}")

    def escribir_log(self, mensaje):
        """Escribe en el log."""
        self.area_log.insert("end", f"{mensaje}\n")
        self.area_log.see("end")

    def al_cerrar(self):
        """Cierra conexiones."""
        if self.conexion_pg:
            self.conexion_pg.close()
        if self.driver_neo:
            self.driver_neo.close()
        self.ventana.destroy()


if __name__ == '__main__':
    ventana = ctk.CTk()
    app = AplicacionRedSocialModerna(ventana)
    ventana.protocol("WM_DELETE_WINDOW", app.al_cerrar)
    ventana.mainloop()
