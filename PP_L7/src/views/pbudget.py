from marshmallow import ValidationError
from datetime import datetime
from flask import Blueprint, request
import src.db as db
from flask_bcrypt import Bcrypt
from src.auth import auth
from src.utils import *
from src.schemas import *

personal_budgets_blueprint = Blueprint('PersonalBudgets', __name__, url_prefix='/personal_budget')
bcrypt = Bcrypt()


@personal_budgets_blueprint.route('/<int:personal_budget_id>', methods=['GET'])
@auth.login_required
def get_personal_budget(personal_budget_id):
    if personal_budget_id != auth.current_user().id:
        return jsonify({'error': 'Forbidden'}), 403

    personal_budget = db.session.query(models.PersonalBudgets).filter_by(id=personal_budget_id).first()

    if personal_budget is None:
        return jsonify({'error': 'Budget not found'}), 404

    return from_personal_model_to_json(personal_budget), 200


@personal_budgets_blueprint.route('/<int:personal_budget_id>/info', methods=['GET'])
@auth.login_required
def get_personal_budget_report(personal_budget_id):
    if personal_budget_id != auth.current_user().id:
        return jsonify({'error': 'Forbidden'}), 403

    report_sender = db.session.query(models.Operation).filter(
        models.Operation.sender_id == personal_budget_id and models.Operation.sender_type == "personal").all()
    report_receiver = db.session.query(models.Operation).filter(
        models.Operation.receiver_id == personal_budget_id and models.Operation.receiver_type == "personal").all()

    if report_sender is None and report_receiver is None:
        return jsonify({'error': 'This budget has no operations'}), 405

    report_json = []

    for el in report_sender:
        res = {'id': el.id, 'sender_id': el.sender_id, "receiver_id": el.receiver_id,
               "sender_type": el.sender_type, "money_amount": el.money_amount, "date": el.date}

        report_json.append(res)

    return jsonify(report_json), 200


@personal_budgets_blueprint.route('/<int:personal_budget_id>/transaction', methods=['POST'])
@auth.login_required
def post_personal_budget_transfer(personal_budget_id):
    if personal_budget_id != auth.current_user().id:
        return jsonify({'error': 'Forbidden'}), 403

    personalBudget = db.session.query(models.PersonalBudgets).filter_by(id=personal_budget_id).first()
    if personalBudget is None:
        return jsonify({'error': 'User not found'}), 404

    try:
        if not request.json:
            raise ValidationError('No input data provided')
        Transfer().load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400

    if request.json['money_amount'] < 0.1:
        return jsonify({'error': 'No money amount less than 0.1'}), 400

    if personalBudget.money_amount < request.json['money_amount']:
        return jsonify({'error': 'Not enough money'}), 400

    operation = models.Operation(sender_id=personal_budget_id, receiver_id=request.json['receiver_budget_id'],
                                 sender_type="personal", receiver_type=request.json['receiver_type'],
                                 money_amount=request.json['money_amount'], date=datetime.now())

    db.session.add(operation)

    receiver_budget = db.session.query(models.FamilyBudgets).filter_by(id=request.json['receiver_budget_id']).first()

    if receiver_budget is None:
        return jsonify({'error': 'Receiving budget doesn`t exist'}), 408

    receiver_budget.money_amount = receiver_budget.money_amount + request.json['money_amount']

    personalBudget.money_amount = personalBudget.money_amount - request.json['money_amount']
    db.session.commit()

    res = {'id': operation.id, 'sender_id': operation.sender_id, "receiver_id": operation.receiver_id,
           "sender_type": operation.sender_type, "receiver_type": operation.receiver_type,
           "money_amount": operation.money_amount, "date": operation.date}

    return jsonify(res), 200
