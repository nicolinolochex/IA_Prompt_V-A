# Proyecto Propuesto: Evaluador Automatizado de Empresas Según Requerimientos (E3)

---

## Hola Profe,

Le presento mi idea y doy un poco de contexto. Trabajo en un equipo de **Adquisiciones** en la rama de **BI**, y basándome en las necesidades operativas del equipo —que se encarga de investigar empresas potenciales para adquirir, de acuerdo a ciertos criterios definidos por el management (como *revenue*, *país*, *headcount*, etc.)—, creo que podamos desarrollar algunos prompts que los ayuden en sus tareas diarias para mejorar los tiempos en la devolución de solicitudes y la exactitud de los datos que manejamos.

A continuación, resumo mi propuesta en tres puntos principales.

---

## Resumen de la Idea

El sistema automatizará la investigación de empresas a partir de información disponible en la web (por ejemplo, en sus sitios corporativos o perfiles de LinkedIn). A partir de parámetros definidos (como **headcount**, **servicios ofrecidos**, **revenue**, **país del headquarter** y si la empresa es **sustentable** o no), el sistema:

- Extraerá la información relevante.
- Generará un resumen evaluativo.
- Asignará un puntaje a cada empresa para determinar cuáles cumplen mejor con los requisitos del equipo.

---

## Funcionalidades Clave

### 1. Listado de Empresas Basado en Requerimientos Predefinidos

- **Objetivo:**  
  Dado un conjunto de criterios (ej.: *headcount*, *servicios*, *revenue*, *ubicación* y *sostenibilidad*), el sistema proporcionará un listado de empresas que cumplan en mayor medida esos requerimientos.

- **Implementación:**  
  - Utilizar un **prompt predefinido** en GPT-4 para solicitar un listado basado en los criterios.
  - Integrar información extraída de sitios corporativos y perfiles de LinkedIn, ya sea mediante **web scraping** o **APIs** disponibles.

---

### 2. Extracción de Información Relevante de Páginas Web y Perfiles en LinkedIn

- **Objetivo:**  
  Recopilar y procesar información clave de las empresas desde sus sitios web y/o perfiles de LinkedIn, extrayendo datos como:
  - Número de empleados.
  - Servicios ofrecidos.
  - Revenue.
  - País de la sede.
  - Iniciativas de sustentabilidad.

- **Implementación:**  
  - **Scraping:**  
    Desarrollar scripts en Python (usando librerías como *BeautifulSoup* o *Selenium*) para obtener el contenido de las páginas y perfiles.
  - **Procesamiento con GPT-4:**  
    Crear un prompt que, al recibir el contenido textual extraído, genere un extracto **estructurado** y **conciso** de los datos relevantes.

  - **Ejemplo de Prompt:**  
    > "A partir del siguiente contenido web, extrae y resume la siguiente información: número de empleados, servicios ofrecidos, revenue, país del headquarter y si la empresa se posiciona como sustentable. Presenta la información de forma estructurada."

---

### 3. Asignación de Puntaje y Selección de las Mejores Opciones

- **Objetivo:**  
  Evaluar cada empresa en función de qué tan bien cumplen con los requerimientos establecidos y asignarles un **puntaje** que permita ordenarlas de acuerdo a su encaje con dichos criterios.

- **Implementación:**  
  - Definir una **fórmula de scoring** en la que cada criterio tenga un peso específico (por ejemplo, *revenue* y *sostenibilidad* pueden tener mayor peso).
  - Generar un prompt para GPT-4 que, a partir de la información extraída, asigne un puntaje y ofrezca una breve justificación.

  - **Ejemplo de Prompt:**  
    > "Dada la siguiente información sobre la empresa [extracto estructurado] y considerando los siguientes pesos para cada criterio (*headcount*, *servicios*, *revenue*, *país*, *sustentabilidad*), asigna un puntaje del 1 al 10 y explica brevemente por qué se asignó ese puntaje."

---

## Flujo de Datos y Consideraciones Técnicas

1. **Entrada de Requerimientos y URLs:**  
   - El usuario define los criterios deseados.  
   - Se provee una lista de URLs o perfiles de LinkedIn a analizar.

2. **Extracción y Preprocesamiento:**  
   - Se utiliza **web scraping** para obtener el contenido textual de las páginas y perfiles.  
   - El contenido es procesado para eliminar ruido y obtener la información relevante.

3. **Procesamiento con GPT-4:**  
   - Se emplean **prompts predefinidos** para extraer la información estructurada de cada fuente.  
   - Se genera un resumen evaluativo de cada empresa basándose en los criterios.

4. **Evaluación y Puntaje:**  
   - Se asigna un puntaje a cada empresa mediante una función o prompt que integre los datos y criterios definidos.  
   - Se presenta un **ranking** de empresas que mejor se ajusten a los requerimientos.

5. **Visualización y Reporte:**  
   - Se pueden generar reportes visuales, dashboards o incluso infografías (posiblemente utilizando **DALL-E** para representar gráficamente el nivel de encaje).

---

## Viabilidad Técnica y Justificación

- **Recursos Disponibles:**  
  Mi experiencia en análisis de datos y el acceso a herramientas de scraping, junto con las APIs de OpenAI, hacen factible la implementación de este sistema.

- **Tiempo y Limitaciones:**  
  Será necesario coordinar la integración de múltiples fuentes de datos, el procesamiento con GPT-4 y la asignación de puntajes, considerando la cuota y el costo de las APIs.

- **Valor Agregado:**  
  Automatizar la evaluación y clasificación de empresas basándose en criterios predefinidos mejora la eficiencia en el proceso de investigación, permitiendo que el equipo se concentre en análisis estratégicos y optimizando la toma de decisiones.

---

Esta propuesta se alinea con las necesidades del equipo y mi rol dentro de la organización, ofreciendo una solución innovadora para agilizar el proceso de research y evaluación de empresas. Quedo atento a sus comentarios o sugerencias para seguir mejorando la propuesta.
