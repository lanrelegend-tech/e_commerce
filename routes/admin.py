from flask import Blueprint, jsonify
from sqlalchemy import func

from extensions import db
from utils.admin import admin_required

from models.user import User
from models.products import Product
from models.category import Category
from models.orders import Order
from models.review import Review
from models.wishlist import Wishlist

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/admin/promote/<int:user_id>", methods=["PUT"])
@admin_required
def promote_user(user_id):
    """
    Promote a user to administrator.
    ---
    tags:
      - Admin
    security:
      - Bearer: []
    parameters:
      - name: user_id
        in: path
        required: true
        type: integer
        description: ID of the user to promote.
    responses:
      200:
        description: User is already an admin or was successfully promoted.
      401:
        description: Authentication required.
      403:
        description: Administrator privileges required.
      404:
        description: User not found.
    """

    user = db.session.get(User, user_id)

    if not user:
        return jsonify({
            "error": "User not found."
        }), 404

    if user.is_admin:
        return jsonify({
            "message": "User is already an admin."
        }), 200

    user.is_admin = True

    db.session.commit()

    return jsonify({
        "message": f"{user.username} is now an admin."
    }), 200


@admin_bp.route("/admin/dashboard", methods=["GET"])
@admin_required
def dashboard():
    """
    Return administrator dashboard statistics.
    ---
    tags:
      - Admin
    security:
      - Bearer: []
    responses:
      200:
        description: Dashboard statistics returned successfully.
        schema:
          type: object
          properties:
            total_users:
              type: integer
            total_products:
              type: integer
            total_categories:
              type: integer
            total_orders:
              type: integer
            total_reviews:
              type: integer
            total_wishlist_items:
              type: integer
            total_revenue:
              type: number
              format: float
      401:
        description: Authentication required.
      403:
        description: Administrator privileges required.
    """

    total_users = User.query.count()
    total_products = Product.query.count()
    total_categories = Category.query.count()
    total_orders = Order.query.count()
    total_reviews = Review.query.count()
    total_wishlist_items = Wishlist.query.count()

    total_revenue = db.session.query(
        func.sum(Order.total_price)
    ).scalar() or 0

    return jsonify({
        "total_users": total_users,
        "total_products": total_products,
        "total_categories": total_categories,
        "total_orders": total_orders,
        "total_reviews": total_reviews,
        "total_wishlist_items": total_wishlist_items,
        "total_revenue": float(total_revenue)
    }), 200