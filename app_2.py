from flask import Flask, jsonify, request, render_template
from flask_sqlalchemy import SQLAlchemy
from werkzeug.exceptions import NotFound
from flask_marshmallow import Marshmallow


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
ma = Marshmallow(app)


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    prise = db.Column(db.Float, nullable=False)


@app.before_request
def create_tables():
    db.create_all()

#@app.route('/')
#def index():
    #pass


@app.route('/products', methods=['GET', 'POST'])
def products():
    if request.method == 'GET':
        products = Product.query.all()
        return render_template('products.html', products=products)
    elif request.method == 'POST':
        data = request.json
        if "name" not in data or "prise" not in data:
            return 'Name and prise required', 400
        product = Product(name=data['name'], prise=float(data['prise']))
        db.session.add(product)
        db.session.commit()
        return jsonify({'message': 'Product was added successfully!'})


@app.route('/product/<int:product_id>', methods=['GET', 'PUT', 'PATCH', 'DELETE'])
def product(product_id):
    product = Product.query.get(product_id)
    if product is None:
        raise NotFound(f'Product with id {product_id} is not found!')
    if request.method == 'GET':
        return render_template('product.html', product=product)
    elif request.method == 'PUT':
        data = request.json
        product.name = data.get('name', product.name)
        product.prise = float(data.get('prise', product.prise))
        db.session.commit()
        return jsonify({'message': 'Product was updated(put) successfully!'})
    elif request.method == 'PATCH':
        data = request.json
        if 'name' in data:
            product.name = data['name']
        if 'prise' in data:
            product.prise = float(data['prise'])
        db.session.commit()
        return jsonify({'message': 'Product was updated(patch) successfully!'})
    elif request.method == 'DELETE':
        db.session.delete(product)
        db.session.commit()
        return jsonify({'message': 'Product was deleted successfully!'})


if __name__ == '__main__':
    app.run(debug=True)
