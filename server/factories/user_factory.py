from domain.user import User


class UserFactory:

    def create_from_tuple(self, tuple):
        return User(
            {
                'id': tuple[0],
                'username': tuple[1],
                'ip': tuple[2],
                'port': tuple[3],
            }
        )
