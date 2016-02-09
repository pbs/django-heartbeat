from django.db import connections, OperationalError


def check(request):
    databases_info = []
    for db in connections:
        databases_info.append(get_connection_info(connections[db]))
    return {'databases': databases_info}


def get_connection_info(connection):
    try:
        cursor = connection.cursor()
    except OperationalError:
        cursor = None

    return {
        connection.alias: {
            'ping': True if cursor else False,
            'postgres_version': execute_sql(cursor),
            'name': connection.settings_dict['NAME'],
            'engine': connection.settings_dict['ENGINE'],
        }
    }


def execute_sql(cursor):
    if not cursor:
        return {'error': 'Could not determine version'}
    cursor.execute("SELECT version();")
    result = cursor.fetchone()
    if not result:
        return {'error': 'SQL version query din not returned any rows'}
    return result
