from flask import Blueprint, jsonify
from flask import redirect
from flask import request
from flask import session
from flask import current_app
from flask import render_template
import random
import re
from datetime import datetime

from utils.captcha.captcha import captcha
from utils.qiniu_xjzx import upload_pic
# from utils.ytx_sdk.CCPRestSDK import REST
# # from utils.ytx_sdk import ConfigParser
from utils.ytx_sdk.ytx_sms_code import sendTemplateSMS
from utils.decorator import is_login
from models import UserInfo, db, NewsInfo
from flask import make_response


user_blueprint = Blueprint("user", __name__, url_prefix="/user")


@user_blueprint.route("/register", methods=["POST"])
def register():
    """注册视图"""
    post_dict = request.form
    phone = post_dict.get("mobile")
    img_code = post_dict.get("code_pwd").upper()
    agree = post_dict.get("agree")
    pwd = post_dict.get("password")
    sms_code = int(post_dict.get("smscode"))

    # 验证数据是否为空
    if not all([phone, img_code, pwd]):
        return "404 请求错误", 400
    # 验证手机号是否已经被注册
    user = UserInfo.query.filter_by(phone=phone).first()
    if user:
        return "404 请求错误", 400
    # 验证密码是否合法
    if len(pwd) < 6 or len(pwd) > 20:
        return "404 请求错误", 400
    # 验证是否勾选同意
    if agree != "true":
        return "404 请求错误", 400
    print(session.get(phone))
    # 验证手机验证码是否正确
    if sms_code != session.get(phone):
        return jsonify(res=3)

    # 检查验证码是否正确
    print(session.get("img_code"))
    if session.get("img_code") == img_code:
        user = UserInfo()
        user.phone = phone
        user.password = pwd
        user.username = phone
        try:
            db.session.add(user)
            db.session.commit()
        except:
            current_app.logger_xjzx.error("注册账号时连接数据库出错")
            return jsonify(res=2)
        return jsonify(res=1)
    else:
        return jsonify(res=0)


@user_blueprint.route('/user_exist')
def user_exist():
    """验证手机号是否已经被注册"""
    phone = request.args.get("mobile")
    user = UserInfo.query.filter_by(phone=phone).first()
    if user:
        return jsonify(res=0)
    else:
        return jsonify(res=1)


@user_blueprint.route('/get_img_code')
def get_img_code():
    """验证码生成"""
    name, img_code, img = captcha.generate_captcha()
    response = make_response(img)
    response.mimetype = "image/png"
    session["img_code"] = img_code
    print("图片验证码:", img_code)
    return response

@user_blueprint.route("/get_sms_code")
def get_sms_code():
    """发送短信验证码"""
    get_dict = request.args
    img_code = get_dict.get("img_code").upper()
    phone = get_dict.get("mobile")
    # 验证数据是否为空
    if not all([img_code, phone]):
        return "", 400

    if not re.match(r"^[1][3,4,5,7,8][0-9]{9}$", phone).group():
        return "", 400
    print(session.get("img_code"),img_code)
    if img_code != session.get("img_code"):
        return jsonify(res=0)
    sms_code = random.randint(1000,9999)
    session[phone] = sms_code
    print("sms_code:", sms_code)
    # sendTemplateSMS("18818777125", [sms_code, 5], 1)
    return jsonify(res=1)



@user_blueprint.route("/login", methods=["POST"])
def login():
    """响应登陆操作"""
    post_dict = request.form
    pwd = post_dict.get("pwd")
    phone = post_dict.get("mobile")

    # 验证数据是否为空
    if not all([pwd, phone]):
        return "404 请求错误", 400

    # 验证手机号是否为11位
    # print(re.match(r"^[1][3,4,5,7,8][0-9]{9}$", phone).group())
    if not re.match(r"^[1][3,4,5,7,8][0-9]{9}$", phone).group():
        return jsonify(res=3)

    # 验证密码是否合法
    if len(pwd) < 6 or len(pwd) > 20:
        return "404 请求错误", 400


    # 检查用户名是否存在
    user = UserInfo.query.filter_by(phone=phone).first()
    if user:
        if user.check_pwd(pwd):
            session["uname"] = user.username
            session["user_id"] = user.id
            session["pic_url"] = user.pic_url
            return jsonify(res=1)
        else:
            return jsonify(res=2)
    else:
        return jsonify(res=3)

@user_blueprint.route('/logout')
def logout():
    """退出登陆"""
    session.pop("uname")
    session.pop("user_id")
    return jsonify(res=1)

@user_blueprint.route("/")
@is_login
def user_center():
    """用户中心页面"""
    return render_template("news/user.html")

@user_blueprint.route("/base_info",methods=["POST","GET"])
@is_login
def user_base_info():
    """用户基本资料"""
    if request.method == "GET":
        user_id = session["user_id"]
        user = UserInfo.query.get(user_id)
        special_name = user.special_name
        if not special_name:
            special_name=""
        return render_template("news/user_base_info.html", username=user.username, special_name=user.special_name, gender=user.gender)
    if request.method == "POST":
        post_dict = request.form
        username = post_dict.get("username")
        special_name = post_dict.get("special_name")
        gender = post_dict.get("gender")
        user_id = session["user_id"]

        # 验证数据是否为空
        if not all([username, gender]):
            return "", 400

        # 验证数据长度

        user = UserInfo.query.get(user_id)
        
        user.username = username
        user.special_name = special_name
        print(gender)
        if gender == "1":
            gender = True
        else:
            gender = False
        user.gender = gender
        try:
            db.session.add(user)
            db.session.commit()
        except:
            # 日志记录
            current_app.logger_xjzx.error("修改用户基本信息连接数据库出错")
            return jsonify(res=2)
        session["uname"] = username
        return jsonify(res=1)


@user_blueprint.route("/pic_info", methods=["POST","GET"])
@is_login
def user_pic_info():
    """用户头像设置"""
    user_id = session.get("user_id")
    user = UserInfo.query.get(user_id)
    if request.method == "GET":
        return render_template("news/user_pic_info.html", pic=user.pic_url)
    if request.method == "POST":
        pic = request.files.get("avatar")
        pic_url = upload_pic(pic)
        user.pic = pic_url
        try:
            db.session.add(user)
            db.session.commit()
        except:
            current.logger_xjzx.error("用户头像设置连接数据库出错")
        session["pic_url"] = user.pic_url
        return jsonify(res=1,pic_url=user.pic_url)


@user_blueprint.route("/follow")
@is_login
def user_follow():
    """我的关注"""
    page = int(request.args.get("page",1))
    user_id = session.get("user_id")
    user = UserInfo.query.get(user_id)
    pagination = user.user_follow.paginate(page,4,False)
    return render_template("news/user_follow.html",  pagination=pagination, page=page)

@user_blueprint.route("/pass_info", methods=["GET", "POST"])
@is_login
def user_pass_info():
    """密码修改"""
    if request.method == "GET":
        return render_template("news/user_pass_info.html")
    if request.method == "POST":
        post_dict = request.form
        current_pwd = post_dict.get("current_pwd")
        new_pwd = post_dict.get("new_pwd")
        cpwd = post_dict.get("cpwd")
        user_id = session.get("user_id")
        user = UserInfo.query.get(user_id)

        if not all([current_pwd, cpwd, new_pwd]):
            return 
        if new_pwd != cpwd:
            return 
        if not user.check_pwd(current_pwd):
            return jsonify(res=0)
        user.password = new_pwd
        try:
            db.session.add(user)
            db.session.commit()
        except:
            current_app.logger_xjzx("修改密码时连接数据库出错")
            return jsonify(res=2)
        return jsonify(res=1)



@user_blueprint.route("/collection")
@is_login
def user_collection():
    """我的收藏"""
    page = int(request.args.get("page", 1))
    user_id = session.get("user_id")
    user = UserInfo.query.get(user_id)
    news_pagination = user.news_collect.order_by(NewsInfo.update_time.desc()).paginate(page, 6, False)
    news = news_pagination.items
    pages = news_pagination.pages
    return render_template("news/user_collection.html",news = news, pages=pages, page=page)

@user_blueprint.route("/news_release", methods=["POST", "GET"])
@is_login
def user_news_release():
    """新闻发布"""
    if request.method == "GET":
        news_id = request.args.get("news_id")
        print(news_id)
        if not news_id:
            return render_template("news/user_news_release.html")
        else:
            news = NewsInfo.query.get(news_id)
            return render_template("news/user_news_release.html",
                                    news_id = news.id,
                                    title=news.title,
                                    news_type=news.type.title,
                                    type_id=news.type_id,
                                    summary=news.summary,
                                    pic=news.pic_url,
                                    content=news.content)
    if request.method == "POST":
        news_id = request.form.get("news_id")
        post_dict = request.form
        title = post_dict.get("title")
        news_type = int(post_dict.get("type"))
        summary = post_dict.get("summary")
        content = post_dict.get("content")
        news_pic = request.files.get("news_pic")

        if not news_id:
            news = NewsInfo()
        else:
            news = NewsInfo.query.get(news_id)
            news.update_time = datetime.now()
        if news_pic:
            news_pic_name = upload_pic(news_pic)
            news.pic = news_pic_name
        news.title = title
        news.type_id = news_type
        news.summary = summary
        news.content = content
        news.user_id = session.get("user_id")
        #try:
        db.session.add(news)
        db.session.commit()
        #except:
            #current_app.logger_xjzx.error("发布新闻时连接数据库出错")
            #return "服务器出错，请稍后重试", 404
        return redirect("/user/news_list?news_id=")

@user_blueprint.route("/news_list")
@is_login
def user_news_list():
    """新闻列表"""
    page = int(request.args.get("page", 1))
    user_id = session.get("user_id")
    user = UserInfo.query.get(user_id)
    news_pagination = user.news.order_by(NewsInfo.update_time.desc()).paginate(page, 6, False)
    news = news_pagination.items
    pages = news_pagination.pages
    return render_template("news/user_news_list.html",news = news, pages=pages, page=page)

@user_blueprint.route("/other/<int:user_id>")
def user_other(user_id):
    """其他用户信息"""
    page = int(request.args.get("page", 1))
    user = UserInfo.query.get(user_id)
    news_pagination = user.news.order_by(NewsInfo.update_time.desc()).paginate(page, 6, False)
    newses = news_pagination.items
    pages = news_pagination.pages
    return render_template("news/other.html",user=user,newses = newses, pages=pages, page=page)

