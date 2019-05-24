from flask import Flask, render_template
from flask import jsonify
from service import Service
app = Flask(__name__)


@app.route('/')
def index():
    return 'bad request'


@app.route('/get_attractions_for_profile/<profile_id>', methods=['GET'])
def get_attractions_for_profile(profile_id, city_id=None):
    agent_service = Service()
    result_vector = agent_service.predict_trip_for_profile(profile_id, city_id)
    return jsonify({'Results': result_vector})
