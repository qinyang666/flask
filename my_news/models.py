from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import check_password_hash,generate_password_hash
from flask import current_app


db = SQLAlchemy()


class BaseModel(object):
    """模型类基类"""
    create_time = db.Column(db.DateTime, default=datetime.now)
    update_time = db.Column(db.DateTime, default=datetime.now)
    is_delete = db.Column(db.Boolean, default=False)


# 用户新闻收藏中间表
tb_user_news = db.Table("tb_user_news",
                        db.Column("user_id", db.Integer, db.ForeignKey("user_info.id"), primary_key=True),
                        db.Column("news_id", db.Integer, db.ForeignKey("news_info.id"), primary_key=True))

# 用户关注中间表
tb_user_follow = db.Table("tb_user_follow",
                          db.Column("user_follow_id", db.Integer, db.ForeignKey("user_info.id"), primary_key=True),
                          db.Column("user_origin_id", db.Integer, db.ForeignKey("user_info.id"), primary_key=True))


class UserInfo(db.Model, BaseModel):
    """用户信息模型类"""
    __tablename__ = "user_info"
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(11), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    special_name = db.Column(db.String(32))
    username = db.Column(db.String(24))
    gender = db.Column(db.Boolean, default=False)
    pic = db.Column(db.String(50), default='user_pic.png')
    is_admin = db.Column(db.Boolean, default=False)
    news = db.relationship("NewsInfo", backref="user", lazy="dynamic")
    news_collect = db.relationship("NewsInfo", secondary=tb_user_news,
                                   backref=db.backref("user_collect", lazy="dynamic"), lazy="dynamic")
    user_follow = db.relationship("UserInfo", secondary=tb_user_follow,
                                  secondaryjoin=id == tb_user_follow.c.user_follow_id,
                                  primaryjoin=id == tb_user_follow.c.user_origin_id,
                                  backref=db.backref("user_origin", lazy="dynamic"), lazy="dynamic")

    @property
    def password(self):
        pass

    @password.setter
    def password(self,pwd):
        self.password_hash = generate_password_hash(pwd)

    def check_pwd(self, pwd):
        return check_password_hash(self.password_hash, pwd)

    @property
    def pic_url(self):
        return current_app.config.get("QINIU_URL") + self.pic



class TypeInfo(db.Model, BaseModel):
    """分类信息模型类"""
    __tablename__ = "type_info"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(24))
    news = db.relationship("NewsInfo", backref="type", lazy="dynamic")


class NewsInfo(db.Model, BaseModel):
    """新闻信息模型类"""
    __tablename__ = "news_info"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64))
    summary = db.Column(db.String(128))
    pic = db.Column(db.String(50),default='user_pic.png')
    content = db.Column(db.Text)
    status = db.Column(db.SmallInteger, default=0)
    reason = db.Column(db.String(64))
    hits = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey("user_info.id"))
    type_id = db.Column(db.ForeignKey("type_info.id"))
    comments = db.relationship("NewsComment",backref="news",lazy="dynamic")

    @property
    def pic_url(self):
        """拼接图片url"""
        return current_app.config.get("QINIU_URL") + self.pic
	
    def to_index_dict(self):
        """把对象的属性封装到字典返回，以便组装json对象"""
        return {
            'id': self.id,
            'pic_url': self.pic_url,
            'title': self.title,
            'summary': self.summary,
            'username': self.user.username,
            'user_pic_url': self.user.pic_url,
            'user_id': self.user_id,
            'udpate_time': self.update_time.strftime('%Y-%m-%d')
        }


class NewsComment(db.Model, BaseModel):
    """新闻评论信息模型类"""
    __tablename__ = "news_comment"
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(128))
    likenum = db.Column(db.Integer, default=0)
    comment_id = db.Column(db.Integer, db.ForeignKey("news_comment.id"))
    news_id = db.Column(db.Integer, db.ForeignKey("news_info.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("user_info.id"))

    comment = db.relationship("NewsComment", backref="origin_comment", remote_side=[id])#remote_side什么意思
    
    @property
    def user(self):
        return UserInfo.query.get(self.user_id)
