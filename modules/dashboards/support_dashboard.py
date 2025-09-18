def show_support_dashboard(st):
    st.title("Panel de Soporte")
    st.write("Bienvenido al panel de soporte de Muyu Demo.")

    if st.button("Cerrar sesión"):
        st.session_state['logged_in'] = False
        st.session_state['role'] = None
        st.rerun()

    # ...aquí puedes agregar la lógica y vistas del dashboard soporte...
