import streamlit as st
import sqlite3
import datetime
import streamlit.components.v1 as components

# إعداد اللغة
lang = st.sidebar.selectbox("Langue / اللغة", ["Français", "العربية"])

texts = {
    "Français": {
        "title": "Application de pointage",
        "full_name": "Nom complet",
        "position": "Poste",
        "department": "Département",
        "start_time": "Heure de début (HH:MM)",
        "end_time": "Heure de fin (HH:MM)",
        "submit": "Enregistrer",
        "location_error": "Vous devez être au lieu de travail pour pointer.",
        "success": "Pointage enregistré avec succès."
    },
    "العربية": {
        "title": "تطبيق تسجيل الحضور",
        "full_name": "الاسم الكامل",
        "position": "الوظيفة",
        "department": "القطاع",
        "start_time": "وقت بداية الدوام (ساعة:دقيقة)",
        "end_time": "وقت نهاية الدوام (ساعة:دقيقة)",
        "submit": "تسجيل",
        "location_error": "يجب أن تكون في مكان العمل لتسجيل الحضور.",
        "success": "تم تسجيل الحضور بنجاح."
    }
}

selected_texts = texts[lang]

st.title(selected_texts["title"])

# معلومات الإدخال
name = st.text_input(selected_texts["full_name"])
position = st.text_input(selected_texts["position"])
department = st.text_input(selected_texts["department"])

# إدخال الوقت على شكل (ساعة:دقيقة)
start_time_input = st.text_input(selected_texts["start_time"], "08:00")
end_time_input = st.text_input(selected_texts["end_time"], "16:00")

# تحقق من أن المدخلات هي في تنسيق الوقت الصحيح
def parse_time(time_str):
    try:
        return datetime.datetime.strptime(time_str, "%H:%M").time()
    except ValueError:
        st.error("يرجى إدخال الوقت بالتنسيق الصحيح (ساعة:دقيقة).")
        return None

start_time = parse_time(start_time_input)
end_time = parse_time(end_time_input)

# إضافة كود JavaScript لتحديد الموقع تلقائيًا عند فتح الصفحة
components.html("""
<script>
navigator.geolocation.getCurrentPosition(
  (position) => {
    const coords = position.coords.latitude + "," + position.coords.longitude;
    const input = window.parent.document.querySelector('input[data-testid="stTextInput"]');
    if (input) input.value = coords;
    const event = new Event("input", { bubbles: true });
    input.dispatchEvent(event);
  },
  (error) => {
    alert("خطأ في تحديد الموقع: " + error.message);
  }
);
</script>
""", height=0)

location = st.text_input("Location (auto-filled)", key="location")

# الموقع المسموح به
allowed_lat = 18.0679325
allowed_lon = -15.9618329
allowed_distance = 0.2  # بالكيلومتر

def calculate_distance(lat1, lon1, lat2, lon2):
    from math import radians, cos, sin, sqrt, atan2
    R = 6371
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return R * c

# التحقق من تنسيق الموقع
def validate_location(location):
    try:
        lat, lon = map(float, location.split(","))
        return lat, lon
    except ValueError:
        st.error("خطأ في تنسيق الموقع. تأكد من إدخال الإحداثيات بالشكل الصحيح (مثال: 18.0678770,-15.9618574).")
        return None, None

if st.button(selected_texts["submit"]):
    if start_time and end_time:
        lat, lon = validate_location(location)
        if lat and lon:
            distance = calculate_distance(lat, lon, allowed_lat, allowed_lon)

            if distance <= allowed_distance:
                conn = sqlite3.connect("pointage.db")
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS pointage (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT,
                        position TEXT,
                        department TEXT,
                        start_time TEXT,
                        end_time TEXT,
                        date TEXT,
                        location TEXT
                    )
                """)
                cursor.execute("INSERT INTO pointage (name, position, department, start_time, end_time, date, location) VALUES (?, ?, ?, ?, ?, ?, ?)",
                               (name, position, department, str(start_time), str(end_time), str(datetime.date.today()), location))
                conn.commit()
                conn.close()
                st.success(selected_texts["success"])
            else:
                st.error(selected_texts["location_error"])
