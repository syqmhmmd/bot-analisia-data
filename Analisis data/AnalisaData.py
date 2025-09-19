import streamlit as st
import pandas as pd
import io
import plotly.express as px

st.set_page_config(page_title="Dashboard Anggaran Advanced", layout="wide")
st.title("📊 Dashboard Anggaran Advanced & Excel Lengkap")

uploaded_file = st.file_uploader("Upload file Excel (.xlsx)", type="xlsx")

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)

        # ===== Pilih kolom otomatis =====
        st.sidebar.header("Pengaturan Kolom")
        col_anggaran = st.sidebar.selectbox("Pilih kolom Anggaran", df.columns.tolist())
        col_realisasi = st.sidebar.selectbox("Pilih kolom Realisasi (opsional)", df.columns.tolist() + [None])
        col_kategori = st.sidebar.multiselect("Pilih kolom Kategori (bisa lebih dari satu)", df.columns.tolist())
        col_tanggal = st.sidebar.selectbox("Pilih kolom Tanggal (opsional)", df.columns.tolist() + [None])

        # Convert ke numeric
        df[col_anggaran] = pd.to_numeric(df[col_anggaran].astype(str).str.replace(',', '').str.replace('.', ''), errors='coerce')
        if col_realisasi:
            df[col_realisasi] = pd.to_numeric(df[col_realisasi].astype(str).str.replace(',', '').str.replace('.', ''), errors='coerce')

        # ===== Filter tanggal range =====
        if col_tanggal:
            df[col_tanggal] = pd.to_datetime(df[col_tanggal], errors='coerce')
            st.sidebar.subheader("Filter Tanggal Range")
            tanggal_start = st.sidebar.date_input("Tanggal mulai", value=df[col_tanggal].min())
            tanggal_end = st.sidebar.date_input("Tanggal akhir", value=df[col_tanggal].max())
            df = df[(df[col_tanggal] >= pd.to_datetime(tanggal_start)) & (df[col_tanggal] <= pd.to_datetime(tanggal_end))]

        # ===== Hitung total & sisa (Anggaran fix) =====
        total_anggaran = int(df[col_anggaran].iloc[0])
        total_realisasi = df[col_realisasi].sum() if col_realisasi else 0
        total_sisa = total_anggaran - total_realisasi
        persen_serapan = round((total_realisasi / total_anggaran * 100), 2) if col_realisasi else 0
        persen_sisa = round((total_sisa / total_anggaran * 100), 2)
        df["Sisa"] = df[col_realisasi] if col_realisasi else 0

        # ================= Tabs =================
        tab1, tab2, tab3 = st.tabs(["Ringkasan", "Chart Interaktif", "Data Mentah"])

        with tab1:
            st.subheader("📌 Ringkasan Anggaran")
            col1, col2, col3, col4, col5 = st.columns(5)
            col1.metric("Total Anggaran", f"Rp{total_anggaran:,.0f}")
            col2.metric("Total Realisasi", f"Rp{total_realisasi:,.0f}")
            col3.metric("Total Sisa", f"Rp{total_sisa:,.0f}")
            col4.metric("Persentase Serapan", f"{persen_serapan}%")
            col5.metric("Persentase Sisa", f"{persen_sisa}%")

        with tab2:
            if col_kategori:
                st.subheader(f"📊 Analisis Berdasarkan Kategori: {', '.join(col_kategori)}")
                df["Kategori Gabungan"] = df[col_kategori].astype(str).agg(" - ".join, axis=1)

                pie_df = df.groupby("Kategori Gabungan")["Sisa"].sum().reset_index()
                pie_fig = px.pie(pie_df, names="Kategori Gabungan", values="Sisa", hole=0.4, color_discrete_sequence=px.colors.qualitative.Set2)
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

        # ================= Export Excel =================
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            df.to_excel(writer, sheet_name="Data", index=False)
            workbook = writer.book
            ws = writer.sheets["Data"]

            # Top 5 Realisasi & Sisa highlight
            if col_realisasi:
                for idx in df.nlargest(5, col_realisasi).index:
                    ws.write(idx+1, df.columns.get_loc(col_realisasi), df.at[idx, col_realisasi],
                             workbook.add_format({'bg_color': '#C6EFCE'}))
            for idx in df.nlargest(5, "Sisa").index:
                ws.write(idx+1, df.columns.get_loc("Sisa"), df.at[idx, "Sisa"],
                         workbook.add_format({'bg_color': '#FFC7CE'}))

            # Bar Chart
            chart_bar = workbook.add_chart({"type": "column"})
            chart_bar.add_series({
                "name": col_realisasi,
                "categories": ["Data", 1, 0, len(df), 0],
                "values": ["Data", 1, df.columns.get_loc(col_realisasi), len(df), df.columns.get_loc(col_realisasi)]
            })
            chart_bar.add_series({
                "name": "Sisa",
                "categories": ["Data", 1, 0, len(df), 0],
                "values": ["Data", 1, df.columns.get_loc("Sisa"), len(df), df.columns.get_loc("Sisa")]
            })
            chart_bar.set_title({"name": "Realisasi vs Sisa"})
            ws.insert_chart("H2", chart_bar)

            # Pie Chart Excel
            chart_pie = workbook.add_chart({"type": "pie"})
            chart_pie.add_series({
                "name": "Sisa per Kategori",
                "categories": ["Data", 1, df.columns.get_loc("Kategori Gabungan"), len(df), df.columns.get_loc("Kategori Gabungan")],
                "values": ["Data", 1, df.columns.get_loc("Sisa"), len(df), df.columns.get_loc("Sisa")],
                "data_labels": {"percentage": True}
            })
            chart_pie.set_title({"name": "Sisa per Kategori"})
            ws.insert_chart("H20", chart_pie)

        output.seek(0)
        st.download_button(
            label="📥 Download Excel Lengkap dengan Chart",
            data=output.getvalue(),
            file_name="Dashboard_Anggaran_Excel_Lengkap.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        st.error(f"Terjadi error: {e}")
else:
    st.info("👆 Upload file Excel untuk memulai analisis.")
