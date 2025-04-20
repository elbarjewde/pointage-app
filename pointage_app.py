import streamlit as st
import sqlite3
import datetime

# كلمات المرور للمشرفين والموظفين
supervisor_password = "#SAMU@101@"
employee_password = "SAMU 101"

# إعداد اللغة
lang = st.sidebar.selectbox("Langue / اللغة", ["Français", "العربية"])

texts = {
    "Français": {
        "title": "Panneau de gestion du superviseur",
        "employee_name": "Nom de l'employé",
        "location": "Emplacement géographique de l'employé",
        "submit": "Ajouter l'emplacement",
        "location_added": "Emplacement ajouté avec succès.",
        "view_attendance": "Voir les présences",
        "view_location_error": "Aucun emplacement n'a été trouvé pour cet employé.",
        "password": "Mot de passe"
    },
    "العربية": {
        "title": "لوحة تحكم المشرف",
        "employee_name": "اسم الموظف",
        "location": "الموقع الجغرافي للموظف",
        "submit": "إضافة الموقع",
        "location_added": "تم إضافة الموقع بنجاح.",
        "view_attendance": "عرض سجلات الحضور",
        "view_location_error": "لم يتم العثور على موقع لهذا الموظف.",
        "password": "كلمة المرور"
    }
}

selected_texts = texts[lang]

# شاشة إدخال كلمة المرور
password = st.text_input(selected_texts["password"], type="password")

if st.button("دخول كمشرف / Log in as Supervisor"):
    if password == supervisor_password:
        st.title(selected_texts["title"])
        # إدارة مواقع الموظفين
        employee_name = st.text_input(selected_texts["employee_name"])
        employee_location = st.text_input(selected_texts["location"])

        if st.button(selected_texts["submit"]):
            if employee_name and employee_location:
                conn = sqlite3.connect("pointage.db")
                cursor = conn.cursor()
                cursor.execute("CREATE TABLE IF NOT EXISTS employee_locations (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, location TEXT)")
                cursor.execute("INSERT INTO employee_locations (name, location) VALUES (?, ?)", (employee_name, employee_location))
                conn.commit()
                conn.close()
                st.success(selected_texts["location_added"])

        # عرض سجلات الحضور
        if st.button(selected_texts["view_attendance"]):
            conn = sqlite3.connect("pointage.db")
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM pointage")
            records = cursor.fetchall()
            conn.close()

            if records:
                st.write("Sujets présents:")
                for record in records:
                    st.write(f"Nom: {record[1]}, Date: {record[7]}, Heure de début: {record[5]}, Heure de fin: {record[6]}, Emplacement: {record[8]}")
            else:
                st.warning(selected_texts["view_location_error"])

    else:
        st.error("كلمة المرور غير صحيحة للمشرف / Incorrect password for Supervisor")

# شاشة إدخال كلمة مرور الموظف
if st.button("دخول كموظف / Log in as Employee"):
    employee_password_input = st.text_input("كلمة مرور الموظف / Employee password", type="password")
    
    if employee_password_input == employee_password:
        # معلومات الإدخال للموظف
        name = st.text_input(selected_texts["full_name"])
        phone_number = st.text_input(selected_texts["phone_number"])
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
                                phone_number TEXT,
                                position TEXT,
                                department TEXT,
                                start_time TEXT,
                                end_time TEXT,
                                date TEXT,
                                location TEXT
                            )
                        """)
                        cursor.execute("INSERT INTO pointage (name, phone_number, position, department, start_time, end_time, date, location) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                                       (name, phone_number, position, department, str(start_time), str(end_time), str(datetime.date.today()), location))
                        conn.commit()
                        conn.close()
                        st.success(selected_texts["success"])
                    else:
                        st.error(selected_texts["location_error"])
    else:
        st.error("كلمة المرور غير صحيحة للموظف / Incorrect password for Employee")
