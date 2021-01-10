from werkzeug.exceptions import abort

from app import app
from flask import jsonify, request, url_for, make_response
from models import User, Advert
from app import db
from auth import auth
import apierrors

from validator import validate
from schema import USER_CREATE, ADVERT_CREATE


#User Registration
@app.route('/api/v1/users', methods = ['POST'])
@validate('json', USER_CREATE)
def new_user():
    username = request.json.get('username')
    password = request.json.get('password')
    email = request.json.get('email')
    if username is None or password is None:
        abort(400) # 400 плохой запрос
    if User.query.filter_by(username = username).first() is not None:
        abort(400) # existing user
    user = User(username = username)
    user.set_password(password)
    user.email=email
    db.session.add(user)
    db.session.commit()
    return jsonify({'username': user.username, 'email': user.email}), 201
    #return jsonify({ 'username': user.username, 'email': user.email }), 201, {'Location': url_for('new_user', id = user.id, _external = True)}

#User info - all
@app.route('/api/v1/users', methods = ['GET'])
@auth.login_required
def user_list():

    # проверка авторизации
    if request.authorization is None:
        abort(401)  # not authorization

    #проверка на администратора
    username = request.authorization.username
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(401)  # user is not exist
    else:
        if not user.is_admin:
            abort(401) # user is not admin

    users_resp=[]
    users=User.query.all()
    for user in users:
        users_resp.append({user.username: user.email})
    return jsonify({ 'users': users_resp }), {'Status': '200'}

#User info - id
# только администратор имеет право получать инфо
@app.route('/api/v1/users/<int:id>', methods = ['GET'])
@auth.login_required
def get_user(id):
    # проверка авторизации
    if request.authorization is None:
        abort(401)  # not authorization

    #проверка на администратора
    username = request.authorization.username
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(401)  # user is not exist
    else:
        if not user.is_admin:
            abort(401) # user is not admin

    #user=User.query.filter_by(id=id).first()
    user = User.query.get(id)
    if user != None:
        return jsonify({ 'user': user.username }), 200
    else:
        abort(404) # нет такого ресурса

#Advert publication
@app.route('/api/v1/adverts', methods = ['POST'])
@validate('json', ADVERT_CREATE)
@auth.login_required
def new_advert():
    #публиковать объявления могут только зарегистрированные пользователи
    user=request.authorization.username
    if user is None:
        abort(401) # 401 (Unauthorized - Неавторизован)

    username=User.query.filter_by(username = user).first()
    if username is None:
        abort(401) # 401 (Unauthorized - Неавторизован)

    advert=Advert()
    title=request.json.get('title')
    advert.title=title
    body=request.json.get('body')
    advert.body=body
    advert.author=username

    db.session.add(advert)
    db.session.commit()

    json_resp=jsonify({'username': user, 'title': title, 'body': body})
    return json_resp, 201

#Delete publication
@app.route('/api/v1/advert_del/<int:id>', methods = ['DELETE'])
@auth.login_required
def del_advert(id):
    #проверка пользователя
    username = request.authorization.username
    user = User.query.filter_by(username=username).first()
    if username is None:
        abort(400)  # user is not exist

    #проверка существования объявления с номером id
    adv=Advert.query.filter_by(id = id).first()
    if adv == None:
        abort(404)  # advert is not exist

    #Удалять/редактировать может только владелец объявления
    if adv.author != user:
        abort(401)  # user is not author of this advert

    else:
        db.session.delete(adv)
        db.session.commit()
        return jsonify({'Advert': adv.title}), {'Status': '204'}


#Delete publication
@app.route('/api/v1/advert_update/<int:id>', methods = ['PUT'])
@auth.login_required
def update_advert(id):
    # проверка авторизации
    if request.authorization is None:
        abort(401)  # not authorization

    #проверка пользователя
    username = request.authorization.username
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(401)  # not authorization

    #проверка существования объявления с номером id
    adv=Advert.query.filter_by(id = id).first()
    if adv == None:
        abort(404)  # advert is not exist

    #Удалять/редактировать может только владелец объявления
    if adv.author != user:
        abort(401)  # user is not author of this advert

    else:
        title = request.json.get('title')
        adv.title = title
        body = request.json.get('body')
        adv.body = body

        db.session.add(adv)
        db.session.commit()
        return jsonify({'Advert': adv.title}), {'Status': '200'}


# Get advert of User - all
# пользователь может видеть только свои объявления - admin все!!
@app.route('/api/v1/adverts', methods = ['GET'])
@auth.login_required
def adverts_list():

    #проверка авторизации
    if request.authorization is None:
        abort(401)  # not authorization

    # проверка пользователя
    username = request.authorization.username
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(401)  # user is not exist

    adverts_resp=[]
    adverts=Advert.query.all()
    for ad in adverts:
        if ad.author == user or user.is_admin:
            adverts_resp.append({ad.id: ad.title})
    return jsonify({ 'adverts': adverts_resp }), {'Status': '200'}


# Get advert of User
# пользователь может видеть только свои объявления - admin все!!
@app.route('/api/v1/adverts/<int:id>', methods = ['GET'])
@auth.login_required
def get_advert_by_id(id):
    #проверка авторизации
    if request.authorization is None:
        abort(401)  # not authorization

    # проверка пользователя
    username = request.authorization.username
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(401)  # user is not exist

    advert=Advert.query.get(id)
    if advert == None:
        abort(404)  # нет такого ресурса

    if advert.author == user or user.is_admin:
        return jsonify({ 'advert title': advert.title}, { 'advert body': advert.body }), {'Status': '200'}
    else:
        abort(401)


