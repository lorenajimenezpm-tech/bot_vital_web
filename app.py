import os
import unicodedata
import difflib
from flask import Flask, render_template, request, session

# ---------- CONFIGURACIÓN DE FLASK ----------
# Forzar a Flask a usar la carpeta 'templates' junto al archivo
app = Flask(
    __name__,
    template_folder=os.path.join(os.path.dirname(__file__), "templates")
)
app.secret_key = "vital_health_123"

# ---------- FUNCIONES ----------
def quitar_tildes(texto):
    """Quita tildes y acentos de un texto."""
    return ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    )

def sugerir_productos(texto, productos_normalizados):
    """Devuelve hasta 3 coincidencias aproximadas de productos."""
    return difflib.get_close_matches(
        texto,
        productos_normalizados.keys(),
        n=3,
        cutoff=0.6
    )

# ---------- DATOS ----------
productos = {
    "ORGANEX": 56.00,
    "VITAREN": 56.00,
    "VITALY": 56.00,
    "VASCULAX": 56.00,
    "BALANCE": 56.00,
    "GLUTATION": 90.00,
    "VITADOL": 56.00,
    "FORTYFLORA": 56.00,
    "NEUROKAFE": 70.00,
    "THERMOKAFE": 70.00,
    "LOVKAFE": 70.00,
    "LATTEKAFE": 70.00,
    "TEDETOX": 25.00,
    "OMEGA3": 90.00,
    "VITALPRO": 90.00,
    "NITRO": 70.00,
    "NRGY": 56.00,
    "COLÁGENO": 90.00,
    "CONTROL": 56.00,
    "VITALBOOST": 56.00,
    "CURCUMAX": 56.00,
    "DAILY": 100.00,
    "GLUTATION PLUS": 100.00,
    "DAILY SACHET": 110.00
}

# Diccionario normalizado para comparación
productos_normalizados = {quitar_tildes(k): k for k in productos}

# Palabras clave especiales
keywords = {
    "CAFE": ["NEUROKAFE", "LOVKAFE", "LATTEKAFE", "THERMOKAFE"]
}

# ---------- RUTA PRINCIPAL ----------
@app.route("/", methods=["GET", "POST"])
def index():
    # Inicializar sesión si no existe
    if "carrito" not in session:
        session["carrito"] = []
    if "nombre" not in session:
        session["nombre"] = None

    mensaje = ""
    producto_encontrado = None
    precio = 0

    if request.method == "POST":
        accion = request.form.get("accion")

        # DATOS PERSONALES
        if accion == "datos":
            session["nombre"] = request.form.get("nombre")
            session["edad"] = request.form.get("edad")

        # CONSULTAR PRODUCTO
        elif accion == "consultar":
            entrada = quitar_tildes(request.form.get("producto").upper())

            # Manejar palabras clave
            encontrado = False
            for key, lista in keywords.items():
                if key in entrada:
                    producto_encontrado = lista[0]
                    encontrado = True
                    break

            # Búsqueda normal
            if not encontrado:
                for p_norm, p_real in productos_normalizados.items():
                    if p_norm in entrada:
                        producto_encontrado = p_real
                        encontrado = True
                        break

            if producto_encontrado:
                precio = productos[producto_encontrado]
            else:
                mensaje = "❌ Producto no encontrado."

        # AGREGAR AL CARRITO
        elif accion == "agregar":
            producto = request.form.get("producto_real")
            if producto:  # Solo agregar si existe
                session["carrito"].append(producto)
                session.modified = True
                mensaje = "✔️ Producto agregado al carrito."

        # FINALIZAR COMPRA
        elif accion == "finalizar":
            session.clear()
            mensaje = "✅ Compra confirmada. Un agente se comunicará contigo."

    # Calcular total del carrito
    total = sum(productos.get(p, 0) for p in session.get("carrito", []))

    return render_template(
        "index.html",
        productos=productos,
        carrito=session.get("carrito", []),
        total=total,
        mensaje=mensaje,
        producto_encontrado=producto_encontrado,
        precio=precio,
        nombre=session.get("nombre")
    )

# ---------- EJECUTAR APP ----------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)