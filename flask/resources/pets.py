import sqlalchemy
from flask_restplus import Namespace, reqparse, Resource

from core.response import (
    CustomeResponse,
    return_500_for_sever_error,
    return_401_for_no_auth,
)
from core.models import Pet as PetModel
from core.database import db

api = Namespace("pets", description="pets related operations")

parser_post = reqparse.RequestParser()
parser_post.add_argument("name", type=str, required=True)
parser_post.add_argument("weight", type=int, required=True)
parser_post.add_argument("birthday", type=str, required=True)
parser_post.add_argument("color", type=str, help="CSS HEX", required=True)
parser_post.add_argument("intro", type=str, required=True)

parser_search = reqparse.RequestParser()
parser_search.add_argument("name", type=str, help="pet name")


def creat_pet(pet_columns):
    try:
        pet = PetModel(**pet_columns)
        pet.create()
        return pet, ""
    except sqlalchemy.exc.IntegrityError as e:
        return False, f"Pet name '{pet['name']}' already exsits."


def get_pets(name=None) -> list:
    if name is not None:
        pets = PetModel.query.filter(PetModel.name.like(f"%{name}%"))
    else:
        pets = PetModel.query.all()
    return [pet.serialize for pet in pets]


def get_pet(id_) -> dict:
    pet = PetModel.query.get(id_)
    return pet.serialize if pet else None


def update_pet(id_, name):
    pet = PetModel.query.get(id_)
    pet.name = name
    db.session.commit()


def delete_pet(id_):
    PetModel.query.filter_by(id=id_).delete()
    db.session.commit()


parser_auth = reqparse.RequestParser()
parser_auth.add_argument("Authorization", type=str, location="headers")


@api.route("/")
class Pets(Resource, CustomeResponse):
    @api.doc("Get all pets")
    @api.expect(parser_search)
    @return_500_for_sever_error
    def get(self):
        args = parser_search.parse_args()
        return self.send(response_type="SUCCESS", result=get_pets(name=args["name"]))

    @api.doc("create a new pet")
    @api.expect(parser_post, parser_auth)
    @return_401_for_no_auth
    @return_500_for_sever_error
    def post(self, **kwargs):
        if kwargs["auth_user"].is_admin():
            args = parser_post.parse_args()
            result, message = creat_pet(args)
            if result:
                return self.send(response_type="CREATED", result=result.id)
            return self.send(response_type="FAIL", additional_message=message)
        return self.send(response_type="FORBIDDEN")


@api.route("/<int:id_>")
@api.param("id_", "The pet identifier")
class Pet(Resource, CustomeResponse):
    @return_500_for_sever_error
    def get(self, id_):
        if pet := get_pet(id_):
            return self.send(response_type="SUCCESS", result=pet)
        return self.send(response_type="NOT_FOUND")

    @api.doc("update pet name")
    @api.expect(parser_post, parser_auth)
    @return_401_for_no_auth
    @return_500_for_sever_error
    def put(self, id_, **kwargs):
        if get_pet(id_):
            if kwargs["auth_user"].is_admin():
                args = parser_post.parse_args()
                update_pet(id_, args["name"])
                return self.send(response_type="NO_CONTENT")
            return self.send(response_type="FORBIDDEN")
        return self.send(response_type="NOT_FOUND")

    @api.doc("delete an pet")
    @api.expect(parser_auth)
    @return_401_for_no_auth
    @return_500_for_sever_error
    def delete(self, id_, **kwargs):
        if get_pet(id_):
            if kwargs["auth_user"].is_admin():
                delete_pet(id_)
                return self.send(response_type="NO_CONTENT")
            return self.send(response_type="FORBIDDEN")
        return self.send(response_type="NOT_FOUND")
