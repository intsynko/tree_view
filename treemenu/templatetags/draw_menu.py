from django import template
from treemenu.models import MenuItem
from collections import defaultdict

register = template.Library()


@register.inclusion_tag('treemenu/draw_menu.html', takes_context=True)
def draw_menu(context, menu_name):
    request = context['request']
    current_url = request.path

    # Получаем все пункты меню одним запросом
    items = list(
        MenuItem.objects
        .filter(menu__name=menu_name)
        .order_by('order', 'id')
    )
    if not len(items):
        return {'menu_items': [], 'menu_name': menu_name, 'request': request}

    children_map = defaultdict(list)
    for item in items:
        if item.parent_id:
            children_map[item.parent_id].append(item)
        else:
            children_map[None].append(item)

    # Определяем активный пункт и путь к нему
    active_item = None
    for item in items:
        if str(current_url).endswith(str(item.id)):
            active_item = item
            break
    # Собираем путь к активному пункту
    active_path = set()
    def collect_parents(item):
        while item:
            active_path.add(item.id)
            item = item.parent
    if active_item:
        collect_parents(active_item)

    # Рекурсивно строим дерево для шаблона
    def build_tree(parent_id=None, level=0):
        nodes = []
        for item in children_map[parent_id]:
            node = {
                'item': item,
                'children': build_tree(item.id, level+1),
                'is_active': item.id in active_path,
                'is_current': active_item and item.id == active_item.id,
                'level': level,
            }
            nodes.append(node)
        return nodes

    menu_tree = build_tree(None, 0)
    return {'menu_items': menu_tree, 'menu_name': menu_name, 'request': request}


