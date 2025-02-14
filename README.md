# 📌 Evaluador Automatizado de Empresas (E3)

![Streamlit](https://img.shields.io/badge/Streamlit-App-red?style=flat&logo=streamlit)
![Python](https://img.shields.io/badge/Python-3.9-blue?style=flat&logo=python)

## 🚀 Accede a la Aplicación Web

🔗 [E3 - Evaluador Automatizado de Empresas](https://iapromptv-a-2eqe8j67tnkvat972ihnmy.streamlit.app/)

---

## 📖 Introducción

### 🎯 Nombre del Proyecto
**Evaluador Automatizado de Empresas (E3)**

### 🧐 Problema a Abordar
El equipo de adquisiciones necesita investigar empresas potenciales para evaluar oportunidades de compra basadas en criterios como *headcount*, *revenue*, *país*, *servicios ofrecidos* y *sostenibilidad*. 

Actualmente, este proceso es manual y consume mucho tiempo, además de que la información puede ser inconsistente o difícil de comparar. La falta de una herramienta automatizada para extraer y estandarizar estos datos genera ineficiencias en la toma de decisiones.

### 💡 Desarrollo de la Propuesta de Solución
La solución planteada consiste en una aplicación basada en **IA generativa** y **web scraping** que extrae, organiza y presenta la información clave de las empresas desde sus sitios web y perfiles de LinkedIn.

A través de **prompts optimizados en GPT-4**, la aplicación transforma el contenido extraído en información estructurada y relevante para el equipo de adquisiciones, reduciendo el tiempo de búsqueda y mejorando la exactitud de los datos.

---

## 🎯 Objetivos

✅ Automatizar la recopilación de información clave de empresas a partir de fuentes en línea.  
✅ Generar resúmenes estructurados sobre cada empresa en base a criterios predefinidos.  
✅ Facilitar la toma de decisiones del equipo de adquisiciones al proporcionar datos comparables.  
✅ Implementar una aplicación web accesible que permita a los usuarios ingresar URLs de empresas y recibir reportes inmediatos.

---

## 🔧 Metodología

1. **Extracción de datos**: Se utiliza *web scraping* para obtener información desde los sitios web y LinkedIn de las empresas.
2. **Procesamiento con GPT-4**: Se envía el contenido extraído a **GPT-4** para extraer y estructurar la información relevante.
3. **Visualización y exportación**: Los datos se presentan en la interfaz de la aplicación con opción de descarga en CSV.

---

## 🛠️ Herramientas y Tecnologías

✅ **Lenguaje de programación**: Python.  
✅ **Framework Web**: Streamlit.  
✅ **Librerías**: `requests`, `BeautifulSoup`, `pandas`, `openai`, `python-dotenv`.  
✅ **IA Generativa**: GPT-4.  
✅ **Hosting**: Streamlit Cloud.  

---

## 🏗️ Arquitectura de la Aplicación

📌 **Interfaz Web**: Los usuarios ingresan URLs de empresas en la app.  
📌 **Scraper**: Extrae contenido de los sitios web y perfiles de LinkedIn.  
📌 **Procesador IA**: Utiliza **GPT-4** para analizar y estructurar la información extraída.  
📌 **Visualización de Datos**: Presenta los datos de forma tabular en la interfaz y permite la exportación en CSV.

---

## 📁 Estructura del Proyecto
```
📂 ia_prompt_v-a
│── .env                 # Variables de entorno (clave API de OpenAI)
│── .gitignore           # Archivos y carpetas ignorados por Git
│── app.py               # Código principal de la aplicación Streamlit
│── requirements.txt     # Dependencias necesarias para ejecutar la app
│── companies_info.csv   # Archivo CSV generado con los datos extraídos
│── README.md            # Documentación del proyecto
│
└─── .devcontainer
    └── devcontainer.json  # Configuración del entorno de desarrollo
```

---

## 🔧 Instalación y Configuración

Para ejecutar la aplicación localmente, sigue estos pasos:

### 1️⃣ Clonar el repositorio
```bash
git clone https://github.com/nicolinolochex/IA_Prompt_V-A.git
cd IA_Prompt_V-A
```

### 2️⃣ Crear un entorno virtual e instalar dependencias
```bash
python -m venv venv
source venv/bin/activate  # En Mac/Linux
venv\Scripts\activate    # En Windows
pip install -r requirements.txt
```

### 3️⃣ Configurar la clave de OpenAI
Crea un archivo `.env` en la raíz del proyecto y agrega:
```
OPENAI_API_KEY=tu_clave_de_openai
```

### 4️⃣ Ejecutar la aplicación
```bash
streamlit run app.py
```

---

## 📌 Próximos Pasos

🚀 **Optimizar la extracción de datos**: Mejorar la precisión de los scrapers para sitios web complejos.  
🚀 **Agregar más fuentes de datos**: Integrar APIs de información empresarial para mejorar la cobertura de datos.  
🚀 **Implementar autenticación de usuarios**: Control de acceso para distintos perfiles de usuario.  

---

## 📩 Contáctame
📧 **Email:** arandigacatriel@gmail.com
🔗 **LinkedIn:** [Catriel Nicolás Arandiga](https://www.linkedin.com/in/catriel-nicolas-arandiga)

