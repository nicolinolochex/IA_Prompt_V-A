# 📌 Evaluador Automatizado de Empresas (E3)

## 🚀 Accede a la Aplicación Web

🔗 **[Evaluador de Empresas - E3](https://iapromptv-a-2eqe8j67tnkvat972ihnmy.streamlit.app/)**

---

## 📖 Introducción

### 📌 Nombre del Proyecto
**Evaluador Automatizado de Empresas Según Requerimientos (E3)**

### 🔍 Presentación del Problema
En el sector de **Adquisiciones**, el proceso de evaluación de empresas es manual y consume mucho tiempo. Se requiere una herramienta que automatice la recopilación de información clave, como el **headcount**, los **servicios ofrecidos**, el **revenue** y el **país de origen**, facilitando la toma de decisiones.

### 🤖 Desarrollo de la Propuesta
La solución utiliza **IA y Web Scraping** para extraer información relevante de sitios web y perfiles de LinkedIn. Mediante **GPT-4**, se procesan los datos y se presentan de forma estructurada.

### ✅ Justificación de la Viabilidad
- **Recursos disponibles:** Se cuenta con herramientas como **Streamlit, Python, BeautifulSoup y OpenAI API**.
- **Tiempo estimado:** Proyecto ya implementado y funcional.
- **Impacto:** Reducción del tiempo de evaluación y mayor precisión en la información obtenida.

---

## 🎯 Objetivos

- Automatizar la recopilación de datos de empresas.
- Presentar la información de manera estructurada.
- Facilitar la toma de decisiones en el equipo de adquisiciones.

---

## 🛠️ Metodología

1. **Definir los criterios de evaluación** (headcount, servicios, revenue, etc.).
2. **Extraer información** mediante scraping de sitios web y LinkedIn.
3. **Procesar y estructurar la información** con GPT-4.
4. **Mostrar resultados** en una interfaz interactiva con Streamlit.

---

## 🔧 Herramientas y Tecnologías

- **Python**: Desarrollo del backend.
- **Streamlit**: Interfaz web.
- **BeautifulSoup**: Web Scraping.
- **OpenAI GPT-4**: Procesamiento de datos.
- **Pandas**: Manejo de datos estructurados.

---

## 🏗️ Arquitectura de la Aplicación

1. **Entrada**: URLs de empresas.
2. **Extracción de datos**: Scraping con BeautifulSoup.
3. **Procesamiento**: GPT-4 analiza los datos y los presenta en JSON.
4. **Visualización**: Streamlit muestra la información en una tabla interactiva.
5. **Exportación**: Generación de archivos CSV descargables.

---

## 📌 Instalación y Configuración

1. **Clona el repositorio**:
   ```bash
   git clone https://github.com/nicolinolochex/IA_Prompt_V-A.git
   ```
2. **Accede al directorio del proyecto**:
   ```bash
   cd IA_Prompt_V-A
   ```
3. **Instala las dependencias**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Configura la API Key de OpenAI**:
   - Crea un archivo `.env` y agrega tu clave:
     ```env
     OPENAI_API_KEY=tu_api_key_aqui
     ```
5. **Ejecuta la aplicación**:
   ```bash
   streamlit run app.py
   ```

---

## 🚀 Próximos Pasos

- Integrar más fuentes de datos.
- Optimizar el scraping y mejorar la precisión de la IA.
- Agregar métricas y visualizaciones avanzadas.

---

## 📩 Contáctame

📧 **Correo:** arandigacatriel@gmail.com
🔗 **LinkedIn:** [Catriel Nicolás Arandiga](https://www.linkedin.com/in/catriel-nicolas-arandiga)

