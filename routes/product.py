

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from extensions import db
from models.products import Product
from models.category import Category

product_bp = Blueprint("product", __name__)


@product_bp.route("/products", methods=["POST"])
@jwt_required()
def create_product():
    data = request.get_json()

    name = data.get("name")
    description = data.get("description")
    price = data.get("price")
    stock = data.get("stock", 0)
    image_url = data.get("image_url")
    category_id = data.get("category_id")

    if not all([name, price, category_id]):
        return jsonify({"error": "name, price and category_id are required."}), 400

    category = Category.query.get(category_id)
    if not category:
        return jsonify({"error": "Category not found."}), 404

    product = Product(name=name, description=description, price=price, stock=stock, image_url=image_url, category_id=category_id)
    db.session.add(product)
    db.session.commit()

    return jsonify({"message": "Product created successfully."}), 201


@product_bp.route("/products", methods=["GET"])
def get_products():
    products = Product.query.all()
    return jsonify([{
        "id": p.id,
        "name": p.name,
        "description": p.description,
        "price": p.price,
        "stock": p.stock,
        "image_url": p.image_url,
        "category_id": p.category_id
    } for p in products]), 200


@product_bp.route("/products/<int:product_id>", methods=["GET"])
def get_product(product_id):
    p = Product.query.get_or_404(product_id)
    return jsonify({"id": p.id, "name": p.name, "description": p.description, "price": p.price, "stock": p.stock, "image_url": p.image_url, "category_id": p.category_id}), 200


@product_bp.route("/products/<int:product_id>", methods=["PUT"])
@jwt_required()
def update_product(product_id):
    p = Product.query.get_or_404(product_id)
    data = request.get_json()
    p.name = data.get("name", p.name)
    p.description = data.get("description", p.description)
    p.price = data.get("price", p.price)
    p.stock = data.get("stock", p.stock)
    p.image_url = data.get("image_url", p.image_url)
    if "category_id" in data:
        category = Category.query.get(data["category_id"])
        if not category:
            return jsonify({"error": "Category not found."}), 404
        p.category_id = data["category_id"]
    db.session.commit()
    return jsonify({"message": "Product updated successfully."}), 200


@product_bp.route("/products/<int:product_id>", methods=["DELETE"])
@jwt_required()
def delete_product(product_id):
    p = Product.query.get_or_404(product_id)
    db.session.delete(p)
    db.session.commit()
    return jsonify({"message": "Product deleted successfully."}), 200