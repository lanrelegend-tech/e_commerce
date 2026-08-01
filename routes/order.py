from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from extensions import db
from models.cart import Cart
from models.orders import Order
from models.orderitems import OrderItem

order_bp = Blueprint("order", __name__)


@order_bp.route("/orders", methods=["POST"])
@jwt_required()
def create_order():
    user_id = int(get_jwt_identity())

    cart_items = Cart.query.filter_by(user_id=user_id).all()
    if not cart_items:
        return jsonify({"error": "Your cart is empty."}), 400

    total_price = sum(item.product.price * item.quantity for item in cart_items)

    order = Order(user_id=user_id, total_price=total_price)
    db.session.add(order)
    db.session.flush()

    for item in cart_items:
        order_item = OrderItem(
            order_id=order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            price=item.product.price
        )
        db.session.add(order_item)
        db.session.delete(item)

    db.session.commit()

    return jsonify({
        "message": "Order created successfully.",
        "order_id": order.id,
        "total_price": total_price
    }), 201


@order_bp.route("/orders", methods=["GET"])
@jwt_required()
def get_orders():
    user_id = int(get_jwt_identity())
    orders = Order.query.filter_by(user_id=user_id).all()

    return jsonify([
        {
            "id": o.id,
            "total_price": o.total_price,
            "status": o.status,
            "created_at": o.created_at.isoformat()
        }
        for o in orders
    ]), 200
