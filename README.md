# Media Tracker

**Media Tracker** is a FastAPI-based module for keeping track of movies, TV shows and YouTube videos/channels/playlists. It provides a RESTful API to create, read, update, and delete media entries, along with translations, visualizations, and TV show episodes.  
It is designed to be installed to [Personal Suite](https://github.com/jruizg22/personalsuite-backend-core)

<details>
<summary>🇪🇸 Español</summary>

**Media Tracker** es un módulo basado en FastAPI para gestionar películas, series de televisión y vídeos/canales/listas de reproducción de YouTube. Proporciona una API RESTful para crear, leer, actualizar y eliminar entradas de medios, junto con traducciones, visualizaciones y episodios de series de televisión.  
Está diseñado para instalarse en [Personal Suite](https://github.com/jruizg22/personalsuite-backend-core).

</details>

---

## Features / Características

- Keep track **Movies**, **TV Shows**, and **YouTube videos** in a single unified module.
- API endpoints for **CRUD operations** on media, translations, and visualizations.
- Flexible views to retrieve media with varying levels of detail.
- Endpoints get the API Key protection from the core.
- PostgreSQL backend with SQLModel / SQLAlchemy ORM.
- Automatic documentation with Swagger UI and ReDoc.

<details>
<summary>🇪🇸 Español</summary>

- Gestiona **películas**, **series de televisión** y **vídeos de YouTube** en un único módulo unificado.
- Endpoints de la API para **operaciones CRUD** sobre medios, traducciones y visualizaciones.
- Vistas flexibles para recuperar medios con distintos niveles de detalle.
- Los endpoints están protegidos mediante la clave API proporcionada por el core.
- Base de datos PostgreSQL utilizando SQLModel / SQLAlchemy ORM.
- Documentación automática con Swagger UI y ReDoc.

</details>

---

## Installation / Instalación

```bash
# Clone the repository / Clonar repositorio
git clone https://github.com/jruizg22/personalsuite-backend-mediatracker.git
cd personalsuite-backend-mediatracker

# Create a virtual environment / Crear el entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Install dependencies / Instalar dependencias
pip install .
```