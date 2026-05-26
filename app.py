from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3

app = Flask(__name__, static_folder=".", static_url_path="")
CORS(app)

# ================= DATABASE =================

def koneksi():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

# ================= BUAT TABLE =================

conn = koneksi()
c = conn.cursor()

# users
c.execute("""
CREATE TABLE IF NOT EXISTS users(
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 username TEXT,
 password TEXT,
 role TEXT
)
""")

# siswa
c.execute("""
CREATE TABLE IF NOT EXISTS siswa(
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 nis TEXT,
 nama TEXT,
 kelas TEXT,
 wali_kelas TEXT,
 orang_tua TEXT
)
""")

# guru
c.execute("""
CREATE TABLE IF NOT EXISTS guru(
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 nip TEXT,
 nama TEXT,
 mapel TEXT,
 alamat TEXT
)
""")

# jadwal
c.execute("""
CREATE TABLE IF NOT EXISTS jadwal(
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 kelas TEXT,
 mapel TEXT,
 guru TEXT,
 hari TEXT,
 jam TEXT
)
""")

# presensi siswa
c.execute("""
CREATE TABLE IF NOT EXISTS presensi(
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 nis TEXT,
 nama TEXT,
 status TEXT
)
""")

# presensi guru
c.execute("""
CREATE TABLE IF NOT EXISTS presensi_guru(
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 nip TEXT,
 nama TEXT,
 status TEXT
)
""")

# pembayaran
c.execute("""
CREATE TABLE IF NOT EXISTS pembayaran(
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 nis TEXT,
 nama TEXT,
 jumlah TEXT
)
""")

conn.commit()
conn.close()

# ================= HOME =================

@app.route("/")
def home():
    return send_from_directory("sma", "login.html")

# ================= LOGIN =================

@app.route("/login", methods=["POST"])
def login():

    data = request.json

    conn = koneksi()
    c = conn.cursor()

    c.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (data["username"], data["password"])
    )

    user = c.fetchone()

    conn.close()

    if not user:
        return jsonify({"ok":False})

    return jsonify({
        "ok":True,
        "role":user["role"]
    })

# ================= TAMBAH SISWA =================

@app.route("/tambah-siswa", methods=["POST"])
def tambah_siswa():

    data = request.json

    conn = koneksi()
    c = conn.cursor()

    c.execute("""
    INSERT INTO siswa(nis,nama,kelas,wali_kelas,orang_tua)
    VALUES(?,?,?,?,?)
    """,(
        data["nis"],
        data["nama"],
        data["kelas"],
        data["wali_kelas"],
        data["orang_tua"]
    ))

    c.execute("""
    INSERT INTO users(username,password,role)
    VALUES(?,?,?)
    """,(
        data["nis"],
        data["password"],
        "siswa"
    ))

    conn.commit()
    conn.close()

    return jsonify({"msg":"Siswa berhasil ditambahkan"})

# ================= GET SISWA =================

@app.route("/get-siswa")
def get_siswa():

    conn = koneksi()
    c = conn.cursor()

    c.execute("SELECT * FROM siswa")

    data = [dict(row) for row in c.fetchall()]

    conn.close()

    return jsonify(data)

# ================= HAPUS SISWA =================

@app.route("/hapus-siswa/<nis>", methods=["DELETE"])
def hapus_siswa(nis):

    conn = koneksi()
    c = conn.cursor()

    c.execute("DELETE FROM siswa WHERE nis=?", (nis,))
    c.execute("DELETE FROM users WHERE username=?", (nis,))

    conn.commit()
    conn.close()

    return jsonify({"msg":"Siswa dihapus"})

# ================= UPDATE SISWA =================

@app.route("/update-siswa/<nis>", methods=["PUT"])
def update_siswa(nis):

    data = request.json

    conn = koneksi()
    c = conn.cursor()

    c.execute("""
    UPDATE siswa
    SET nis=?, nama=?, kelas=?, wali_kelas=?, orang_tua=?
    WHERE nis=?
    """,(
        data["nis"],
        data["nama"],
        data["kelas"],
        data["wali_kelas"],
        data["orang_tua"],
        nis
    ))

    conn.commit()
    conn.close()

    return jsonify({"msg":"Siswa diupdate"})

# ================= TAMBAH GURU =================

@app.route("/tambah-guru", methods=["POST"])
def tambah_guru():

    data = request.json

    conn = koneksi()
    c = conn.cursor()

    c.execute("""
    INSERT INTO guru(username,nama,mapel,alamat)
    VALUES(?,?,?,?)
    """,(
        data["username"],
        data["nama"],
        data["mapel"],
        data["jabatan"]
    ))

    c.execute("""
    INSERT INTO users(username,password,role)
    VALUES(?,?,?)
    """,(
        data["nip"],
        data["password"],
        "guru"
    ))

    conn.commit()
    conn.close()

    return jsonify({"msg":"Guru berhasil ditambahkan"})

# ================= GET GURU =================

@app.route("/get-guru")
def get_guru():

    conn = koneksi()
    c = conn.cursor()

    c.execute("SELECT * FROM guru")

    data = [dict(row) for row in c.fetchall()]

    conn.close()

    return jsonify(data)

# ================= HAPUS GURU =================

@app.route("/hapus-guru/<nip>", methods=["DELETE"])
def hapus_guru(nip):

    conn = koneksi()
    c = conn.cursor()

    c.execute("DELETE FROM guru WHERE nip=?", (nip,))
    c.execute("DELETE FROM users WHERE username=?", (nip,))

    conn.commit()
    conn.close()

    return jsonify({"msg":"Guru dihapus"})

# ================= UPDATE GURU =================

@app.route("/update-guru/<nip>", methods=["PUT"])
def update_guru(nip):

    data = request.json

    conn = koneksi()
    c = conn.cursor()

    c.execute("""
    UPDATE guru
    SET nip=?, nama=?, mapel=?, alamat=?
    WHERE nip=?
    """,(
        data["username"],
        data["nama"],
        data["mapel"],
        data["alamat"],
        nip
    ))

    conn.commit()
    conn.close()

    return jsonify({"msg":"Guru diupdate"})

# ================= JADWAL =================

@app.route("/tambah-jadwal", methods=["POST"])
def tambah_jadwal():

    data = request.json

    conn = koneksi()
    c = conn.cursor()

    c.execute("""
    INSERT INTO jadwal(kelas,mapel,guru,hari,jam)
    VALUES(?,?,?,?,?)
    """,(
        data["kelas"],
        data["mapel"],
        data["guru"],
        data["hari"],
        data["jam"]
    ))

    conn.commit()
    conn.close()

    return jsonify({"msg":"Jadwal berhasil ditambahkan"})

@app.route("/get-jadwal")
def get_jadwal():

    conn = koneksi()
    c = conn.cursor()

    c.execute("SELECT * FROM jadwal")

    data = [dict(row) for row in c.fetchall()]

    conn.close()

    return jsonify(data)

# ================= PEMBAYARAN =================

@app.route("/pembayaran", methods=["POST"])
def pembayaran():

    data = request.json

    conn = koneksi()
    c = conn.cursor()

    c.execute("""
    INSERT INTO pembayaran(nis,nama,jumlah)
    VALUES(?,?,?)
    """,(
        data["nis"],
        data["nama"],
        data["jumlah"]
    ))

    conn.commit()
    conn.close()

    return jsonify({"msg":"Pembayaran berhasil"})

@app.route("/get-pembayaran")
def get_pembayaran():

    conn = koneksi()
    c = conn.cursor()

    c.execute("SELECT * FROM pembayaran")

    data = [dict(row) for row in c.fetchall()]

    conn.close()

    return jsonify(data)

# ================= RUN =================

if __name__ == "__main__":
    app.run(debug=True)