import pandas as pd
from db_setup import get_conn

def role_crud(st):
    conn = get_conn()
    df = pd.read_sql_query("SELECT * FROM role", conn)
    st.subheader("Roles")
    st.dataframe(df)

    with st.form("add_role_form"):
        name = st.text_input("Nombre del rol")
        submitted = st.form_submit_button("Agregar rol")
        if submitted and name:
            conn.execute("INSERT INTO role (name) VALUES (?)", (name,))
            conn.commit()
            st.success("Rol agregado")
            st.rerun()

    role_ids = df['id'].tolist() if not df.empty else []
    if role_ids:
        del_id = st.selectbox("Eliminar rol (ID)", role_ids)
        if st.button("Eliminar rol"):
            conn.execute("DELETE FROM role WHERE id=?", (del_id,))
            conn.commit()
            st.success("Rol eliminado")
            st.rerun()
    conn.close()
