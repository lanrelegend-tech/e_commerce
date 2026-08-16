from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from extensions import db
from models.cart import Cart
from models.products import Product

cart_bp = Blueprint("cart", __name__)


@cart_bp.route("/cart", methods=["POST"])
@jwt_required()
def add_to_cart():
    """
    Add a product to the authenticated user's shopping cart.
    ---
    tags:
      - Cart
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
            quantity:
              type: integer
              default: 1
    responses:
      201:
        description: Product added to cart.
      400:
        description: product_id is missing.
      401:
        description: Authentication required.
      404:
        description: Product not found.
    """

    user_id = int(get_jwt_identity())
    data = request.get_json()

    product_id = data.get("product_id")
    quantity = data.get("quantity", 1)

    if not product_id:
        return jsonify({"error": "product_id is required."}), 400

    product = Product.query.get(product_id)
    if not product:
        return jsonify({"error": "Product not found."}), 404

    item = Cart.query.filter_by(
        user_id=user_id,
        product_id=product_id
    ).first()

    if item:
        item.quantity += quantity
    else:
        item = Cart(
            user_id=user_id,
            product_id=product_id,
            quantity=quantity
        )
        db.session.add(item)

    db.session.commit()

    return jsonify({
        "message": "Product added to cart."
    }), 201


@cart_bp.route("/cart", methods=["GET"])
@jwt_required()
def view_cart():
    """
    View the authenticated user's shopping cart.
    ---
    tags:
      - Cart
    security:
      - Bearer: []
    responses:
      200:
        description: Shopping cart returned successfully.
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
              product_id:
                type: integer
              product:
                type: string
              price:
                type: number
              quantity:
                type: integer
      401:
        description: Authentication required.
    """

    user_id = int(get_jwt_identity())
    items = Cart.query.filter_by(user_id=user_id).all()

    return jsonify([
        {
            "id": i.id,
            "product_id": i.product_id,
            "product": i.product.name,
            "price": i.product.price,
            "quantity": i.quantity
        }
        for i in items
    ]), 200


@cart_bp.route("/cart/<int:item_id>", methods=["PUT"])
@jwt_required()
def update_cart(item_id):
    """
    Update the quantity of an item in the authenticated user's cart.
    ---
    tags:
      - Cart
    security:
      - Bearer: []
    consumes:
      - application/json
    parameters:
      - name: item_id
        in: path
        required: true
        type: integer
        description: ID of the cart item.
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            quantity:
              type: integer
    responses:
      200:
        description: Cart updated successfully.
      401:
        description: Authentication required.
      404:
        description: Cart item not found.
    """

    user_id = int(get_jwt_identity())

    item = Cart.query.filter_by(
        id=item_id,
        user_id=user_id
    ).first_or_404()

    data = request.get_json()

    item.quantity = data.get(
        "quantity",
        item.quantity
    )

    db.session.commit()

    return jsonify({
        "message": "Cart updated successfully."
    }), 200


@cart_bp.route("/cart/<int:item_id>", methods=["DELETE"])
@jwt_required()
def remove_from_cart(item_id):
    """
    Remove an item from the authenticated user's shopping cart.
    ---
    tags:
      - Cart
    security:
      - Bearer: []
    parameters:
      - name: item_id
        in: path
        required: true
        type: integer
        description: ID of the cart item.
    responses:
      200:
        description: Item removed from cart.
      401:
        description: Authentication required.
      404:
        description: Cart item not found.
    """

    user_id = int(get_jwt_identity())

    item = Cart.query.filter_by(
        id=item_id,
        user_id=user_id
    ).first_or_404()

    db.session.delete(item)
    db.session.commit()

    return jsonify({
        "message": "Item removed from cart."
    }), 200