

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from utils.admin import admin_required

from extensions import db
from models.products import Product
from models.category import Category

product_bp = Blueprint("product", __name__)


@product_bp.route("/products", methods=["POST"])
@admin_required
def create_product():
    """
    Create a new product.
    ---
    tags:
      - Products
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - name
            - price
            - category_id
          properties:
            name:
              type: string
              example: iPhone 15
            description:
              type: string
              example: Brand new iPhone 15
            price:
              type: number
              example: 750000
            stock:
              type: integer
              example: 10
            image_url:
              type: string
              example: /static/uploads/iphone15.jpg
            category_id:
              type: integer
              example: 1
    responses:
      201:
        description: Product created successfully.
      400:
        description: Required product information is missing.
      404:
        description: Category not found.
      401:
        description: Authentication required.
      403:
        description: Admin access required.
    """
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
    search = request.args.get("search")
    category = request.args.get("category", type=int)
    min_price = request.args.get("min_price", type=float)
    max_price = request.args.get("max_price", type=float)
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    query = Product.query

    if search:
        query = query.filter(Product.name.ilike(f"%{search}%"))

    if category:
        query = query.filter(Product.category_id == category)

    if min_price is not None:
        query = query.filter(Product.price >= min_price)

    if max_price is not None:
        query = query.filter(Product.price <= max_price)

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        "page": pagination.page,
        "per_page": pagination.per_page,
        "total": pagination.total,
        "pages": pagination.pages,
        "products": [{
            "id": p.id,
            "name": p.name,
            "description": p.description,
            "price": p.price,
            "stock": p.stock,
            "in_stock": p.stock > 0,
            "image_url": p.image_url,
            "category_id": p.category_id
        } for p in pagination.items]
    }), 200


@product_bp.route("/products/<int:product_id>", methods=["GET"])
def get_product(product_id):
    """
    Get a single product by ID.
    ---
    tags:
      - Products
    parameters:
      - in: path
        name: product_id
        required: true
        type: integer
        example: 1
    responses:
      200:
        description: Product retrieved successfully.
      404:
        description: Product not found.
    """
    p = Product.query.get_or_404(product_id)
    return jsonify({
        "id": p.id,
        "name": p.name,
        "description": p.description,
        "price": p.price,
        "stock": p.stock,
        "in_stock": p.stock > 0,
        "image_url": p.image_url,
        "category_id": p.category_id
    }), 200


@product_bp.route("/products/<int:product_id>", methods=["PUT"])
@admin_required
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
@admin_required
def delete_product(product_id):
    p = Product.query.get_or_404(product_id)
    db.session.delete(p)
    db.session.commit()
    return jsonify({"message": "Product deleted successfully."}), 200