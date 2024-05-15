from typing import Dict, List

menu = [{'title': "Добавить статью", 'url_name': 'add_page'},
        {'title': "Обратная связь", 'url_name': 'contact'},
        ]

Menu = List[Dict[str, str]]


def get_menu(request: object) -> Dict[str, Menu]:
    """Функция возвращает меню"""
    return {'menu': menu}
