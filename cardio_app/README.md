# Gestión de Consultas de Cardiología

Aplicación de escritorio para la gestión de consultas de un cuadro médico de
cardiólogos. Desarrollada en Python con Tkinter y PyMongo.

## Requisitos

- Python 3.10+
- MongoDB 6.x corriendo en `localhost:27017`

## Instalación

```bash
pip install -r requirements.txt
```

## Inicializar la base de datos

Ejecutar **una sola vez** para cargar los datos de prueba:

```bash
python init_db.py
```

## Arrancar la aplicación

```bash
python main.py
```

## Credenciales de prueba

| Rol           | DNI        | Contraseña   |
|---------------|------------|--------------|
| Administrador | 12345678A  | Admin12ab    |
| Auxiliar      | 23456789B  | Aux11iliar   |
| Médico 1      | 34567890C  | Doctor12x    |
| Médico 2      | 45678901D  | Medic12ab    |

## Estructura del proyecto

```
cardio_app/
├── main.py                          # Punto de entrada (agnóstico a tecnologías)
├── init_db.py                       # Script de carga de datos iniciales
├── requirements.txt
├── data/                            # Ficheros JSON para poblar la BD
│   ├── profesionales.json
│   ├── franjas.json
│   ├── pacientes.json
│   ├── consultas.json
│   └── tensiones.json
└── src/
    ├── datos/                       # Capa de Datos
    │   ├── config_db.py
    │   ├── modelos/
    │   │   └── entidades.py         # Modelos de dominio (dataclasses)
    │   └── repositorios/
    │       ├── interfaces.py        # Contratos abstractos (ABC)
    │       ├── base_mongo.py
    │       ├── repositorio_profesionales.py
    │       ├── repositorio_franjas.py
    │       ├── repositorio_pacientes.py
    │       ├── repositorio_consultas.py
    │       └── repositorio_tensiones.py
    ├── negocio/                     # Capa de Negocio
    │   ├── servicios/
    │   │   ├── servicio_autenticacion.py
    │   │   ├── servicio_profesionales.py
    │   │   ├── servicio_franjas.py
    │   │   ├── servicio_pacientes.py
    │   │   ├── servicio_consultas.py
    │   │   └── servicio_tensiones.py
    │   └── validadores/
    │       └── validadores.py       # Todas las reglas de validación centralizadas
    └── presentacion/                # Capa de Presentación (MVC)
        ├── controladores/
        │   └── controlador_app.py   # Controller central de sesión y navegación
        └── vistas/
            ├── componentes.py       # Widgets reutilizables y estilos
            ├── vista_principal.py   # Ventana raíz con menú lateral
            ├── vista_login.py
            ├── vista_inicio.py
            ├── vista_profesionales.py
            ├── vista_franjas.py
            ├── vista_pacientes.py
            ├── vista_agenda.py
            ├── vista_consultas_auxiliar.py
            ├── vista_consultas_medico.py
            ├── vista_tensiones.py
            └── vista_perfil.py
```

## Arquitectura

El proyecto sigue una **arquitectura de 3 capas**:

- **Datos**: Repositorios con interfaces abstractas (ABC). Las implementaciones
  concretas usan PyMongo. Cambiar la base de datos no afecta a capas superiores.
- **Negocio**: Servicios que contienen toda la lógica y reglas de negocio.
  Validadores centralizados en su propio módulo.
- **Presentación**: Arquitectura **MVC**. El controlador gestiona la sesión y
  la navegación. Las vistas solo presentan datos y capturan entrada del usuario.

La **inyección de dependencias** se realiza en `main.py`, que actúa como
contenedor de dependencias sin conocer los detalles de implementación.
