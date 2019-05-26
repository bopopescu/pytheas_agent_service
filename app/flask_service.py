from flask import Flask, request, jsonify
from app.service import Service
#from app.business_logic import  BusinessLogic
app = Flask(__name__)


@app.route('/')
def index():
	return 'OK!(:'


@app.route('/aa')
def index1():
	aaa = Service()
	#agent_service = Service()
	return 'OK1111!'


'''
@app.route('/a')
def get_attractions_for_profile():
    profile_id = int(request.args.get('ProfileId'))
    city_id = int(request.args.get('CityId')) if request.args.get('CityId') is not None else None
    agent_service = Service()
    result_vector = agent_service.predict_trip_for_profile(profile_id, city_id)
    return jsonify({'Results': result_vector})
'''

if __name__ == '__main__':
    app.run()
