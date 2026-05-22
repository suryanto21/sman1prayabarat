from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["db_sekolah"]

db.users.update_many(
    {"role": {"$exists": False}},
    {"$set": {"role": "guru"}}
)

print("Role guru berhasil ditambahkan")