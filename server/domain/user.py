class User:

    def __init__(self, attributes={}):
        self.id = attributes.get('id')
        self.username = attributes.get('username')
        self.ip = attributes.get('ip')
        self.port = attributes.get('port')
