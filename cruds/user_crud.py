import pandas as pd
from db_setup import get_conn

def user_crud(st):
    conn = get_conn()
    df = pd.read_sql_query("SELECT * FROM user", conn)
    st.subheader("Usuarios")
    st.dataframe(df)

    # Obtener roles disponibles
    roles_df = pd.read_sql_query("SELECT name FROM role", conn)
    roles = roles_df['name'].tolist() if not roles_df.empty else []

    with st.form("add_user_form"):
        username = st.text_input("Usuario")
        password = st.text_input("Contraseña")
        role = st.selectbox("Rol", roles)  # Selector de roles
        submitted = st.form_submit_button("Agregar usuario")
        if submitted and username and password and role:
            conn.execute("INSERT INTO user (username, password, role) VALUES (?, ?, ?)", (username, password, role))
            conn.commit()
            st.success("Usuario agregado")
            st.rerun()

    user_ids = df['id'].tolist() if not df.empty else []
    if user_ids:
        del_id = st.selectbox("Eliminar usuario (ID)", user_ids)
        if st.button("Eliminar usuario"):
            conn.execute("DELETE FROM user WHERE id=?", (del_id,))
            conn.commit()
            st.success("Usuario eliminado")
            st.rerun()
    conn.close()
