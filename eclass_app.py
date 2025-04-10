import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(layout="wide")
st.title("ECLASS Match-Auswahl Tool")

# Hochladen der Excel-Datei
uploaded_file = st.file_uploader("Lade deine Excel-Datei hoch:", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # Gruppieren nach eigener ID
    grouped = list(df.groupby("ID"))
    total_pages = len(grouped)

    # Initialisiere Session-State zur Speicherung der Auswahl
    if "selected_checks" not in st.session_state:
        st.session_state.selected_checks = {}

    # Seitenwahl für Pagination
    st.sidebar.header("Navigation")
    page = st.sidebar.number_input("Seite", min_value=1, max_value=total_pages, step=1)
    current_group = grouped[page - 1]

    st.markdown("---")
    st.header("Durchsuche und wähle Vorschläge aus")

    id_val, group = current_group
    with st.expander(f"**{id_val} – {group['Deutsch_Attribut'].iloc[0]}**", expanded=True):
        st.write("**Eigene Beschreibung:**", group['Custom_Beschreibung'].iloc[0])
        for idx, row in group.iterrows():
            key = f"check_{id_val}_{idx}"
            # Checkbox-Zustand laden oder False
            checked = st.session_state.selected_checks.get(key, False)
            new_checked = st.checkbox(
                f"{row['Matched_ECLASS_IRDI']} – {row['Matched_Name']} - {row['Matched_Definition']} - (Sim: {row['Similarity']})",
                value=checked,
                key=key
            )
            st.session_state.selected_checks[key] = new_checked

    # Sammle alle ausgewählten Zeilen aus allen Gruppen
    selected_rows = []
    for id_val, group in grouped:
        for idx, row in group.iterrows():
            key = f"check_{id_val}_{idx}"
            if st.session_state.selected_checks.get(key):
                selected_rows.append(row)

    st.markdown("---")
    if selected_rows:
        st.success(f"{len(selected_rows)} Vorschläge ausgewählt.")

        if st.button("Exportiere ausgewählte Vorschläge als Excel"):
            result_df = pd.DataFrame(selected_rows)

            # Excel in Memory schreiben
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                result_df.to_excel(writer, index=False, sheet_name='Auswahl')
            output.seek(0)

            st.download_button(
                label="Herunterladen",
                data=output,
                file_name="ECLASS_Auswahl.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    else:
        st.info("Noch keine Vorschläge ausgewählt.")
        