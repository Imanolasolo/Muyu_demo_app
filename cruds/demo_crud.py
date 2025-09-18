import pandas as pd
from db_setup import get_conn

def demo_crud(st):
    conn = get_conn()
    df = pd.read_sql_query(
        "SELECT d.*, i.name as institution_name FROM demo d LEFT JOIN institution i ON d.institution_id=i.id",
        conn
    )
    st.subheader("Demos")
    st.dataframe(df)

    # Obtener instituciones para el selector
    inst_df = pd.read_sql_query("SELECT id, name FROM institution", conn)
    inst_names = inst_df['name'].tolist()

    estados = ['Preparación', 'Activación y Bienvenida', 'Sesión informativa', 'Grabaciones', 'Encuesta', 'Cierre', 'Resultados']
    fases = ['Inicio', 'En curso', 'Finalizada']

    with st.expander("Agregar demo"):
        inst_name = st.selectbox("Institución", inst_names)
        inst_id = int(inst_df[inst_df['name'] == inst_name]['id'].iloc[0]) if inst_name else None

        # Obtener participantes de la institución seleccionada
        part_df = pd.read_sql_query("SELECT name FROM contact WHERE institution_id=?", conn, params=(inst_id,))
        participantes = part_df['name'].tolist() if not part_df.empty else []

        titulo = st.text_input("Título demo")
        participante = st.selectbox("Participante", participantes) if participantes else st.text_input("Participante (nombre)")
        responsable = st.text_input("Responsable MUYU")
        estado = st.selectbox("Estado", estados)
        fase = st.selectbox("Fase", fases)
        num_users = st.number_input("Usuarios planificados", min_value=1, value=10)
        fecha_inicio_demo = st.date_input("Fecha inicio demo")
        fecha_inicio_fase = st.date_input("Fecha inicio fase")
        fecha_fin_fase = st.date_input("Fecha fin fase")
        fecha_fin_demo = st.date_input("Fecha fin demo")
        if st.button("Agregar demo"):
            if inst_name and titulo and participante and responsable:
                cur = conn.cursor()
                cur.execute(
                    "INSERT INTO demo (institution_id, title, participante, responsable_muyu, num_users, state, phase, start_date, start_phase_date, end_phase_date, end_date, metadata) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        inst_id,
                        titulo,
                        participante,
                        responsable,
                        num_users,
                        estado,
                        fase,
                        fecha_inicio_demo.isoformat(),
                        fecha_inicio_fase.isoformat(),
                        fecha_fin_fase.isoformat(),
                        fecha_fin_demo.isoformat(),
                        '{}'
                    )
                )
                demo_id = cur.lastrowid
                # Crear participante en la tabla participant si no existe
                part_df = pd.read_sql_query("SELECT name, email, phone FROM contact WHERE name=? AND institution_id=?", conn, params=(participante, inst_id))
                if not part_df.empty:
                    p = part_df.iloc[0]
                    cur.execute(
                        "INSERT INTO participant (demo_id, name, email, phone, activated) VALUES (?, ?, ?, ?, ?)",
                        (demo_id, p['name'], p['email'], p['phone'], 0)
                    )
                    conn.commit()
                st.success("Demo agregada")
                st.rerun()

    demo_ids = df['id'].tolist() if not df.empty else []
    if demo_ids:
        del_id = st.selectbox("Eliminar demo (ID)", demo_ids)
        if st.button("Eliminar demo"):
            conn.execute("DELETE FROM demo WHERE id=?", (del_id,))
            conn.commit()
            st.success("Demo eliminada")
            st.rerun()
    conn.close()
