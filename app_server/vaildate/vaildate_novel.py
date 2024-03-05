# 新增或更新character时的必填字段校验函数
def validate_novel_data(data):

    if not data.get('book_id'):
        return 'book_id is required'
    if not data.get('title'):
        return 'book_name is required'
    if not data.get('introduction'):
        return 'book_introduction is required'
    return None
