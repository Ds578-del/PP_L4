from marshmallow import Schema, fields, ValidationError
# from marshmallow_enum import EnumField
from enum import Enum
from flask import Blueprint, jsonify, request
import src.models as models
import src.db as db
from src.auth import auth
from flask_bcrypt import Bcrypt

user_blueprint = Blueprint('user', __name__, url_prefix='/user')
bcrypt = Bcrypt()


@user_blueprint.route('/', methods=['POST'])
def create_user():
    class User(Schema):
        username = fields.Str(required=True)
        password = fields.Str(required=True)
        firstName = fields.Str(required=True)
        lastName = fields.Str(required=True)
        balance = fields.Int(required=True)

    try:
        if not request.json:
            raise ValidationError('No input data provided')
        User().load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400

    new_user_model = models.Users(surname=request.json['lastName'], name=request.json['firstName'],
                                  username=request.json['username'],
                                  password=bcrypt.generate_password_hash(request.json['password']).decode('utf-8'))
    user_already_exists = db.session.query(models.Users).filter(
        models.Users.username == new_user_model.username).count() != 0

    if user_already_exists:
        return jsonify({'ERROR': 'User already exists'}), 401

    try:
        db.session.add(new_user_model)
    except:
        db.session.rollback()
        return jsonify({"Incorrect input data"}), 400

    new_user = db.session.query(models.Users).filter_by(username=request.json['username']).first()
    new_PersonalBudget_model = models.PersonalBudgets(id=new_user_model.id, money_amount=request.json["balance"])
    try:
        db.session.add(new_PersonalBudget_model)
    except:
        db.session.rollback()
        return jsonify({"Error with database, user not added"}), 405

    db.session.commit()

    res_json = {}

    res_json['id'] = new_user_model.id
    res_json['lastName'] = new_user_model.surname
    res_json['firstName'] = new_user_model.name
    res_json['username'] = new_user_model.username
    res_json['personal_budget'] = new_user_model.id
    res_json['family_budgets'] = [int(row.family_budget_id) for row in
                                  db.session.query(models.FamilyBudgetsUsers).filter_by(
                                      user_id=new_user_model.id).all()]

    return jsonify(res_json), 200


@user_blueprint.route('/<int:user_id>', methods=['GET'])
@auth.login_required
def get_user(user_id):
    user = db.session.query(models.Users).filter_by(id=user_id).first()
    if user != auth.current_user():
        return jsonify({'error': 'Forbidden'}), 403
    if user is None:
        return jsonify({'ERROR': 'No user budget with this ID'}), 404

    res_json = {}

    res_json['id'] = user.id
    res_json['lastName'] = user.surname
    res_json['firstName'] = user.name
    res_json['username'] = user.username
    res_json['pbudget'] = user.id
    res_json['fbudgets'] = [int(row.family_budget_id) for row in
                            db.session.query(models.FamilyBudgetsUsers).filter_by(user_id=user_id).all()]

    return jsonify(res_json), 200


@user_blueprint.route('/<int:user_id>', methods=['PUT'])
@auth.login_required
def update_user(user_id):
    try:
        class User(Schema):
            username = fields.Str(required=True)
            password = fields.Str(required=True)
            firstName = fields.Str(required=True)
            lastName = fields.Str(required=True)

        if not request.json:
            raise ValidationError('No input data provided')
        User().load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400

    user = db.session.query(models.Users).filter(models.Users.id == user_id).first()
    user_n = db.session.query(models.Users).filter(models.Users.username == request.json['username']).first()
    if user != auth.current_user():
        return jsonify({'error': 'Unauthorized access'}), 401
    if user is None:
        return jsonify({'ERROR': 'No user with this ID'}), 404

    try:
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
    except:
        db.session.rollback()
        return jsonify({'ERROR': "User data is not valid"}), 400

    db.session.commit()

    return "", 200


@user_blueprint.route('/<int:user_id>', methods=['DELETE'])
@auth.login_required
def delete_user(user_id):
    user = db.session.query(models.Users).filter(models.Users.id == user_id).first()
    if user != auth.current_user():
        return jsonify({'error': 'Unauthorized access'}), 401
    if user is None:
        return jsonify({'ERROR': 'User does not exist'}), 404

    try:
        db.session.delete(user)
    except:
        db.session.rollback()
        return jsonify({'ERROR': "Incorrect input data"}), 400

    db.session.commit()

    return jsonify({'message': "Successfully deleted"}), 200