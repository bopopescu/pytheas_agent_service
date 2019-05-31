from flask import Flask, request, jsonify, abort
from app.service import Service

app = Flask(__name__)


@app.route('/')
def index():
    return 'OK!(:'


@app.route('/api/get_attractions_for_profile', methods=['GET'])
def get_attractions_for_profile():
    try:
        arg_profile_id = request.args.get('profile_id')
        arg_city_id = request.args.get('city_id')

        if arg_profile_id is None or not is_represent_integer(arg_profile_id):
            abort(401, 'profile_id is missing or invalid.')
        if arg_city_id is not None and not is_represent_integer(arg_city_id):
            abort(401, 'city_id is invalid. If you don''t wish to provide a valid vale, you may ignore this argument.')

        profile_id = int(arg_profile_id)
        city_id = int(arg_profile_id) if arg_profile_id is not None else None
        agent_service = Service()
        result_vector = agent_service.predict_trip_for_profile(profile_id, city_id)
        return jsonify(result_vector)
    except:
        abort(404, 'The server encountered an internal error. The profile or city may be missing')


@app.route('/api/get_tags', methods=['GET'])
def get_top_attraction_tags():
    try:
        agent_service = Service()
        tags = agent_service.get_top_attraction_tags()
        return jsonify(tags)
    except ValueError:
        return ValueError


def is_represent_integer(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


if __name__ == '__main__':
    app.run(port=8080)
