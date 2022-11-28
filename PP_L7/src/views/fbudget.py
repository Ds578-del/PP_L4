from marshmallow import ValidationError
from datetime import datetime
from flask import Blueprint, jsonify, request
import src.models as models
import src.db as db
from flask_bcrypt import Bcrypt
from src.auth import auth
from src.schemas import *

family_budgets_blueprint = Blueprint('FamilyBudgets', __name__, url_prefix='/family_budget')
bcrypt = Bcrypt()


@family_budgets_blueprint.route('/', methods=['POST'])
@auth.login_required
def create_new_familybudget():
    try:
        if not request.json:
            raise ValidationError('No input data provided')
        MembersIds().load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400

    family_budget = models.FamilyBudgets()

    db.session.add(family_budget)
    db.session.commit()

    if auth.current_user().id not in request.json['members_ids']:
        request.json['members_ids'].append(auth.current_user().id)

    for members_ids in request.json['members_ids']:
        family_budget_user = models.FamilyBudgetsUsers(family_budget_id=family_budget.id, user_id=members_ids)
        db.session.add(family_budget_user)

    db.session.commit()

    res = {'id': family_budget.id, 'money_amount': family_budget.money_amount, "members": request.json['members_ids']}

    return jsonify(res), 200


@family_budgets_blueprint.route('/<int:family_budget_id>', methods=['GET'])
@auth.login_required
def get_familybudget(family_budget_id):
    family_budget = db.session.query(models.FamilyBudgets).filter_by(id=family_budget_id).first()
    if family_budget is None:
        return jsonify({'error': 'Budget not found'}), 404

    members = [int(row.user_id) for row in
               db.session.query(models.FamilyBudgetsUsers).filter_by(family_budget_id=family_budget_id).all()]

    if auth.current_user().id not in members:
        return jsonify({'error': 'You are not a member of this budget'}), 403

    res = {'id': family_budget.id, 'money_amount': family_budget.money_amount, "members": request.json['members_ids']}

    return jsonify(res), 200


@family_budgets_blueprint.route('/<int:family_budget_id>', methods=['DELETE'])
@auth.login_required
def delete_familybudget(family_budget_id):
    family_budget = db.session.query(models.FamilyBudgets).filter_by(id=family_budget_id).first()
    if family_budget is None:
        return jsonify({'error': 'Family budget not found'}), 404

    members = [int(row.user_id) for row in
               db.session.query(models.FamilyBudgetsUsers).filter_by(family_budget_id=family_budget_id).all()]
    if auth.current_user().id not in members:
        return jsonify({'error': 'You are not a member of this budget'}), 403

    db.session.delete(family_budget)
    db.session.commit()

    return "Success", 200


@family_budgets_blueprint.route('/<int:family_budgets_id>/info', methods=['GET'])
@auth.login_required
def get_familybudget_report(family_budgets_id):
    family_budget = db.session.query(models.FamilyBudgets).filter_by(id=family_budgets_id).first()
    if family_budget is None:
        return jsonify({'error': 'Budget not found'}), 404

    members = [int(row.user_id) for row in
               db.session.query(models.FamilyBudgetsUsers).filter_by(family_budget_id=family_budgets_id).all()]
    if auth.current_user().id not in members:
        return jsonify({'error': 'You are not a member of this budget'}), 403

    report_sender = db.session.query(models.Operation).filter(
        models.Operation.sender_id == family_budgets_id and models.Operation.sender_type == "personal").all()
    report_receiver = db.session.query(models.Operation).filter(
        models.Operation.receiver_id == family_budgets_id and models.Operation.receiver_type == "personal").all()

    if report_sender is None and report_receiver is None:
        return jsonify({'error': 'This budget has no operations'}), 405

    report_json = []

    for el in report_sender:
        res = {'id': el.id, 'sender_id': el.sender_id, "receiver_id": el.receiver_id,
               "sender_type": el.sender_type, "money_amount": el.money_amount, "date": el.date}

        report_json.append(res)

    return jsonify(report_json), 200


@family_budgets_blueprint.route('/<int:family_budget_id>/transaction', methods=['POST'])
@auth.login_required
def post_familybudget_transfer(family_budget_id):
    family_budget = db.session.query(models.FamilyBudgets).filter_by(id=family_budget_id).first()

    if family_budget is None:
        return jsonify({'error': 'Family budget not found'}), 404

    members = [int(row.user_id) for row in
               db.session.query(models.FamilyBudgetsUsers).filter_by(family_budget_id=family_budget_id).all()]

    if auth.current_user().id not in members:
        return jsonify({'error': 'You are not a member of this budget'}), 403

    try:
        if not request.json:
            raise ValidationError('No input data provided')
        Transfer().load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400

    if request.json['money_amount'] < 0.1:
        return jsonify({'error': 'Money amount couldn`t be less than 0.1'}), 407

    if family_budget.money_amount < request.json['money_amount']:
        return jsonify({'error': 'Not enough money'}), 406

    operation = models.Operation(sender_id=family_budget_id, receiver_id=request.json['receiver_budget_id'],
                                 sender_type="personal", receiver_type=request.json['receiver_type'],
                                 money_amount=request.json['money_amount'], date=datetime.now())

    db.session.add(operation)

    receiver_budget = db.session.query(models.FamilyBudgets).filter_by(id=request.json['receiver_budget_id']).first()

    if receiver_budget is None:
        return jsonify({'error': 'Receiving budget doesn`t exist'}), 408

    receiver_budget.money_amount = receiver_budget.money_amount + request.json['money_amount']
    family_budget.money_amount = family_budget.money_amount - request.json['money_amount']

    db.session.commit()

    res = {'id': operation.id, 'sender_id': operation.sender_id, "receiver_id": operation.receiver_id,
           "sender_type": operation.sender_type, "receiver_type": operation.receiver_type,
           "money_amount": operation.money_amount, "date": operation.date}

    return jsonify(res), 200
