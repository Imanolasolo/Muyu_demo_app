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
    inst_ids = inst_df['id'].tolist()

    with st.form("add_demo_form"):
        inst_name = st.selectbox("Institución", inst_names)
        title = st.text_input("Título demo")
        responsable = st.text_input("Responsable MUYU")
        num_users = st.number_input("Usuarios planificados", min_value=1, value=10)
        submitted = st.form_submit_button("Agregar demo")
        if submitted and inst_name and title and responsable:
            inst_id = int(inst_df[inst_df['name'] == inst_name]['id'].iloc[0])
            conn.execute(
                "INSERT INTO demo (institution_id, title, responsable_muyu, num_users, state, phase, start_date, metadata) VALUES (?, ?, ?, ?, ?, ?, datetime('now'), ?)",
                (inst_id, title, responsable, num_users, 'Preparación', 'Inicio', '{}')
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
