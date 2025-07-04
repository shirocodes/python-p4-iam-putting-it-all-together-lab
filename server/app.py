from flask import request, session, jsonify, make_response
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe

class Signup(Resource):
    def post(self):
        json = request.get_json()
        try:
            new_user = User(
                username=json.get('username'),
                image_url=json.get('image_url'),
                bio=json.get('bio')
            )
            new_user.password_hash = json.get('password')

            db.session.add(new_user)
            db.session.commit()

            session['user_id'] = new_user.id
            return new_user.to_dict(), 201
        except (IntegrityError, ValueError) as e:
            db.session.rollback()
            return {"errors": [str(e)]}, 422

class CheckSession(Resource):
    def get(self):
        user_id = session.get("user_id")
        if user_id:
            user = User.query.get(user_id)
            if user:
                return user.to_dict(), 200
        return {"error": "Unauthorized"}, 401

class Login(Resource):
    def post(self):
        json = request.get_json()
        user = User.query.filter_by(username=json.get("username")).first()

        if user and user.authenticate(json.get("password")):
            session['user_id'] = user.id
            return user.to_dict(), 200

        return {"error": "Invalid username or password"}, 401

class Logout(Resource):
    def delete(self):
        if session.get("user_id"):
            session['user_id'] = None
            return {}, 204
        return {"error": "Unauthorized"}, 401

class RecipeIndex(Resource):
    def get(self):
        if not session.get("user_id"):
            return {"error": "Unauthorized"}, 401

        recipes = Recipe.query.all()
        return [r.to_dict() for r in recipes], 200

    def post(self):
        if not session.get("user_id"):
            return {"error": "Unauthorized"}, 401

        json = request.get_json()
        try:
            new_recipe = Recipe(
                title=json.get("title"),
                instructions=json.get("instructions"),
                minutes_to_complete=json.get("minutes_to_complete"),
                user_id=session.get("user_id")
            )

            db.session.add(new_recipe)
            db.session.commit()

            return new_recipe.to_dict(), 201

        except (IntegrityError, ValueError) as e:
            db.session.rollback()
            return {"errors": [str(e)]}, 422

api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')

if __name__ == '__main__':
    app.run(port=5555, debug=True)