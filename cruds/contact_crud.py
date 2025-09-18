import pandas as pd
from db_setup import get_conn

def contact_crud(st):
    conn = get_conn()
    df = pd.read_sql_query("SELECT * FROM contact", conn)
    st.subheader("Contactos")
    st.dataframe(df)

    with st.form("add_contact_form"):
        name = st.text_input("Nombre")
        email = st.text_input("Email")
        phone = st.text_input("Teléfono")
        submitted = st.form_submit_button("Agregar contacto")
        if submitted and name:
            conn.execute("INSERT INTO contact (name, email, phone) VALUES (?, ?, ?)", (name, email, phone))
            conn.commit()
            st.success("Contacto agregado")
            st.experimental_rerun()

    contact_ids = df['id'].tolist() if not df.empty else []
    if contact_ids:
        del_id = st.selectbox("Eliminar contacto (ID)", contact_ids)
        if st.button("Eliminar contacto"):
            conn.execute("DELETE FROM contact WHERE id=?", (del_id,))
            conn.commit()
            st.success("Contacto eliminado")
            st.experimental_rerun()
    conn.close()
