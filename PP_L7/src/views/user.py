from marshmallow import ValidationError
from flask import Blueprint, jsonify, request
import src.models as models
import src.db as db
from src.auth import auth
from src.schemas import *
from flask_bcrypt import Bcrypt

user_blueprint = Blueprint('user', __name__, url_prefix='/user')
bcrypt = Bcrypt()


@user_blueprint.route('/', methods=['POST'])
def create_user():
    try:
        if not request.json:
            raise ValidationError('Wrong input data')
        CreateUser().load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400

    new_user_model = models.Users(surname=request.json['lastName'], name=request.json['firstName'],
                                  username=request.json['username'],
                                  password=bcrypt.generate_password_hash(request.json['password']).decode('utf-8'))
    user_already_exists = db.session.query(models.Users).filter(
        models.Users.username == new_user_model.username).count() != 0

    if user_already_exists:
        return jsonify({'error': 'User already exists'}), 401

    db.session.add(new_user_model)

    new_PersonalBudget_model = models.PersonalBudgets(id=new_user_model.id, money_amount=request.json["balance"])

    db.session.add(new_PersonalBudget_model)
    db.session.commit()

    return "Success", 200


@user_blueprint.route('/<int:user_id>', methods=['GET'])
@auth.login_required
def get_user(user_id):
    user = db.session.query(models.Users).filter_by(id=user_id).first()
    if user != auth.current_user():
        return jsonify({'error': 'Forbidden'}), 403
    if user is None:
        return jsonify({'error': 'No user budget with this id'}), 404

    res = {'id': user.id, 'username': user.username, "firstName": user.name,
           "lastName": user.surname, "pbudget": user.id, "fbudgets": [int(row.family_budget_id) for row in
                                                                      db.session.query(
                                                                          models.FamilyBudgetsUsers).filter_by(
                                                                          user_id=user_id).all()]}
    return jsonify(res), 200


@user_blueprint.route('/<int:user_id>', methods=['PUT'])
@auth.login_required
def update_user(user_id):
    try:
        if not request.json:
            raise ValidationError('Wrong input data')
        UpdateUser().load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400

    user = db.session.query(models.Users).filter(models.Users.id == user_id).first()
    user_n = db.session.query(models.Users).filter(models.Users.username == request.json['username']).first()

    if user != auth.current_user():
        return jsonify({'error': 'Unauthorized access'}), 401
    if user is None:
        return jsonify({'error': 'No user with this id'}), 404
    if user_n is not None:
        return jsonify({'message': 'User already exists'}), 400

    if 'username' in request.json:
        user.username = request.json['username']
    if 'firstName' in request.json:
        user.name = request.json['firstName']
    if 'password' in request.json:
        user.password = bcrypt.generate_password_hash(request.json['password']).decode('utf-8')
    if 'lastName' in request.json:
        user.surname = request.json['lastName']

    db.session.commit()

    return "Success", 200


@user_blueprint.route('/<int:user_id>', methods=['DELETE'])
@auth.login_required
def delete_user(user_id):
    user = db.session.query(models.Users).filter(models.Users.id == user_id).first()

    if user != auth.current_user():
        return jsonify({'error': 'Unauthorized access'}), 401
    if user is None:
        return jsonify({'error': 'User does not exist'}), 404

    db.session.delete(user)
    db.session.commit()

    return "Success", 200
