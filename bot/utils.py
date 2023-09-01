import os

import psycopg2

from dotenv import load_dotenv

from openpyxl import Workbook
from openpyxl.reader.excel import load_workbook

load_dotenv()


def connect_to_db():
    '''Подключеине к БД.'''
    dbname = os.getenv('POSTGRES_DB')
    user = os.getenv('POSTGRES_USER')
    password = os.getenv('POSTGRES_PASSWORD')
    #host = 
    #port =

    conn = psycopg2.connect(dbname=dbname, user=user, password=password)
    cursor = conn.cursor()

    return conn, cursor


def get_categories():
    '''Получение категорий.'''
    try:
        conn, cursor = connect_to_db()
        cursor.execute("SELECT * FROM bot_admin_app_category")
        rows = cursor.fetchall()

        categories = []
        for row in rows:
            category = {'id': row[0], 'name': row[1]}
            categories.append(category)
        
        cursor.close()
        conn.close()

        return categories
    except (Exception, psycopg2.Error) as error:
        print(f'Ошибка при извлечении категорий из базы данных: {error}')
        return None


def get_subcategories(category_id):
    '''Получение подкатегорий.'''
    try:
        conn, cursor = connect_to_db()

        query = "SELECT * FROM bot_admin_app_subcategory WHERE category_id = %s;"
        cursor.execute(query, (category_id,))
        rows = cursor.fetchall()

        subcategories = []
        for row in rows:
            subcategory = {'id': row[0], 'name': row[1]}
            subcategories.append(subcategory)
        
        cursor.close()
        conn.close()
        return subcategories
    except (Exception, psycopg2.Error) as error:
        print(f'Ошибка при извлечении подкатегорий из базы данных: {error}')
        return None


def get_products(subcategory_id):
    try:
        conn, cursor = connect_to_db()

        products = []

        query = "SELECT * FROM bot_admin_app_product WHERE subcategory_id = %s"
        cursor.execute(query, (subcategory_id,))
        rows = cursor.fetchall()

        for row in rows:
            product = {'id': row[0], 'name': row[1], 'price': row[2]}
            products.append(product)
        
        cursor.close()
        conn.close()

        return products
    except(Exception, psycopg2.Error) as error:
        print(f'Ошибка при извлечении продуктов из базы данных: {error}')
        return None
    

def add_to_cart(user_id, product_id):
    '''Добавление в корзину.'''
    try:
        conn, cursor =connect_to_db()

        # Проверка, существует ли уже запись с таким user_id и product_id
        cursor.execute("SELECT id, quantity  FROM bot_admin_app_cart WHERE user_id = %s AND product_id = %s",
                       (str(user_id), product_id))
        row = cursor.fetchone()
        if row:
            cart_id = row[0]
            quantity = row[1] + 1
            cursor.execute("UPDATE bot_admin_app_cart SET quantity = %s WHERE id = %s", (quantity, cart_id))
        else:
            quantity = 1
            cursor.execute("INSERT INTO bot_admin_app_cart (user_id, product_id, quantity) VALUES (%s, %s, %s)",
                           (str(user_id), product_id, quantity))
            
        conn.commit()
        cursor.close()
        conn.close()
        return quantity
    except Exception as e:
        print("Ошибка при добавлении продукта в корзину:", e)
        return "Ошибка при добавлении продукта в корзину"


def get_cart_by_user(user_id):
    '''Получение корзины пользователя с агрегированными значениями.'''
    try:
        conn, cursor = connect_to_db()

        cursor.execute("""
            SELECT
                c.user_id,
                c.quantity,
                p.name,
                p.price,
                c.id,
                array_agg(c.product_id) AS product_ids
            FROM
                bot_admin_app_cart c
            INNER JOIN
                bot_admin_app_product p ON c.product_id = p.id
            WHERE
                c.user_id = %s
            GROUP BY
                c.user_id,
                c.quantity,
                p.name,
                p.price,
                c.id
        """, (str(user_id),))
        cart = cursor.fetchall()

        cart_products = []
        for row in cart:
            product = {
                'id': row[0],
                'quantity': row[1],
                'name': row[2],
                'price': row[3],
                'cart_id': row[4]
            }
            cart_products.append(product)
        
        cursor.close()
        conn.close()

        return cart_products
    except Exception as e:
        print("Ошибка при получении корзины пользователя:", e)
        return None


def change_cart_quantity(cart_id, action):
    '''Изменение количества товара.'''
    try:
        conn, cursor = connect_to_db()
        cursor.execute("SELECT id, quantity FROM bot_admin_app_cart WHERE id = %s", (str(cart_id),))
        row = cursor.fetchone()
        if row:
            quantity = row[1]
            if action == 'increase':
                quantity += 1
            elif action == 'decrease':
                quantity -= 1

            if action == 'del' or quantity == 0:
                cursor.execute("DELETE FROM bot_admin_app_cart WHERE id = %s", (str(cart_id),))
                conn.commit()
                cursor.close()
                conn.close()
                return None
            else:
                cursor.execute("UPDATE bot_admin_app_cart SET quantity = %s WHERE id = %s", (quantity, cart_id))
            
            conn.commit()
            cursor.close()
            conn.close()
            return quantity
    except Exception as e:
        print("Ошибка при изменении количества товара:", e)
        return None


def delete_all_cart_items(user_id):
    '''Удаление всех товаров пользователя из корзины.'''
    try:
        conn, cursor = connect_to_db()
        cursor.execute("DELETE FROM bot_admin_app_cart WHERE user_id = %s", (str(user_id),))
        conn.commit()
        cursor.close()
        conn.close()
        print('Все товары из корзины пользователя удалены.')
    except Exception as e:
        print('Ошибка при удалении всех товаров из корзины пользователя.')


def save_subscriber(chat_id, username, phone, adress):
    '''Сохранение пользователя.'''
    try:
        conn, cursor = connect_to_db()
        cursor.execute(
            """
            INSERT INTO bot_admin_app_subscriber (chat_id, username, phone, adress)
            VALUES (%s,%s,%s,%s)
            ON CONFLICT (chat_id) DO UPDATE
            SET username = excluded.username,
                phone = excluded.phone,
                adress = excluded.adress
            """,
            (chat_id, username, phone, adress)
        )
        conn.commit()
    except psycopg2.Error as error:
        print(f'Ошибка при сохранение пользователя: {error}')
        conn.rollback()
    finally:
        cursor.close()
        conn.close()


def get_subscriber(chat_id):
    try:
        conn, cursor = connect_to_db()
        cursor.execute("SELECT * FROM bot_admin_app_subscriber WHERE chat_id = %s", (str(chat_id),))
        row = cursor.fetchone()
        username = row[2]
        phone = row[3]
        adress = row[4]
        return username, phone, adress
    except psycopg2.Error as error:
        print(f'Ошибка при получении пользователя: {error}.')
    finally:
        cursor.close()
        conn.close()


def get_subscribers():
    try:
        conn, cursor = connect_to_db()
        cursor.execute("SELECT * FROM bot_admin_app_subscriber")
        rows = cursor.fetchall()
        subscribers = []
        for row in rows:
            subscriber = {
                'subscriber_id': row[0],
                'user_id': row[1],
                'username': row[2],
                'phone': row[3],
                'adress': row[4]
            }
            subscribers.append(subscriber)
        return subscribers
    except psycopg2.Error as error:
        print(f'Ошибка при получении пользователей: {error}.')
    finally:
        cursor.close()
        conn.close()

