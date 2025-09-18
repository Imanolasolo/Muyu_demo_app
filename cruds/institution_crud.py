import pandas as pd
from db_setup import get_conn

def institution_crud(st):
    conn = get_conn()
    df = pd.read_sql_query("SELECT * FROM institution", conn)
    st.subheader("Instituciones")
    st.dataframe(df)

    with st.form("add_institution_form"):
        name = st.text_input("Nombre")
        country = st.text_input("País")
        city = st.text_input("Ciudad")
        submitted = st.form_submit_button("Agregar institución")
        if submitted and name:
            conn.execute("INSERT INTO institution (name, country, city) VALUES (?, ?, ?)", (name, country, city))
            conn.commit()
            st.success("Institución agregada")
            st.rerun()

    inst_ids = df['id'].tolist() if not df.empty else []
    if inst_ids:
        del_id = st.selectbox("Eliminar institución (ID)", inst_ids)
        if st.button("Eliminar institución"):
            conn.execute("DELETE FROM institution WHERE id=?", (del_id,))
            conn.commit()
            st.success("Institución eliminada")
            st.rerun()
    conn.close()
