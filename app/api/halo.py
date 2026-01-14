from flask_restx import Namespace, Resource, fields
from app.services.halo_service import get_halo, post_halo

api = Namespace("halo", description="Halo API")

post_model = api.model("HaloPost", {
    "nama": fields.String(required=True),
    "message": fields.String(required=True)
})

@api.route("/")
class HaloResource(Resource):

    def get(self):
        return get_halo()

    @api.expect(post_model)
    def post(self):
        payload = api.payload
        return post_halo(payload)
