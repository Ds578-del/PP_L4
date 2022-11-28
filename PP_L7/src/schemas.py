from marshmallow import Schema, fields


class CreateUser(Schema):
    username = fields.Str(required=True)
    password = fields.Str(required=True)
    firstName = fields.Str(required=True)
    lastName = fields.Str(required=True)
    balance = fields.Int(required=True)


class UpdateUser(Schema):
    username = fields.Str(required=True)
    password = fields.Str(required=True)
    firstName = fields.Str(required=True)
    lastName = fields.Str(required=True)


class Transfer(Schema):
    receiver_budget_id = fields.Int(required=True)
    receiver_type = fields.Str(required=True)
    money_amount = fields.Int(required=True)


class MembersIds(Schema):
    members_ids = fields.List(fields.Int(), required=True)
