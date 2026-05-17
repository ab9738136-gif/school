from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

app = Flask(__name__)
app.secret_key = 'ssm_super_secure_key_2026'
DB_NAME = 'school_v2.db'

ADMIN_USER = 'admin'
ADMIN_PASSWORD_HASH = generate_password_hash('ssm@2026')

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # एडमिशन टेबल
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL, father_name TEXT NOT NULL, mother_name TEXT NOT NULL,
            dob TEXT NOT NULL, class_name TEXT NOT NULL, aadhaar TEXT NOT NULL,
            mobile TEXT NOT NULL, address TEXT NOT NULL
        )
    ''')
    # रिजल्ट टेबल
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS results (
            roll_no TEXT PRIMARY KEY, name TEXT NOT NULL, class_name TEXT NOT NULL,
            hindi INT, english INT, math INT, science INT, total INT, status TEXT
        )
    ''')
    # 🛡️ नई टेबल: फीडबैक और शिकायत बॉक्स
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS queries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            parent_name TEXT NOT NULL,
            mobile TEXT NOT NULL,
            msg_type TEXT NOT NULL,
            message TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def home(): return render_template('index.html')

@app.route('/about')
def about(): return render_template('about.html')

@app.route('/gallery')
def gallery(): return render_template('gallery.html')

@app.route('/rules')
def rules(): return render_template('rules.html')

@app.route('/teachers')
def teachers(): return render_template('teachers.html')

@app.route('/vandana')
def vandana(): return render_template('vandana.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        data = (
            request.form.get('name'), request.form.get('father_name'),
            request.form.get('mother_name'), request.form.get('dob'),
            request.form.get('class_name'), request.form.get('aadhaar'),
            request.form.get('mobile'), request.form.get('address')
        )
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO admissions (name, father_name, mother_name, dob, class_name, aadhaar, mobile, address) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', data)
        conn.commit()
        conn.close()
        return "<h1>🚩 प्रवेश आवेदन सफलतापूर्वक पंजीकृत हो गया है!</h1><a href='/'>होम पेज पर जाएं</a>"
    return render_template('contact.html')

@app.route('/result', methods=['GET', 'POST'])
def check_result():
    student_result = None
    error_msg = None
    if request.method == 'POST':
        roll_no = request.form.get('roll_no')
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM results WHERE roll_no = ?', (roll_no,))
        student_result = cursor.fetchone()
        conn.close()
        if not student_result:
            error_msg = "दर्ज किया गया रोल नंबर रिकॉर्ड में नहीं मिला।"
    return render_template('result.html', result=student_result, error=error_msg)

# 🛡️ फीडबैक/शिकायत सबमिट करने का रूट
@app.route('/submit_query', methods=['POST'])
def submit_query():
    p_name = request.form.get('parent_name')
    mobile = request.form.get('mobile')
    msg_type = request.form.get('msg_type')
    message = request.form.get('message')
    
    # डेटाबेस में सेव करें
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO queries (parent_name, mobile, msg_type, message) VALUES (?, ?, ?, ?)', (p_name, mobile, msg_type, message))
    conn.commit()
    conn.close()
    
    # व्हाट्सएप के लिए मैसेज तैयार करना
    whatsapp_text = f"🚩 *सरस्वती शिशु मंदिर फीडबैक* 🚩\n\n*अभिभावक:* {p_name}\n*मोबाइल:* {mobile}\n*प्रकार:* {msg_type}\n*संदेश:* {message}"
    import urllib.parse
    encoded_text = urllib.parse.quote(whatsapp_text)
    
    # स्कूल का व्हाट्सएप नंबर (यहाँ प्रधानाचार्य जी का असली नंबर डाल सकते हैं)
    school_whatsapp = "919415XXXXXX" 
    
    # अभिभावक को व्हाट्सएप पर रीडायरेक्ट करने के लिए सफलता संदेश पेज
    return f'''
    <div style="text-align:center; margin-top:100px; font-family:sans-serif;">
        <h1>🚩 आपका संदेश वेबसाइट डेटाबेस में सुरक्षित सेव हो गया है!</h1>
        <p>प्रधानाचार्य जी को सीधे सूचित करने के लिए नीचे दिए गए बटन पर क्लिक करें।</p>
        <br>
        <a href="https://wa.me{school_whatsapp}?text={encoded_text}" target="_blank" style="background:#25D366; color:white; padding:12px 25px; text-decoration:none; font-weight:bold; border-radius:5px; font-size:18px;">
            💬 व्हाट्सएप द्वारा प्रधानाचार्य जी को भेजें
        </a>
        <br><br><br>
        <a href="/">होम पेज पर वापस जाएं</a>
    </div>
    '''

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == ADMIN_USER and check_password_hash(ADMIN_PASSWORD_HASH, password):
            session['logged_in'] = True
            return redirect(url_for('admin_panel'))
        else:
            error = 'गलत यूज़रनेम या密码! दोबारा प्रयास करें।'
    return render_template('login.html', error=error)

@app.route('/admin', methods=['GET', 'POST'])
def admin_panel():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
        
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    if request.method == 'POST' and 'add_result' in request.form:
        roll = request.form.get('roll_no')
        r_name = request.form.get('name')
        r_class = request.form.get('class_name')
        h = int(request.form.get('hindi', 0))
        e = int(request.form.get('english', 0))
        m = int(request.form.get('math', 0))
        s = int(request.form.get('science', 0))
        total = h + e + m + s
        status = 'पास' if total >= 132 else 'फेल'
        try:
            cursor.execute('INSERT OR REPLACE INTO results VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', (roll, r_name, r_class, h, e, m, s, total, status))
            conn.commit()
        except Exception as msg:
            print("Error adding result:", msg)

    cursor.execute('SELECT COUNT(*) FROM admissions')
    total_admissions = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(*) FROM results')
    total_results = cursor.fetchone()[0]
    # शिकायतों की कुल गिनती
    cursor.execute('SELECT COUNT(*) FROM queries')
    total_queries = cursor.fetchone()[0]

    cursor.execute('SELECT * FROM admissions')
    all_students = cursor.fetchall()
    
    # सभी शिकायतों की लिस्ट एडमिन पैनल के लिए निकालना
    cursor.execute('SELECT * FROM queries')
    all_queries = cursor.fetchall()
    conn.close()
    
    return render_template('admin.html', students=all_students, queries=all_queries, count_adm=total_admissions, count_res=total_results, count_que=total_queries)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
