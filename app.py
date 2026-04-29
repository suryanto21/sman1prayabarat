from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__, static_folder=".", static_url_path="")
CORS(app)

# ================= DB =================
client = MongoClient("mongodb://localhost:27017/")
db = client["db_sekolah"]

siswa_col = db["siswa"]

# ================= HOME =================
@app.route("/")
def home():
    return send_from_directory("sma", "login.html")

# ================= LOGIN =================
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    username = str(data.get("username"))
    password = data.get("password")

    user = db.users.find_one({
        "username": username,
        "password": password
    })

    if not user:
        return jsonify({"ok": False})

    nama = ""

    if user["role"] == "siswa":
        s = db.siswa.find_one({"nis": username})
        if s:
            nama = s.get("nama", "")

    elif user["role"] == "guru":
        g = db.guru.find_one({"nip": username})
        if g:
            nama = g.get("nama", "")

    elif user["role"] == "admin":
        nama = "Admin"

    return jsonify({
        "ok": True,
        "role": user["role"],
        "nama": nama,
        "username": username
    })

# ================= SISWA =================
@app.route("/tambah-siswa", methods=["POST"])
def tambah_siswa():
    data = request.get_json()

    db.siswa.insert_one({
        "nis": str(data["nis"]),
        "nama": data["nama"],
        "kelas": data["kelas"],
        "wali_kelas": data["wali_kelas"],
        "orang_tua": data["orang_tua"]
    })

    db.users.insert_one({
        "username": str(data["nis"]),
        "password": data["password"],
        "role": "siswa"
    })

    return jsonify({"msg":"Siswa berhasil ditambahkan"})

@app.route("/get-siswa")
def get_siswa():
    return jsonify(list(db.siswa.find({}, {"_id":0})))

@app.route("/update-siswa/<nis>", methods=["PUT"])
def update_siswa(nis):
    db.siswa.update_one(
        {"nis": nis},
        {"$set": request.get_json()}
    )
    return jsonify({"msg":"Siswa diupdate"})

@app.route("/hapus-siswa/<nis>", methods=["DELETE"])
def hapus_siswa(nis):
    db.siswa.delete_one({"nis": nis})
    db.users.delete_one({"username": nis})
    return jsonify({"msg":"Siswa dihapus"})

# ================= GURU =================
@app.route("/tambah-guru", methods=["POST"])
def tambah_guru():
    data = request.get_json()

    db.guru.insert_one({
        "nip": str(data["nip"]),
        "nama": data["nama"],
        "mapel": data["mapel"],
        "alamat": data["alamat"]
    })

    db.users.insert_one({
        "username": str(data["nip"]),
        "password": data["password"],
        "role": "guru"
    })

    return jsonify({"msg":"Guru berhasil ditambahkan"})

@app.route("/get-guru")
def get_guru():
    return jsonify(list(db.guru.find({}, {"_id":0})))

@app.route("/hapus-guru/<nip>", methods=["DELETE"])
def hapus_guru(nip):
    db.guru.delete_one({"nip": nip})
    db.users.delete_one({"username": nip})
    return jsonify({"msg":"Guru dihapus"})

# ================= KELAS =================
@app.route('/get_kelas')
def get_kelas():
    return jsonify(siswa_col.distinct("kelas"))

# ================= SISWA BY KELAS =================
@app.route('/get_siswa_by_kelas/<kelas>')
def get_siswa_by_kelas(kelas):
    data = siswa_col.find({"kelas": kelas})

    hasil = []
    for d in data:
        hasil.append({
            "nis": d["nis"],
            "nama": d["nama"]
        })

    return jsonify(hasil)

# ================= HALAMAN PRESENSI =================
@app.route('/presensi-page')
def presensi_page():
    return send_from_directory("sma", "presensi.html")

# ================= SIMPAN PRESENSI =================
@app.route("/presensi", methods=["POST"])
def simpan_presensi():
    data = request.get_json()

    data["tanggal"] = data.get(
        "tanggal",
        datetime.now().strftime("%Y-%m-%d")
    )

    db.presensi.insert_one(data)
    return jsonify({"msg":"Presensi siswa disimpan"})

@app.route("/get-presensi")
def get_presensi():
    return jsonify(list(db.presensi.find({}, {"_id":0})))

# ================= JADWAL =================
@app.route("/tambah-jadwal", methods=["POST"])
def tambah_jadwal():
    db.jadwal.insert_one(request.get_json())
    return jsonify({"msg":"Jadwal ditambahkan"})

@app.route("/get-jadwal")
def get_jadwal():
    return jsonify(list(db.jadwal.find({}, {"_id":0})))

@app.route("/jadwal-guru/<nama>")
def jadwal_guru(nama):
    data = list(db.jadwal.find({
        "guru": {"$regex": nama, "$options":"i"}
    }, {"_id":0}))
    return jsonify(data)

# ================= PRESENSI GURU =================
@app.route("/presensi-guru", methods=["POST"])
def presensi_guru():
    data = request.get_json()

    db.presensi_guru.insert_one(data)

    return jsonify({"msg":"Presensi guru berhasil disimpan"})

@app.route("/get-presensi-guru")
def get_presensi_guru():
    return jsonify(list(db.presensi_guru.find({}, {"_id":0})))

# ================= TAGIHAN =================
@app.route("/tambah-tagihan", methods=["POST"])
def tambah_tagihan():
    data = request.get_json()

    data["nis"] = str(data["nis"])
    data["status"] = "belum"

    db.tagihan.update_one(
        {"nis": data["nis"]},
        {"$set": data},
        upsert=True
    )

    return jsonify({"msg":"Tagihan berhasil disimpan"})

@app.route("/get-tagihan/<nis>")
def get_tagihan(nis):
    data = db.tagihan.find_one({"nis": nis}, {"_id":0})
    return jsonify(data if data else {})

# ================= PEMBAYARAN =================
@app.route("/pembayaran", methods=["POST"])
def pembayaran():
    data = request.get_json()

    data["nis"] = str(data["nis"])
    data["tanggal"] = datetime.now().strftime("%Y-%m-%d")

    db.pembayaran.insert_one(data)

    # update status jadi lunas
    db.tagihan.update_one(
        {"nis": data["nis"]},
        {"$set": {"status": "lunas"}}
    )

    return jsonify({"msg":"Pembayaran berhasil"})

@app.route("/get-pembayaran")
def get_pembayaran():
    return jsonify(list(db.pembayaran.find({}, {"_id":0})))

# ================= DATA =================
@app.route("/get-all-data")
def get_all_data():

    users = list(db.users.find({}, {"_id":0}))
    siswa = list(db.siswa.find({}, {"_id":0}))
    guru  = list(db.guru.find({}, {"_id":0}))

    return jsonify({
        "users": users,
        "siswa": siswa,
        "guru": guru
    })


# ================= UPDATE GURU =================
@app.route("/update-guru/<nip>", methods=["PUT"])
def update_guru(nip):
    db.guru.update_one(
        {"nip": nip},
        {"$set": request.json}
    )
    return jsonify({"msg":"Guru diupdate"})

# ================= UPDATE USER =================
@app.route("/update-user/<username>", methods=["PUT"])
def update_user(username):
    db.users.update_one(
        {"username": username},
        {"$set": request.json}
    )
    return jsonify({"msg":"User diupdate"})

# ================= DELETE USER =================
@app.route("/hapus-user/<username>", methods=["DELETE"])
def hapus_user(username):
    db.users.delete_one({"username": username})
    return jsonify({"msg":"User dihapus"})


# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True, port=5000, use_reloader=False)