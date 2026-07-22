import io
import pandas as pd
import streamlit as st

from engine.config_loader import load_config
from engine.addition_deletion import build_addition_deletion_workbook
from engine.monthly_accrual import build_master, build_hc_pivot, build_regional_outputs

st.set_page_config(page_title="Report Automation", layout="wide")

CFG = load_config("sample_config.json")


def read_upload(file):
    return pd.read_excel(file) if file is not None else None


def df_dict_to_excel_bytes(sheets: dict) -> bytes:
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        for name, df in sheets.items():
            # Excel sheet names cap at 31 chars
            df.to_excel(writer, sheet_name=name[:31], index=False)
    return buf.getvalue()


st.title("Report automation — demo")
st.caption("Runs fully offline. All data shown is synthetic sample data — no real client information.")

task = st.radio("Choose a task", ["Addition & Deletion File", "Monthly Accrual File"], horizontal=True)

st.divider()

if task == "Addition & Deletion File":
    st.subheader("Task 1: Addition & Deletion File")
    c1, c2 = st.columns(2)
    with c1:
        functional_info_f = st.file_uploader("Functional Information", type=["xlsx"])
        personal_info_f = st.file_uploader("Personal Information (DOB)", type=["xlsx"])
    with c2:
        terminations_f = st.file_uploader("Terminations report", type=["xlsx"])
        prior_month_f = st.file_uploader("Prior month Functional Information", type=["xlsx"])

    if st.button("Process", type="primary"):
        if not all([functional_info_f, personal_info_f, terminations_f, prior_month_f]):
            st.error("Please upload all four files.")
        else:
            result = build_addition_deletion_workbook(
                read_upload(functional_info_f),
                read_upload(personal_info_f),
                read_upload(terminations_f),
                read_upload(prior_month_f),
                CFG,
            )
            st.success("Done.")
            tab1, tab2 = st.tabs(["Addition", "Deletion"])
            with tab1:
                st.dataframe(result["Addition"], use_container_width=True)
            with tab2:
                st.dataframe(result["Deletion"], use_container_width=True)

            st.download_button(
                "Download Addition & Deletion File.xlsx",
                data=df_dict_to_excel_bytes(result),
                file_name="Addition_Deletion_File.xlsx",
            )

else:
    st.subheader("Task 2: Monthly Accrual File")
    c1, c2 = st.columns(2)
    with c1:
        comp_roster_f = st.file_uploader("Comp Roster", type=["xlsx"])
    with c2:
        distribution_list_f = st.file_uploader("Distribution List (for lookup)", type=["xlsx"])

    if st.button("Process", type="primary"):
        if not all([comp_roster_f, distribution_list_f]):
            st.error("Please upload both files.")
        else:
            master = build_master(read_upload(comp_roster_f), read_upload(distribution_list_f), CFG)
            hc = build_hc_pivot(master, CFG)
            regional = build_regional_outputs(master, CFG)

            st.success(f"Done. Master: {len(master)} rows across {len(regional)} regional files.")

            st.markdown("**Master + HC**")
            t1, t2 = st.tabs(["Master", "HC"])
            with t1:
                st.dataframe(master, use_container_width=True)
            with t2:
                st.dataframe(hc, use_container_width=True)

            st.download_button(
                "Download Master File.xlsx",
                data=df_dict_to_excel_bytes({"Master": master, "HC": hc}),
                file_name="Monthly_Accrual_Master.xlsx",
            )

            st.markdown("**Regional files**")
            region_names = list(regional.keys())
            picked = st.selectbox("Preview a regional file", region_names)
            sheets = regional[picked]
            tabs = st.tabs(list(sheets.keys()))
            for tab, (sheet_name, df) in zip(tabs, sheets.items()):
                with tab:
                    st.dataframe(df, use_container_width=True)

            st.download_button(
                f"Download {picked}.xlsx",
                data=df_dict_to_excel_bytes(sheets),
                file_name=f"{picked}.xlsx",
                key=f"dl_{picked}",
            )

            st.markdown("**Or download everything at once**")
            all_buf = io.BytesIO()
            import zipfile
            with zipfile.ZipFile(all_buf, "w") as zf:
                for file_name, sheets in regional.items():
                    zf.writestr(f"{file_name}.xlsx", df_dict_to_excel_bytes(sheets))
            st.download_button(
                "Download all regional files (.zip)",
                data=all_buf.getvalue(),
                file_name="Monthly_Accrual_All_Regions.zip",
            )
