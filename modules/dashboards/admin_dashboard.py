import pandas as pd
from cruds.user_crud import user_crud
from cruds.role_crud import role_crud
from cruds.institution_crud import institution_crud
from cruds.contact_crud import contact_crud
from cruds.demo_crud import demo_crud

def show_admin_dashboard(st):
    st.title("Panel de Administración")
    st.write("Bienvenido al panel de administración de Muyu Demo.")

    if st.button("Cerrar sesión"):
        st.session_state['logged_in'] = False
        st.session_state['role'] = None
        st.rerun()

    accion = st.sidebar.selectbox(
        "Gestión",
        ["Panel Kanban", "Usuarios", "Roles", "Instituciones", "Participantes", "Demos"],
        key="admin_gestion_selector"
    )

    if accion == "Panel Kanban":
        from modules.kanban_dashboard import show_kanban_dashboard
        show_kanban_dashboard(st)
    elif accion == "Usuarios":
        user_crud(st)
    elif accion == "Roles":
        role_crud(st)
    elif accion == "Instituciones":
        institution_crud(st)
    elif accion == "Participantes":
        contact_crud(st)
    elif accion == "Demos":
        demo_crud(st)
