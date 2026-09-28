from datetime import datetime

from app.models import Client, Order


def generate_client_number():
    last_client = (
        Client.query
        .order_by(Client.id.desc())
        .first()
    )

    if last_client:
        next_number = last_client.id + 1
    else:
        next_number = 1

    return f"OPT-C-{next_number:06d}"


def generate_order_number():
    year = datetime.utcnow().year

    last_order = (
        Order.query
        .filter(
            Order.order_number.like(f"OPT-{year}-%")
        )
        .order_by(Order.id.desc())
        .first()
    )

    if last_order:
        last_sequence = int(
            last_order.order_number.split("-")[-1]
        )
        next_number = last_sequence + 1
    else:
        next_number = 1

    return f"OPT-{year}-{next_number:06d}"