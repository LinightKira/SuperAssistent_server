from datetime import datetime


def validate_chapter_data(data):
    if not data.get('title'):
        return 'title is required'
    if not data.get('book_id'):
        return 'book_id is required'
    if not data.get('content'):
        return 'content is required'
    return None

