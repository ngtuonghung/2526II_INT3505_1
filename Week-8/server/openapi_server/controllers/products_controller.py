import datetime

from bson import ObjectId
from bson.errors import InvalidId
from flask import jsonify
from pymongo import MongoClient, ReturnDocument

_client = MongoClient("mongodb://localhost:27017/")
_col = _client["product_db"]["products"]


def _serialize(doc):
    doc["id"] = str(doc.pop("_id"))
    if isinstance(doc.get("createdAt"), datetime.datetime):
        doc["createdAt"] = doc["createdAt"].isoformat() + "Z"
    return doc


def _oid(id_str):
    try:
        return ObjectId(id_str)
    except (InvalidId, TypeError):
        return None


def products_get():
    return jsonify([_serialize(d) for d in _col.find()]), 200


def products_post(body):
    doc = {
        "name": body["name"],
        "description": body.get("description", ""),
        "price": float(body["price"]),
        "stock": int(body.get("stock", 0)),
        "createdAt": datetime.datetime.utcnow(),
    }
    result = _col.insert_one(doc)
    doc["_id"] = result.inserted_id
    return jsonify(_serialize(doc)), 201


def products_id_get(id_):
    oid = _oid(id_)
    if not oid:
        return jsonify({"error": "invalid id"}), 400
    doc = _col.find_one({"_id": oid})
    if not doc:
        return jsonify({"error": "product not found"}), 404
    return jsonify(_serialize(doc)), 200


def products_id_put(id_, body):
    oid = _oid(id_)
    if not oid:
        return jsonify({"error": "invalid id"}), 400
    update = {k: body[k] for k in ("name", "description", "price", "stock") if k in body}
    if not update:
        return jsonify({"error": "no fields to update"}), 400
    doc = _col.find_one_and_update(
        {"_id": oid}, {"$set": update}, return_document=ReturnDocument.AFTER
    )
    if not doc:
        return jsonify({"error": "product not found"}), 404
    return jsonify(_serialize(doc)), 200


def products_id_delete(id_):
    oid = _oid(id_)
    if not oid:
        return jsonify({"error": "invalid id"}), 400
    result = _col.delete_one({"_id": oid})
    if result.deleted_count == 0:
        return jsonify({"error": "product not found"}), 404
    return "", 204
