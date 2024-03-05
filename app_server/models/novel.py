from sqlalchemy import UniqueConstraint

from app_server.db import Base, db


class Novel(Base):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment="自增主键")
    book_id = db.Column(db.String(255), comment="小说第三方id")
    title = db.Column(db.String(255), comment="标题")
    alias = db.Column(db.String(255), comment="别名")
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), comment="创建者id")
    introduction = db.Column(db.Text, comment="简介")
    remarks = db.Column(db.String(255), comment="备注")
    __table_args__ = (UniqueConstraint('book_id', 'user_id', name='_book_uid_uc'),)  # 同一个用户，第三方id不能重复
    # 单向一对多引用
    chapters = db.relationship("Chapter")


def GetNovelById(nid):
    return Novel.query.get(nid)


def GetNovelByBookId(bid):
    return Novel.query.filter_by(book_id=bid).first()