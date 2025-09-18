import pandas as pd
from db_setup import get_conn

def contact_crud(st):
    conn = get_conn()
    df = pd.read_sql_query(
        "SELECT c.*, i.name as institution_name FROM contact c LEFT JOIN institution i ON c.institution_id=i.id",
        conn
    )
    st.subheader("Participantes")
    st.dataframe(df)

    # Obtener instituciones para el selector
    inst_df = pd.read_sql_query("SELECT id, name FROM institution", conn)
    inst_names = inst_df['name'].tolist()
    inst_ids = inst_df['id'].tolist()

    with st.expander("Agregar participante"):
        name = st.text_input("Nombre")
        email = st.text_input("Email")
        phone = st.text_input("Teléfono")
        inst_name = st.selectbox("Institución", inst_names)
        if st.button("Agregar participante"):
            if name and inst_name:
                inst_id = int(inst_df[inst_df['name'] == inst_name]['id'].iloc[0])
                conn.execute(
                    "INSERT INTO contact (name, email, phone, institution_id) VALUES (?, ?, ?, ?)",
                    (name, email, phone, inst_id)
                )
                conn.commit()
                st.success("Participante agregado")
                st.rerun()

    contact_ids = df['id'].tolist() if not df.empty else []
    if contact_ids:
        del_id = st.selectbox("Eliminar participante (ID)", contact_ids)
        if st.button("Eliminar participante"):
            conn.execute("DELETE FROM contact WHERE id=?", (del_id,))
            conn.commit()
            st.success("Participante eliminado")
            st.rerun()
    conn.close()
