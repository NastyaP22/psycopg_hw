import psycopg2
conn = psycopg2.connect(database='clients', user='postgres', password='')

def create_table(conn):
   with conn.cursor() as cur:
    cur.execute("""
			DROP TABLE IF EXISTS phones;
			DROP TABLE IF EXISTS clients_info;
			""")
    cur.execute("""
			CREATE TABLE IF NOT EXISTS clients_info(
			client_id SERIAL PRIMARY KEY,
			name VARCHAR(40) NOT NULL,
			surname VARCHAR(40) NOT NULL,
			email VARCHAR(40) NOT NULL UNIQUE);
            """)
    conn.commit()
    cur.execute("""
			CREATE TABLE IF NOT EXISTS phones(
            phone_id SERIAL PRIMARY KEY,
			number VARCHAR(12) UNIQUE,
			client_id INTEGER REFERENCES clients_info(client_id));
			""")
    conn.commit()

def add_client(conn, name, surname, email):
    with conn.cursor() as cur:
      cur.execute("""
      INSERT INTO clients_info (name, surname, email)
      VALUES (%s, %s, %s)
      RETURNING client_id, name, surname, email;
      """, (name, surname, email))
      conn.commit()
      print(cur.fetchone())

def add_phone(conn, number, client_id):
   with conn.cursor() as cur:
     cur.execute("""
     INSERT INTO phones(number, client_id)
     VALUES(%s, %s)
     RETURNING client_id, number
     """, (number, client_id))
     conn.commit()
     print(cur.fetchone())

def update_client_info(conn, client_id, name=None, surname=None, email=None, number=None):
   arg_list = {'name': name, 'surname': surname, 'email': email}
   cur = conn.cursor()
   for key, arg in arg_list.items():
      if arg:
         cur.execute("""
         UPDATE clients_info
         SET {}=%s
         WHERE client_id = %s
         """.format(key), (arg, client_id))
   arg_list = {'number': number}
   for key, arg in arg_list.items():
      if arg:
         cur.execute("""
         SELECT COUNT(phone_id) FROM phones
         WHERE client_id = %s
         """, (client_id))
         numbers_count = int(cur.fetchone()[0])
         if numbers_count == 1:
            cur.execute("""
            UPDATE phones
            SET {}=%s
            WHERE client_id = %s
            """.format(key), (number, client_id))
         elif numbers_count > 1:
            number_for_change = input('Введите id номера, который вы хотите изменить')
            cur.execute("""
            UPDATE phones
            SET {}=%s
            WHERE client_id = %s AND phone_id = %s
            """.format(key), (number, client_id, number_for_change))
         else:
            add_phone(conn, arg, client_id)
   cur.execute("""
   SELECT * FROM clients_info
   WHERE client_id=%s
   """, (client_id))
   conn.commit()
   print(cur.fetchone())
   cur.execute("""
   SELECT * FROM phones
   WHERE client_id=%s
   """, (client_id))
   print(cur.fetchall())

def delete_number(conn, phone_id):
   cur = conn.cursor()
   cur.execute("""
   DELETE FROM phones
   WHERE phone_id = %s
   """, (phone_id))
   cur.execute("""
   SELECT * FROM phones
   """)
   print(cur.fetchall())
   conn.commit()

def delete_client(conn, client_id):
   cur = conn.cursor()
   try:
      cur.execute("""
                  DELETE FROM phones
                  WHERE client_id = %s
                  """, (client_id))
   except:
      pass
   cur.execute("""
   DELETE FROM clients_info
   WHERE client_id = %s
   """, (client_id))
   cur.execute("""
   SELECT * FROM clients_info
   """)
   print(cur.fetchall())
   cur.execute("""
   SELECT * FROM phones
   """)
   print(cur.fetchall())
   conn.commit()

def find_client(conn, name=None, surname=None, email=None, number=None):
   cur = conn.cursor()
   arg_list = {'name': name, 'surname': surname, 'email': email, 'number': number}
   for key, arg in arg_list.items():
      if arg:
         cur.execute("""
         SELECT DISTINCT clients_info.client_id FROM clients_info
         JOIN phones ON clients_info.client_id = phones.client_id
         WHERE {}='%s';
         """.format(key) % arg)
         print(cur.fetchall())
   conn.commit()



with psycopg2.connect(database="clients", user="postgres", password="") as conn:
   create_table(conn)
   add_client(conn, 'Alina', 'Novikova', 'alnov@mail.ru')
   add_phone(conn, '89216550090', 1)
   add_phone(conn, '89015641777', 1)
   update_client_info(conn, '1', name='Irina')
   update_client_info(conn, number='89115616161', client_id='1')
   add_client(conn, 'Sergey', 'Popov', 'serpopov@mail.ru')
   update_client_info(conn, number='89007654321', client_id='2')
   add_client(conn, 'Olesya', 'Semenova', 'olsem@mail.ru')
   add_phone(conn, '89154321151', 3)
   delete_number(conn, '3')
   delete_client(conn, '3')
   find_client(conn, name="Irina")