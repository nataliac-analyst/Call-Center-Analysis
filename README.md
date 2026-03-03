# 📊 Análisis Tarifario y Eficiencia Operativa – CallMeMaybe

Dashboard analítico desarrollado en **Python y Dash** para evaluar el desempeño operativo de un call center y analizar los factores que influyen en la Resolución en Primera Llamada (FCR).

🔗 Aplicación desplegada en Render: https://call-center-analysis-ftc5.onrender.com/

---

## 🎯 Objetivo del Proyecto

Evaluar la eficiencia de los planes tarifarios y determinar qué variables influyen en la probabilidad de resolver una llamada en el primer contacto (FCR).

---

## 📈 Métricas Analizadas

- Número total de suscriptores
- Número de operarios
- FCR (%) empresarial
- Tiempo Operativo Medio (TOM), para este análisis usamos el Tiempo de Conversación
- Tiempo de espera por plan
- Modelo logístico explicativo del FCR

---

## 🧠 Metodología

1. Limpieza y preprocesamiento de datos
2. Cálculo de KPIs operativos
3. Análisis comparativo por plan tarifario
4. Modelado estadístico mediante regresión logística:

FCR ~ call_duration * tariff_plan + direction + weekday

El modelo permitió estimar qué variables influyen significativamente en la probabilidad de resolución en primera llamada.

---

## 🔎 Principales Hallazgos

- El **Plan C** concentra mayor número de suscriptores y presenta el FCR más alto.
- Menor tiempo operativo promedio se asocia con mayor eficiencia.
- El FCR depende significativamente del plan tarifario y del día de la semana.
- La duración de la conversación no resulta estadísticamente significativa en el modelo.

---

## 💡 Recomendaciones Estratégicas

- Replicar prácticas operativas del Plan C en otros planes.
- Optimizar asignación de operarios según comportamiento semanal.
- Revisar estructura del Plan A para mejorar su desempeño en FCR.

---

## 🛠️ Tecnologías Utilizadas

- Python
- Pandas
- Plotly
- Dash
- Statsmodels
- Gunicorn (deploy)

---

## 📌 Estructura del Proyecto

- app.py
- telecom_clients.csv
- telecom_dataset_new.csv
- requirements.txt
- README.md
- Informe Final

---

## 👩‍💻 Autora

Natalia Cáceres  
Proyecto de análisis de datos orientado a eficiencia operativa y modelado estadístico.
