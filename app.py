import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="LESCO Meter Reading Verification",
    page_icon="⚡",
    layout="wide",
)

# --- PASSWORD CONFIGURATION ---
CORRECT_PASSWORD = "LESCO"


def check_password():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if not st.session_state["authenticated"]:
        st.title("🔐 LESCO Portal Login")
        st.write("Is tool ko access karne ke liye password darj karein.")

        user_input = st.text_input("Password:", type="password")
        if st.button("Login"):
            if user_input == CORRECT_PASSWORD:
                st.session_state["authenticated"] = True
                st.success("Login Successful!")
                st.rerun()
            else:
                st.error("Incorrect Password! Dobara koshish karein.")
        return False
    return True


if check_password():
    st.title("⚡ LESCO Meter Reading Verification Tool")
    st.write(
        "Meter reading text file upload karke 0 units / same reading wale reference numbers filter karein."
    )

    with st.sidebar:
        st.write("### User Session")
        if st.button("Logout"):
            st.session_state["authenticated"] = False
            st.rerun()

    uploaded_file = st.file_uploader(
        "Apni Meter Reading File Upload Karein (.txt, .dat)",
        type=["txt", "dat"],
    )

    if uploaded_file is not None:
        content = uploaded_file.getvalue().decode("utf-8", errors="ignore")
        lines = content.splitlines()

        zero_records = []

        for idx, line in enumerate(lines, 1):
            line_str = line.strip()

            # Record length check (At least 39 characters)
            if len(line_str) >= 39:
                # Layout Slicing:
                # Index 0..5: Serial No (e.g. 00075)
                # Index 5..7: Batch (e.g. 14)
                # Index 7..8: Extra Zero (Skipped)
                # Index 8..13: Sub Div (e.g. 11341)
                # Index 13..20: Account No (7 digits e.g. 1177800)
                batch = line_str[5:7]
                sub_div = line_str[8:13]
                acc_no = line_str[13:20]

                ref_no = batch + sub_div + acc_no  # Exact 14 Digits Ref No

                # Units Position: Index 29 to 39
                units_part = line_str[29:39]

                try:
                    units_val = int(units_part)
                    if units_val == 0:
                        zero_records.append(
                            {
                                "Line No": idx,
                                "Batch": batch,
                                "Sub Div": sub_div,
                                "Reference Number": ref_no,
                                "Status": "0 Units / Same Reading",
                            }
                        )
                except ValueError:
                    pass

        if zero_records:
            df = pd.DataFrame(zero_records)
            st.error(
                f"⚠️ Total {len(zero_records)} Zero-Reading / Same Reading Records Found!"
            )

            # Display Table
            st.dataframe(df, use_container_width=True)

            # CSV Download Button
            csv_data = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Report Download Karein (CSV/Excel)",
                data=csv_data,
                file_name="LESCO_Zero_Readings_Report.csv",
                mime="text/csv",
            )
        else:
            st.success("✅ Koi bhi 0 unit / same reading record nahi mila.")
