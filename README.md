# Evaluador Automatizado de Empresas Según Requerimientos (E3)

## 🌍 Accede a la Aplicación Web 📌

La aplicación ya está desplegada y lista para su uso en:

🔗 **[Company Research Tool](https://iapromptv-a-2eqe8j67tnkvat972ihnmy.streamlit.app/)**

---

## 📌 Resumen del Proyecto

Este sistema automatiza la investigación de empresas a partir de información disponible en la web, con el objetivo de facilitar el trabajo del equipo de **Adquisiciones**. Basado en parámetros definidos como:

- **Headcount** (Número de empleados)
- **Servicios ofrecidos**
- **Revenue** (Ingresos anuales)
- **Ubicación del Headquarter**
- **Sostenibilidad**

La aplicación permite extraer información relevante, generar un resumen evaluativo y asignar un puntaje para determinar qué empresas cumplen mejor con los requisitos del equipo.

---

## 🚀 Funcionalidades Clave

### ✅ 1. Extracción de Información desde Sitios Web y Perfiles de LinkedIn

- **Objetivo:** Recopilar y procesar información clave de empresas desde sus sitios web y/o perfiles de LinkedIn.
- **Implementación:**
  - Uso de **web scraping** con `BeautifulSoup` para obtener contenido relevante.
  - Procesamiento con **GPT-4** para extraer y estructurar la información.
  - Generación de un resumen claro y conciso con datos clave.

🔹 **Ejemplo de Prompt:**

> "Dado el contenido web extraído, genera un JSON con los siguientes datos: nombre, website, tipo de empresa (pública, privada, adquirida, etc.), país, breve descripción, servicios, headcount y revenue."

### ✅ 2. Evaluación y Asignación de Puntaje

- **Objetivo:** Clasificar a las empresas según qué tan bien cumplen los criterios de adquisición.
- **Implementación:**
  - Uso de una fórmula de **scoring** basada en los parámetros ingresados.
  - Generación de un ranking automático de las empresas más adecuadas.

🔹 **Ejemplo de Prompt:**

> "Dada la siguiente información sobre la empresa y los criterios de evaluación, asigna un puntaje del 1 al 10 y justifica la puntuación."

### ✅ 3. Generación de Reportes y Exportación de Datos

- **Objetivo:** Facilitar la visualización y descarga de la información extraída.
- **Implementación:**
  - Presentación en formato de tabla dentro de la app.
  - **Exportación a CSV** para análisis externo.
  - **Botón de descarga** para obtener los datos estructurados.

🔹 **Ejemplo:**

> Generación de un archivo `companies_info.csv` con la información procesada.

---

## 🏗️ Arquitectura de la Aplicación

La aplicación está desarrollada utilizando:

- **Streamlit**: Para la interfaz web.
- **Python**: Para la lógica del backend.
- **BeautifulSoup**: Para el scraping de datos.
- **OpenAI API (GPT-4)**: Para la extracción y análisis de datos.
- **Pandas**: Para estructurar los datos y generar reportes en CSV.
- **Dotenv**: Para la gestión segura de la API Key de OpenAI.

### 📂 Estructura del Proyecto

```
📂 Proyecto E3
│── .env              # Archivo con API Key (no se sube al repo)
│── .gitignore        # Ignora archivos sensibles
│── app.py            # Código principal de la app
│── companies_info.csv # Archivo de salida con los datos procesados
│── README.md         # Documentación del proyecto
│── requeriments.txt  # Dependencias del proyecto
└─── .devcontainer    # Configuración para entornos de desarrollo
```

---

## 🛠️ Instalación y Configuración

Para ejecutar el proyecto en local:

1. **Clonar el repositorio:**

   ```bash
   git clone https://github.com/tu-repositorio/aqui.git
   cd proyecto-e3
   ```

2. **Instalar dependencias:**

   ```bash
   pip install -r requeriments.txt
   ```

3. **Configurar la API Key de OpenAI:**

   - Crear un archivo `.env` con el siguiente contenido:
     ```plaintext
     OPENAI_API_KEY=tu_api_key_aqui
     ```

4. **Ejecutar la aplicación:**

   ```bash
   streamlit run app.py
   ```

---

## 🌟 Próximos Pasos

✔️ **Mejorar la extracción de datos** para reducir errores en LinkedIn.
✔️ **Optimizar el proceso de scoring** para ajustar mejor las evaluaciones.
✔️ **Agregar más criterios de selección** según necesidades del equipo.
✔️ **Implementar una base de datos** para almacenar búsquedas pasadas.

---

## 📩 Contacto

Si tienes preguntas o sugerencias, ¡contáctame! 🚀

✅ 2. Evaluación y Asignación de Puntaje sacame esto

