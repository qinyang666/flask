from flask import Blueprint
from flask import render_template
from models import NewsInfo,TypeInfo,UserInfo,NewsComment
from models import db
from flask import jsonify
from flask import request
from flask import current_app,session


news_blueprint = Blueprint("news", __name__, url_prefix="")

@news_blueprint.route("/")
def index():
    """显示首页"""
    newses = NewsInfo.query.order_by(NewsInfo.update_time.desc())[0:4]
    type_list = TypeInfo.query.all()
    top_hot_news = NewsInfo.query.order_by(NewsInfo.hits.desc()).paginate(1,6,False).items
    return render_template("news/index.html",type_list=type_list, top_hot_news=top_hot_news)


@news_blueprint.route("/news")
def get_news_by_type():
    """返回对应类型的新闻"""
    page = int(request.args.get("page",1))
    type_id = int(request.args.get("type_id"))
    if type_id == 0:
        newses = NewsInfo.query.order_by(NewsInfo.update_time.desc()).paginate(page,4,False).items
    else:
        newses = NewsInfo.query.filter_by(type_id=type_id).order_by(NewsInfo.update_time.desc()).paginate(page,4,False).items
    news_list = []
    for news in newses:
        news_list.append(news.to_index_dict())
    # 对象无法转化为json对象
    return jsonify(page=page,newses=news_list)

@news_blueprint.route("/detail/<int:news_id>")
def news_detail(news_id):
    """显示新闻详情页"""
    user_id = session.get("user_id")
    user = UserInfo.query.get(user_id)
    collected = 1
    news = NewsInfo.query.get(news_id)
    # 判断用户是否已收藏该新闻
    if user in  news.user_collect:
        collected = 0

    if news:
        news.hits += 1
        db.session.commit()

        return render_template("news/detail.html",news=news,collected=collected)
    else:
        return render_template("news/404.html")

@news_blueprint.route("/collect/<int:news_id>")
def collect(news_id):
    """收藏新闻"""
    user_id = session.get("user_id")
    if not user_id:
        return jsonify(res=0)
    else:
        user = UserInfo.query.get(user_id)
        news = NewsInfo.query.get(news_id)
        if not all([user,news]):
            """如果没有改用户或者该新闻，则退出"""
            return 
        if news not in user.news_collect:
            user.news_collect.append(news)
        else:
            user.news_collect.remove(news)
        try:
            db.session.add(user)
            db.session.commit()
        except:
            current_app.logger_xjzx.error("收藏新闻上传数据库出错")
            return jsonify(res=2)
        return jsonify(res=1)
    
@news_blueprint.route("/comment",methods=["POST"])
def push_comment():
    """发表评论"""
    comment = request.form.get("comment")
    if not comment:
        return 
    user_id = session.get("user_id")
    news_id = request.form.get("news_id")
    new_comment = NewsComment()
    new_comment.content = comment
    new_comment.news_id = news_id
    new_comment.user_id = user_id
    try:
        db.session.add(new_comment)
        db.session.commit()
    except:
        current_app.logger_xjzx.error("发表评论连接数据库出错")
        return jsonify(res=2)
    return jsonify(res=1)
    

