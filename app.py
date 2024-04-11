from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from werkzeug.exceptions import NotFound
from flask_marshmallow import Marshmallow
from flask_swagger_ui import get_swaggerui_blueprint
from marshmallow import Schema, fields


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
ma = Marshmallow(app)


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    prise = db.Column(db.Float, nullable=False)


class ProductSchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True)
    prise = fields.Float(required=True)


@app.before_request
def create_tables():
    db.create_all()


SWAGGER_URL = '/api/docs'
API_URL = '/static/swagger.json'

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        "app_name": 'Product api documentation'
    }
    )


app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)


#@app.route('/')
#def index():
    #pass


@app.route('/products', methods=['GET', 'POST'])
def products():
    if request.method == 'GET':
        products = Product.query.all()
        return jsonify([{'id': p.id, 'name': p.name, 'price': p.prise} for p in products])
    elif request.method == 'POST':
        data = request.json
        product = Product(name=data['name'], prise=data['prise'])
        db.session.add(product)
        db.session.commit()
        return jsonify({'message': 'Product was added successfully!'})


@app.route('/products/<int:product_id>', methods=['GET', 'PUT', 'PATCH', 'DELETE'])
def product(product_id):
    product = Product.query.get(product_id)
    if product is None:
        raise NotFound(f'Product with id {product_id} is not found!')
    if request.method == 'GET':
        return jsonify({'id': product.id, 'name': product.name, 'price': product.prise})
    elif request.method == 'PUT':
        data = request.json
        product.name = data.get('name', product.name)
        product.prise = data.get('prise', product.prise)
        db.session.commit()
        return jsonify({'message': 'Product was updated(put) successfully!'})
    elif request.method == 'PATCH':
        data = request.json
        if 'name' in data:
            product.name = data['name']
        if 'prise' in data:
            product.prise = data['prise']
        db.session.commit()
        return jsonify({'message': 'Product was updated(patch) successfully!'})
    elif request.method == 'DELETE':
        db.session.delete(product)
        db.session.commit()
        return jsonify({'message': 'Product was deleted successfully!'})


if __name__ == '__main__':
    app.run(debug=True)
