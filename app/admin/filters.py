from . import admin


@admin.app_template_filter()
def dateformat(value, format='%Y-%m-%d'):
    return value.strftime(format)


@admin.app_template_filter()
def substr(value):
    if len(value) > 30:
        value = value[:24] + '...' + value[-3:]
    return value
