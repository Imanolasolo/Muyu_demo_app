import streamlit as st
import pandas as pd
from db_setup import get_conn, init_db

st.set_page_config(page_title='Muyu Demo Management', layout='wide')

init_db()  # <-- inicializa la base de datos y crea las tablas

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
    st.session_state['role'] = None

if not st.session_state['logged_in']:
    st.title('Muyu Demo Management — Login')
    user = st.text_input('Usuario')
    pwd = st.text_input('Contraseña', type='password')
    if st.button('Ingresar'):
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT role FROM user WHERE username=? AND password=?", (user, pwd))
        result = cur.fetchone()
        conn.close()
        if result:
            st.session_state['logged_in'] = True
            st.session_state['role'] = result['role']
            st.rerun()
        else:
            st.error('Credenciales incorrectas')
    st.stop()

# Conexión a la base de datos
conn = get_conn()
conn.close()

# Mostrar dashboard según rol
if st.session_state['role'] == 'admin':
    from modules.dashboards.admin_dashboard import show_admin_dashboard
    show_admin_dashboard(st)
elif st.session_state['role'] == 'comercial':
    from modules.dashboards.comercial_dashboard import show_comercial_dashboard
    show_comercial_dashboard(st)
elif st.session_state['role'] == 'soporte':
    from modules.dashboards.support_dashboard import show_support_dashboard
    show_support_dashboard(st)
else:
    st.error('Rol no reconocido')