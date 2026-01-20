from flask_restx import Namespace, Resource, fields
from flask import request
from app.services.user_service import UserService

api = Namespace("users", description="User CRUD Operations")

# Definisi Model untuk Swagger UI
user_response_model = api.model("UserResponse", {
    "id": fields.Integer(readonly=True),
    "name": fields.String(required=True),
    "email": fields.String(required=True),
    "password": fields.String(required=True)
})

@api.route("")
class UserList(Resource):
    @api.marshal_list_with(user_response_model)
    def get(self):
        return UserService.get_all_users()

    @api.expect(user_response_model, validate=True)
    def post(self):
        data = request.json
        user, error = UserService.create_user(
            data["name"],
            data["email"],
            data["password"]
        )
        if error:
            return {"message": error}, 400
        return user, 201

@api.route("/<int:id>")
class UserItem(Resource):
    @api.marshal_with(user_response_model)
    def get(self, id):
        user = UserService.get_user(id)
        if not user:
            api.abort(404, "User tidak ditemukan")
        return user

    @api.expect(user_response_model)
    def put(self, id):
        data = request.json
        user, error = UserService.update_user(
            id,
            data["name"],
            data["email"],
            data["password"]
        )
        if error:
            return {"message": error}, 400
        return user

    def delete(self, id):
        if UserService.delete_user(id):
            return {"message": f"User {id} berhasil dihapus"}, 200
        api.abort(404, "User tidak ditemukan")