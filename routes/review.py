from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func

from extensions import db
from models.review import Review
from models.products import Product

review_bp = Blueprint("review", __name__)


@review_bp.route("/products/<int:product_id>/reviews", methods=["POST"])
@jwt_required()
def add_review(product_id):
    """
    Add a review and rating for a product.
    ---
    tags:
      - Reviews
    security:
      - Bearer: []
    consumes:
      - application/json
    parameters:
      - name: product_id
        in: path
        required: true
        type: integer
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - rating
          properties:
            rating:
              type: integer
              minimum: 1
              maximum: 5
            comment:
              type: string
    responses:
      201:
        description: Review added successfully.
      400:
        description: Rating must be between 1 and 5.
      401:
        description: Authentication required.
      404:
        description: Product not found.
    """

    product = db.session.get(Product, product_id)

    if not product:
        return jsonify({
            "error": "Product not found."
        }), 404

    data = request.get_json()

    rating = data.get("rating")
    comment = data.get("comment")

    if rating is None or not (1 <= rating <= 5):
        return jsonify({
            "error": "Rating must be between 1 and 5."
        }), 400

    review = Review(
        rating=rating,
        comment=comment,
        user_id=int(get_jwt_identity()),
        product_id=product_id
    )

    db.session.add(review)
    db.session.commit()

    return jsonify({
        "message": "Review added successfully."
    }), 201


@review_bp.route("/products/<int:product_id>/reviews", methods=["GET"])
def get_reviews(product_id):
    """
    Get all reviews for a product.
    ---
    tags:
      - Reviews
    parameters:
      - name: product_id
        in: path
        required: true
        type: integer
    responses:
      200:
        description: Product reviews returned successfully.
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
              rating:
                type: integer
              comment:
                type: string
              user_id:
                type: integer
              created_at:
                type: string
      404:
        description: Product not found.
    """

    reviews = Review.query.filter_by(
        product_id=product_id
    ).all()

    return jsonify([
        {
            "id": review.id,
            "rating": review.rating,
            "comment": review.comment,
            "user_id": review.user_id,
            "created_at": review.created_at
        }
        for review in reviews
    ]), 200


@review_bp.route("/products/<int:product_id>/rating", methods=["GET"])
def get_rating(product_id):
    """
    Get the average rating for a product.
    ---
    tags:
      - Reviews
    parameters:
      - name: product_id
        in: path
        required: true
        type: integer
    responses:
      200:
        description: Average product rating returned successfully.
        schema:
          type: object
          properties:
            product_id:
              type: integer
            average_rating:
              type: number
              format: float
    """

    average = db.session.query(
        func.avg(Review.rating)
    ).filter(
        Review.product_id == product_id
    ).scalar()

    return jsonify({
        "product_id": product_id,
        "average_rating": round(average, 2) if average else 0
    }), 200