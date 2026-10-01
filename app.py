import re
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
    # --- HEADER & BRANDING SECTION ---
    col1, col2 = st.columns([1, 5])

    with col1:
        # LESCO Logo Image
        st.image(
            "https://upload.wikimedia.org/wikipedia/commons/f/f8/LESCO_Logo.png",
            width=110,
        )

    with col2:
        st.title("⚡ LESCO Meter Reading Verification Tool")
        st.caption(
            "**Developed & Maintained by:** Mian Muzamil (Mustafabad Sub Divn LESCO)"
        )

    st.markdown("---")

    # --- SIDEBAR SESSION INFO ---
    with st.sidebar:
        st.write("### 👤 User Information")
        st.info("**Officer:** Mian Muzamil\n\n**Sub Division:** Mustafabad")
        st.markdown("---")
        if st.button("Logout", type="primary"):
            st.session_state["authenticated"] = False
            st.rerun()

    # --- FILE UPLOAD SECTION ---
    st.subheader("📂 File Upload")
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
                # Slicing Logic:
                batch = line_str[5:7]  # Batch (2 digits)
                sub_div = line_str[8:13]  # Sub Div (5 digits)
                acc_no = line_str[13:20]  # Account No (7 digits)

                ref_no = batch + sub_div + acc_no  # Exact 14-digit Ref No

                units_part = line_str[29:39]  # Current Month Units Position

                # Extract Meter Reader Name accurately from line end
                # 1. Pehle dekhein ke line ke end me alphabetic name hai ya nahi
                match = re.search(r"([A-Za-z\s\.\'-]+)$", line_str)
                if match:
                    extracted_name = match.group(1).strip()
                    # Agar extracted string me zeroes/numbers ke baad text hai
                    extracted_name = re.sub(
                        r"^[0-9\.\*\s]+", "", extracted_name
                    ).strip()
                else:
                    extracted_name = ""

                # Fallback check agar regex miss kare
                if not extracted_name or len(extracted_name) < 2:
                    # Line ke aakhri 20 characters se numbers aur symbols saaf karein
                    tail = line_str[-25:]
                    cleaned_tail = re.sub(r"[0-9\*\.]", "", tail).strip()
                    reader_name = (
                        cleaned_tail if len(cleaned_tail) >= 2 else "N/A"
                    )
                else:
                    reader_name = extracted_name

                try:
                    units_val = int(units_part)
                    if units_val == 0:
                        zero_records.append(
                            {
                                "Batch": batch,
                                "Sub Div": sub_div,
                                "Reference Number": ref_no,
                                "Status": "0 Units / Same Reading",
                                "Meter Reader": reader_name,
                            }
                        )
                except ValueError:
                    pass

        st.markdown("---")
        if zero_records:
            df = pd.DataFrame(zero_records)

            st.error(
                f"⚠️ **Total {len(zero_records)} Zero-Reading / Same Reading Records Found!**"
            )

            # Display Clean Table with Meter Reader Column
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
            st.success("✅ **Koi bhi 0 unit / same reading record nahi mila.**")
