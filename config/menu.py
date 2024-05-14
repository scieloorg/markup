WAGTAIL_MENU_APPS_ORDER = [
    "core",
    "django_celery_beat",
    "tracker",
    "files_storage",
    "Configurações",
    "Páginas",
    "Relatórios",
    "Ajuda",
    "Images",
    "Documentos",
]


def get_menu_order(app_name):
    try:
        return WAGTAIL_MENU_APPS_ORDER.index(app_name)
    except:
        return 9000
