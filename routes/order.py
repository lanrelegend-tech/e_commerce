from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from extensions import db
from models.cart import Cart
from models.orders import Order
from models.orderitems import OrderItem
from models.products import Product
from utils.email import send_order_confirmation
from models.user import User

order_bp = Blueprint("order", __name__)


@order_bp.route("/orders", methods=["POST"])
@jwt_required()
def create_order():
    """
    Create an order from the authenticated user's shopping cart.
    ---
    tags:
      - Orders
    security:
      - Bearer: []
    responses:
      201:
        description: Order created successfully.
        schema:
          type: object
          properties:
            message:
              type: string
            order_id:
              type: integer
            total_price:
              type: number
              format: float
      400:
        description: Cart is empty or there is insufficient stock.
      401:
        description: Authentication required.
      404:
        description: Product in cart not found.
    """

    user_id = int(get_jwt_identity())

    cart_items = Cart.query.filter_by(user_id=user_id).all()
    if not cart_items:
        return jsonify({"error": "Your cart is empty."}), 400

    for item in cart_items:
        product = db.session.get(Product, item.product_id)

        if not product:
            return jsonify({
                "error": f"Product with ID {item.product_id} not found."
            }), 404

        if item.quantity > product.stock:
            return jsonify({
                "error": f"Insufficient stock for {product.name}. Available: {product.stock}"
            }), 400

    total_price = sum(
        item.product.price * item.quantity
        for item in cart_items
    )

    order = Order(
        user_id=user_id,
        total_price=total_price
    )

    db.session.add(order)
    db.session.flush()

    for item in cart_items:
        order_item = OrderItem(
            order_id=order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            price=item.product.price
        )

        item.product.stock -= item.quantity

        db.session.add(order_item)
        db.session.delete(item)

    db.session.commit()

    user = db.session.get(User, user_id)

    try:
        send_order_confirmation(
            user_email=user.email,
            order_id=order.id,
            total_price=order.total_price
        )
    except Exception as e:
        print(f"Failed to send email: {e}")

    return jsonify({
        "message": "Order created successfully.",
        "order_id": order.id,
        "total_price": total_price
    }), 201


@order_bp.route("/orders", methods=["GET"])
@jwt_required()
def get_orders():
    """
    Get all orders belonging to the authenticated user.
    ---
    tags:
      - Orders
    security:
      - Bearer: []
    responses:
      200:
        description: User orders returned successfully.
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
              total_price:
                type: number
                format: float
              status:
                type: string
              created_at:
                type: string
      401:
        description: Authentication required.
    """

    user_id = int(get_jwt_identity())

    orders = Order.query.filter_by(
        user_id=user_id
    ).all()

    return jsonify([
        {
            "id": o.id,
            "total_price": o.total_price,
            "status": o.status,
            "created_at": o.created_at.isoformat()
        }
        for o in orders
    ]), 200


@order_bp.route("/orders/history", methods=["GET"])
@jwt_required()
def order_history():
    """
    Get the authenticated user's order history with order items.
    ---
    tags:
      - Orders
    security:
      - Bearer: []
    responses:
      200:
        description: Order history returned successfully.
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
              total_price:
                type: number
                format: float
              status:
                type: string
              created_at:
                type: string
              items:
                type: array
                items:
                  type: object
                  properties:
                    product_id:
                      type: integer
                    quantity:
                      type: integer
                    price:
                      type: number
                      format: float
      401:
        description: Authentication required.
    """

    user_id = int(get_jwt_identity())

    orders = Order.query.filter_by(
        user_id=user_id
    ).order_by(
        Order.created_at.desc()
    ).all()

    return jsonify([
        {
            "id": order.id,
            "total_price": order.total_price,
            "status": order.status,
            "created_at": (
                order.created_at.isoformat()
                if order.created_at
                else None
            ),
            "items": [
                {
                    "product_id": item.product_id,
                    "quantity": item.quantity,
                    "price": item.price
                }
                for item in order.items
            ]
        }
        for order in orders
    ]), 200