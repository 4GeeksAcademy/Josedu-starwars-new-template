"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, People, Planets, FavoritePlanets, FavoritePeople
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET'])
def get_users():
    all_users = User.query.all()
    results = list(map(lambda usuario: usuario.serialize(),all_users)) 
    return jsonify(results), 200

@app.route('/user/<int:user_id>', methods=['GET'])
def get_user_id(user_id):
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return jsonify({'message': 'User not found'}), 404
    return jsonify(user.serialize()), 200

@app.route('/people', methods=['GET'])
def get_people():
    all_people = People.query.all()
    results = list(map(lambda usuario: usuario.serialize(),all_people)) 
    return jsonify(results), 200

@app.route('/people/<int:person_id>', methods=['GET'])
def get_people_id(person_id):
    print(person_id)
    person = People.query.filter_by(id=person_id).first() 

    return jsonify(person.serialize()), 200

@app.route('/planets', methods=['GET'])
def get_planets():
    all_planets = Planets.query.all()
    results = list(map(lambda usuario: usuario.serialize(),all_planets)) 
    return jsonify(results), 200

@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_plnnet_id(planet_id):
    print(planet_id)
    planet = Planets.query.filter_by(id=planet_id).first() 

    return jsonify(planet.serialize()), 200


USER_ID = 1  

@app.route('/user/favorites', methods=['GET'])
def get_user_favorites():
    favorite_people = FavoritePeople.query.all()
    favorite_planets = FavoritePlanets.query.all()
    people_results = list(map(lambda favorite: favorite.serialize(), favorite_people))
    planets_results = list(map(lambda favorite: favorite.serialize(), favorite_planets))
    results = {
        "favorite_people": people_results,
        "favorite_planets": planets_results
    }
    
    return jsonify(results), 200



@app.route('/favorite/planet/<int:planet_id>/<int:user_id>', methods=['POST'])
def add_favorite_planet(planet_id, user_id):
    planet = Planets.query.filter_by(id=planet_id).first()
    if not planet:
        return jsonify({'message': 'Planet not found'}), 404  
    new_favorite = FavoritePlanets(user_id=user_id, planet_id=planet_id)
    db.session.add(new_favorite)
    db.session.commit()
    return jsonify(new_favorite.serialize()), 201 

@app.route('/favorite/people/<int:people_id>/<int:user_id>', methods=['POST'])
def add_favorite_people(people_id, user_id):
    person = People.query.filter_by(id=people_id).first()
    if not person:
        return jsonify({'message': 'Person not found'}), 404  
    new_favorite = FavoritePeople(user_id=user_id, people_id=people_id)
    db.session.add(new_favorite)
    db.session.commit()
    return jsonify(new_favorite.serialize()), 201 

@app.route('/favorite/planet/<int:planet_id>/<int:user_id>', methods=['DELETE'])
def delete_favorite_planet(planet_id, user_id):
    favorite = FavoritePlanets.query.filter_by(user_id=user_id, planet_id=planet_id).first()
    if favorite:
        db.session.delete(favorite)
        db.session.commit()
        return jsonify({'message': 'Favorite planet deleted'}), 200
    return jsonify({'message': 'Favorite planet not found'}), 404

@app.route('/favorite/people/<int:people_id>/<int:user_id>', methods=['DELETE'])
def delete_favorite_people(people_id, user_id):
    favorite = FavoritePeople.query.filter_by(user_id=user_id, people_id=people_id).first()
    if favorite:
        db.session.delete(favorite)
        db.session.commit()
        return jsonify({'message': 'Favorite person deleted'}), 200
    return jsonify({'message': 'Favorite person not found'}), 404


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
