import streamlit as st
import pandas as pd
import io
import plotly.express as px
import matplotlib.pyplot as plt

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet


# =================== CONFIG ===================
st.set_page_config(page_title="Dashboard Anggaran Advanced", layout="wide")
st.title("📊 Dashboard Anggaran Advanced & Export Lengkap")

uploaded_file = st.file_uploader("Upload file Excel (.xlsx)", type="xlsx")

# =================== EXPORT PDF ===================
def export_pdf(dataframe, summary):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=(595, 842))  # A4
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("📊 Laporan Anggaran", styles["Title"]))
    elements.append(Spacer(1, 12))

    # Ringkasan
    for key, val in summary.items():
        elements.append(Paragraph(f"<b>{key}:</b> {val}", styles["Normal"]))
    elements.append(Spacer(1, 12))

    # === PIE CHART (Realisasi vs Sisa) ===
    if "Total Realisasi" in summary and "Total Anggaran" in summary:
        total_anggaran = int(summary["Total Anggaran"].replace("Rp", "").replace(".", "").replace(",", ""))
        total_realisasi = int(summary["Total Realisasi"].replace("Rp", "").replace(".", "").replace(",", ""))
        total_sisa = total_anggaran - total_realisasi

        fig, ax = plt.subplots(figsize=(4,4))
        ax.pie([total_realisasi, total_sisa], labels=["Realisasi", "Sisa"], autopct='%1.1f%%')
        ax.set_title("Realisasi vs Sisa")
        pie_img = io.BytesIO()
        plt.savefig(pie_img, format="png", bbox_inches="tight")
        plt.close(fig)
        pie_img.seek(0)
        elements.append(Image(pie_img, width=200, height=200))
        elements.append(Spacer(1, 12))

    # === TABEL DATA ===
    table_data = [list(dataframe.columns)] + dataframe.values.tolist()
    table = Table(table_data, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold")
    ]))
    elements.append(table)

    doc.build(elements)
    buffer.seek(0)
    return buffer


# =================== MAIN ===================
if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)

        # Sidebar
        st.sidebar.header("Pengaturan Kolom")
        col_anggaran = st.sidebar.selectbox("Pilih kolom Anggaran", df.columns.tolist())
        col_realisasi = st.sidebar.selectbox("Pilih kolom Realisasi (opsional)", df.columns.tolist() + [None])
        col_kategori = st.sidebar.multiselect("Pilih kolom Kategori", df.columns.tolist())
        col_tanggal = st.sidebar.selectbox("Pilih kolom Tanggal (opsional)", df.columns.tolist() + [None])

        # Convert ke numeric
        df[col_anggaran] = pd.to_numeric(df[col_anggaran].astype(str).str.replace(',', '').str.replace('.', ''), errors='coerce')
        if col_realisasi:
            df[col_realisasi] = pd.to_numeric(df[col_realisasi].astype(str).str.replace(',', '').str.replace('.', ''), errors='coerce')

        # Filter tanggal
        if col_tanggal:
            df[col_tanggal] = pd.to_datetime(df[col_tanggal], errors='coerce')
            st.sidebar.subheader("Filter Tanggal")
            tanggal_start = st.sidebar.date_input("Mulai", value=df[col_tanggal].min())
            tanggal_end = st.sidebar.date_input("Akhir", value=df[col_tanggal].max())
            df = df[(df[col_tanggal] >= pd.to_datetime(tanggal_start)) & (df[col_tanggal] <= pd.to_datetime(tanggal_end))]

        # Hitung
        total_anggaran = int(df[col_anggaran].iloc[0])
        total_realisasi = df[col_realisasi].sum() if col_realisasi else 0
        total_sisa = total_anggaran - total_realisasi
        persen_serapan = round((total_realisasi / total_anggaran * 100), 2) if col_realisasi else 0
        persen_sisa = round((total_sisa / total_anggaran * 100), 2)
        df["Sisa"] = df[col_realisasi] if col_realisasi else 0

        summary = {
            "Total Anggaran": f"Rp{total_anggaran:,.0f}",
            "Total Realisasi": f"Rp{total_realisasi:,.0f}",
            "Total Sisa": f"Rp{total_sisa:,.0f}",
            "Persentase Serapan": f"{persen_serapan}%",
            "Persentase Sisa": f"{persen_sisa}%"
        }

        # ================= Tabs =================
        tab1, tab2, tab3, tab4 = st.tabs(["Ringkasan", "Chart Interaktif", "Data Mentah", "Export"])

        with tab1:
            st.subheader("📌 Ringkasan Anggaran")
            col1, col2, col3, col4, col5 = st.columns(5)
            col1.metric("Total Anggaran", summary["Total Anggaran"])
            col2.metric("Total Realisasi", summary["Total Realisasi"])
            col3.metric("Total Sisa", summary["Total Sisa"])
            col4.metric("Persentase Serapan", summary["Persentase Serapan"])
            col5.metric("Persentase Sisa", summary["Persentase Sisa"])

        with tab2:
            if col_kategori:
                st.subheader(f"📊 Analisis Berdasarkan Kategori: {', '.join(col_kategori)}")
                df["Kategori Gabungan"] = df[col_kategori].astype(str).agg(" - ".join, axis=1)

                pie_df = df.groupby("Kategori Gabungan")["Sisa"].sum().reset_index()
                pie_fig = px.pie(pie_df, names="Kategori Gabungan", values="Sisa", hole=0.4)
                st.plotly_chart(pie_fig, use_container_width=True)

                bar_cols = ["Sisa"]
                if col_realisasi:
                    bar_cols.insert(0, col_realisasi)
                bar_df = df.groupby("Kategori Gabungan")[bar_cols].sum().reset_index()
                bar_fig = px.bar(bar_df, x="Kategori Gabungan", y=bar_cols, barmode="group", text_auto=True)
                st.plotly_chart(bar_fig, use_container_width=True)

        with tab3:
            st.subheader("🗂️ Data Mentah")
            st.dataframe(df, use_container_width=True)

        with tab4:
            # Export Excel
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                df.to_excel(writer, sheet_name="Data", index=False)
            output.seek(0)
            st.download_button("📥 Download Excel", data=output, file_name="Dashboard_Anggaran.xlsx")

            # Export PDF
            pdf_file = export_pdf(df, summary)
            st.download_button("📄 Download PDF", data=pdf_file, file_name="Dashboard_Anggaran.pdf")

    except Exception as e:
        st.error(f"Terjadi error: {e}")
else:
    st.info("👆 Upload file Excel untuk memulai analisis.")
