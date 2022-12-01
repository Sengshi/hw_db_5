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
            INSERT INTO clients(first_name, last_name, email, phone) VALUES(%s, %s, %s, %s) RETURNING id;
            """, (first_name, last_name, email, phone))
            cur.execute("""
            INSERT INTO phones(phone, client_id) VALUES(%s, %s);
            """, (phone, cur.fetchone()[0]))
            # connect.commit()


def count_phone(cursor, client_id):
    cursor.execute("""
    SELECT COUNT(phone) FROM phones WHERE client_id=%s;
    """, str(client_id))
    return cursor.fetchone()[0]


def add_phone(connect, phone, client_id):
    with connect.cursor() as cur:
        if count_phone(cur, client_id) >= 1:
            cur.execute("""
            INSERT INTO phones(phone, client_id) VALUES(%s, %s);
            """, (phone, client_id))
            connect.commit()
        else:
            cur.execute("""
            INSERT INTO phones(phone, client_id) VALUES(%s, %s);
            """, (phone, client_id))
            change_client(connect, client_id=client_id, phone=phone)


def search_phone(cursor, client_id):
    cursor.execute("""
    SELECT phone FROM clients WHERE id=%s;
    """, str(client_id))
    return cursor.fetchone()[0]


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
            if search_phone(cur, client_id) is not None:
                cur.execute("""
                UPDATE phones SET phone=%s WHERE phone=%s;
                """, (phone, search_phone(cur, client_id)))
            cur.execute("""
            UPDATE clients SET phone=%s WHERE id=%s;
            """, (phone, client_id))
            connect.commit()


def delete_phone(connect, client_id, phone):
    with connect.cursor() as cur:
        cur.execute("""
        DELETE FROM phones WHERE phone=%s;
        """, (phone,))

        cur.execute("""
        DELETE phone FROM clients WHERE id=%s;
        """, (client_id,))



def delete_client(connect, client_id):
    pass


def find_client(connect, first_name=None, last_name=None, email=None, phone=None):
    pass


with psycopg2.connect(database="clients_db", user="postgres", password="123") as conn:
    create_db(conn)
    add_client(conn, '1Rob1', '1Wholes1', '1rob@rob.com')
    add_client(conn, '2Rob2', '2Wholes2', '2rob@rob.com', '79999999999')
    add_client(conn, '3Rob3', '3Wholes3', '3rob@rob.com')
    add_client(conn, '4Rob4', '4Wholes4', '4rob@rob.com')
    add_phone(conn, client_id=3, phone='79991111111')
    add_phone(conn, client_id=3, phone='79992222222')
    add_phone(conn, client_id=3, phone='79993333333')
    add_phone(conn, client_id=4, phone='79994444444')
    change_client(conn, client_id=1, first_name='1Bob1')
    change_client(conn, client_id=3, phone='77777777777')
    delete_phone(conn, client_id=4, phone='79994444444')
    delete_phone(conn, client_id=3, phone='79992222222')


conn.close()
