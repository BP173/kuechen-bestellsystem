import csv
from app import create_app
from app.models import db, Product, Supplier

app = create_app()

with app.app_context():
    supplier = Supplier.query.first()
    if not supplier:
        supplier = Supplier(name="Standard")
        db.session.add(supplier)
        db.session.commit()

    with open('produkte.csv', newline='', encoding='utf-8-sig') as file:
        reader = csv.DictReader(file)

        for row in reader:
            # keys sauber machen
            row = {k.strip().lower(): v for k, v in row.items()}

            product = Product(
                name=row['name'],
                unit=row['unit'],
                price_per_unit=float(row['price_per_unit']),
                supplier_id=supplier.id
            )

            db.session.add(product)

        db.session.commit()