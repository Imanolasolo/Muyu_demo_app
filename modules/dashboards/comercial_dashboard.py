import streamlit as st

def show_comercial_dashboard(st):
    st.title("Panel Comercial")
    st.write("Bienvenido al panel comercial de Muyu Demo.")

    if st.button("Cerrar sesión"):
        st.session_state['logged_in'] = False
        st.session_state['role'] = None
        st.rerun()

    # ...aquí puedes agregar la lógica y vistas del dashboard comercial...

