from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, abort, session
from models import db, Store, setup_db, db_drop_and_create_all, Product
from auth import AuthError, requires_auth, req_auth
from flask_cors import CORS
import os
from urllib.parse import quote_plus, urlencode
from authlib.integrations.flask_client import OAuth
from dotenv import find_dotenv, load_dotenv
import json

def create_app(db_URI="", test_config=None):
    app = Flask(__name__)
    app.secret_key = os.getenv("APP_SECRET_KEY")
    oauth = OAuth(app)
    oauth.register(
    "auth0",
    client_id=os.getenv("AUTH0_CLIENT_ID"),
    client_secret=os.getenv("AUTH0_CLIENT_SECRET"),
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f'https://{os.getenv("AUTH0_DOMAIN")}/.well-known/openid-configuration')
    if db_URI:
        with app.app_context():
            setup_db(app,db_URI)
    else:
        with app.app_context():
            setup_db(app)

    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # CORS Headers
    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
        )
        return response



    # 👆 We're continuing from the steps above. Append this to your server.py file.

    @app.route("/")
    def home():
        return render_template("home.html", session=session.get('user'), pretty=json.dumps(session.get('user'), indent=4))
    
    @app.route("/login")
    def login():
        return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("callback", _external=True))
    
    @app.route("/callback", methods=["GET", "POST"])
    def callback():
        token = oauth.auth0.authorize_access_token()
        session["user"] = token
        return redirect("/")
    
    @app.route("/logout")
    def logout():
        session.clear()
        return redirect(
            "https://" + os.getenv("AUTH0_DOMAIN")
            + "/v2/logout?"
            + urlencode({
                "returnTo": url_for("home", _external=True),
                "client_id": os.getenv("AUTH0_CLIENT_ID"),},quote_via=quote_plus,))

    @app.route('/login-results', methods=['GET', 'POST'])
    @req_auth
    def login_results(jwt):
        print(jwt)
        return 'successfull login'


    ## _______________________________________________________ GET _______________________________________________________
    @app.route('/store/<int:store_id>', methods=['GET'])
    @requires_auth('get:store')
    def get_store(store_id):
        store = Store.query.get(store_id)
        if not store:
            # Raise a 404 error if the store is not found
            abort(404)
        return jsonify({
            'success': True,
            'store': store.format()
        })

    @app.route('/product/<int:product_id>', methods=['GET'])
    @requires_auth('get:product')
    def get_product(product_id):
        product = Product.query.get(product_id)
        if not product:
            # Raise a 404 error if the product is not found
            abort(404)
                
        return jsonify({
            'success': True,
            'product': product.format()
        })


    @app.route('/stores', methods=['GET', 'POST'])
    @requires_auth('get:stores')
    def stores(jwt):
        stores = Store.query.all()
        if not stores:
            # Raise a 404 error if no stores are found
            abort(404)
        return jsonify({
            'success': True,
            'stores': [store.format() for store in stores]
        })

    @app.route('/products', methods=['GET'])
    @requires_auth('get:products')
    def products(jwt):
        products = Product.query.all()
        if not products:
            # Raise a 404 error if no products are found
            abort(404)
        return jsonify({
            'success': True,
            'products': [product.format() for product in products]
        })

    @app.route('/store/<int:store_id>/products', methods=['GET'])
    @requires_auth('get:product')
    def get_products_for_store(store_id, jwt):
        store = Store.query.get(store_id)
        if not store:
            # Raise a 404 error if the store is not found
            abort(404)
        products = Product.query.filter(Product.store_id == store_id).all()
        return jsonify({
            'success': True,
            'products': [product.format() for product in products]
        })

    @app.route('/product/<int:product_id>/stores', methods=['GET'])
    @requires_auth('get:stores')
    def get_stores_for_product(product_id, jwt):
        product = Product.query.get(product_id)
        if not product:
            # Raise a 404 error if the product is not found
            abort(404)
        stores = Store.query.filter(Store.product_id == products_id).all()
        return jsonify({
            'success': True,
            'stores': [store.format() for store in stores]
        })
    ## _______________________________________________________ POST _______________________________________________________

    @app.route('/store', methods=['GET', 'POST'])
    @requires_auth('post:store')
    def store(jwt):
        try:
            data = request.get_json()
            store_name = data.get('store_name')
            store = Store(store_name=store_name)
            store.insert()
            return jsonify({
                'success': True,
                'store': store.format()
            })
        except Exception:
            abort(422)


    @app.route('/product', methods=['GET', 'POST'])
    @requires_auth('post:product')
    def product(jwt):
        try:
            data = request.get_json()
            name = data.get('name')
            quantity = data.get('quantity')
            price = data.get('price')
            store_id = data.get('store_id')
            product = Product(name=name, quantity=quantity, price=price, store_id=store_id)
            product.insert()
            return jsonify({
                'success': True,
                'product': product.format()
            })
        except Exception:
            abort(422)


    ## _______________________________________________________ PATCH _______________________________________________________
    @app.route('/store/<int:store_id>', methods=['PATCH'])
    @requires_auth('patch:store')
    def update_store(store_id, jwt):
        try:
            store = Store.query.get(store_id)
            if not store:
                # Raise a 404 error if the store is not found
                abort(404)
            data = request.get_json()
            store_name = data.get('store_name')
            store.store_name = store_name
            store.update()
            return jsonify({
                'success': True,
                'store': store.format()
            })
        except Exception:
            # Raise a 422 error if there's a problem updating the store
            abort(422)


    @app.route('/product/<int:product_id>', methods=['PATCH'])
    @requires_auth('patch:product')
    def update_product(product_id, jwt):
        try:
            product = Product.query.get(product_id)
            if not product:
                # Raise a 404 error if the product is not found
                abort(404)
            data = request.get_json()
            name = data.get('name')
            quantity = data.get('quantity')
            price = data.get('price')
            store_id = data.get('store_id')
            product.name = name
            product.quantity = quantity
            product.price = price
            product.store_id = store_id
            product.update()
            return jsonify({
                'success': True,
                'product': product.format()
            })
        except Exception:
            # Raise a 422 error if there's a problem updating the product
            abort(422)


    ## _______________________________________________________ DELETE _______________________________________________________
    @app.route('/store/<int:store_id>', methods=['DELETE'])
    @requires_auth('delete:store')
    def delete_store(store_id, jwt):
        store = Store.query.get(store_id)
        if not store:
            abort(404)
        store.delete()
        return jsonify({
            'success': True,
            'deleted': store_id
        })

    @app.route('/product/<int:product_id>', methods=['DELETE'])
    @requires_auth('delete:product')
    def delete_product(product_id, jwt):
        product = Product.query.get(product_id)
        if not product:
            abort(404)
        product.delete()
        return jsonify({
            'success': True,
            'deleted': product_id
        })

    @app.route('/store/<int:store_id>/products', methods=['DELETE'])
    @requires_auth('delete:products')
    def delete_products_for_store(store_id, jwt):
        store = Store.query.get(store_id)
        if not store:
            abort(404)
        products = Product.query.filter(Product.store_id == store_id).all()
        for product in products:
            product.delete()
        return jsonify({
            'success': True,
            'deleted': store_id
        })

    ## _______________________________________________________ ERROR HANDLERS _______________________________________________________
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': 'Resource not found'
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            'success': False,
            'error': 422,
            'message': 'Unprocessable Entity'
        }), 422

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'error': 400,
            'message': 'Bad Request'
        }), 400  

    @app.errorhandler(405)
    def not_allowed(error):
        return jsonify({
            'success': False,
            'error': 405,
            'message': 'Method Not Allowed'
        }), 405

    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            'success': False,
            'error': 500,
            'message': 'Internal Server Error'
        }), 500


    @app.errorhandler(AuthError)
    def handle_auth_error(ex):
        response = jsonify(ex.error)
        response.status_code = ex.status_code
        return response



    return app

app = create_app()

if __name__ == '__main__':
    app.run()