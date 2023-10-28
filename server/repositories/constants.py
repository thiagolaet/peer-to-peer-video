DB_NAME = 'tcp_server.db'

CREATE_TABLES_QUERY = '''
    CREATE TABLE IF NOT EXISTS user (
        id INTEGER PRIMARY KEY,
        username VARCHAR(50) NOT NULL,
        ip VARCHAR(20) NOT NULL,
        port INTEGER NOT NULL
    );
'''

INSERT_QUERY = '''
    INSERT INTO user (username, ip, port) VALUES (?, ?, ?);
'''

DELETE_QUERY = '''
    DELETE FROM user WHERE id = ?
'''

SELECT_BY_USERNAME_QUERY = '''
    SELECT * FROM user WHERE name LIKE ?
'''

SELECT_BY_IP_QUERY = '''
    SELECT * FROM user WHERE ip = ?
'''
