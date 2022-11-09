from marshmallow import Schema, fields, ValidationError
# from marshmallow_enum import EnumField
from enum import Enum
from flask import Blueprint, jsonify, request
import src.models as models
import src.db as db
from flask_bcrypt import Bcrypt

user_blueprint = Blueprint('user', __name__, url_prefix='/user')
bcrypt = Bcrypt()


@user_blueprint.route('/', methods=['POST'])
def create_user():
    class User(Schema):
        email = fields.Str(required=True)
        password = fields.Str(required=True)
        firstname = fields.Str(required=True)
        lastname = fields.Str(required=True)


    try:
        if not request.json:
            raise ValidationError('Invalid input')
        User().load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400

    new_user_model = models.Users(surname=request.json['lastname'], name=request.json['firstname'],
                                  username=request.json['email'],
                                  password=bcrypt.generate_password_hash(request.json['password']).decode('utf-8'))
    user_already_exists = db.session.query(models.Users).filter(
        models.Users.email == new_user_model.email).count() != 0

    if user_already_exists:
        return jsonify({'Error': 'Duplicate user'}), 401

    try:
        db.session.add(new_user_model)
    except:
        db.session.rollback()
        return jsonify({"Wrong user info"}), 400

    new_user = db.session.query(models.Users).filter_by(email=request.json['email']).first()
    new_PersonalBudget_model = models.PersonalBudgets(id=new_user_model.id, money_amount=0)
    try:
        db.session.add(new_PersonalBudget_model)
    except:
        db.session.rollback()
        return jsonify({"Database error!"}), 405

    db.session.commit()

    res_json = {}

    res_json['id'] = new_user_model.id
    res_json['email'] = new_user_model.email
    res_json['firstname'] = new_user_model.firstname
    res_json['lastname'] = new_user_model.lastname




    return jsonify(res_json), 200


@user_blueprint.route('/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = db.session.query(models.Users).filter_by(id=user_id).first()
    if user is None:
        return jsonify({'Error': 'User with id not found'}), 404

    res_json = {}

    res_json['id'] = user.id
    res_json['email'] = user.email
    res_json['lastname'] = user.lastname
    res_json['firstname'] = user.name
    return jsonify(res_json), 200


@user_blueprint.route('/<int:user_id>', methods=['PATCH'])
def update_user(user_id):
    try:
        class User(Schema):
            email = fields.Str(required=True)
            password = fields.Str(required=True)
            firstname = fields.Str(required=True)
            lastname = fields.Str(required=True)



        if not request.json:
            raise ValidationError('Invalid id supplied')
        User().load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400

    user = db.session.query(models.Users).filter(models.Users.id == user_id).first()
    if user is None:
        return jsonify({'Error': 'User not found'}), 404

    try:
        if 'id' in request.json:
            user.id = request.json['id']
        if 'email' in request.json:
            user.email = request.json['email']
        if 'firstname' in request.json:
            user.name = request.json['firstname']
        if 'lastname' in request.json:
            user.suename = request.json['lastname']
    except:
        db.session.rollback()
        return jsonify({'Error': "Invalid id supplied"}), 400

    db.session.commit()

    return "", 200


@user_blueprint.route('/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = db.session.query(models.Users).filter(models.Users.id == user_id).first()
    if user is None:
        return jsonify({'Error': 'User not found'}), 404

    try:
        db.session.delete(user)
    except:
        db.session.rollback()
        return jsonify({'Error': "Invalid id supplied"}), 400

    db.session.commit()

    return jsonify({'Message': "User removed"}), 200