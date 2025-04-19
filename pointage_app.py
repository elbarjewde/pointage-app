
import streamlit as st
import sqlite3
from datetime import datetime
import pandas as pd

st.set_page_config(page_title="تسجيل الحضور", layout="centered")

# إنشاء قاعدة البيانات
conn = sqlite3.connect("pointage.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS pointage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT,
    telephone TEXT,
    fonction TEXT,
    secteur TEXT,
    action TEXT,
    datetime TEXT,
    latitude TEXT,
    longitude TEXT
)
""")
conn.commit()

st.title("تسجيل الحضور اليومي")

st.components.v1.html("""
<script src="geolocation.js"></script>
""")

with st.form("pointage_form"):
    nom = st.text_input("الاسم الكامل")
    telephone = st.text_input("رقم الهاتف")
    fonction = st.text_input("الوظيفة")
    secteur = st.text_input("القطاع")
    action = st.radio("اختر العملية", ["دخول", "خروج"])
    location = st.text_input("الموقع الجغرافي (سيُملأ تلقائيًا)", disabled=True)
    
    submit = st.form_submit_button("تسجيل")

    if submit:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        latitude = st.session_state.get("latitude", "")
        longitude = st.session_state.get("longitude", "")
        
        if not all([nom, telephone, fonction, secteur]):
            st.warning("يرجى ملء جميع الحقول.")
        elif not latitude or not longitude:
            st.warning("تعذر الحصول على الموقع الجغرافي. يرجى إعادة تحميل الصفحة والسماح بالموقع.")
        else:
            cursor.execute("INSERT INTO pointage (nom, telephone, fonction, secteur, action, datetime, latitude, longitude) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (nom, telephone, fonction, secteur, action, now, latitude, longitude))
            conn.commit()
            st.success(f"تم تسجيل {action} بنجاح!")

# عرض السجلات (للمدير أو المشرف)
with st.expander("عرض كافة التسجيلات"):
    data = pd.read_sql("SELECT * FROM pointage ORDER BY datetime DESC", conn)
    st.dataframe(data)
    st.download_button("تحميل Excel", data.to_csv(index=False), file_name="pointage.csv")
