# Librerias
import pandas as pd
import numpy as np
import dash
from dash import Dash, html, dcc
import plotly.express as px
import statsmodels.formula.api as smf

# Cargo mi dataset
clientes = pd.read_csv("telecom_clients.csv")
dataset = pd.read_csv("telecom_dataset_new.csv")
#
#
#
#
#
#
#
# Preprocesamiento
# Convertir datos de fecha a datetime
clientes["date_start"] = pd.to_datetime(clientes['date_start'])
dataset["date"] = pd.to_datetime(dataset['date'])
# Calculo tiempo de espera
dataset["t_espera"] = dataset["total_call_duration"] - dataset["call_duration"]
# Transformo tipo de dato aquellas columnas con varibles binarias (0,1) que están como object y booleano
dataset["internal"] = dataset["internal"].astype("Int64")
dataset["direction"] = dataset["direction"].replace({"in": 0, "out": 1})
dataset["is_missed_call"] = dataset["is_missed_call"].astype(int)
# Simplifico la fecha quitándo el componente de las horas, porque siempre es la misma hora y no aporta información de valor
dataset["date"] = dataset["date"].dt.date
dataset["date"] = pd.to_datetime(dataset['date'])
# Creo columna con nombre del dia, para una futura curva de llamadas
dataset["weekday"] = dataset["date"].dt.day_name()
# Investigo si hay duplicados en los dataframes
# Duplicados en clientes
clientes_duplicadas = clientes[clientes.duplicated()]
# Cuplicados en dataset o en el registro de llamadas
data_duplicadas = dataset[dataset.duplicated(keep=False)] \
                        .sort_values(by=["user_id", "date"])
data_duplicadas = data_duplicadas.reset_index(drop=True)
# Elimino duplicados de tabla de registros telefónicos
dataset_no_duplicados = dataset.drop_duplicates(keep="first")
# Uno los datasets (clientes y registros telefónicos) para análisis futuros. No incluyo la fecha de registro en la unión...
dataset_merge = dataset_no_duplicados.merge(
    clientes[["user_id", "tariff_plan"]],
    on="user_id",
    how="left"
)

#
#
#
#
#
#
#
#
#
#
#
# Dashboard contiene: KPIS generales de la empresa, tarifas y usuarios gráfica FCR por tarifa, tiempos promedio de conversacion y espera, gráfica modelo
# KPIs y Generales
Num_users = dataset_merge["user_id"].nunique()
Num_operators = dataset_merge["operator_id"].nunique()
# FCR EMPRESARIAL - GENERAL
# Calcularé el FCR por usuario
# Primero filtraré las llamadas que NO fueron perdidas
dataset_calls = dataset_merge[dataset_merge["is_missed_call"]==0]
# Segundo ordeno dataframe
dataset_calls = dataset_calls.sort_values(["user_id", "date"])
# Creo columna de llamada futura
dataset_calls["next_call"] = (
    dataset_calls
    .groupby("user_id")["date"]
    .shift(-1)
)
# Encuentro la diferencia de tiempo entre la primera llamada y la siguiente llamada
dataset_calls["hours_until_next_call"] = (
    (dataset_calls["next_call"] - dataset_calls["date"])
    .dt.total_seconds() / 3600
)
# Definimos FCR, tomando como tiempo máximo 24 hrs para un siguiente intento de llamada
dataset_calls["FCR"] = (((dataset_calls["hours_until_next_call"].isna()) |
        (dataset_calls["hours_until_next_call"] >= 24)
    )
)


dataset_calls["FCR"] = dataset_calls["FCR"].astype(int)

# Cual es el FCR promedio de la empresa?
FCR = dataset_calls['FCR'].mean()*100
# TOM
TOM = dataset_calls['call_duration'].mean()/60
#
#
#
#
#
#
#
#
#
#
#
#
#
# AHORA CREARÉ LAS GRÁFICAS
# NÚMERO SUSCRIPTORES POR TARIFA
fig_suscriptores = px.pie(
    dataset_merge.groupby("tariff_plan")["user_id"]
    .nunique()
    .reset_index(),
    names="tariff_plan",
    values="user_id",
    title="Distribución de Usuarios por Plan"
)
fig_suscriptores.update_traces(textposition='inside', textinfo='percent+label')

fig_suscriptores.update_layout(yaxis_title="Usuarios")
# FCR POR TARIFA
fcr_plan = (
    dataset_calls.groupby("tariff_plan")["FCR"]
    .mean()
    .reset_index()
)

fcr_plan["FCR_pct"] = fcr_plan["FCR"] * 100

fig_fcr_plan = px.bar(
    fcr_plan,
    x="tariff_plan",
    y="FCR_pct",
    title="FCR por Plan Tarifario",
    text="FCR_pct"
)

fig_fcr_plan.update_traces(
    texttemplate="%{text:.2f}%",
    textposition="outside"
)

fig_fcr_plan.update_layout(
    yaxis_title="FCR (%)",
    yaxis=dict(range=[0, 60])
)
# GRÁFICO DE BARRAS HORIZONTALES: TIEMPOS POR TARIFA
# Promedios por tarifa
tiempos_tarifa = (
    dataset_calls
    .groupby("tariff_plan")[["call_duration", "t_espera"]]
    .mean()
    .reset_index()
)

# Convertir a minutos
tiempos_tarifa["call_duration"] = tiempos_tarifa["call_duration"] / 60
tiempos_tarifa["t_espera"] = tiempos_tarifa["t_espera"] / 60

tiempos_tarifa.rename(columns={
    "call_duration": "Tiempo de conversación",
    "t_espera": "Tiempo de espera"
}, inplace=True)

# GRAFICO DOBLE
tiempos_tarifa_melt = tiempos_tarifa.melt(
    id_vars="tariff_plan",
    value_vars=["Tiempo de conversación", "Tiempo de espera"],
    var_name="Tipo",
    value_name="Minutos"
)
# GRÁFICO HORIZONTAL
fig_tiempos_tarifa = px.bar(
    tiempos_tarifa_melt,
    x="Minutos",
    y="tariff_plan",
    color="Tipo",
    orientation="h",
    barmode="group",
    title="Tiempo Promedio de Conversación y Espera por Tarifa"
)

fig_tiempos_tarifa.update_layout(
    xaxis_title="Minutos",
    yaxis_title="Tarifa"
)

# MODELO REGRESIÓN LOGÍSTICA
model = smf.logit(
    "FCR ~ call_duration * C(tariff_plan) + C(direction) + C(weekday)",
    data=dataset_calls
).fit(disp=False)

params = model.params
conf = model.conf_int()

or_df = pd.DataFrame({
    "OR": np.exp(params),
    "CI_lower": np.exp(conf[0]),
    "CI_upper": np.exp(conf[1])
})

or_df = or_df.drop("Intercept")
or_df = or_df.sort_values("OR")
or_df["error_plus"] = or_df["CI_upper"] - or_df["OR"]
or_df["error_minus"] = or_df["OR"] - or_df["CI_lower"]

fig_modelo = px.scatter(
    or_df,
    x="OR",
    y=or_df.index,
    error_x="error_plus",
    title="Factores que influyen en el FCR"
)

fig_modelo.update_traces(
    error_x=dict(
        type="data",
        symmetric=False,
        array=or_df["error_plus"],
        arrayminus=or_df["error_minus"]
    )
)

fig_modelo.add_vline(x=1)

# definición del diseño LAYOUT
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([

    html.H1("Análisis tarifario y KPIs de ¡CallMeMaybe!"),

    html.Div([
        html.Div([
            html.H4("Número de Suscriptores"),
            html.H2(f"{Num_users}")
        ], className="three columns"),

        html.Div([
            html.H4("Número de Operarios"),
            html.H2(f"{Num_operators}")
        ], className="three columns"),

        html.Div([
            html.H4("FCR (%) empresarial"),
            html.H2(f"{FCR:.2f}%")
        ], className="three columns"),

        html.Div([
            html.H4("TOM (min) empresarial"),
            html.H2(f"{TOM:.2f}")
        ], className="three columns"),
    ], className="row"),

dcc.Graph(figure=fig_suscriptores),
dcc.Graph(figure=fig_fcr_plan),
html.P("El Plan C concentra la mayor proporción de suscriptores y presenta el FCR más alto."),

dcc.Graph(figure=fig_tiempos_tarifa),
html.P("El Plan C muestra menor tiempo promedio operativo, lo que sugiere mayor eficiencia."),

dcc.Graph(figure=fig_modelo),
html.P("El modelo logístico indica que el FCR está influenciado principalmente por el plan tarifario y el día de la semana, no por la duración de la conversación."),

html.H3("Recomendaciones Estratégicas"),
html.Ul([
    html.Li("Priorizar el Plan C como modelo operativo por su mayor eficiencia."),
    html.Li("Revisar la estrategia del Plan A para mejorar su FCR."),
    html.Li("Optimizar asignación de operarios según día de la semana.")
])

])

# lógica del dashboard
server = app.server

if __name__ == "__main__":
    app.run(debug=False)