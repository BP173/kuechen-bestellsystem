from flask import Blueprint, render_template, request, redirect, url_for, send_file
from collections import defaultdict
from io import BytesIO

from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

from .models import db, Product, Department, Order, OrderItem


main = Blueprint('main', __name__)


# -----------------------------
# HELPER: offene Bestellung
# -----------------------------
def get_open_order():
    order = Order.query.filter_by(is_closed=False).first()

    if not order:
        order = Order()
        db.session.add(order)
        db.session.commit()

    return order


# -----------------------------
# STARTSEITE
# -----------------------------
@main.route('/')
def index():
    order = get_open_order()

    products = Product.query.all()
    departments = Department.query.all()
    items = order.items

    department_costs = defaultdict(float)

    for item in items:
        department_costs[item.department.name] += item.quantity * item.price_at_order

    return render_template(
        'index.html',
        products=products,
        departments=departments,
        items=items,
        department_costs=department_costs
    )


# -----------------------------
# ITEM HINZUFÜGEN
# -----------------------------
@main.route('/add-item', methods=['POST'])
def add_item():
    order = get_open_order()

    product_id = int(request.form['product_id'])
    department_id = int(request.form['department_id'])
    quantity = float(request.form['quantity'])

    product = Product.query.get(product_id)

    item = OrderItem(
        order_id=order.id,
        product_id=product_id,
        department_id=department_id,
        quantity=quantity,
        price_at_order=product.price_per_unit
    )

    db.session.add(item)
    db.session.commit()

    return redirect(url_for('main.index'))


# -----------------------------
# BESTELLUNG ABSCHLIESSEN
# -----------------------------
@main.route('/close-order')
def close_order():
    order = Order.query.filter_by(is_closed=False).first()

    if not order:
        return "Keine offene Bestellung vorhanden", 400

    order.is_closed = True
    db.session.commit()

    return redirect(url_for('main.supplier_orders'))


# -----------------------------
# LIEFERANTEN-ÜBERSICHT
# -----------------------------
@main.route('/supplier-orders')
def supplier_orders():
    order = Order.query.filter_by(is_closed=True).order_by(Order.id.desc()).first()

    if not order:
        return "Keine abgeschlossene Bestellung vorhanden", 400

    grouped = defaultdict(lambda: defaultdict(float))

    for item in order.items:
        supplier = item.product.supplier.name
        product = item.product.name
        grouped[supplier][product] += item.quantity

    return render_template('supplier_orders.html', grouped=grouped)


# -----------------------------
# PDF EXPORT PRO LIEFERANT
# -----------------------------
@main.route('/supplier/<supplier_name>/pdf')
def supplier_pdf(supplier_name):

    order = Order.query.filter_by(is_closed=True).order_by(Order.id.desc()).first()

    if not order:
        return "Keine Bestellung vorhanden", 400

    data_map = defaultdict(float)

    for item in order.items:
        if item.product.supplier.name != supplier_name:
            continue

        data_map[item.product.name] += item.quantity

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer)

    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph(f"Bestellung - {supplier_name}", styles["Title"]))
    elements.append(Spacer(1, 12))

    data = [["Produkt", "Menge"]]

    for product, qty in data_map.items():
        data.append([product, str(qty)])

    table = Table(data)

    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.grey),
        ("TEXTCOLOR", (0,0), (-1,0), colors.whitesmoke),
        ("GRID", (0,0), (-1,-1), 0.5, colors.black),
        ("BACKGROUND", (0,1), (-1,-1), colors.lightgrey),
    ]))

    elements.append(table)

    doc.build(elements)

    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"{supplier_name}_bestellung.pdf",
        mimetype='application/pdf'
    )