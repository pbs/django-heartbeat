from django.db import connections, OperationalError


def check(request):
    databases_info = []
    for db in connections:
        databases_info.append(get_connection_info(connections[db]))
    return {'databases': databases_info}


def get_connection_info(connection):
    engine = connection.settings_dict.get('ENGINE')
    name = connection.settings_dict.get('NAME')
    host = connection.settings_dict.get('HOST')
    port = connection.settings_dict.get('PORT')

    connection_info = {
        connection.alias: {
            'version': get_database_version(connection, engine),
            'name': name,
            'engine': engine,
            'host': host,
            'port': port,
        }
    }
    return connection_info


def get_database_version(connection, engine):
    if engine in ['django.db.backends.postgresql_psycopg2',
                  'django.db.backends.mysql']:
        query = 'SELECT version();'
    elif engine == 'django.db.backends.sqlite3':
        query = 'select sqlite_version();'
    elif engine == 'django.db.backends.oracle':
        query = 'select * from v$version;'
    return execute_sql(connection, query)


def execute_sql(connection, stmt):
    try:
        cursor = connection.cursor()
    except OperationalError as e:
        return {'error': str(e)}

    cursor.execute(stmt)
    result = cursor.fetchone()
    return result[0]
