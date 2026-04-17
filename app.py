from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from pymongo import MongoClient

app = Flask(__name__, static_folder=".", static_url_path="")
CORS(app)

client = MongoClient("mongodb://localhost:27017/")
db = client["db_sekolah"]

# ================= HOME =================
@app.route("/")
def home():
    return send_from_directory("sma", "login.html")

# ================= LOGIN =================
@app.route("/login", methods=["POST"])
def login():
    data = request.json

    user = db.users.find_one({
        "username": data["username"],
        "password": data["password"]
    })

    if not user:
        return jsonify({"ok": False})

    return jsonify({
        "ok": True,
        "role": user["role"]
    })

# ================= SISWA =================
@app.route("/tambah-siswa", methods=["POST"])
def tambah_siswa():
    data = request.json

    db.siswa.insert_one({
        "nis": data["nis"],
        "nama": data["nama"],
        "kelas": data["kelas"],
        "wali_kelas": data["wali_kelas"],
        "orang_tua": data["orang_tua"]
    })

    db.users.insert_one({
        "username": data["nis"],
        "password": data["password"],
        "role": "siswa"
    })

    return jsonify({"msg":"Siswa berhasil ditambahkan"})

@app.route("/get-siswa")
def get_siswa():
    return jsonify(list(db.siswa.find({}, {"_id":0})))

@app.route("/update-siswa/<nis>", methods=["PUT"])
def update_siswa(nis):
    data = request.json

    db.siswa.update_one(
        {"nis": nis},
        {"$set": data}
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
    data = request.json

    db.guru.insert_one({
        "nip": data["nip"],
        "nama": data["nama"],
        "mapel": data["mapel"],
        "alamat": data["alamat"]
    })

    db.users.insert_one({
        "username": data["nip"],
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

# ================= JADWAL =================
@app.route("/tambah-jadwal", methods=["POST"])
def tambah_jadwal():
    data = request.json
    db.jadwal.insert_one(data)
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

# ================= PRESENSI SISWA =================
@app.route("/presensi", methods=["POST"])
def presensi():
    db.presensi.insert_one(request.json)
    return jsonify({"msg":"Presensi siswa disimpan"})

@app.route("/get-presensi")
def get_presensi():
    return jsonify(list(db.presensi.find({}, {"_id":0})))

# ================= PRESENSI GURU =================
@app.route("/presensi-guru", methods=["POST"])
def presensi_guru():
    db.presensi_guru.insert_one(request.json)
    return jsonify({"msg":"Presensi guru disimpan"})

@app.route("/get-presensi-guru")
def get_presensi_guru():
    return jsonify(list(db.presensi_guru.find({}, {"_id":0})))

# ================= PEMBAYARAN =================
@app.route("/pembayaran", methods=["POST"])
def pembayaran():
    db.pembayaran.insert_one(request.json)
    return jsonify({"msg":"Pembayaran berhasil"})

@app.route("/get-pembayaran")
def get_pembayaran():
    return jsonify(list(db.pembayaran.find({}, {"_id":0})))

# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True, port=5000)