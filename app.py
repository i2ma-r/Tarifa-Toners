from flask import Flask, render_template, request, url_for
import pandas as pd
import math

app = Flask(__name__)

# Cargar el catálogo completo desde el CSV.
# Se asume que el CSV tiene la siguiente estructura:
# MacroCat, Cat, Code, Description, Brand, Color, Price, Stock, Barcode, Weight,
# Qty_box, Box_discount, Street_price, Vat, MOQ, URL_photo, Data_version, Description_HTML
df_products = pd.read_csv('life365-cat-prodlistfinal - life365-cat-prodlist.csv')

# Añadir una nueva columna "Producto" a partir de la columna "MacroCat"
df_products["Producto"] = df_products["MacroCat"]

# Renombrar columnas para que se ajusten a lo que usa la aplicación.
# Se asigna:
# "Nombre"         <-- corresponde a la columna "Code" (el nombre real del producto)
# "Descripción"    <-- corresponde a la columna "Description_HTML"
# "Marca"          <-- corresponde a la columna "Brand"
# "Precio"         <-- corresponde a la columna "Price"
# "URL_photo"      <-- permanece igual
df_products.rename(columns={
    "Code": "Nombre",
    "Description_HTML": "Descripción",
    "Brand": "Marca",
    "Price": "Precio"
}, inplace=True)

PRODUCTS_PER_PAGE = 50

# Variables globales para la barra lateral:
unique_brands = sorted(df_products['Marca'].dropna().unique())
unique_productos = sorted(df_products["Producto"].dropna().unique())

@app.route('/')
def index():
    # Parámetros de búsqueda vía query string.
    query = request.args.get('q', default='').strip()
    selected_brand = request.args.get('brand', default='').strip()
    try:
        page = int(request.args.get('page', 1))
        if page < 1:
            page = 1
    except ValueError:
        page = 1

    # Filtrar el DataFrame según búsqueda y/o marca.
    filtered_df = df_products.copy()
    if selected_brand:
        filtered_df = filtered_df[filtered_df['Marca'] == selected_brand]
    if query:
        filtered_df = filtered_df[
            filtered_df['Nombre'].str.contains(query, case=False, na=False) |
            filtered_df['Descripción'].str.contains(query, case=False, na=False)
        ]
    
    # Paginación.
    total_products = len(filtered_df)
    total_pages = math.ceil(total_products / PRODUCTS_PER_PAGE)
    
    start = (page - 1) * PRODUCTS_PER_PAGE
    end = start + PRODUCTS_PER_PAGE
    current_products = filtered_df.iloc[start:end].to_dict(orient='records')
    
    # Renderizar la plantilla principal, pasando además la barra lateral con las categorías.
    return render_template(
        'catalogo.html',
        products=current_products,
        query=query,
        selected_brand=selected_brand,
        brands=unique_brands,
        productos_sidebar=unique_productos,
        page=page,
        total_pages=total_pages,
        current_category=None  # No se ha seleccionado categoría desde la barra lateral
    )

@app.route('/categoria/<producto>')
def show_category(producto):
    # Filtrar los productos según la categoría (Producto = MacroCat)
    filtered_df = df_products[df_products["Producto"] == producto]
    
    try:
        page = int(request.args.get('page', 1))
        if page < 1:
            page = 1
    except ValueError:
        page = 1

    total_products = len(filtered_df)
    total_pages = math.ceil(total_products / PRODUCTS_PER_PAGE)
    
    start = (page - 1) * PRODUCTS_PER_PAGE
    end = start + PRODUCTS_PER_PAGE
    current_products = filtered_df.iloc[start:end].to_dict(orient='records')
    
    return render_template(
        'catalogo.html',
        products=current_products,
        query="",
        selected_brand="",
        brands=unique_brands,
        productos_sidebar=unique_productos,
        page=page,
        total_pages=total_pages,
        current_category=producto  # Se pasa la categoría actualmente seleccionada
    )

if __name__ == '__main__':
    app.run(debug=True)
