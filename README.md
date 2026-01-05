# YouTube Channel Scraper & Visualizations

Scraper incremental para canales de YouTube con análisis NLP y visualizaciones interactivas.

## 🎯 Objetivo

Scrapear el canal de **Historias Innecesarias** para:
1. Extraer metadata de videos (fecha, duración, views, likes)
2. Obtener transcripciones completas
3. Procesar con NLP (NER para eventos, lugares, personas)
4. Crear visualizaciones interactivas:
   - Línea de tiempo de eventos históricos
   - Mapa geográfico de historias
   - Grafo de temas y personas relacionadas

## 🚀 Instalación

### 1. Clonar el repositorio

```bash
git clone <repo-url>
cd scrapping-youtube
```

### 2. Crear entorno virtual

```bash
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

```bash
cp .env.example .env
```

Editar `.env` con tus valores:
```bash
CHANNEL_URL=https://www.youtube.com/@Historias.Innecesarias
DATABASE_PATH=data/youtube_data.db
LOG_LEVEL=INFO
```

## 📊 Uso

### Scraper Incremental

El scraper solo procesa videos nuevos (no re-procesa videos ya descargados):

```bash
# Usar configuración de .env
python scrape.py

# O especificar canal manualmente
python scrape.py --channel-url "https://www.youtube.com/@Historias.Innecesarias"

# Con logging a archivo
python scrape.py --log-file logs/scraper.log --log-level DEBUG
```

### Características del Scraper

✅ **Incremental**: Solo procesa videos nuevos
✅ **Robusto**: Si un video falla, continúa con los demás
✅ **Resumible**: Si se interrumpe (Ctrl+C), el progreso se guarda
✅ **Sin API Key**: Usa yt-dlp + youtube-transcript-api (sin límites)

### Estructura de la Base de Datos

La base de datos SQLite almacena:
- `video_id`: ID único del video
- `title`, `description`: Información básica
- `upload_date`, `duration_seconds`: Metadata temporal
- `view_count`, `like_count`, `comment_count`: Métricas de engagement
- `transcript`: Transcripción completa del video
- `transcript_language`: Idioma de la transcripción
- `processing_status`: Estado del procesamiento (completed/failed/pending)

## 📁 Estructura del Proyecto

```
scrapping-youtube/
├── src/
│   ├── scraper/          # YouTube scraping
│   │   └── youtube_scraper.py
│   ├── nlp/              # Procesamiento NLP (próximamente)
│   ├── visualizations/   # Visualizaciones (próximamente)
│   ├── database/         # Modelos SQLAlchemy
│   │   └── models.py
│   └── utils/            # Utilidades (logger, etc)
│       └── logger.py
├── data/                 # Datos (ignorado en git)
│   └── youtube_data.db   # Base de datos SQLite
├── notebooks/            # Jupyter notebooks para análisis
├── scrape.py             # Script principal
├── requirements.txt      # Dependencias
├── .env.example          # Plantilla de configuración
└── README.md
```

## 🔄 Workflow

### Fase 1: Scraping ✅ (COMPLETADO)
- [x] Scraper incremental con yt-dlp
- [x] Descarga de transcripciones
- [x] Base de datos SQLite
- [x] Manejo de errores y logging

### Fase 2: NLP (Próximamente)
- [ ] NER con spaCy (español)
- [ ] Extracción de fechas/eventos históricos
- [ ] Extracción de lugares geográficos
- [ ] Extracción de personas/organizaciones
- [ ] Geocoding de lugares

### Fase 3: Visualizaciones (Próximamente)
- [ ] Timeline interactiva (Plotly/D3.js)
- [ ] Mapa geográfico (Folium/Leaflet)
- [ ] Grafo de relaciones (NetworkX + Pyvis)
- [ ] Dashboard web (Streamlit/Dash)

## 🛠️ Tecnologías

- **Scraping**: yt-dlp, youtube-transcript-api
- **Database**: SQLAlchemy + SQLite
- **NLP**: spaCy (español)
- **Visualizaciones**: Plotly, Folium, NetworkX
- **Dashboard**: Streamlit/Dash

## 📝 Notas

- El scraper NO requiere API key de YouTube
- Las transcripciones se obtienen en español (con fallback a inglés)
- La base de datos crece incrementalmente - no se sobre-escribe
- Los videos que fallan quedan marcados con `processing_status='failed'`

## 🤝 Contribuir

Este es un proyecto personal de análisis de datos. Sugerencias bienvenidas!

## 📄 Licencia

MIT
