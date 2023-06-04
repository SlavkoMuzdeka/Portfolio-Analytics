from functools import wraps
import os, json
from flask import Flask, request, abort, jsonify
from flask_cors import CORS
from urllib.request import urlopen
from jose import jwt
from models import AssetPriceHistory, Portfolio, setup_db

AUTH0_DOMAIN = os.environ['AUTH0_DOMAIN']
API_AUDIENCE = os.environ['API_AUDIENCE'] 
ALGORITHMS = ['RS256']


def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  CORS(app)
  return app


app = create_app()


class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


def get_token_auth_header():
    """Obtains the Access Token from the Authorization Header
    """
    auth = request.headers.get('Authorization', None)
    if not auth:
        raise AuthError({
            'code': 'authorization_header_missing',
            'description': 'Authorization header is expected.'
        }, 401)
    
    parts = auth.split()

    if parts[0].lower() != 'bearer':
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization header must start with "Bearer".'
        }, 401)
    elif len(parts) == 1:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Token not found.'
        }, 401)
    elif len(parts) > 2:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization header must be bearer token.'
        }, 401)
    
    token = parts[1]
    return token


def verify_decode_jwt(token):
    jsonurl = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
    jwks = json.loads(jsonurl.read())
    unverified_header = jwt.get_unverified_header(token)
    rsa_key = {}
    if 'kid' not in unverified_header:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization malformed.'
        }, 401)

    for key in jwks['keys']:
        if key['kid'] == unverified_header['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
            }

    if rsa_key:
        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer='https://' + AUTH0_DOMAIN + '/'
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise AuthError({
                'code': 'token_expired',
                'description': 'Token expired.'
            }, 401)
        except jwt.JWTClaimsError:
            raise AuthError({
                'code': 'invalid_claims',
                'description': 'Incorrect claims. Please, check the audience and issuer.'
            }, 401)
        except Exception as e:
            raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to parse authentication token.'
            }, 400)
    raise AuthError({
        'code': 'invalid_header',
                'description': 'Unable to find the appropriate key.'
    }, 400)


def check_permissions(permission, payload):
    if 'permissions' not in payload:
        raise AuthError({
            'code': 'invalid_claims',
            'description': 'Permissions not included in JWT.'
        }, 400)

    if permission not in payload['permissions']:
        raise AuthError({
            'code': 'unauthorized',
            'description': 'Permission not found.'
        }, 403)
    return True


def requires_auth(permission=''):
    def requires_auth_decorater(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_token_auth_header()
            try:
                payload = verify_decode_jwt(token)
                check_permissions(permission, payload)
            except Exception as e:
                abort(401)
            return f(payload, *args, **kwargs)

        return wrapper
    return requires_auth_decorater


@app.route('/portfolios', methods=['GET'])
@requires_auth('get:portfolios')
def get_portfolios(jwt):
    portfolios = Portfolio.query.all()

    if len(portfolios) == 0:
        abort(404)

    return jsonify({
        'success': True,
        'portfolios': [portfolio.format() for portfolio in portfolios]
    }), 200


@app.route('/asset_price_histories', methods=['GET'])
@requires_auth('get:asset_price_histories')
def get_asset_price_histories(jwt):
    asset_price_histories = AssetPriceHistory.query.all()
    
    if len(asset_price_histories) == 0:
        abort(404) 
    
    return jsonify({
        'success': True,
        'asset_price_histories': [asset_price_history.format() for asset_price_history in asset_price_histories]
    }), 200


@app.route('/portfolios', methods=['POST'])
@requires_auth('post:portfolios')
def create_portfolio(jwt):
    body = request.get_json()

    if not('asset_class_desc' in body and 'weight' in body and 'benchmark_desc' in body and 'sort_id' in body and 'bloomberg_qry' in body):
        abort(422)

    asset_class_desc = body.get('asset_class_desc')
    weight = body.get('weight')
    benchmark_desc = body.get('benchmark_desc')
    sort_id = body.get('sort_id')
    bloomberg_qry = body.get('bloomberg_qry')

    try:
        portfolio = Portfolio(asset_class_desc, weight, benchmark_desc, sort_id, bloomberg_qry)
        portfolio.insert()

        return jsonify({
            'success': True,
            'created': portfolio.id
        }), 200
    except:
        abort(422)


@app.route('/asset_price_histories/<int:id>/edit', methods=['PATCH'])
@requires_auth('patch:asset_price_histories')
def edit_asset_price_history(jwt, id):
    body = request.get_json()
    asset_price_history = AssetPriceHistory.query.filter(AssetPriceHistory.id == id).one_or_none()

    if not asset_price_history:
        abort(404)

    if not('asset_type' in body and 'price' in body and 'date' in body and 'portfolio_id' in body):
        abort(422)

    asset_type = body.get('asset_type')
    price = body.get('price')
    date = body.get('date')
    portfolio_id = body.get('portfolio_id')

    try:
        if asset_type:
            asset_price_history.asset_type = asset_type
        if price:
            asset_price_history.price = price
        if date:
            asset_price_history.date = date
        if portfolio_id:
            asset_price_history.portfolio_id = portfolio_id
        asset_price_history.update()

        return jsonify({
            'success': True,
            'updated': asset_price_history.id
        }), 200
    except:
        abort(422)


@app.route('/portfolios/<int:id>', methods=['DELETE'])
@requires_auth('delete:portfolios')
def delete_portfolio(jwt, id):
    try:
        portfolio = Portfolio.query.filter(Portfolio.id == id).one_or_none()
        if portfolio is None:
            abort(404)

        try:
            portfolio.delete()
        except:
            abort(403)

        return jsonify({
            'success': True,
            'deleted': id
        }), 200
    except:
        abort(422)


# Error Handling

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": error.error['description']
    }), error.status_code


@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": 'Unathorized'
    }), 401


@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": 'Internal Server Error'
    }), 500


@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": 'Bad Request'
    }), 400


@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        "success": False,
        "error": 405,
        "message": 'Method Not Allowed'
    }), 405


@app.errorhandler(403)
def unauthorized(error):
    return jsonify({
        "success": False,
        "error": 403,
        "message": 'Forbidden'
    }), 403


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)