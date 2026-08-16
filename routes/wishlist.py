from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from extensions import db
from models.wishlist import Wishlist
from models.products import Product

wishlist_bp = Blueprint("wishlist", __name__)


@wishlist_bp.route("/wishlist", methods=["POST"])
@jwt_required()
def add_to_wishlist():
    """
    Add a product to the authenticated user's wishlist.
    ---
    tags:
      - Wishlist
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
            - product_id
          properties:
            product_id:
              type: integer
    responses:
      201:
        description: Product added to wishlist successfully.
      401:
        description: Authentication required.
      404:
        description: Product not found.
      409:
        description: Product already exists in wishlist.
    """

    data = request.get_json()

    product = db.session.get(
        Product,
        data.get("product_id")
    )

    if not product:
        return jsonify({
            "error": "Product not found."
        }), 404

    existing = Wishlist.query.filter_by(
        user_id=int(get_jwt_identity()),
        product_id=product.id
    ).first()

    if existing:
        return jsonify({
            "message": "Product already in wishlist."
        }), 409

    item = Wishlist(
        user_id=int(get_jwt_identity()),
        product_id=product.id
    )

    db.session.add(item)
    db.session.commit()

    return jsonify({
        "message": "Product added to wishlist."
    }), 201


@wishlist_bp.route("/wishlist", methods=["GET"])
@jwt_required()
def get_wishlist():
    """
    Get the authenticated user's wishlist.
    ---
    tags:
      - Wishlist
    security:
      - Bearer: []
    responses:
      200:
        description: Wishlist returned successfully.
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
              product_id:
                type: integer
              name:
                type: string
              price:
                type: number
                format: float
              image_url:
                type: string
      401:
        description: Authentication required.
    """

    items = Wishlist.query.filter_by(
        user_id=int(get_jwt_identity())
    ).all()

    return jsonify([
        {
            "id": item.id,
            "product_id": item.product.id,
            "name": item.product.name,
            "price": item.product.price,
            "image_url": item.product.image_url,
        }
        for item in items
    ]), 200


@wishlist_bp.route("/wishlist/<int:product_id>", methods=["DELETE"])
@jwt_required()
def remove_from_wishlist(product_id):
    """
    Remove a product from the authenticated user's wishlist.
    ---
    tags:
      - Wishlist
    security:
      - Bearer: []
    parameters:
      - name: product_id
        in: path
        required: true
        type: integer
        description: ID of the product to remove from the wishlist.
    responses:
      200:
        description: Product removed from wishlist successfully.
      401:
        description: Authentication required.
      404:
        description: Wishlist item not found.
    """

    item = Wishlist.query.filter_by(
        user_id=int(get_jwt_identity()),
        product_id=product_id
    ).first()

    if not item:
        return jsonify({
            "error": "Wishlist item not found."
        }), 404

    db.session.delete(item)
    db.session.commit()

    return jsonify({
        "message": "Product removed from wishlist."
    }), 200