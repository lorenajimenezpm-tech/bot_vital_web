import os
import unicodedata
import difflib
from flask import Flask, render_template, request, session

# ---------- CONFIGURACIÓN DE FLASK ----------
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
    """
    Devuelve hasta 3 coincidencias aproximadas de productos.
    Funciona para errores de escritura, mayúsculas/minúsculas, tildes.
    """
    texto_norm = quitar_tildes(texto.upper())
    return difflib.get_close_matches(
        texto_norm,
        productos_normalizados.keys(),
        n=3,
        cutoff=0.5
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

# Productos “fijos” que no están en el diccionario principal
precios_fijos = {
    "TÉ DETOX 1 SEMANA": 25.00,
    "TÉ DETOX 2 SEMANAS": 42.00,
    "TÉ DETOX 3 SEMANAS": 56.00,
    "TÉ DETOX 4 SEMANAS": 68.00,
    "TÉ DETOX 5 SEMANAS": 80.00,
    "KIT PÉRDIDA DE PESO 5 SEMANAS": 175.49,
    "KIT PÉRDIDA DE PESO 4 SEMANAS": 162.49
}

# Diccionario normalizado para comparación
productos_normalizados = {quitar_tildes(k): k for k in {**productos, **precios_fijos}}

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
    if "edad" not in session:
        session["edad"] = None

    mensaje = ""
    producto_encontrado = None
    precio = 0
    sugerencias = []

    if request.method == "POST":
        accion = request.form.get("accion")

        # DATOS PERSONALES
        if accion == "datos":
            session["nombre"] = request.form.get("nombre")
            session["edad"] = request.form.get("edad")

        # CONSULTAR PRODUCTO
        elif accion == "consultar":
            entrada = request.form.get("producto")
            entrada_norm = quitar_tildes(entrada.upper())

            # Manejar palabras clave
            encontrado = False
            for key, lista in keywords.items():
                if key in entrada_norm:
                    producto_encontrado = lista[0]
                    encontrado = True
                    break

            # Búsqueda normal (exacta o aproximada)
            if not encontrado:
                if entrada_norm in productos_normalizados:
                    producto_encontrado = productos_normalizados[entrada_norm]
                    encontrado = True
                else:
                    # Sugerir productos cercanos
                    sugerencias_norm = sugerir_productos(entrada, productos_normalizados)
                    if sugerencias_norm:
                        sugerencias = [productos_normalizados[s] for s in sugerencias_norm]
                        mensaje = f"❌ Producto no encontrado. Quizás quiso decir: {', '.join(sugerencias)}"

            if producto_encontrado:
                precio = productos.get(producto_encontrado, precios_fijos.get(producto_encontrado, 0))
                mensaje = f"✔️ Producto encontrado: {producto_encontrado} – ${precio:.2f}"

        # AGREGAR AL CARRITO
        elif accion == "agregar":
            producto = request.form.get("producto_real")
            if producto:
                session["carrito"].append(producto)
                session.modified = True
                mensaje = f"✔️ Producto agregado al carrito: {producto}"

        # FINALIZAR COMPRA
        elif accion == "finalizar":
            session.clear()
            mensaje = "✅ Compra confirmada. Un agente se comunicará contigo."

    # Calcular total del carrito
    total = sum(
        productos.get(p, precios_fijos.get(p, 0))
        for p in session.get("carrito", [])
    )

    return render_template(
        "index.html",
        productos=productos,
        carrito=session.get("carrito", []),
        total=total,
        mensaje=mensaje,
        producto_encontrado=producto_encontrado,
        precio=precio,
        sugerencias=sugerencias,
        nombre=session.get("nombre"),
        edad=session.get("edad")
    )

# ---------- EJECUTAR APP ----------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)