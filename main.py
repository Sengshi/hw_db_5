import psycopg2


def create_db(connect):
    with connect.cursor() as cur:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS clients(
            id SERIAL PRIMARY KEY,
            first_name VARCHAR(50),
            last_name VARCHAR(50),
            email VARCHAR(50) UNIQUE
        );
        """)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS phones(
            id SERIAL PRIMARY KEY,
            phone VARCHAR(20) UNIQUE,
            client_id INTEGER NOT NULL REFERENCES clients(id)
            ON DELETE CASCADE
        );
        """)
        connect.commit()


def add_client(connect, first_name, last_name, email, phone=None):
    with connect.cursor() as cur:
        if phone is None:
            cur.execute("""
            INSERT INTO clients(first_name, last_name, email) VALUES(%s, %s, %s);
            """, (first_name, last_name, email))
            connect.commit()
        else:
            cur.execute("""
            INSERT INTO clients(first_name, last_name, email) VALUES(%s, %s, %s) RETURNING id;
            """, (first_name, last_name, email))
            cur.execute("""
            INSERT INTO phones(phone, client_id) VALUES(%s, %s);
            """, (phone, cur.fetchone()[0]))
            connect.commit()


def add_phone(connect, phone, client_id):
    with connect.cursor() as cur:
        cur.execute("""
        INSERT INTO phones(phone, client_id) VALUES(%s, %s);
        """, (phone, client_id))
        connect.commit()


def search_phone(cursor, client_id):
    cursor.execute("""
    SELECT id, phone FROM phones WHERE client_id=%s ORDER BY id ASC;
    """, str(client_id))
    return cursor.fetchone()[1]


def change_client(connect, client_id, first_name=None, last_name=None, email=None, phone=None):
    with connect.cursor() as cur:
        if first_name is not None:
            cur.execute("""
            UPDATE clients SET first_name=%s WHERE id=%s;
            """, (first_name, client_id))
            connect.commit()
        if last_name is not None:
            cur.execute("""
            UPDATE clients SET last_name=%s WHERE id=%s;
            """, (last_name, client_id))
            connect.commit()
        if email is not None:
            cur.execute("""
            UPDATE clients SET email=%s WHERE id=%s;
            """, (email, client_id))
            connect.commit()
        if phone is not None:
            try:
                cur.execute("""
                UPDATE phones SET phone=%s WHERE phone=%s;
                """, (phone, search_phone(cur, client_id)))
                connect.commit()
            except TypeError:
                add_phone(conn, client_id=client_id, phone=phone)


def delete_phone(connect, client_id, phone):
    with connect.cursor() as cur:
        cur.execute("""
        DELETE FROM phones WHERE phone=%s AND client_id=%s;
        """, (phone, client_id))
        connect.commit()


def delete_client(connect, client_id):
    with connect.cursor() as cur:
        cur.execute("""
        DELETE FROM clients WHERE id=%s RETURNING *;
        """, (client_id,))
        connect.commit()


# def check_client(cursor):
#     try:
#         return f'Имя: {cursor[1]}\nФамилия: {cursor[2]}'
#     except TypeError:
#         return 'Нет клиента'
#
#
# def check_client_phone(cursor):
#     try:
#         return f'Имя: {cursor[4]}\nФамилия: {cursor[5]}'
#     except TypeError:
#         return 'Нет клиента, либо у него не указан телефон'


def find_client(connect, first_name=None, last_name=None, email=None, phone=None):
    with connect.cursor() as cur:
        if first_name is not None:
            cur.execute("""
            SELECT * FROM clients WHERE first_name=%s;
            """, (first_name, ))
            return cur.fetchall()
        if last_name is not None:
            cur.execute("""
            SELECT * FROM clients WHERE last_name=%s;
            """, (last_name, ))
            return cur.fetchall()
        if email is not None:
            cur.execute("""
            SELECT * FROM clients WHERE email=%s;
            """, (email, ))
            # return check_client(cur.fetchone())
            return cur.fetchone()
        if phone is not None:
            cur.execute("""
            SELECT * FROM phones p
            LEFT JOIN clients c ON p.client_id = c.id
            WHERE p.phone = %s;
            """, (phone, ))
            # return check_client_phone(cur.fetchone())
            return cur.fetchone()


with psycopg2.connect(database="clients_db", user="postgres", password="123") as conn:
    create_db(conn)
    add_client(conn, '1Rob1', '1Wholes1', '1rob@rob.com')
    add_client(conn, '2Rob2', '2Wholes2', '2rob@rob.com', '79999999999')
    add_client(conn, '3Rob3', '3Wholes3', '3rob@rob.com')
    add_client(conn, '4Rob4', '4Wholes4', '4rob@rob.com')
    add_client(conn, '5Rob5', '5Wholes5', '5rob@rob.com')
    add_client(conn, '6Rob6', '6Wholes6', '6rob@rob.com')
    add_client(conn, '7Rob7', '7Wholes7', '7rob@rob.com')
    add_client(conn, '8Rob8', '8Wholes8', '8rob@rob.com', '88888888888')
    add_phone(conn, client_id=3, phone='79991111111')
    add_phone(conn, client_id=3, phone='79992222222')
    add_phone(conn, client_id=3, phone='79993333333')
    add_phone(conn, client_id=4, phone='79994444444')
    change_client(conn, client_id=1, first_name='1Bob1')
    change_client(conn, client_id=5, first_name='5Bob5', last_name='5Robbi5', email='5whol@rob.com', phone='444444')
    change_client(conn, client_id=3, phone='77777777777')
    delete_phone(conn, client_id=4, phone='79994444444')
    delete_phone(conn, client_id=3, phone='79992222222')
    delete_client(conn, client_id=7)
    print(find_client(conn, first_name='6Rob6'))
    print(find_client(conn, last_name='8Wholes8'))
    print(find_client(conn, last_name='7Rob7'))
    print(find_client(conn, email='2rob@rob.com'))
    print(find_client(conn, phone='88888888888'))

conn.close()
