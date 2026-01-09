from flask import Flask, render_template, request, session
import unicodedata
import difflib

app = Flask(__name__)
app.secret_key = "vital_health_123"

# ---------- FUNCIONES ----------
def quitar_tildes(texto):
    return ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    )

def sugerir_productos(texto, productos_normalizados):
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

productos_normalizados = {quitar_tildes(k): k for k in productos}

# Secciones de Kits (para desplegar con botones)
kits_te = {
    "TÉ DETOX 1 SEMANA": 25.00,
    "TÉ DETOX 2 SEMANAS": 42.00,
    "TÉ DETOX 3 SEMANAS": 56.00,
    "TÉ DETOX 4 SEMANAS": 68.00,
    "TÉ DETOX 5 SEMANAS": 80.00
}

kits_perdida = {
    "KIT PÉRDIDA DE PESO 4 SEMANAS": 162.49,
    "KIT PÉRDIDA DE PESO 5 SEMANAS": 175.49
}

# Keywords especiales (opcional)
keywords = {
    "CAFE": ["NEUROKAFE", "LOVKAFE", "LATTEKAFE", "THERMOKAFE"]
}

# ---------- RUTA PRINCIPAL ----------
@app.route("/", methods=["GET", "POST"])
def index():
    if "carrito" not in session:
        session["carrito"] = []

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
            entrada = quitar_tildes(request.form.get("producto").upper())

            if "CAFE" in entrada:
                producto_encontrado = "NEUROKAFE"
            else:
                for p_norm, p_real in productos_normalizados.items():
                    if p_norm in entrada:
                        producto_encontrado = p_real
                        break

            if producto_encontrado:
                precio = productos[producto_encontrado]
            else:
                mensaje = "❌ Producto no encontrado."
                sugerencias = sugerir_productos(entrada, productos_normalizados)

        # AGREGAR AL CARRITO
        elif accion == "agregar":
            producto = request.form.get("producto_real")
            session["carrito"].append(producto)
            session.modified = True
            mensaje = f"✔️ {producto} agregado al carrito."

        # FINALIZAR COMPRA
        elif accion == "finalizar":
            session.clear()
            mensaje = "✅ Compra confirmada. Un agente se comunicará contigo."

    total = sum(productos.get(p, 0) for p in session.get("carrito", []))

    return render_template(
        "index.html",
        productos=productos,
        kits_te=kits_te,
        kits_perdida=kits_perdida,
        carrito=session.get("carrito", []),
        total=total,
        mensaje=mensaje,
        producto_encontrado=producto_encontrado,
        precio=precio,
        sugerencias=sugerencias,
        nombre=session.get("nombre"),
        edad=session.get("edad")
    )

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")