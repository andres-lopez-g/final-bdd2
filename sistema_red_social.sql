-- =============================================
-- SCRIPT DE CREACIÓN: SISTEMA DE RED SOCIAL
-- Descripción: Script SQL para crear la estructura de base de datos
-- de un sistema de red social con usuarios, publicaciones y amistades
-- =============================================

-- Eliminar la base de datos si existe y crear una nueva
DROP DATABASE IF EXISTS red_social_db;
CREATE DATABASE red_social_db;
\c red_social_db;

-- =============================================
-- SECCIÓN 1: CREACIÓN DE TABLAS
-- =============================================

-- Tabla principal de usuarios del sistema
-- Almacena la información básica de cada usuario registrado
CREATE TABLE usuarios (
    id_usuario SERIAL PRIMARY KEY,              -- Identificador único autoincrementable
    nombre VARCHAR(100) NOT NULL,               -- Nombre completo del usuario
    email VARCHAR(100) UNIQUE NOT NULL,         -- Correo electrónico único para cada usuario
    fecha_registro DATE DEFAULT CURRENT_DATE,   -- Fecha de registro automática
    pais VARCHAR(50)                            -- País de origen del usuario (opcional)
);

-- Tabla de publicaciones (posts) creados por los usuarios
-- Contiene el contenido que los usuarios comparten en la red
CREATE TABLE publicaciones (
    id_publicacion SERIAL PRIMARY KEY,                  -- Identificador único de la publicación
    texto_contenido TEXT,                               -- Contenido de la publicación
    fecha_publicacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Fecha y hora de publicación automática
    likes_contador INT DEFAULT 0,                       -- Contador de "me gusta" inicializado en 0
    -- Clave foránea pendiente de relacionar (se agrega en la siguiente fase)
    autor_id INT NOT NULL                               -- Referencia al usuario que creó la publicación
);

-- Tabla de comentarios en las publicaciones
-- Permite a los usuarios comentar en las publicaciones de otros
CREATE TABLE comentarios (
    id_comentario SERIAL PRIMARY KEY,                   -- Identificador único del comentario
    contenido VARCHAR(255),                             -- Texto del comentario (máximo 255 caracteres)
    fecha_comentario TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Fecha y hora del comentario
    -- Claves foráneas pendientes de relacionar
    usuario_id INT NOT NULL,                            -- Usuario que hizo el comentario
    publicacion_id INT NOT NULL                         -- Publicación que fue comentada
);

-- Tabla de amistades (relación muchos a muchos entre usuarios)
-- Gestiona las conexiones entre usuarios del sistema
CREATE TABLE amistades (
    id_amistad SERIAL PRIMARY KEY,                      -- Identificador único de la amistad
    fecha_amistad DATE DEFAULT CURRENT_DATE,            -- Fecha en que se creó la solicitud
    estado VARCHAR(20),                                 -- Estado: 'ACEPTADA', 'PENDIENTE', etc.
    -- Claves foráneas pendientes de relacionar
    usuario_solicitante_id INT NOT NULL,                -- Usuario que envía la solicitud
    usuario_receptor_id INT NOT NULL                    -- Usuario que recibe la solicitud
);

-- =============================================
-- SECCIÓN 2: INGENIERÍA Y NORMALIZACIÓN DE DATOS
-- Agregando restricciones de integridad referencial
-- =============================================

-- Agregar llave foránea en publicaciones para relacionar con usuarios
ALTER TABLE publicaciones
ADD CONSTRAINT fk_autor
FOREIGN KEY (autor_id) REFERENCES usuarios(id_usuario);

-- Agregar llaves foráneas en comentarios para relacionar con usuarios y publicaciones
ALTER TABLE comentarios
ADD CONSTRAINT fk_usuario
FOREIGN KEY (usuario_id) REFERENCES usuarios(id_usuario),
ADD CONSTRAINT fk_publicacion
FOREIGN KEY (publicacion_id) REFERENCES publicaciones(id_publicacion);

-- Agregar llaves foráneas en amistades para relacionar usuarios
ALTER TABLE amistades
ADD CONSTRAINT fk_usuario_solicitante
FOREIGN KEY (usuario_solicitante_id) REFERENCES usuarios(id_usuario),
ADD CONSTRAINT fk_usuario_receptor
FOREIGN KEY (usuario_receptor_id) REFERENCES usuarios(id_usuario);

-- Restricción de validación: evitar que un usuario se agregue a sí mismo como amigo
ALTER TABLE amistades
ADD CONSTRAINT chk_no_auto_amistad
CHECK (usuario_solicitante_id <> usuario_receptor_id);

-- =============================================
-- SECCIÓN 3: DATOS DE PRUEBA (SEED DATA)
-- Datos iniciales para probar el sistema
-- =============================================

-- Insertar usuarios de prueba de diferentes países
INSERT INTO usuarios (nombre, email, pais) VALUES
('Ana Garcia', 'ana@mail.com', 'Colombia'),
('Carlos Perez', 'carlos@mail.com', 'Mexico'),
('Beatriz Lopez', 'bea@mail.com', 'Argentina'),
('David Ruiz', 'david@mail.com', 'Colombia'),
('Elena Rodriguez', 'elena@mail.com', 'España'),
('Francisco Gomez', 'francisco@mail.com', 'Chile'),
('Gabriela Hernandez', 'gabriela@mail.com', 'Peru'),
('Hector Jimenez', 'hector@mail.com', 'Ecuador'),
('Irene Morales', 'irene@mail.com', 'Bolivia'),
('Javier Castillo', 'javier@mail.com', 'Uruguay'),
('Karla Ortiz', 'karla@mail.com', 'Paraguay'),
('Luis Mendoza', 'luis@mail.com', 'Venezuela'),
('Maria Flores', 'maria@mail.com', 'Colombia'),
('Nestor Vargas', 'nestor@mail.com', 'Mexico'),
('Olivia Paredes', 'olivia@mail.com', 'Argentina'),
('Pedro Guzman', 'pedro@mail.com', 'Colombia'),
('Quintina Soto', 'quintina@mail.com', 'Chile'),
('Roberto Acuña', 'roberto@mail.com', 'Peru'),
('Sofia Navarro', 'sofia@mail.com', 'Ecuador'),
('Tomas Vidal', 'tomas@mail.com', 'Bolivia'),
('Ursula Ponce', 'ursula@mail.com', 'Uruguay'),
('Victor Rivas', 'victor@mail.com', 'Paraguay'),
('Wendy Salazar', 'wendy@mail.com', 'Venezuela'),
('Ximena Correa', 'ximena@mail.com', 'Colombia');

-- Insertar publicaciones de ejemplo creadas por diferentes usuarios
INSERT INTO publicaciones (texto_contenido, autor_id) VALUES
('Hola mundo, este es mi primer post', 1),
('Me encanta el café de Colombia', 2),
('Buscando recomendaciones de libros', 3),
('El fútbol argentino es el mejor del mundo', 3),
('Alguien sabe dónde comprar empanadas en Madrid?', 5),
('Acabo de terminar de leer Cien Años de Soledad, increíble!', 4),
('Recomendaciones de restaurantes en Santiago?', 6),
('Mi primer día en la universidad, nervioso pero emocionado', 7),
('El ceviche peruano es patrimonio de la humanidad', 7),
('Buscando compañeros para jugar al fútbol los domingos', 10),
('Las montañas de Bolivia son espectaculares', 9),
('Consejos para aprender a programar desde cero?', 12),
('Hoy probé arepas por primera vez, deliciosas!', 13),
('Alguien más viendo la serie nueva de Netflix?', 14),
('El tango es música del alma', 15),
('Fotos del atardecer en Cartagena, hermoso!', 16),
('Recién llegué a Perú, todo es increíble aquí', 18),
('Buscando grupo de estudio para matemáticas', 19),
('El mate es la mejor bebida del mundo', 20),
('Consejos para viajar con poco presupuesto?', 22);

-- Insertar relaciones de amistad entre usuarios
-- Algunas están aceptadas y otras pendientes de aprobación
INSERT INTO amistades (usuario_solicitante_id, usuario_receptor_id, estado) VALUES
(1, 2, 'ACEPTADA'),
(2, 3, 'ACEPTADA'),
(3, 4, 'ACEPTADA'),
(1, 3, 'ACEPTADA'),
(1, 4, 'ACEPTADA'),
(2, 4, 'ACEPTADA'),
(5, 6, 'ACEPTADA'),
(5, 7, 'PENDIENTE'),
(6, 8, 'ACEPTADA'),
(7, 9, 'ACEPTADA'),
(8, 10, 'ACEPTADA'),
(9, 11, 'ACEPTADA'),
(10, 12, 'PENDIENTE'),
(11, 13, 'ACEPTADA'),
(12, 14, 'ACEPTADA'),
(13, 15, 'ACEPTADA'),
(14, 16, 'ACEPTADA'),
(15, 17, 'PENDIENTE'),
(16, 18, 'ACEPTADA'),
(17, 19, 'ACEPTADA'),
(18, 20, 'ACEPTADA'),
(19, 21, 'ACEPTADA'),
(20, 22, 'PENDIENTE'),
(21, 23, 'ACEPTADA'),
(22, 24, 'ACEPTADA');

-- =============================================
-- SECCIÓN 4: LÓGICA DE NEGOCIO
-- Procedimientos almacenados y vistas para funcionalidad avanzada
-- =============================================

-- Procedimiento almacenado: Crear solicitud de amistad
-- Valida que no exista amistad duplicada y que no sea auto-amistad
CREATE OR REPLACE PROCEDURE crear_amistad(id1 INT, id2 INT)
LANGUAGE plpgsql
AS $$
BEGIN
    -- Validación 1: Verificar que no sean el mismo usuario
    IF id1 = id2 THEN
        RAISE EXCEPTION 'Un usuario no puede ser amigo de sí mismo.';
    END IF;

    -- Validación 2: Verificar si ya existe una amistad (en cualquier dirección)
    IF EXISTS (
        SELECT 1 FROM amistades
        WHERE (usuario_solicitante_id = id1 AND usuario_receptor_id = id2)
           OR (usuario_solicitante_id = id2 AND usuario_receptor_id = id1)
    ) THEN
        RAISE NOTICE 'La amistad entre el usuario % y % ya existe.', id1, id2;
    ELSE
        -- Insertar la nueva solicitud de amistad con estado PENDIENTE
        INSERT INTO amistades (usuario_solicitante_id, usuario_receptor_id, estado)
        VALUES (id1, id2, 'PENDIENTE');
        RAISE NOTICE 'Solicitud de amistad enviada del usuario % al usuario %.', id1, id2;
    END IF;
END;
$$;

-- Vista: Feed de noticias
-- Muestra todas las publicaciones con información del autor y cantidad de comentarios
CREATE OR REPLACE VIEW feed_noticias AS
SELECT
    u.nombre AS nombre_usuario,                 -- Nombre del usuario que publicó
    p.texto_contenido AS contenido_post,        -- Contenido de la publicación
    p.fecha_publicacion,                        -- Fecha y hora de publicación
    (SELECT COUNT(*) FROM comentarios c 
     WHERE c.publicacion_id = p.id_publicacion) AS cantidad_comentarios  -- Total de comentarios
FROM
    publicaciones p
JOIN
    usuarios u ON p.autor_id = u.id_usuario
ORDER BY
    p.fecha_publicacion DESC;                   -- Ordenar de más reciente a más antigua
