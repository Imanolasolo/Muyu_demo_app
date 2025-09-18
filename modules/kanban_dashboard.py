import pandas as pd
from db_setup import fetch_demos, run_automation_checks, get_conn, update_demo_state

def show_kanban_dashboard(st):
    st.header("Kanban de Fases de Demos")
    df = fetch_demos()
    states = ['Preparación', 'Activación y Bienvenida', 'Sesión informativa', 'Grabaciones', 'Encuesta', 'Cierre', 'Resultados']
    cols = st.columns(len(states))
    demos = df.to_dict('records')
    state_map = {s:[] for s in states}
    for d in demos:
        st_item = d.get('state') or 'Preparación'
        if st_item not in state_map:
            state_map[st_item] = []
        state_map[st_item].append(d)
    for i, s in enumerate(states):
        with cols[i]:
            st.subheader(s)
            items = state_map.get(s, [])
            for it in items:
                with st.expander(f"{it['institution_name']} — {it['title']}", expanded=False):
                    new_title = st.text_input("Título demo", value=it['title'], key=f"title_{it['id']}")
                    new_responsable = st.text_input("Responsable", value=it['responsable_muyu'], key=f"resp_{it['id']}")
                    new_num_users = st.number_input("Usuarios planificados", min_value=1, value=int(it['num_users']), key=f"numusers_{it['id']}")
                    new_state = st.selectbox(
                        "Fase actual", states, index=states.index(it['state']) if it['state'] in states else 0, key=f"state_{it['id']}"
                    )
                    if st.button("Guardar cambios", key=f"save_demo_{it['id']}"):
                        conn = get_conn()
                        conn.execute(
                            "UPDATE demo SET title=?, responsable_muyu=?, num_users=?, state=? WHERE id=?",
                            (new_title, new_responsable, new_num_users, new_state, it['id'])
                        )
                        conn.commit()
                        conn.close()
                        st.success("Datos de demo actualizados")
                        st.rerun()
                    if st.button(f"Ejecutar automatización demo {it['id']}", key=f"run_auto_{it['id']}"):
                        alerts = run_automation_checks(it['id'])
                        if alerts:
                            for a in alerts:
                                st.warning(a['msg'])
                            st.success(f'{len(alerts)} alertas creadas como tareas')
                        else:
                            st.success('No se detectaron alertas')
                    # Tareas / Alertas asociadas
                    st.markdown("**Tareas / Alertas asociadas:**")
                    conn = get_conn()
                    tasks_df = pd.read_sql_query(
                        "SELECT * FROM task WHERE demo_id=? ORDER BY created_at DESC", conn, params=(it['id'],)
                    )
                    conn.close()
                    if tasks_df.empty:
                        st.info("No hay tareas/alertas para esta demo.")
                    else:
                        for idx, row in tasks_df.iterrows():
                            st.write(f"- [{ '✔️' if row['done'] else '❌' }] {row['title']}: {row['description']}")
                            if not row['done']:
                                if st.button(f"Marcar como realizada: {row['title']}", key=f"done_task_{row['id']}"):
                                    conn = get_conn()
                                    conn.execute("UPDATE task SET done=1 WHERE id=?", (row['id'],))
                                    conn.commit()
                                    conn.close()
                                    st.success("Tarea marcada como realizada")
                                    st.rerun()
