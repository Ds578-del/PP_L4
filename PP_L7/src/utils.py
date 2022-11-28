import src.models as models
from flask import jsonify


def from_personal_model_to_json(personal_budget: models.PersonalBudgets):
    personal_budgets_json = {}

    personal_budgets_json['id'] = personal_budget.id
    personal_budgets_json['money_amount'] = personal_budget.money_amount

    return jsonify(personal_budgets_json)
