from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from utils.admin import admin_required

from extensions import db
from models.category import Category

category_bp = Blueprint("category", __name__)


@category_bp.route("/categories", methods=["POST"])
@admin_required
def create_category():
    """
    Create a new product category.
    ---
    tags:
      - Categories
    security:
      - Bearer: []
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - name
          properties:
            name:
              type: string
            description:
              type: string
    responses:
      201:
        description: Category created successfully.
      400:
        description: Category name is required.
      409:
        description: Category already exists.
      401:
        description: Authentication required.
      403:
        description: Administrator privileges required.
    """

    data = request.get_json()
    name = data.get("name")
    description = data.get("description")

    if not name:
        return jsonify({"error": "Category name is required."}), 400

    if Category.query.filter_by(name=name).first():
        return jsonify({"error": "Category already exists."}), 409

    category = Category(name=name, description=description)
    db.session.add(category)
    db.session.commit()

    return jsonify({"message": "Category created successfully."}), 201


@category_bp.route("/categories", methods=["GET"])
def get_categories():
    """
    Get all product categories.
    ---
    tags:
      - Categories
    responses:
      200:
        description: List of categories returned successfully.
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
              name:
                type: string
              description:
                type: string
    """

    categories = Category.query.all()

    return jsonify([
        {
            "id": c.id,
            "name": c.name,
            "description": c.description
        }
        for c in categories
    ]), 200


@category_bp.route("/categories/<int:category_id>", methods=["GET"])
def get_category(category_id):
    """
    Get a product category by ID.
    ---
    tags:
      - Categories
    parameters:
      - name: category_id
        in: path
        required: true
        type: integer
    responses:
      200:
        description: Category returned successfully.
      404:
        description: Category not found.
    """

    category = Category.query.get_or_404(category_id)

    return jsonify({
        "id": category.id,
        "name": category.name,
        "description": category.description
    }), 200


@category_bp.route("/categories/<int:category_id>", methods=["PUT"])
@admin_required
def update_category(category_id):
    """
    Update a product category.
    ---
    tags:
      - Categories
    security:
      - Bearer: []
    consumes:
      - application/json
    parameters:
      - name: category_id
        in: path
        required: true
        type: integer
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            name:
              type: string
            description:
              type: string
    responses:
      200:
        description: Category updated successfully.
      401:
        description: Authentication required.
      403:
        description: Administrator privileges required.
      404:
        description: Category not found.
    """

    category = Category.query.get_or_404(category_id)
    data = request.get_json()

    category.name = data.get("name", category.name)
    category.description = data.get(
        "description",
        category.description
    )

    db.session.commit()

    return jsonify({
        "message": "Category updated successfully."
    }), 200


@category_bp.route("/categories/<int:category_id>", methods=["DELETE"])
@admin_required
def delete_category(category_id):
    """
    Delete a product category.
    ---
    tags:
      - Categories
    security:
      - Bearer: []
    parameters:
      - name: category_id
        in: path
        required: true
        type: integer
    responses:
      200:
        description: Category deleted successfully.
      401:
        description: Authentication required.
      403:
        description: Administrator privileges required.
      404:
        description: Category not found.
    """

    category = Category.query.get_or_404(category_id)

    db.session.delete(category)
    db.session.commit()

    return jsonify({
        "message": "Category deleted successfully."
    }), 200