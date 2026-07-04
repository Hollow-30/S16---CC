
import os
import psycopg2
import random
import pandas as pd
import psycopg # Not strictly used in app functions but was imported earlier

# Database connection URL (replace with your actual URL)
DATABASE_URL="postgresql://gabriel:O1JqMd7jyWGNLMMY46bXBA@young-fawn-28533.j77.aws-us-east-1.cockroachlabs.cloud:26257/defaultdb?sslmode=verify-full"

def get_conn():
    """Establishes and returns a new CockroachDB connection."""
    return psycopg2.connect(DATABASE_URL)

def listar_productos():
    """Lista todos los productos en la base de datos."""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SET DATABASE = tienda_db;")
            cur.execute("SELECT id, nombre, precio, stock FROM productos;")
            rows = cur.fetchall()
            column_names = [desc[0] for desc in cur.description]
    return pd.DataFrame(rows, columns=column_names)

def añadir_producto(nombre, precio, stock):
    """Añade un nuevo producto a la base de datos."""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SET DATABASE = tienda_db;")
            cur.execute("INSERT INTO productos (nombre, precio, stock) VALUES (%s, %s, %s)",
                        (nombre, precio, stock))
        conn.commit()
    print(f"Producto '{nombre}' añadido con éxito.")

def registrar_venta(producto_id, cantidad):
    """Registra una venta y actualiza el stock del producto."""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SET DATABASE = tienda_db;")
            # Insertar la venta
            cur.execute("INSERT INTO ventas (producto_id, cantidad) VALUES (%s, %s)",
                        (producto_id, cantidad))

            # Actualizar el stock del producto
            cur.execute("UPDATE productos SET stock = stock - %s WHERE id = %s",
                        (cantidad, producto_id))
        conn.commit()
    print(f"Venta de {cantidad} unidades para producto {producto_id} registrada y stock actualizado.")



if __name__ == '__main__':
    print("Demostración de la aplicación ---")

    # 1. Listar productos iniciales
    print("1. Productos actuales:")
    df_initial_products = listar_productos()
    print(df_initial_products.to_string())
    print(f"Total de productos: {len(df_initial_products)}")

    # 2. Añadir un nuevo producto
    print("2. Añadiendo 'Laptop Gaming'...")
    añadir_producto("Laptop Gaming", 1200.50, 10)
    df_after_add = listar_productos()
    print("Productos después de añadir 'Laptop Gaming':")
    print(df_after_add[df_after_add['nombre'] == 'Laptop Gaming'].to_string())
    print(f"Total de productos: {len(df_after_add)}")

    # 3. Registrar una venta para el nuevo producto
    print("3. Registrando una venta para 'Laptop Gaming'...")
    # Obtener el ID del 'Laptop Gaming' recién añadido
    laptop_gaming_id = df_after_add[df_after_add['nombre'] == 'Laptop Gaming']['id'].iloc[0]
    cantidad_vendida = 2
    initial_stock_laptop = df_after_add[df_after_add['nombre'] == 'Laptop Gaming']['stock'].iloc[0]
    print(f"Stock inicial de 'Laptop Gaming': {initial_stock_laptop}")

    registrar_venta(laptop_gaming_id, cantidad_vendida)

    df_after_sale = listar_productos()
    final_stock_laptop = df_after_sale[df_after_sale['nombre'] == 'Laptop Gaming']['stock'].iloc[0]
    print("Stock final de 'Laptop Gaming':")
    print(df_after_sale[df_after_sale['nombre'] == 'Laptop Gaming'].to_string())
    print(f"Stock final esperado: {initial_stock_laptop - cantidad_vendida}")

    print("--- Demostración completada ---")
