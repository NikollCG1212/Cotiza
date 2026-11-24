import streamlit as st
#Estilos
st.markdown("""
   <style>
    /* Fondo general */
    .stApp {
        background-color: #F5F7FB;
    }

    /* Espaciado general */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    /* Títulos */
    h1 {
        color: #24476B !important;
        font-weight: 700 !important;
        letter-spacing: -0.5px;
    }

    h2, h3 {
        color: #24476B;
        font-weight: 600;
    }

    /* Tarjetas de estadísticas */
    div[data-testid="stMetric"] {
        background-color: #FFFFFF;
        border: 1px solid #E1E8F0;
        border-top: 3px solid #477EAC;
        padding: 18px 20px;
        border-radius: 12px;
        box-shadow: 0 2px 6px rgba(36, 71, 107, 0.05);
        transition: box-shadow 0.2s ease;
    }

    div[data-testid="stMetric"]:hover {
        box-shadow: 0 4px 10px rgba(36, 71, 107, 0.09);
    }

    div[data-testid="stMetricLabel"] {
        color: #5B6B7C;
    }

    div[data-testid="stMetricValue"] {
        color: #24476B;
    }

    /* Campos del formulario */
    div[data-testid="stForm"] {
        background-color: #FFFFFF;
        padding: 24px;
        border: 1px solid #E1E8F0;
        border-radius: 12px;
    }

    div[data-baseweb="input"] input {
        background-color: #FFFFFF;
    }

    /* Botones */
    div.stButton > button,
    div.stFormSubmitButton > button {
        background-color: #315F8C;
        color: #FFFFFF;
        border-radius: 8px;
        border: 1px solid #315F8C;
        font-weight: 600;
        padding: 8px 18px;
        transition: background-color 0.2s ease;
    }

    div.stButton > button:hover,
    div.stFormSubmitButton > button:hover {
        background-color: #24476B;
        color: #FFFFFF;
        border-color: #24476B;
    }

    /* Enfoque de los campos */
    div[data-baseweb="input"]:focus-within {
        border-color: #477EAC;
    }
</style>
""", unsafe_allow_html=True)
import sqlite3

st.set_page_config(
    page_title="Cotiza",
    page_icon="C",
    layout="wide"
)


# conexión a la base de datos
def conectar_bd():
    conexion = sqlite3.connect("cotiza.db")
    return conexion


# crear la tabla si no existe
def crear_tabla():
    conexion = conectar_bd()

    conexion.execute("""
        CREATE TABLE IF NOT EXISTS cotizaciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente TEXT NOT NULL,
            fecha TEXT NOT NULL,
            descripcion TEXT NOT NULL,
            cantidad INTEGER NOT NULL,
            precio REAL NOT NULL,
            total REAL NOT NULL,
            estado TEXT NOT NULL
        )
    """)

    conexion.commit()
    conexion.close()


crear_tabla()


#encabezado
col_titulo, col_subtitulo = st.columns([3, 1])

with col_titulo:
    st.title("Cotiza")
    st.write("Tu espacio para gestionar cotizaciones de forma sencilla y organizada.")

with col_subtitulo:
    st.markdown(
        """
        <div style="
            text-align: right;
            padding-top: 20px;
            color: #477EAC;
            font-size: 14px;
            font-weight: 600;
        ">
            GESTIÓN DE COTIZACIONES
        </div>
        """,
        unsafe_allow_html=True
    )

 #estadísticas
conexion = conectar_bd()

total_cotizaciones = conexion.execute(
    "SELECT COUNT(*) FROM cotizaciones"
).fetchone()[0]

total_pendientes = conexion.execute(
    "SELECT COUNT(*) FROM cotizaciones WHERE estado = 'Pendiente'"
).fetchone()[0]

total_aprobadas = conexion.execute(
    "SELECT COUNT(*) FROM cotizaciones WHERE estado = 'Aprobada'"
).fetchone()[0]

valor_cotizado = conexion.execute(
    "SELECT SUM(total) FROM cotizaciones"
).fetchone()[0]

conexion.close()

if valor_cotizado is None:
    valor_cotizado = 0

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total de cotizaciones", total_cotizaciones)

with col2:
    st.metric("Pendientes", total_pendientes)

with col3:
    st.metric("Aprobadas", total_aprobadas)

with col4:
    st.metric(
        "Valor cotizado",
        f"${valor_cotizado:,.0f} COP"
    )

# formulario
st.subheader("Nueva cotización")

with st.form("formulario_cotizacion"):

    columna1, columna2 = st.columns(2)

    with columna1:
        cliente = st.text_input("Nombre del cliente")

    with columna2:
        fecha = st.date_input("Fecha de la cotización")

    columna3, columna4 = st.columns(2)

    with columna3:
        descripcion = st.text_input(
            "Descripción del producto o servicio"
        )

    with columna4:
        estado = st.selectbox(
            "Estado",
            ["Pendiente", "Aprobada", "Rechazada"]
        )

    columna5, columna6 = st.columns(2)

    with columna5:
        cantidad = st.number_input(
            "Cantidad",
            min_value=1,
            step=1
        )

    with columna6:
        precio = st.number_input(
            "Precio por unidad (COP)",
            min_value=0,
            step=1000
        )

    total = cantidad * precio

    st.info(f"Total de la cotización: ${total:,.0f} COP")

    guardar = st.form_submit_button("Guardar cotización")

    if guardar:
        if cliente.strip() and descripcion.strip():

            conexion = conectar_bd()

            conexion.execute("""
                INSERT INTO cotizaciones
                (cliente, fecha, descripcion, cantidad, precio, total, estado)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                cliente.strip(),
                fecha.isoformat(),
                descripcion.strip(),
                cantidad,
                precio,
                total,
                estado
            ))

            conexion.commit()
            conexion.close()

            st.success("¡Cotización guardada correctamente!")

        else:
            st.error("Escribe el nombre del cliente y la descripción.")

# Cotizaciones guardadas

st.subheader("Cotizaciones registradas")

conexion = conectar_bd()

registros = conexion.execute("""
    SELECT id, cliente, fecha, descripcion,
           cantidad, precio, total, estado
    FROM cotizaciones
    ORDER BY id DESC
""").fetchall()

conexion.close()

if registros:
    # Búsqueda y filtro
    columna1, columna2 = st.columns(2)

    with columna1:
        busqueda = st.text_input(
            "Buscar cotización",
            placeholder="Escribe el nombre del cliente..."
        )

    with columna2:
        filtro_estado = st.selectbox(
            "Filtrar por estado",
            ["Todos", "Pendiente", "Aprobada", "Rechazada"]
        )

    # aplicar los filtros
    cotizaciones_filtradas = []

    for fila in registros:
        coincide_cliente = (
            busqueda.lower() in fila[1].lower()
            or busqueda.lower() in fila[3].lower()
        )

        coincide_estado = (
            filtro_estado == "Todos"
            or fila[7] == filtro_estado
        )

        if coincide_cliente and coincide_estado:
            cotizaciones_filtradas.append({
                "Código": f"COT-{fila[0]:04d}",
                "Cliente": fila[1],
                "Fecha": fila[2],
                "Descripción": fila[3],
                "Cantidad": fila[4],
                "Precio unitario": fila[5],
                "Total": fila[6],
                "Estado": fila[7]
            })

    # resultados
    if cotizaciones_filtradas:
        st.dataframe(
    cotizaciones_filtradas,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Código": st.column_config.TextColumn("Código"),
        "Cliente": st.column_config.TextColumn("Cliente"),
        "Fecha": st.column_config.DateColumn(
            "Fecha",
            format="DD/MM/YYYY"
        ),
        "Descripción": st.column_config.TextColumn("Descripción"),
        "Cantidad": st.column_config.NumberColumn("Cantidad"),
        "Precio unitario": st.column_config.NumberColumn(
            "Precio unitario",
            format="$ %d COP"
        ),
        "Total": st.column_config.NumberColumn(
            "Total",
            format="$ %d COP"
        ),
        "Estado": st.column_config.TextColumn("Estado")
    }
)

        st.caption(
            f"Cotizaciones encontradas: {len(cotizaciones_filtradas)}"
        )

        st.subheader("Administrar cotizaciones")

        opciones = {
            f"COT-{fila[0]:04d} - {fila[1]}": fila[0]
            for fila in registros
        }

        cotizacion_seleccionada = st.selectbox(
            "Selecciona una cotización",
            options=list(opciones.keys())
        )

        if st.button("Eliminar cotización"):
            conexion = conectar_bd()

            conexion.execute(
                "DELETE FROM cotizaciones WHERE id = ?",
                (opciones[cotizacion_seleccionada],)
            )

            conexion.commit()
            conexion.close()

            st.success("Cotización eliminada correctamente.")
            st.rerun()
        st.subheader("Editar cotización")

        cotizacion_editar = st.selectbox(
            "Selecciona la cotización que deseas editar",
            options=list(opciones.keys()),
            key="seleccionar_edicion"
        )

        id_editar = opciones[cotizacion_editar]

        conexion = conectar_bd()

        datos_editar = conexion.execute(
            "SELECT * FROM cotizaciones WHERE id = ?",
            (id_editar,)
        ).fetchone()

        conexion.close()

        with st.form("formulario_edicion"):
            nuevo_cliente = st.text_input(
                "Nombre del cliente",
                value=datos_editar[1]
            )

            nueva_fecha = st.date_input(
                "Fecha de la cotización",
                value=__import__("datetime").date.fromisoformat(datos_editar[2])
            )

            nueva_descripcion = st.text_input(
                "Descripción",
                value=datos_editar[3]
            )

            nueva_cantidad = st.number_input(
                "Cantidad",
                min_value=1,
                value=datos_editar[4],
                step=1
            )

            nuevo_precio = st.number_input(
                "Precio por unidad (COP)",
                min_value=0,
                value=int(datos_editar[5]),
                step=1000
            )

            estados = ["Pendiente", "Aprobada", "Rechazada"]

            nuevo_estado = st.selectbox(
                "Estado",
                estados,
                index=estados.index(datos_editar[7])
            )

            guardar_cambios = st.form_submit_button("Guardar cambios")

            if guardar_cambios:
                if nuevo_cliente.strip() and nueva_descripcion.strip():
                    nuevo_total = nueva_cantidad * nuevo_precio

                    conexion = conectar_bd()

                    conexion.execute("""
                        UPDATE cotizaciones
                        SET cliente = ?,
                            fecha = ?,
                            descripcion = ?,
                            cantidad = ?,
                            precio = ?,
                            total = ?,
                            estado = ?
                        WHERE id = ?
                    """, (
                        nuevo_cliente.strip(),
                        nueva_fecha.isoformat(),
                        nueva_descripcion.strip(),
                        nueva_cantidad,
                        nuevo_precio,
                        nuevo_total,
                        nuevo_estado,
                        id_editar
                    ))

                    conexion.commit()
                    conexion.close()

                    st.success("Cotización actualizada correctamente.")
                    st.rerun()

                else:
                    st.error("Completa el nombre del cliente y la descripción.")
    else:
        st.info("No se encontraron cotizaciones con esos criterios.")

else:
    st.info("Todavía no hay cotizaciones registradas.")