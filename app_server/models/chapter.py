from app_server.db import Base, db


class Chapter(Base):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment="自增主键")
    title = db.Column(db.String(255), comment="标题")
    c_type = db.Column(db.Integer, comment="状态类型")  # 0未处理 1已完成 2已发布
    use_id = db.Column(db.Integer, db.ForeignKey('user.id'), comment="创建者id")
    novel_id = db.Column(db.Integer, db.ForeignKey('novel.id'), comment="小说id")
    content = db.Column(db.Text, comment="正文内容")
    rewrite = db.Column(db.Text, comment="重写内容")


def GetAllChaptersByNovelId(nid):
    return Chapter.query.filter_by(novel_id=nid).all()
