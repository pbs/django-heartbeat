from django.db import connections, OperationalError


def check(request):
    databases_info = []
    for db in connections:
        databases_info.append(get_connection_info(connections[db]))
    return databases_info


def get_connection_info(connection):
    engine = connection.settings_dict.get('ENGINE')
    name = connection.settings_dict.get('NAME')
    host = connection.settings_dict.get('HOST')
    port = connection.settings_dict.get('PORT')
    version = get_database_version(connection, engine) or ''

    connection_info = {
        connection.alias: {
            'version': version,
            'name': name,
            'engine': engine,
            'host': host,
            'port': port,
        }
    }
    return connection_info


def get_database_version(connection, engine):
    if connection.settings_dict['ENGINE'] == 'django.db.backends.dummy':
        return None
    engines = {
        'django.db.backends.postgresql_psycopg2': 'SELECT version();',
        'django.db.backends.mysql': 'SELECT version();',
        'django.db.backends.sqlite3': 'select sqlite_version();',
        'django.db.backends.oracle': 'select * from v$version;',
        'django.contrib.gis.db.backends.mysql': 'SELECT version();',
        'django.contrib.gis.db.backends.postgis': 'SELECT version();',
        'django.contrib.gis.db.backends.spatialite': (
            'select sqlite_version();'
        ),
        'django.contrib.gis.db.backends.oracle': 'select * from v$version;',
    }
    query = engines[engine]
    return execute_sql(connection, query)


def execute_sql(connection, stmt):
    try:
        cursor = connection.cursor()
    except OperationalError as e:
        return {'error': str(e)}

    cursor.execute(stmt)
    result = cursor.fetchone()
    return result[0]
