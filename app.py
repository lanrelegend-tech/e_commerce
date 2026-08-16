from flask import Flask
from models.user import User
from models.category import Category
from models.products import Product
from models.cart import Cart
from models.orders import Order
from models.orderitems import OrderItem
from config import Config
from extensions import db, migrate, jwt, bcrypt
from routes.auth import auth_bp
from routes.category import category_bp
from routes.product import product_bp
from routes.cart import cart_bp
from routes.order import order_bp
from flasgger import Swagger
from routes.admin import admin_bp
from models.wishlist import Wishlist
from routes.wishlist import wishlist_bp
from models.review import Review
from routes.review import review_bp
from mail_config import mail
from routes.profile import profile_bp
from routes.password_reset import password_reset_bp



app = Flask(__name__)

app.config.from_object(Config)
Swagger(app)
db.init_app(app)
migrate.init_app(app, db)
jwt.init_app(app)
bcrypt.init_app(app)
app.register_blueprint(password_reset_bp)
app.register_blueprint(profile_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(category_bp)
app.register_blueprint(product_bp)
app.register_blueprint(cart_bp)
app.register_blueprint(order_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(wishlist_bp)
app.register_blueprint(review_bp)
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = "YOUR_EMAIL@gmail.com"
app.config["MAIL_PASSWORD"] = "YOUR_APP_PASSWORD"
app.config["MAIL_DEFAULT_SENDER"] = "YOUR_EMAIL@gmail.com"

mail.init_app(app)




@app.route("/")
def home():
    return {"message": "E-Commerce API is running!"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)