# 📌 Evaluador Automatizado de Empresas Según Requerimientos (E3)

## 🌐 Accede a la Aplicación Web
🔗 [Haz clic aquí para probar la app en Streamlit](https://iapromptv-a-2eqe8j67tnkvat972ihnmy.streamlit.app/)

---

## 📝 Descripción
**Evaluador Automatizado de Empresas Según Requerimientos (E3)** es una aplicación diseñada para ayudar a equipos de adquisiciones a investigar empresas potenciales de manera eficiente. 

🔍 **¿Cómo funciona?**
1. El usuario ingresa hasta **cinco URLs** de sitios web de empresas.
2. La app extrae información clave de los sitios web y LinkedIn (si está disponible).
3. Se procesan los datos con **GPT-4** para generar un resumen estructurado.
4. La información se muestra en una tabla y se puede descargar en formato **CSV**.

---

## 🚀 Introducción
### 📌 Nombre del Proyecto
**Evaluador Automatizado de Empresas Según Requerimientos (E3)**

### 🏆 Problema a Abordar
Los equipos de adquisiciones invierten mucho tiempo en investigar empresas potenciales según criterios como **headcount**, **servicios ofrecidos**, **revenue**, **país del headquarter** y **sustentabilidad**. Este proceso manual puede ser ineficiente, propenso a errores y con información desactualizada. 

### 💡 Propuesta de Solución
E3 utiliza técnicas de **web scraping** y **procesamiento con GPT-4** para **automatizar la investigación** de empresas. A través de **prompts predefinidos**, extrae y resume la información relevante de sitios web y perfiles de LinkedIn.

---

## 🎯 Objetivos
✅ Extraer información estructurada de sitios web y LinkedIn.
✅ Generar reportes con los datos obtenidos.
✅ Reducir el tiempo de investigación manual.
✅ Proveer una interfaz amigable para el usuario.

---

## 🔧 Metodología
### 📌 Procedimientos Implementados
1. **Scraping de contenido** de sitios web y LinkedIn.
2. **Procesamiento con GPT-4** para estructurar y resumir la información.
3. **Visualización de los datos** en Streamlit.
4. **Generación de archivos CSV** descargables.

### 📌 Justificación de la Viabilidad
El proyecto es viable ya que:
- Utiliza tecnologías de acceso libre y bajo costo.
- Está desarrollado en **Python**, con librerías eficientes para scraping y procesamiento de datos.
- Aprovecha la **API de OpenAI** para obtener información estructurada.

---

## 🛠️ Herramientas y Tecnologías
- **Streamlit** → Para la interfaz interactiva.
- **BeautifulSoup** → Para el scraping de datos.
- **OpenAI API** → Para el análisis de contenido con GPT-4.
- **Pandas** → Para estructurar y exportar los datos.
- **Python-dotenv** → Para la gestión segura de credenciales.

---

## 📌 Arquitectura de la Aplicación
```
📂 E3-Project
│── .env  # Variables de entorno (API Key)
│── .gitignore  # Archivos a excluir en Git
│── app.py  # Código principal de la aplicación
│── companies_info.csv  # Datos exportados en CSV
│── README.md  # Documentación del proyecto
│── requeriments.txt  # Dependencias necesarias
│── .devcontainer/  # Configuración para entornos de desarrollo
```

---

## ⚡ Instalación y Configuración
### 🔧 Instalación
1. **Clona el repositorio**:
   ```bash
   git clone https://github.com/tuusuario/E3-Project.git
   cd E3-Project
   ```
2. **Crea un entorno virtual**:
   ```bash
   python -m venv env
   source env/bin/activate  # Mac/Linux
   env\Scripts\activate  # Windows
   ```
3. **Instala dependencias**:
   ```bash
   pip install -r requeriments.txt
   ```
4. **Configura tu API Key de OpenAI**:
   - Crea un archivo `.env` en la raíz del proyecto.
   - Agrega la línea:
     ```
     OPENAI_API_KEY=tu_clave_aqui
     ```

### 🚀 Ejecución de la Aplicación
Para iniciar la aplicación, ejecuta:
```bash
streamlit run app.py
```

---

## 📌 Próximos Pasos
✅ Optimización de scraping para obtener más información.
✅ Implementación de análisis adicionales con IA.
✅ Integración con bases de datos para almacenamiento de información.

---

## 📞 Contáctame
Si tienes dudas o sugerencias, ¡hablemos! 

📧 Email: [arandigacatriel@gmail.com](mailto:arandigacatriel@gmail.com)  
🔗 LinkedIn: [Catriel Nicolás Arándiga](https://www.linkedin.com/in/catriel-nicolas-arandiga)

🚀 ¡Gracias por leer!

