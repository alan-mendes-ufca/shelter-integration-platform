from flask import Blueprint, request, jsonify

blueprint_example = Blueprint('blueprint_example', __name__, url_prefix='/')

@blueprint_example.route('/hello', methods=['GET'])
def hello():
    """
    A simple endpoint that returns a greeting message.
    """
    name = request.args.get('name', 'World')
    return jsonify({'message': f'Hello, {name}!'})
