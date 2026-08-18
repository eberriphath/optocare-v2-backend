import pytest

from app import create_app


@pytest.fixture
def app():
    app = create_app()

    app.config.update(
        TESTING=True
    )

    with app.app_context():
        yield app


@pytest.fixture
def client(app):
    return app.test_client()


def login(client, email, password):
    response = client.post(
        "/api/auth/login",
        json={
            "email": email,
            "password": password
        }
    )

    assert response.status_code == 200

    return response.get_json()["access_token"]


@pytest.fixture
def admin_token(client):
    return login(
        client,
        "riphatheber@gmail.com",
        "  "
    )


@pytest.fixture
def partner_token(client):
    return login(
        client,
        "productiontest@gmail.com",
        "NewSecurePassword123!"
    )


def test_app_starts(client):
    response = client.get("/api/partners")

    assert response.status_code == 200


def test_application_requires_required_fields(client):
    response = client.post(
        "/api/applications",
        json={
            "full_name": "Test Partner"
        }
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["error"] == "Missing required fields"
    assert "email" in data["fields"]


def test_invalid_login_is_rejected(client):
    response = client.post(
        "/api/auth/login",
        json={
            "email": "does-not-exist@example.com",
            "password": "WrongPassword123!"
        }
    )

    assert response.status_code == 401


def test_protected_route_requires_token(client):
    response = client.get("/api/partner/dashboard")

    assert response.status_code == 401


def test_partner_can_access_dashboard(client, partner_token):
    response = client.get(
        "/api/partner/dashboard",
        headers={
            "Authorization": f"Bearer {partner_token}"
        }
    )

    assert response.status_code == 200

    data = response.get_json()

    assert "user" in data
    assert "partner" in data
    assert "statistics" in data


def test_partner_can_access_profile(client, partner_token):
    response = client.get(
        "/api/partner/profile",
        headers={
            "Authorization": f"Bearer {partner_token}"
        }
    )

    assert response.status_code == 200

    data = response.get_json()

    assert "user" in data
    assert "partner" in data


def test_partner_cannot_access_admin_routes(client, partner_token):
    response = client.get(
        "/api/admin/dashboard",
        headers={
            "Authorization": f"Bearer {partner_token}"
        }
    )

    assert response.status_code == 403


def test_admin_can_access_admin_dashboard(client, admin_token):
    response = client.get(
        "/api/admin/dashboard",
        headers={
            "Authorization": f"Bearer {admin_token}"
        }
    )

    assert response.status_code == 200

    data = response.get_json()

    assert "statistics" in data


def test_partner_service_crud(client, partner_token):
    headers = {
        "Authorization": f"Bearer {partner_token}"
    }

    # CREATE
    response = client.post(
        "/api/partner/services",
        headers=headers,
        json={
            "name": "Automated Test Eye Examination",
            "description": "Test service",
            "category": "Eye Care",
            "price": 1500,
            "is_active": True
        }
    )

    assert response.status_code == 201

    data = response.get_json()
    assert "service" in data

    service_id = data["service"]["id"]

    # READ
    response = client.get(
        "/api/partner/services",
        headers=headers
    )

    assert response.status_code == 200

    services = response.get_json()["services"]

    assert any(
        service["id"] == service_id
        for service in services
    )

    # UPDATE
    response = client.patch(
        f"/api/partner/services/{service_id}",
        headers=headers,
        json={
            "price": 2000,
            "description": "Updated test service"
        }
    )

    assert response.status_code == 200

    updated = response.get_json()["service"]

    assert updated["price"] == 2000.0
    assert updated["description"] == "Updated test service"

    # INVALID UPDATE
    response = client.patch(
        f"/api/partner/services/{service_id}",
        headers=headers,
        json={
            "name": ""
        }
    )

    assert response.status_code == 400

    # DELETE
    response = client.delete(
        f"/api/partner/services/{service_id}",
        headers=headers
    )

    assert response.status_code == 200

    # VERIFY DELETED
    response = client.patch(
        f"/api/partner/services/{service_id}",
        headers=headers,
        json={
            "price": 1000
        }
    )

    assert response.status_code == 404


def test_partner_product_crud(client, partner_token):
    headers = {
        "Authorization": f"Bearer {partner_token}"
    }

    # CREATE
    response = client.post(
        "/api/partner/products",
        headers=headers,
        json={
            "name": "Automated Test Frame",
            "description": "Test optical frame",
            "category": "Frames",
            "brand": "Optocare Test",
            "price": 3500,
            "stock_quantity": 10,
            "is_available": True
        }
    )

    assert response.status_code == 201

    data = response.get_json()
    assert "product" in data

    product_id = data["product"]["id"]

    # READ
    response = client.get(
        "/api/partner/products",
        headers=headers
    )

    assert response.status_code == 200

    products = response.get_json()["products"]

    assert any(
        product["id"] == product_id
        for product in products
    )

    # UPDATE
    response = client.patch(
        f"/api/partner/products/{product_id}",
        headers=headers,
        json={
            "price": 4000,
            "stock_quantity": 15
        }
    )

    assert response.status_code == 200

    updated = response.get_json()["product"]

    assert updated["price"] == 4000.0
    assert updated["stock_quantity"] == 15

    # INVALID PRICE
    response = client.patch(
        f"/api/partner/products/{product_id}",
        headers=headers,
        json={
            "price": -500
        }
    )

    assert response.status_code == 400

    # INVALID STOCK
    response = client.patch(
        f"/api/partner/products/{product_id}",
        headers=headers,
        json={
            "stock_quantity": -1
        }
    )

    assert response.status_code == 400

    # DELETE
    response = client.delete(
        f"/api/partner/products/{product_id}",
        headers=headers
    )

    assert response.status_code == 200

    # VERIFY DELETED
    response = client.patch(
        f"/api/partner/products/{product_id}",
        headers=headers,
        json={
            "price": 1000
        }
    )

    assert response.status_code == 404

def test_review_submission_and_moderation(
    client,
    admin_token
):
    # Submit review
    response = client.post(
        "/api/reviews",
        json={
            "partner_id": 3,
            "reviewer_name": "Automated Test Reviewer",
            "reviewer_email": "reviewer@example.com",
            "rating": 5,
            "comment": "Excellent optical service."
        }
    )

    assert response.status_code == 201

    data = response.get_json()

    assert "review" in data

    review_id = data["review"]["id"]

    # Admin retrieves review
    response = client.get(
        f"/api/admin/reviews/{review_id}",
        headers={
            "Authorization": f"Bearer {admin_token}"
        }
    )

    assert response.status_code == 200

    review = response.get_json()["review"]

    assert review["id"] == review_id
    assert review["is_approved"] is False

    # Approve review
    response = client.patch(
        f"/api/admin/reviews/{review_id}",
        headers={
            "Authorization": f"Bearer {admin_token}"
        },
        json={
            "is_approved": True,
            "admin_notes": "Approved by automated test."
        }
    )

    assert response.status_code == 200

    updated = response.get_json()["review"]

    assert updated["is_approved"] is True
    assert updated["admin_notes"] == "Approved by automated test."

    # Verify public visibility
    response = client.get(
        "/api/reviews/partner/3"
    )

    assert response.status_code == 200

    reviews = response.get_json()["reviews"]

    assert any(
        review["id"] == review_id
        for review in reviews
    )


def test_partner_cannot_modify_another_partners_service(
    client,
    partner_token
):
    headers = {
        "Authorization": f"Bearer {partner_token}"
    }

    # Try to update a service that does not belong to this partner
    response = client.patch(
        "/api/partner/services/999999",
        headers=headers,
        json={
            "price": 1
        }
    )

    assert response.status_code in (403, 404)


def test_partner_cannot_modify_another_partners_product(
    client,
    partner_token
):
    headers = {
        "Authorization": f"Bearer {partner_token}"
    }

    # Try to update a product that does not belong to this partner
    response = client.patch(
        "/api/partner/products/999999",
        headers=headers,
        json={
            "price": 1
        }
    )

    assert response.status_code in (403, 404)


def test_admin_can_get_partners(
    client,
    admin_token
):
    response = client.get(
        "/api/admin/partners",
        headers={
            "Authorization": f"Bearer {admin_token}"
        }
    )

    assert response.status_code == 200

    data = response.get_json()

    assert "partners" in data
    assert isinstance(data["partners"], list)


def test_admin_can_get_reviews(
    client,
    admin_token
):
    response = client.get(
        "/api/admin/reviews",
        headers={
            "Authorization": f"Bearer {admin_token}"
        }
    )

    assert response.status_code == 200

    data = response.get_json()

    assert "reviews" in data
    assert isinstance(data["reviews"], list)


def test_partner_cannot_access_admin_partners(
    client,
    partner_token
):
    response = client.get(
        "/api/admin/partners",
        headers={
            "Authorization": f"Bearer {partner_token}"
        }
    )

    assert response.status_code == 403


def test_partner_cannot_access_admin_reviews(
    client,
    partner_token
):
    response = client.get(
        "/api/admin/reviews",
        headers={
            "Authorization": f"Bearer {partner_token}"
        }
    )

    assert response.status_code == 403


def test_password_change_requires_authentication(client):
    response = client.patch(
        "/api/partner/password",
        json={
            "current_password": "wrong",
            "new_password": "AnotherSecurePassword123!",
            "confirm_password": "AnotherSecurePassword123!"
        }
    )

    assert response.status_code == 401


def test_public_partner_endpoints(client):
    # Public partner list
    response = client.get(
        "/api/partners"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert "partners" in data
    assert isinstance(data["partners"], list)

    # Public partner detail
    response = client.get(
        "/api/partners/3"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert "partner" in data

    # Public products
    response = client.get(
        "/api/partners/3/products"
    )

    assert response.status_code == 200

    # Public services
    response = client.get(
        "/api/partners/3/services"
    )

    assert response.status_code == 200


def test_nonexistent_partner_returns_404(client):
    response = client.get(
        "/api/partners/999999"
    )

    assert response.status_code == 404


def test_nonexistent_service_returns_404(
    client,
    partner_token
):
    response = client.patch(
        "/api/partner/services/999999",
        headers={
            "Authorization": f"Bearer {partner_token}"
        },
        json={
            "price": 1000
        }
    )

    assert response.status_code == 404


def test_nonexistent_product_returns_404(
    client,
    partner_token
):
    response = client.patch(
        "/api/partner/products/999999",
        headers={
            "Authorization": f"Bearer {partner_token}"
        },
        json={
            "price": 1000
        }
    )

    assert response.status_code == 404


def test_application_admin_workflow(
    client,
    admin_token
):
    admin_headers = {
        "Authorization": f"Bearer {admin_token}"
    }

    # -------------------------------------------------
    # 1. Submit a new application
    # -------------------------------------------------

    response = client.post(
        "/api/applications",
        json={
            "full_name": "Automated Application Test",
            "position": "Optometrist",
            "email": "automated-application-test@example.com",
            "phone": "0711111111",
            "company_name": "Automated Test Optical",
            "services_offered": (
                "Eye examinations and prescription lenses"
            ),
            "partner_type": "clinic"
        }
    )

    assert response.status_code == 201

    data = response.get_json()

    application_id = data["application"]["id"]

    assert data["application"]["status"] == "pending"

    # -------------------------------------------------
    # 2. Admin retrieves application
    # -------------------------------------------------

    response = client.get(
        f"/api/admin/applications/{application_id}",
        headers=admin_headers
    )

    assert response.status_code == 200

    application = response.get_json()["application"]

    assert application["id"] == application_id
    assert application["status"] == "pending"

    # -------------------------------------------------
    # 3. Admin rejects application
    # -------------------------------------------------

    response = client.patch(
        f"/api/admin/applications/{application_id}/reject",
        headers=admin_headers,
        json={
            "review_notes": (
                "Rejected during automated backend test."
            )
        }
    )

    assert response.status_code == 200

    rejected = response.get_json()["application"]

    assert rejected["status"] == "rejected"
    assert rejected["review_notes"] == (
        "Rejected during automated backend test."
    )

    # -------------------------------------------------
    # 4. Already-rejected application cannot be rejected again
    # -------------------------------------------------

    response = client.patch(
        f"/api/admin/applications/{application_id}/reject",
        headers=admin_headers,
        json={
            "review_notes": "Trying again."
        }
    )

    assert response.status_code == 400

    # -------------------------------------------------
    # 5. Admin can retrieve application list
    # -------------------------------------------------

    response = client.get(
        "/api/admin/applications",
        headers=admin_headers
    )

    assert response.status_code == 200

    applications = response.get_json()["applications"]

    assert any(
        application["id"] == application_id
        for application in applications
    )


def test_rejection_requires_review_notes(
    client,
    admin_token
):
    admin_headers = {
        "Authorization": f"Bearer {admin_token}"
    }

    # Create application
    response = client.post(
        "/api/applications",
        json={
            "full_name": "Rejection Notes Test",
            "position": "Optician",
            "email": f"rejection-notes-test-{__import__('uuid').uuid4().hex}@example.com",
            "phone": "0722222222",
            "company_name": "Rejection Notes Optical",
            "services_offered": "Optical services",
            "partner_type": "clinic"
        }
    )

    assert response.status_code == 201

    application_id = response.get_json()["application"]["id"]

    # Attempt rejection without notes
    response = client.patch(
        f"/api/admin/applications/{application_id}/reject",
        headers=admin_headers,
        json={}
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["error"] == (
        "Review notes are required when rejecting an application"
    )


def test_admin_partner_controls(
    client,
    admin_token
):
    headers = {
        "Authorization": f"Bearer {admin_token}"
    }

    partner_id = 3

    # ---------------------------------------------
    # Get individual partner
    # ---------------------------------------------

    response = client.get(
        f"/api/admin/partners/{partner_id}",
        headers=headers
    )

    assert response.status_code == 200

    partner = response.get_json()["partner"]

    assert partner["id"] == partner_id

    # ---------------------------------------------
    # Deactivate partner
    # ---------------------------------------------

    response = client.patch(
        f"/api/admin/partners/{partner_id}/status",
        headers=headers,
        json={
            "is_active": False
        }
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["partner"]["user"]["is_active"] is False

    # ---------------------------------------------
    # Reactivate partner
    # ---------------------------------------------

    response = client.patch(
        f"/api/admin/partners/{partner_id}/status",
        headers=headers,
        json={
            "is_active": True
        }
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["partner"]["user"]["is_active"] is True

    # ---------------------------------------------
    # Remove verification
    # ---------------------------------------------

    response = client.patch(
        f"/api/admin/partners/{partner_id}/verification",
        headers=headers,
        json={
            "is_verified": False
        }
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["partner"]["is_verified"] is False

    # ---------------------------------------------
    # Restore verification
    # ---------------------------------------------

    response = client.patch(
        f"/api/admin/partners/{partner_id}/verification",
        headers=headers,
        json={
            "is_verified": True
        }
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["partner"]["is_verified"] is True


def test_admin_partner_controls_validate_input(
    client,
    admin_token
):
    headers = {
        "Authorization": f"Bearer {admin_token}"
    }

    partner_id = 3

    # Invalid status value
    response = client.patch(
        f"/api/admin/partners/{partner_id}/status",
        headers=headers,
        json={
            "is_active": "yes"
        }
    )

    assert response.status_code == 400

    # Invalid verification value
    response = client.patch(
        f"/api/admin/partners/{partner_id}/verification",
        headers=headers,
        json={
            "is_verified": "yes"
        }
    )

    assert response.status_code == 400

    # Missing status
    response = client.patch(
        f"/api/admin/partners/{partner_id}/status",
        headers=headers,
        json={}
    )

    assert response.status_code == 400

    # Missing verification
    response = client.patch(
        f"/api/admin/partners/{partner_id}/verification",
        headers=headers,
        json={}
    )

    assert response.status_code == 400