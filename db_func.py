import psycopg2

connection = psycopg2.connect(
    dbname='bot_db', user='postgres', password='552281', host='bot_db', )
connection.autocommit = True
cursor = connection.cursor()


def create_tables():
    cursor.execute(
        '''CREATE TABLE IF NOT EXISTS USERS
         (user_id TEXT PRIMARY KEY NOT NULL,
         username TEXT,
         first_name TEXT,
         last_name TEXT,
         job_group TEXT);''')


success_text = 'Вы успешно зарегистрировались в группу'
already_registered_text = 'Вы уже зарегистрированы'
registration_error = 'Регистрация не удалась, пожалуйста, повторите позднее'


def register_user(user, chat_id, callback):
    message = ''
    try:
        cursor.execute('SELECT user_id from users;')

        users_id_list = cursor.fetchone()

        if users_id_list is None or (str(user['user_id']) not in users_id_list):
            cursor.execute(
                f'''INSERT INTO USERS ( user_id, username, first_name, last_name, job_group) VALUES ({user['user_id']}, 
                '{user['username']}', '{user['first_name']}', '{user['last_name']}', '{user['job_group']}'); ''')

            message = f"{success_text} {user['job_group']}"

        else:
            message = already_registered_text
    except:
        print(f'Регистрация юзера не удалась')
        message = registration_error

    finally:
        print(message)
        callback(chat_id, message)
        return message


def check_role(user):
    query = """SELECT job_group from users where user_id = %s;"""
    try:
        cursor.execute(query, (str(user),))
        job_group_check = cursor.fetchone()
        if job_group_check is None:
            raise Exception('job_group_check is not found')
        return job_group_check[0]
    except Exception as e:
        print(e)
        return None
