from django.test import TestCase, RequestFactory
from django.template import Context, Template
from .models import Menu, MenuItem
from .templatetags.draw_menu import draw_menu


class MenuTagTest(TestCase):
    def setUp(self):
        self.menu = Menu.objects.create(name='main_menu')
        self.root = MenuItem.objects.create(menu=self.menu, title='Root', order=1)
        self.child = MenuItem.objects.create(menu=self.menu, parent=self.root, title='Child', order=1)
        self.child2 = MenuItem.objects.create(menu=self.menu, parent=self.root, title='Child2', order=2)
        self.sub_child1 = MenuItem.objects.create(menu=self.menu, parent=self.child, title='SubChild1', order=2)

    def test_draw_menu_tag(self):
        factory = RequestFactory()
        request = factory.get('/fake-url/')
        template = Template("""{% load draw_menu %}{% draw_menu 'main_menu' %}""")
        context = Context({'request': request})
        rendered = template.render(context)
        self.assertIn('Root', rendered)
        self.assertIn('Child', rendered)
        self.assertIn('Child2', rendered)

    def test_draw_menu_tag_queries(self):
        factory = RequestFactory()
        request = factory.get('/fake-url/')
        template = Template("""{% load draw_menu %}{% draw_menu 'main_menu' %}""")
        context = Context({'request': request})
        with self.assertNumQueries(1):
            template.render(context)

    def test_draw_menu_func(self):
        factory = RequestFactory()
        request = factory.get('/active-child/')
        context = Context({'request': request})
        data = draw_menu(context, 'main_menu')

        expected = {
            'menu_items': [
                {
                    'item': self.root,
                    'children': [
                        {
                            'item': self.child,
                            'children': [
                                {
                                    'item': self.sub_child1,
                                    'children': [],
                                    'is_active': False,
                                    'is_current': None,
                                    'level': 2
                                }
                            ],
                            'is_active': False,
                            'is_current': None,
                            'level': 1
                        },
                        {
                            'item': self.child2,
                            'children': [],
                            'is_active': False,
                            'is_current': None,
                            'level': 1
                        }
                    ],
                    'is_active': False,
                    'is_current': None,
                    'level': 0
                }
            ],
            'menu_name': 'main_menu',
            'request': request
        }
        self.assertEquals(expected ,data)
