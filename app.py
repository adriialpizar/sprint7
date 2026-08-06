import pandas as pd
import plotly.express as px
import streamlit as st


def load_data() -> pd.DataFrame:
    data = pd.read_csv("datasets/vehicles_us.csv")
    data["model_year"] = pd.to_numeric(data["model_year"], errors="coerce").astype("Int64")
    data["odometer"] = pd.to_numeric(data["odometer"], errors="coerce")
    data["price"] = pd.to_numeric(data["price"], errors="coerce")
    data["date_posted"] = pd.to_datetime(data["date_posted"], errors="coerce")
    data["days_listed"] = pd.to_numeric(data["days_listed"], errors="coerce")
    return data


@st.cache_data
def get_data() -> pd.DataFrame:
    return load_data()


def filter_data(df: pd.DataFrame) -> pd.DataFrame:
    st.sidebar.header("Filtros")

    year_min = int(df["model_year"].min())
    year_max = int(df["model_year"].max())
    year_range = st.sidebar.slider(
        "Año del modelo",
        min_value=year_min,
        max_value=year_max,
        value=(year_min, year_max),
        step=1,
    )

    fuel_options = sorted(df["fuel"].dropna().unique())
    fuel_selected = st.sidebar.multiselect("Combustible", fuel_options, default=fuel_options)

    condition_options = sorted(df["condition"].dropna().unique())
    condition_selected = st.sidebar.multiselect("Condición", condition_options, default=condition_options)

    type_options = sorted(df["type"].dropna().unique())
    type_selected = st.sidebar.multiselect("Tipo de vehículo", type_options, default=type_options)

    transmission_options = sorted(df["transmission"].dropna().unique())
    transmission_selected = st.sidebar.multiselect(
        "Transmisión", transmission_options, default=transmission_options
    )

    price_min = int(df["price"].min(skipna=True))
    price_max = int(df["price"].quantile(0.95))
    price_range = st.sidebar.slider(
        "Rango de precio",
        min_value=price_min,
        max_value=price_max,
        value=(price_min, price_max),
        step=100,
    )

    only_4wd = st.sidebar.checkbox("Solo vehículos 4WD", value=False)

    filtered = df[
        (df["model_year"] >= year_range[0])
        & (df["model_year"] <= year_range[1])
        & (df["fuel"].isin(fuel_selected))
        & (df["condition"].isin(condition_selected))
        & (df["type"].isin(type_selected))
        & (df["transmission"].isin(transmission_selected))
        & (df["price"] >= price_range[0])
        & (df["price"] <= price_range[1])
    ]

    if only_4wd:
        filtered = filtered[filtered["is_4wd"] == 1]

    return filtered


def main() -> None:
    st.set_page_config(
        page_title="Análisis de vehículos usados",
        layout="wide",
        page_icon="🚗",
    )

    st.title("Proyecto Sprint 7: Análisis de vehículos usados")
    st.write(
        "Esta aplicación carga el dataset de vehículos usados y permite explorar precios, condiciones y características principales."
    )

    df = get_data()
    filtered = filter_data(df)

    st.markdown("### Resumen rápido")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Registros", len(filtered), delta=len(filtered) - len(df))
    col2.metric(
        "Precio promedio",
        f"${filtered['price'].mean():,.0f}" if len(filtered) > 0 else "N/A",
    )
    col3.metric(
        "Kilometraje promedio",
        f"{filtered['odometer'].mean():,.0f}" if len(filtered) > 0 else "N/A",
    )
    col4.metric(
        "Año promedio",
        f"{filtered['model_year'].mean():.0f}" if len(filtered) > 0 else "N/A",
    )

    st.markdown("---")
    st.markdown("### Visualizaciones")

    if len(filtered) == 0:
        st.warning("No hay datos con los filtros seleccionados. Ajusta los filtros para ver resultados.")
        return

    fig_price = px.histogram(
        filtered,
        x="price",
        nbins=35,
        title="Distribución de precios",
        labels={"price": "Precio (USD)"},
    )
    fig_price.update_layout(yaxis_title="Cantidad")

    fig_type = px.bar(
        filtered["type"].value_counts().reset_index(),
        x="index",
        y="type",
        labels={"index": "Tipo de vehículo", "type": "Cantidad"},
        title="Cantidad de vehículos por tipo",
    )

    fig_fuel = px.box(
        filtered,
        x="fuel",
        y="price",
        title="Distribución de precio por tipo de combustible",
        labels={"fuel": "Combustible", "price": "Precio (USD)"},
    )

    fig_year = px.scatter(
        filtered,
        x="model_year",
        y="price",
        color="fuel",
        hover_data=["model", "odometer", "condition"],
        title="Precio vs Año del modelo",
        labels={"model_year": "Año del modelo", "price": "Precio (USD)"},
    )

    st.plotly_chart(fig_price, use_container_width=True)
    st.plotly_chart(fig_type, use_container_width=True)
    st.plotly_chart(fig_fuel, use_container_width=True)
    st.plotly_chart(fig_year, use_container_width=True)

    st.markdown("---")
    st.markdown("### Datos filtrados")
    st.dataframe(filtered.reset_index(drop=True))

    st.markdown("#### Estadísticas básicas")
    st.write(filtered.describe(include="all"))


if __name__ == "__main__":
    main()
