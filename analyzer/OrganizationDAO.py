
from DatabaseConnection import DatabaseConnection


class OrganizationDAO:

    def getEmail(self, name):
        email = None
        conn = DatabaseConnection().conn
        cur = conn.cursor()

        sql = "SELECT email FROM Organizacion WHERE nombre=%s"
        data_tuple = (name,)

        cur.execute(sql, data_tuple)
        resultSet = cur.fetchone()
        if resultSet is not None:
            email = resultSet[0]

        conn.close()
        return email

