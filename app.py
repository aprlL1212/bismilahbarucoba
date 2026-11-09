"""Structura - antarmuka Streamlit. Jalankan: streamlit run app.py"""
import json
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components
from structura import engine, examples, moving_load, plots, report, storage, validation, insights

st.set_page_config(page_title="Structura — Analisis Portal 2D & Beban Bergerak", page_icon="🏗️", layout="wide")

# Styling antarmuka modern, bersih, profesional (SaaS-grade UI)
st.markdown("""<style>
/* Font & Base layout */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', -apple-system, sans-serif; }

.hero {
    background: linear-gradient(135deg, #0f2b46 0%, #1a4f78 50%, #0284c7 100%);
    color: #ffffff;
    padding: 1.8rem 2.2rem;
    border-radius: 18px;
    margin-bottom: 1.2rem;
    box-shadow: 0 10px 25px -5px rgba(15, 43, 70, 0.25);
}
.hero h1 { margin: 0; color: #ffffff; font-size: 2.1rem; font-weight: 700; letter-spacing: -0.02em; }
.hero p { margin: 0.5rem 0 0; opacity: 0.92; font-size: 1.05rem; line-height: 1.5; }

/* Cards & Metrics */
.custom-card {
    background: #ffffff;
    border: 1px solid rgba(226, 232, 240, 0.9);
    border-radius: 14px;
    padding: 1.2rem;
    margin-bottom: 1rem;
    box-shadow: 0 2px 6px rgba(0,0,0,0.03);
}
div[data-testid="stMetric"] {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 0.8rem 1rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.02);
}
div[data-testid="stMetric"] label {
    font-size: 0.85rem !important;
    font-weight: 600 !important;
    color: #475569 !important;
}
div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
    font-size: 1.35rem !important;
    font-weight: 700 !important;
    color: #0f172a !important;
}

/* Insight Cards */
.insight-box {
    border-radius: 12px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.8rem;
    border-left: 5px solid;
    background: #f8fafc;
}
.insight-box.normal { border-left-color: #0ea5e9; background: #f0f9ff; }
.insight-box.info { border-left-color: #6366f1; background: #eef2ff; }
.insight-box.warning { border-left-color: #f59e0b; background: #fffbeb; }
.insight-box.success { border-left-color: #10b981; background: #ecfdf5; }
.insight-box.error { border-left-color: #ef4444; background: #fef2f2; }
.insight-title { font-weight: 700; font-size: 0.95rem; margin-bottom: 0.25rem; color: #0f172a; }
.insight-desc { font-size: 0.88rem; color: #334155; line-height: 1.45; }

/* Tabs modern */
.stTabs [data-baseweb="tab-list"] { gap: 8px; }
.stTabs [data-baseweb="tab"] {
    border-radius: 8px 8px 0 0;
    padding: 8px 16px;
    font-weight: 600;
}
.block-container { padding-top: 1.5rem; max-width: 1280px; }
</style>""", unsafe_allow_html=True)

KEYS = list(examples.COLS)
ss = st.session_state
if "tables" not in ss:
    ss.tables = examples.load(next(iter(examples.MODELS)))
    ss.base = {k: v.copy() for k, v in ss.tables.items()}
    ss.name, ss.ver, ss.res, ss.sig, ss.pdf, ss.last = "Proyek Portal Edukasi", 0, None, None, None, None


def set_tables(tables, name):
    ss.tables, ss.name, ss.res, ss.pdf = tables, name, None, None
    ss.base = {k: v.copy() for k, v in tables.items()}
    ss.ver += 1


def current_model():
    model, errs = validation.to_model(ss.tables)
    if not errs:
        e, w = validation.validate(model)
        errs += e
    else:
        w = []
    return model, errs, w


def show_msgs(errs, warns=()):
    for e in errs: st.error(e, icon="⛔")
    for w in warns: st.warning(w, icon="⚠️")


# 2 Menu Utama
PAGES = ["🏗️ Perhitungan Portal 2D", "🚚 Simulasi Beban Bergerak"]

if "redirect_page" in ss:
    ss.nav_page = ss.pop("redirect_page")

if "nav_page" not in ss:
    ss.nav_page = PAGES[0]

page = st.sidebar.radio("Pilih Menu Utama", PAGES, key="nav_page")
st.sidebar.caption(f"Proyek aktif: **{ss.name}**")
st.sidebar.markdown("""
---
**Structura 2.0 (Edisi Pembelajaran)**
Aplikasi analisis struktur portal & balok 2D berbasis metode kekakuan langsung matriks komputasional.
""")

# ==============================================================================
# MENU 1: PERHITUNGAN STRUKTUR PORTAL 2D (Metode Matriks)
# ==============================================================================
if page.startswith("🏗️"):
    st.markdown("""
    <div class="hero">
        <h1>🏗️ Structura — Analisis Portal 2D</h1>
        <p>Aplikasi komputasi analisis struktur portal dan balok 2D dengan <b>Metode Kekakuan Langsung (Direct Stiffness Method)</b> yang transparan, interaktif, dan terverifikasi secara analitis.</p>
    </div>
    """, unsafe_allow_html=True)
    
    tab_dash, tab_input, tab_analisis, tab_laporan, tab_proyek = st.tabs([
        "🏠 Dashboard & Mulai Cepat",
        "📐 Input Model & Validasi",
        "🧮 Analisis, Transparansi & Hasil",
        "📄 Laporan Resmi PDF",
        "💾 Simpan / Buka Proyek"
    ])

    # ---------------- 1. Dashboard & Mulai Cepat ----------------
    with tab_dash:
        model, errs, warns = current_model()
        c = st.columns(5)
        c[0].metric("Jumlah Node", len(model["nodes"]))
        c[1].metric("Jumlah Elemen", len(model["members"]))
        c[2].metric("Titik Tumpuan", len(model["supports"]))
        c[3].metric("Total Beban", len(model["nodal_loads"]) + len(model["member_loads"]))
        c[4].metric("Status Analisis", "Selesai ✅" if ss.res else "Belum Dijalankan ⏳")
        st.write("")

        a, b = st.columns([1.1, 1])
        with a:
            st.markdown("#### 📚 Mulai Cepat & Pilihan Contoh Soal")
            kat_pilihan = st.selectbox("Kategori Soal", [
                "Semua Kategori",
                "🏢 Portal Gedung & Industri",
                "🌉 Jembatan & Balok Menerus",
                "📐 Kasus Khusus & Soal Ujian"
            ])
            if kat_pilihan.startswith("🏢"):
                filtered_models = [k for k in examples.MODELS if any(s in k for s in ["🏢", "🏭", "🏗️", "Portal"])]
            elif kat_pilihan.startswith("🌉"):
                filtered_models = [k for k in examples.MODELS if any(s in k for s in ["🌉", "Menerus", "Overhang"])]
            elif kat_pilihan.startswith("📐"):
                filtered_models = [k for k in examples.MODELS if any(s in k for s in ["📐", "Momen", "Kantilever", "Tangga", "Propped"])]
            else:
                filtered_models = list(examples.MODELS)

            ex = st.selectbox("Pilih Model Pembelajaran", filtered_models)
            x, y = st.columns(2)
            if x.button("Muat Contoh Soal", type="primary", use_container_width=True):
                set_tables(examples.load(ex), ex)
                st.rerun()
            if y.button("Buat Proyek Kosong", use_container_width=True):
                set_tables(examples.from_model({}), "Proyek Baru")
                st.rerun()

            st.markdown(r"""
            **💡 Alur Belajar Terstruktur:**
            1. **Input Geometri:** Atur koordinat node, dimensi balok/kolom ($b \times h$), dan beban.
            2. **Jalankan Solver:** Klik tombol analisis untuk merakit $[K]$ global dan menghitung perpindahan $\{u\}$.
            3. **Pelajari Transparansi:** Telusuri matriks kekakuan elemen, gaya jepit, dan interpretasi makna fisik.
            4. **Validasi & Ekspor:** Bandingkan dengan rumus tertutup dan cetak laporan PDF siap pakai.
            """)
        with b:
            if not errs and model["members"]:
                st.plotly_chart(plots.model_fig(model, "Pratinjau Geometri Model Aktif"), width="stretch", key="chart_dash_preview")
            else:
                show_msgs(errs, warns)

        with st.expander("📘 Landasan Teori & Formulasi Metode Kekakuan Langsung"):
            st.markdown(r"""
**1. Persamaan Kesetimbangan Global:**
$$\mathbf{K}\,\mathbf{u} = \mathbf{F}$$
Di mana $\mathbf{K}$ adalah matriks kekakuan struktur global ukuran $(3N \times 3N)$, $\mathbf{u}$ vektor perpindahan titik buhul, dan $\mathbf{F}$ vektor gaya luar ekivalen.

**2. Transformasi Koordinat Lokal ke Global:**
$$\mathbf{k}_{\text{global}} = \mathbf{T}^T\,\mathbf{k}_{\text{lokal}}\,\mathbf{T}$$
dengan matriks rotasi $\mathbf{T}$ yang memetakan derajat kebebasan lokal $(u_x', u_y', \theta_z')$ ke sumbu global $(u_x, u_y, \theta_z)$.

**3. Matriks Kekakuan Elemen Balok-Kolom (Euler-Bernoulli):**
$$\mathbf{k}_{\text{lokal}} = \begin{bmatrix}
EA/L & 0 & 0 & -EA/L & 0 & 0 \\
0 & 12EI/L^3 & 6EI/L^2 & 0 & -12EI/L^3 & 6EI/L^2 \\
0 & 6EI/L^2 & 4EI/L & 0 & -6EI/L^2 & 2EI/L \\
-EA/L & 0 & 0 & EA/L & 0 & 0 \\
0 & -12EI/L^3 & -6EI/L^2 & 0 & 12EI/L^3 & -6EI/L^2 \\
0 & 6EI/L^2 & 2EI/L & 0 & -6EI/L^2 & 4EI/L
\end{bmatrix}$$
""")

    # ---------------- 2. Input Model & Validasi ----------------
    with tab_input:
        st.subheader("📐 Input Geometri Struktur, Penampang, Tumpuan & Beban")
        L_col, R_col = st.columns([1.1, 1])
        cfg = st.column_config
        with L_col:
            ss.name = st.text_input("Nama Proyek / Kasus Analisis", ss.name, key="proj_name_input")
            t_sub = st.tabs(["1. Titik Node", "2. Elemen & Dimensi", "3. Kondisi Tumpuan", "4. Pembebanan"])
            ed = lambda k, **kw: st.data_editor(ss.base[k], key=f"ed_{k}_{ss.ver}", num_rows="dynamic", width="stretch", hide_index=True, **kw)
            
            with t_sub[0]:
                st.caption("Koordinat dalam meter (m). Pastikan tidak ada node ganda pada koordinat yang sama.")
                ss.tables["nodes"] = ed("nodes", column_config={
                    "id": cfg.NumberColumn("ID Node", step=1, required=True),
                    "x": cfg.NumberColumn("Posisi x (m)", format="%.3f", required=True),
                    "y": cfg.NumberColumn("Posisi y (m)", format="%.3f", required=True)
                })
            with t_sub[1]:
                st.caption("Penampang persegi b × h (mm). Beton bertulang ≈ 25.000 MPa, Baja struktural ≈ 200.000 MPa.")
                ss.tables["members"] = ed("members", column_config={
                    "id": cfg.NumberColumn("ID Elemen", step=1, required=True),
                    "ni": cfg.NumberColumn("Node Awal (i)", step=1, required=True),
                    "nj": cfg.NumberColumn("Node Akhir (j)", step=1, required=True),
                    "E": cfg.NumberColumn("Modulus E (MPa)", min_value=1.0, required=True),
                    "b": cfg.NumberColumn("Lebar b (mm)", min_value=1.0, required=True),
                    "h": cfg.NumberColumn("Tinggi h (mm)", min_value=1.0, required=True)
                })
            with t_sub[2]:
                st.caption("Centang derajat kebebasan yang tertahan: Jepit = Ux+Uy+Rz, Sendi = Ux+Uy, Rol = Uy.")
                ss.tables["supports"] = ed("supports", column_config={
                    "node": cfg.NumberColumn("Node", step=1, required=True),
                    "ux": cfg.CheckboxColumn("Tahan Ux (Horizontal)"),
                    "uy": cfg.CheckboxColumn("Tahan Uy (Vertikal)"),
                    "rz": cfg.CheckboxColumn("Tahan Rz (Momen/Rotasi)")
                })
            with t_sub[3]:
                st.markdown("**A. Beban Pada Titik Buhul (Nodal Loads):**")
                ss.tables["nodal_loads"] = ed("nodal_loads", column_config={
                    "node": cfg.NumberColumn("Node", step=1, required=True),
                    "Fx": cfg.NumberColumn("Fx (kN) [+ : Kanan]", format="%.2f"),
                    "Fy": cfg.NumberColumn("Fy (kN) [+ : Atas]", format="%.2f"),
                    "M": cfg.NumberColumn("Momen M (kN·m) [+ : Berlawanan Jarum Jam]", format="%.2f")
                })
                st.markdown("**B. Beban Pada Bentang Elemen (Member Loads):**")
                ss.tables["member_loads"] = ed("member_loads", column_config={
                    "member": cfg.NumberColumn("Elemen", step=1, required=True),
                    "type": cfg.SelectboxColumn("Jenis Beban", options=["UDL", "Titik"], default="UDL"),
                    "dir": cfg.SelectboxColumn("Arah Gaya", options=["Gravitasi", "Lokal-y", "Lokal-x"], default="Gravitasi"),
                    "value": cfg.NumberColumn("Besar Beban (kN/m atau kN)", format="%.2f"),
                    "a": cfg.NumberColumn("Jarak a dari Node i (m) [khusus Beban Titik]", format="%.3f")
                })
        with R_col:
            model, errs, warns = current_model()
            st.markdown("#### 🔍 Status Validasi Geometri & Keamanan Input")
            if errs:
                st.error(f"Ditemukan {len(errs)} kesalahan data yang harus diperbaiki sebelum analisis dapat dijalankan:", icon="⛔")
                for e in errs: st.markdown(f"- ❌ {e}")
            elif warns:
                st.warning(f"Peringatan kelayakan model ({len(warns)} catatan):", icon="⚠️")
                for w in warns: st.markdown(f"- ⚠️ {w}")
                st.success("Model stabil dan memenuhi syarat untuk dianalisis ✅")
            else:
                st.success("Model valid, tumpuan stabil (≥ 3 reaksi), dan siap dianalisis! ✅")

            if model["members"] and not errs:
                st.plotly_chart(plots.model_fig(model), width="stretch", key="chart_input_preview")
            elif not errs:
                st.info("Tambahkan data node dan elemen untuk memunculkan pratinjau struktur.")

    # ---------------- 3. Analisis, Transparansi & Hasil ----------------
    with tab_analisis:
        st.subheader("🧮 Solusi Komputasi, Transparansi Matriks & Interpretasi Rekayasa")
        model, errs, warns = current_model()
        show_msgs(errs, warns)

        c_run1, c_run2 = st.columns([1, 3])
        with c_run1:
            if st.button("▶ Jalankan Analisis Matriks", type="primary", disabled=bool(errs), key="btn_run_analysis", use_container_width=True):
                try:
                    ss.res = engine.analyze(model)
                    ss.sig = json.dumps(model, sort_keys=True, default=float)
                    ss.pdf = None
                    st.toast("Analisis struktur berhasil dihitung!", icon="🎉")
                except engine.ModelError as e:
                    ss.res = None
                    st.error(str(e), icon="⛔")

        res = ss.res
        if res is not None and ss.sig != json.dumps(model, sort_keys=True, default=float):
            st.warning("Data model telah berubah sejak perhitungan terakhir. Klik 'Jalankan Analisis Matriks' untuk memperbarui hasil.", icon="⚠️")

        if res is not None:
            tb = engine.tables(res)
            u = res["u"]
            ext = tb["ext"]

            # Key Summary Cards
            c = st.columns(4)
            c[0].metric("Lendutan Maks. |Uy|", f"{abs(u[1::3]).max()*1e3:.3f} mm")
            c[1].metric("Pergeseran Horiz. |Ux|", f"{abs(u[0::3]).max()*1e3:.3f} mm")
            c[2].metric("Gaya Geser Maks. |V|", f"{ext['|V| maks (kN)'].max():.2f} kN")
            c[3].metric("Momen Lentur Kritis |M|", f"{max(ext['M maks + (kN·m)'].max(), -ext['M maks − (kN·m)'].min()):.2f} kN·m")

            sub_tabs = st.tabs([
                "📊 Visualisasi Diagram",
                "📈 Bentuk Deformasi",
                "🧠 Makna & Interpretasi Hasil",
                "🔍 Transparansi Langkah Matriks",
                "📋 Tabel Lengkap Hasil",
                "⚖️ Verifikasi & Benchmark"
            ])

            # Sub-Tab 1: Visualisasi Diagram N, V, M
            with sub_tabs[0]:
                diag_type = st.radio("Pilih Diagram Gaya Dalam:", ["Momen Lentur (M)", "Gaya Geser (V)", "Gaya Aksial (N)"], horizontal=True)
                kind_code = "M" if "Momen" in diag_type else ("V" if "Geser" in diag_type else "N")
                st.plotly_chart(plots.diagram_fig(res, kind_code), width="stretch", key=f"chart_diag_{kind_code}")
                st.caption("ℹ️ **Petunjuk Gambar:** Angka pada diagram menunjukkan nilai gaya dalam pada ujung batang serta nilai puncak ekstrem.")

            # Sub-Tab 2: Bentuk Deformasi
            with sub_tabs[1]:
                f = st.slider("Faktor Pengali Skala Deformasi (Visual)", 0.1, 5.0, 1.0, 0.1, key="slider_def_f")
                st.plotly_chart(plots.deformed_fig(res, f), width="stretch", key="chart_deformed")
                st.caption("Garis putus-putus abu-abu = konfigurasi struktur mula-mula. Garis merah = bentuk deformasi elastis terperbesar.")

            # Sub-Tab 3: Makna & Interpretasi Rekayasa Otomatis
            with sub_tabs[2]:
                st.markdown("#### 🧠 Interpretasi Rekayasa Struktur Otomatis (*Engineering Insights*)")
                st.write("Penjelasan otomatis terhadap makna fisik dari angka-angka hasil analisis struktur:")
                insight_list = insights.generate_engineering_insights(res)
                for ins in insight_list:
                    st.markdown(f"""
                    <div class="insight-box {ins['status']}">
                        <div class="insight-title">{ins['ikon']} {ins['kategori']} — {ins['ringkasan']}</div>
                        <div class="insight-desc">{ins['detail']}</div>
                    </div>
                    """, unsafe_allow_html=True)

            # Sub-Tab 4: Transparansi Langkah Matriks
            with sub_tabs[3]:
                st.markdown("#### 🔍 Transparansi Tahapan Komputasi Metode Kekakuan Langsung")
                calc_info = insights.generate_calculation_steps(res)
                st.markdown(f"""
                Analisis diselesaikan melalui sistem persamaan linear matriks:
                $$\\mathbf{K}_{{ff}} \\cdot \\mathbf{u}_f = \\mathbf{F}_f$$
                - **Total Derajat Kebebasan (DOF):** {calc_info['total_dof']} DOF
                - **DOF Bebas (Bergerak):** {calc_info['free_dof']} DOF
                - **DOF Tertahan (Reaksi Tumpuan):** {calc_info['restrained_dof']} DOF
                """)
                st.markdown("**1. Properti Kekakuan Lokal Elemen ($EA/L, 12EI/L^3, 6EI/L^2, 4EI/L$):**")
                st.dataframe(calc_info["df_elem"], hide_index=True, width="stretch")

                st.markdown("**2. Pemetaan Status Derajat Kebebasan (DOF) per Titik Buhul:**")
                st.dataframe(calc_info["df_dof"], hide_index=True, width="stretch")

                if not calc_info["df_fe"].empty and "f1 (N_i)" in calc_info["df_fe"].columns:
                    st.markdown("**3. Vektor Gaya Ujung Jepit Elemen (Fixed End Forces $\\mathbf{f}_e$):**")
                    st.dataframe(calc_info["df_fe"], hide_index=True, width="stretch")

            # Sub-Tab 5: Tabel Lengkap
            with sub_tabs[4]:
                fmt = lambda df: {col: st.column_config.NumberColumn(col, format="%.6f" if "rad" in col else "%.4f") for col in df.columns if col not in ("Node", "Elemen")}
                for title, k in (("Perpindahan Titik Buhul (Node Displacements)", "disp"),
                                  ("Gaya Reaksi Tumpuan (Support Reactions)", "reac"),
                                  ("Gaya-Gaya Dalam Ujung Elemen (Member End Actions)", "forces"),
                                  ("Nilai Ekstrem Gaya Dalam per Elemen", "ext")):
                    st.markdown(f"**{title}**")
                    st.dataframe(tb[k], hide_index=True, width="stretch", column_config=fmt(tb[k]))
                st.caption("Konvensi: N tarik (+) · V (+) bila gaya kiri-potongan ke atas · M sagging (+) digambar di sisi serat tarik.")

            # Sub-Tab 6: Verifikasi & Benchmark
            with sub_tabs[5]:
                st.markdown("#### ⚖️ Validasi Kesetimbangan & Pembandingan Solusi")
                eq = res["equilibrium"]
                ok = max(abs(eq["SFx"]), abs(eq["SFy"]), abs(eq["SM"])) < 1e-5
                
                col_eq1, col_eq2 = st.columns(2)
                with col_eq1:
                    st.markdown("**Pemeriksaan Keseimbangan Statika Global:**")
                    st.markdown(f"- $\\sum F_x$ (Beban + Reaksi) = `{eq['SFx']:.3e}` kN")
                    st.markdown(f"- $\\sum F_y$ (Beban + Reaksi) = `{eq['SFy']:.3e}` kN")
                    st.markdown(f"- $\\sum M$ (Titik Asal O) = `{eq['SM']:.3e}` kN·m")
                    st.markdown(f"- Residu Solusi Matriks ($|K \\cdot u - F|$) = `{res['residual']:.3e}`")
                    if ok:
                        st.success("Keseimbangan Statika Global Terpenuhi Sempurna ✅")
                    else:
                        st.error("Keseimbangan tidak terpenuhi — periksa model ⚠️")
                with col_eq2:
                    st.markdown("**Pembandingan Terhadap Solusi Teoritis Tertutup:**")
                    bench_df = insights.compare_with_benchmarks(res)
                    st.dataframe(bench_df, hide_index=True, width="stretch")
                    st.caption("Perbandingan ini membuktikan ketepatan matematis formulasi matriks terhadap mekanika analitis.")

    # ---------------- 4. Laporan Resmi PDF ----------------
    with tab_laporan:
        st.subheader("📄 Laporan Resmi Analisis Struktur (Format PDF)")
        st.write("Cetak dokumen laporan komprehensif yang memuat asumsi, data penampang, transparansi tahapan perhitungan, interpretasi rekayasa, tabel hasil, dan seluruh diagram gaya dalam.")
        if ss.res is None:
            st.info("Jalankan analisis terlebih dahulu pada tab *Analisis, Transparansi & Hasil* sebelum membuat laporan.")
        else:
            if st.button("Buat Laporan Resmi PDF Lengkap", type="primary", key="btn_build_pdf"):
                with st.spinner("Menyusun laporan PDF beserta gambar vektor dan tabel matriks..."):
                    ss.pdf = report.build_pdf(ss.name, ss.res["model"], ss.res)
            if ss.pdf:
                st.success("Laporan PDF berhasil dibuat dan siap diunduh!")
                st.download_button(
                    "⬇ Unduh Berkas Laporan PDF",
                    ss.pdf,
                    file_name=f"Laporan_Structura_{ss.name.replace(' ', '_')}.pdf",
                    mime="application/pdf",
                    key="btn_download_pdf"
                )

    # ---------------- 5. Simpan / Buka Proyek ----------------
    with tab_proyek:
        st.subheader("💾 Manajemen Database Proyek Struktur")
        a_col, b_col = st.columns(2)
        with a_col:
            st.markdown("#### Simpan Proyek Aktif")
            p_name = st.text_input("Nama Proyek Simpan", ss.name, key="savename_tab")
            if st.button("Simpan ke Database Lokal", type="primary", disabled=not p_name.strip(), key="btn_save_proj"):
                model, errs = validation.to_model(ss.tables)
                storage.save_project(p_name.strip(), model)
                ss.name = p_name.strip()
                st.success(f"Proyek '{p_name}' berhasil disimpan ke database!")
        with b_col:
            st.markdown("#### Buka / Kelola Proyek Tersimpan")
            rows = storage.list_projects()
            if not rows:
                st.info("Belum ada proyek yang tersimpan di database.")
            else:
                sel = st.selectbox("Pilih Proyek", [r[0] for r in rows], format_func=lambda n: f"{n}  ({dict(rows)[n]})", key="select_load_proj")
                x_b, y_b = st.columns(2)
                if x_b.button("Buka Proyek Ini", width="stretch", key="btn_open_proj"):
                    set_tables(examples.from_model(storage.load_project(sel)), sel)
                    st.success(f"Proyek '{sel}' dibuka.")
                    st.rerun()
                if y_b.button("Hapus", width="stretch", key="btn_del_proj"):
                    storage.delete_project(sel)
                    st.rerun()

# ==============================================================================
# MENU 2: SIMULASI BEBAN BERGERAK (INTERAKTIF DRAG & DROP)
# ==============================================================================
else:
    st.markdown("""
    <div class="hero">
        <h1>🚚 Simulasi Beban Bergerak</h1>
        <p>Visualisasi interaktif jembatan balok — seret truk langsung dengan kursor, amati reaksi dinamis R₁ & R₂, dan pertumbuhan kurva momen lentur real-time.</p>
    </div>
    """, unsafe_allow_html=True)
    
    ctrl1, ctrl2, ctrl3, ctrl4 = st.columns([1.5, 1, 1, 1])
    preset = ctrl1.selectbox("Pilihan Skenario Kendaraan", [
        "🎯 Truk Standar (L=20m, P=100kN)",
        "🚛 Truk Standar Bina Marga BM-100 (L=25m, P=100kN)",
        "🚚 Truk AASHTO HS-20 (L=30m, P=145kN)",
        "🚗 Mobil Ringan (L=15m, P=25kN)",
        "⚙️ Kustom Sendiri"
    ])
    
    def_L, def_P, def_x = 20.0, 100.0, 4.6
    if "Bina Marga" in preset: def_L, def_P, def_x = 25.0, 100.0, 6.0
    elif "AASHTO" in preset: def_L, def_P, def_x = 30.0, 145.0, 8.0
    elif "Mobil" in preset: def_L, def_P, def_x = 15.0, 25.0, 3.5
    
    L_val = ctrl2.number_input("Bentang Jembatan L (m)", min_value=5.0, max_value=100.0, value=def_L, step=1.0)
    P_val = ctrl3.number_input("Beban Truk P (kN)", min_value=5.0, max_value=1000.0, value=def_P, step=5.0)
    x_val = ctrl4.slider("Posisi Truk x (m)", min_value=0.0, max_value=float(L_val), value=min(float(def_x), float(L_val)), step=0.1)

    sim_html = moving_load.render_moving_load_html(L=L_val, P=P_val, initial_x=x_val)
    components.html(sim_html, height=580, scrolling=False)
    
    r1, r2 = moving_load.reactions(L_val, P_val, x_val)
    m_curr = moving_load.moment_under_load(L_val, P_val, x_val)
    m_max_abs = (P_val * L_val) / 4.0
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Reaksi Kiri R₁", f"{r1:.2f} kN", delta=f"{r1/P_val*100:.1f}% P")
    c2.metric("Reaksi Kanan R₂", f"{r2:.2f} kN", delta=f"{r2/P_val*100:.1f}% P")
    c3.metric("Momen di Bawah Beban M(x)", f"{m_curr:.2f} kN·m")
    c4.metric("Momen Maks. Absolut (x=L/2)", f"{m_max_abs:.2f} kN·m", help="Terjadi saat beban tepat di tengah bentang")
    
    mv_tabs = st.tabs([
        "📊 Bidang Momen (BMD) & Geser (SFD)",
        "📈 Garis Pengaruh (Influence Line)",
        "🚀 Ekspor ke Solver Matriks Structura",
        "📘 Penjelasan Teori & Rumus"
    ])
    
    with mv_tabs[0]:
        st.caption("Diagram gaya dalam seketika di sepanjang bentang balok untuk posisi truk saat ini.")
        col_bmd, col_sfd = st.columns(2)
        with col_bmd:
            st.plotly_chart(moving_load.plotly_diagrams_figure(L_val, P_val, x_val), width="stretch", key="chart_mv_bmd")
        with col_sfd:
            st.plotly_chart(moving_load.plotly_sfd_figure(L_val, P_val, x_val), width="stretch", key="chart_mv_sfd")
            
    with mv_tabs[1]:
        st.markdown("#### Garis Pengaruh (Influence Line)")
        st.caption("Garis pengaruh menunjukkan variasi nilai reaksi, gaya geser, atau momen pada potongan tertentu.")
        sec_c = st.slider("Titik Potongan Tinjauan c (m)", 0.0, float(L_val), float(L_val)/2.0, 0.5)
        xs_il, il_r1, il_r2, il_vc, il_mc = moving_load.influence_lines(L_val, sec_c)
        
        il_fig = go.Figure()
        il_fig.add_trace(go.Scatter(x=xs_il, y=il_r1, mode="lines", name="GP Reaksi R₁", line=dict(color="#2563eb", width=2.5)))
        il_fig.add_trace(go.Scatter(x=xs_il, y=il_r2, mode="lines", name="GP Reaksi R₂", line=dict(color="#7c3aed", width=2.5)))
        il_fig.add_trace(go.Scatter(x=xs_il, y=il_mc, mode="lines", name=f"GP Momen di c={sec_c:.1f}m", line=dict(color="#1971c2", width=3, dash="dash")))
        il_fig.update_layout(title=f"Garis Pengaruh untuk Potongan c = {sec_c:.1f} m", xaxis_title="Posisi Beban Satuan x (m)", yaxis_title="Nilai Pengaruh", height=380, hovermode="x unified")
        st.plotly_chart(il_fig, width="stretch", key="chart_mv_il")
        
    with mv_tabs[2]:
        st.markdown("#### Integrasi dengan Mesin Analisis Matriks Structura")
        st.write("Konversi model jembatan ini menjadi model diskrit portal/balok 2D untuk dianalisis dengan metode kekakuan langsung ($K \\cdot u = F$).")
        n_elem = st.slider("Jumlah Elemen Diskrit", min_value=4, max_value=40, value=10, step=2)
        if st.button("🚀 Kirim ke Solver Matriks Structura", type="primary"):
            new_model = moving_load.to_structura_model(L=L_val, P=P_val, x=x_val, num_elements=n_elem)
            new_tables = examples.from_model(new_model)
            set_tables(new_tables, f"Jembatan L={L_val:.0f}m (Truk x={x_val:.1f}m, P={P_val:.0f}kN)")
            ss.redirect_page = "🏗️ Perhitungan Portal 2D"
            st.success("Model berhasil dikonversi dan dialihkan ke menu Perhitungan Portal 2D!")
            st.rerun()
            
    with mv_tabs[3]:
        st.markdown(r"""
### 📘 Dasar Teori Beban Bergerak pada Jembatan Sederhana
Pada balok sederhana di atas tumpuan sendi (kiri, $x=0$) dan rol (kanan, $x=L$) yang dilewati beban titik bergerak $P$ pada koordinat $x$:

#### 1. Keseimbangan Statika & Reaksi Tumpuan
$$R_1(x) = \frac{P\,(L - x)}{L}, \quad R_2(x) = \frac{P\,x}{L}, \quad R_1 + R_2 = P$$

#### 2. Momen Lentur di Bawah Beban
$$M(x) = R_1(x) \cdot x = \frac{P\,x\,(L - x)}{L}$$

#### 3. Momen Maksimum Absolut
Terjadi saat beban berada tepat di tengah bentang ($x = L/2$):
$$M_{\max} = \frac{P \cdot L}{4}$$
""")
