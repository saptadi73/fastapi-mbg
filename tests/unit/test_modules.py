from fastapi.testclient import TestClient

from app.main import app


def test_identity_endpoint_returns_envelope() -> None:
    with TestClient(app) as client:
        login_response = client.post(
            "/api/v1/identity/login",
            data={"username": "operator@example.com", "password": "mbg12345"},
        )
        access_token = login_response.json()["data"]["access_token"]
        response = client.get(
            "/api/v1/identity/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["data"]["email"] == "operator@example.com"


def test_identity_login_returns_token() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/identity/login",
            data={"username": "operator@example.com", "password": "mbg12345"},
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["data"]["token_type"] == "bearer"


def test_create_tenant_requires_authorized_role() -> None:
    with TestClient(app) as client:
        login_response = client.post(
            "/api/v1/identity/login",
            data={"username": "viewer@example.com", "password": "viewer123"},
        )
        access_token = login_response.json()["data"]["access_token"]
        response = client.post(
            "/api/v1/tenants/",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "code": "MBG-FORBIDDEN",
                "name": "Should Not Create",
                "is_active": True,
            },
        )

    assert response.status_code == 403
    payload = response.json()
    assert payload["code"] == "INSUFFICIENT_ROLE"


def test_create_tenant_without_token_is_rejected() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/tenants/",
            json={
                "code": "MBG-NOAUTH",
                "name": "Should Not Create",
                "is_active": True,
            },
        )

    assert response.status_code == 401
    payload = response.json()
    assert payload["success"] is False
    assert payload["code"] == "AUTHENTICATION_REQUIRED"
    assert "timestamp" in payload["meta"]


def test_identity_me_with_invalid_token_uses_standard_error_envelope() -> None:
    with TestClient(app) as client:
        response = client.get(
            "/api/v1/identity/me",
            headers={"Authorization": "Bearer invalid-token"},
        )

    assert response.status_code == 401
    payload = response.json()
    assert payload["success"] is False
    assert payload["code"] == "INVALID_ACCESS_TOKEN"
    assert "request_id" in payload["meta"]
    assert "timestamp" in payload["meta"]


def test_tenant_endpoint_returns_items() -> None:
    with TestClient(app) as client:
        response = client.get("/api/v1/tenants")

    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload["data"], list)
    assert "total" in payload["meta"]


def test_sppg_endpoint_returns_items() -> None:
    with TestClient(app) as client:
        response = client.get("/api/v1/sppg")

    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload["data"], list)


def test_school_endpoint_returns_items() -> None:
    with TestClient(app) as client:
        response = client.get("/api/v1/geography/schools/")

    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload["data"], list)


def test_beneficiary_endpoint_returns_items() -> None:
    with TestClient(app) as client:
        response = client.get("/api/v1/beneficiaries/")

    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload["data"], list)


def test_uom_endpoint_returns_items() -> None:
    with TestClient(app) as client:
        response = client.get("/api/v1/uoms/")

    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload["data"], list)


def test_product_endpoint_returns_items() -> None:
    with TestClient(app) as client:
        response = client.get("/api/v1/products/")

    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload["data"], list)


def test_recipe_endpoint_returns_items() -> None:
    with TestClient(app) as client:
        response = client.get("/api/v1/recipes/")

    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload["data"], list)


def test_meal_plan_endpoint_returns_items() -> None:
    with TestClient(app) as client:
        response = client.get("/api/v1/meal-plans/")

    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload["data"], list)


def test_recipe_line_endpoint_returns_items() -> None:
    with TestClient(app) as client:
        recipes = client.get("/api/v1/recipes/").json()["data"]
        recipe_id = recipes[0]["id"]
        response = client.get(f"/api/v1/recipes/{recipe_id}/lines")

    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload["data"], list)


def test_meal_plan_calculate_requirements_returns_preview() -> None:
    with TestClient(app) as client:
        login_response = client.post(
            "/api/v1/identity/login",
            data={"username": "operator@example.com", "password": "mbg12345"},
        )
        access_token = login_response.json()["data"]["access_token"]
        meal_plans = client.get("/api/v1/meal-plans/").json()["data"]
        meal_plan_id = meal_plans[0]["id"]
        response = client.post(
            f"/api/v1/meal-plans/{meal_plan_id}/calculate-requirements",
            headers={"Authorization": f"Bearer {access_token}"},
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["code"] == "MEAL_PLAN_REQUIREMENTS_CALCULATED"
    assert isinstance(payload["data"], list)


def test_meal_plan_submit_approve_and_reserve_flow_works() -> None:
    with TestClient(app) as client:
        login_response = client.post(
            "/api/v1/identity/login",
            data={"username": "operator@example.com", "password": "mbg12345"},
        )
        access_token = login_response.json()["data"]["access_token"]
        tenant_id = client.get("/api/v1/tenants/").json()["data"][0]["id"]
        sppg_id = client.get("/api/v1/sppg/").json()["data"][0]["id"]
        recipe_id = client.get("/api/v1/recipes/").json()["data"][0]["id"]
        create_response = client.post(
            "/api/v1/meal-plans/",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "tenant_id": tenant_id,
                "sppg_id": sppg_id,
                "recipe_id": recipe_id,
                "plan_date": "2026-07-21",
                "meal_type": "LUNCH",
                "status": "DRAFT",
                "planned_portions": 1,
                "budget_cost_per_portion": 15000,
                "notes": "Flow test meal plan",
            },
        )
        assert create_response.status_code == 201
        meal_plan_id = create_response.json()["data"]["id"]

        submit_response = client.post(
            f"/api/v1/meal-plans/{meal_plan_id}/submit",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert submit_response.status_code == 200
        assert submit_response.json()["data"]["status"] == "SUBMITTED"

        approve_response = client.post(
            f"/api/v1/meal-plans/{meal_plan_id}/approve",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert approve_response.status_code == 200
        assert approve_response.json()["data"]["status"] == "APPROVED"

        reserve_response = client.post(
            f"/api/v1/meal-plans/{meal_plan_id}/reserve-materials",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert reserve_response.status_code == 200
        payload = reserve_response.json()
        assert payload["code"] == "MEAL_PLAN_MATERIALS_RESERVED"
        assert payload["data"]["status"] == "MATERIAL_RESERVED"
        assert isinstance(payload["data"]["reserved_items"], list)


def test_meal_plan_cost_preview_returns_estimates() -> None:
    with TestClient(app) as client:
        meal_plan_id = client.get("/api/v1/meal-plans/").json()["data"][0]["id"]
        response = client.get(f"/api/v1/meal-plans/{meal_plan_id}/cost-preview")

    assert response.status_code == 200
    payload = response.json()
    assert payload["code"] == "MEAL_PLAN_COST_PREVIEW_FOUND"
    assert payload["data"]["total_estimated_cost"] >= 0
    assert isinstance(payload["data"]["line_items"], list)


def test_create_purchase_request_from_meal_plan_shortage_works() -> None:
    with TestClient(app) as client:
        login_response = client.post(
            "/api/v1/identity/login",
            data={"username": "operator@example.com", "password": "mbg12345"},
        )
        access_token = login_response.json()["data"]["access_token"]
        tenant_id = client.get("/api/v1/tenants/").json()["data"][0]["id"]
        sppg_id = client.get("/api/v1/sppg/").json()["data"][0]["id"]
        recipe_id = client.get("/api/v1/recipes/").json()["data"][0]["id"]
        create_meal_plan_response = client.post(
            "/api/v1/meal-plans/",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "tenant_id": tenant_id,
                "sppg_id": sppg_id,
                "recipe_id": recipe_id,
                "plan_date": "2026-07-22",
                "meal_type": "LUNCH",
                "status": "DRAFT",
                "planned_portions": 5000,
                "budget_cost_per_portion": 15000,
                "notes": "Shortage PR test",
            },
        )
        assert create_meal_plan_response.status_code == 201
        meal_plan_id = create_meal_plan_response.json()["data"]["id"]

        response = client.post(
            f"/api/v1/procurement/purchase-requests/from-meal-plan/{meal_plan_id}",
            headers={"Authorization": f"Bearer {access_token}"},
        )

    assert response.status_code == 201
    payload = response.json()
    assert payload["code"] == "PURCHASE_REQUEST_CREATED"
    assert len(payload["data"]["lines"]) > 0


def test_create_goods_receipt_from_purchase_request_posts_inventory() -> None:
    with TestClient(app) as client:
        login_response = client.post(
            "/api/v1/identity/login",
            data={"username": "operator@example.com", "password": "mbg12345"},
        )
        access_token = login_response.json()["data"]["access_token"]
        tenant_id = client.get("/api/v1/tenants/").json()["data"][0]["id"]
        sppg_id = client.get("/api/v1/sppg/").json()["data"][0]["id"]
        recipe_id = client.get("/api/v1/recipes/").json()["data"][0]["id"]
        warehouse_id = client.get("/api/v1/inventory/warehouses/").json()["data"][0]["id"]
        create_meal_plan_response = client.post(
            "/api/v1/meal-plans/",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "tenant_id": tenant_id,
                "sppg_id": sppg_id,
                "recipe_id": recipe_id,
                "plan_date": "2026-07-23",
                "meal_type": "LUNCH",
                "status": "DRAFT",
                "planned_portions": 1200,
                "budget_cost_per_portion": 15000,
                "notes": "Goods receipt test",
            },
        )
        meal_plan_id = create_meal_plan_response.json()["data"]["id"]
        purchase_request_response = client.post(
            f"/api/v1/procurement/purchase-requests/from-meal-plan/{meal_plan_id}",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        purchase_request_id = purchase_request_response.json()["data"]["purchase_request"]["id"]
        transaction_count_before = len(client.get("/api/v1/inventory/transactions/").json()["data"])

        response = client.post(
            f"/api/v1/procurement/purchase-requests/goods-receipts/from-purchase-request/{purchase_request_id}",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "warehouse_id": warehouse_id,
                "receipt_date": "2026-07-19",
                "notes": "Received from supplier",
            },
        )

        transaction_count_after = len(client.get("/api/v1/inventory/transactions/").json()["data"])

    assert response.status_code == 201
    payload = response.json()
    assert payload["code"] == "GOODS_RECEIPT_CREATED"
    assert len(payload["data"]["lines"]) > 0
    assert transaction_count_after > transaction_count_before


def test_create_and_complete_production_order_flow_works() -> None:
    with TestClient(app) as client:
        login_response = client.post(
            "/api/v1/identity/login",
            data={"username": "operator@example.com", "password": "mbg12345"},
        )
        access_token = login_response.json()["data"]["access_token"]
        tenant_id = client.get("/api/v1/tenants/").json()["data"][0]["id"]
        sppg_id = client.get("/api/v1/sppg/").json()["data"][0]["id"]
        recipe_id = client.get("/api/v1/recipes/").json()["data"][0]["id"]

        meal_plan_response = client.post(
            "/api/v1/meal-plans/",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "tenant_id": tenant_id,
                "sppg_id": sppg_id,
                "recipe_id": recipe_id,
                "plan_date": "2026-07-24",
                "meal_type": "LUNCH",
                "status": "DRAFT",
                "planned_portions": 10,
                "budget_cost_per_portion": 15000,
                "notes": "Production flow test"
            },
        )
        meal_plan_id = meal_plan_response.json()["data"]["id"]

        client.post(f"/api/v1/meal-plans/{meal_plan_id}/submit", headers={"Authorization": f"Bearer {access_token}"})
        client.post(f"/api/v1/meal-plans/{meal_plan_id}/approve", headers={"Authorization": f"Bearer {access_token}"})
        reserve_response = client.post(
            f"/api/v1/meal-plans/{meal_plan_id}/reserve-materials",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert reserve_response.status_code == 200

        create_response = client.post(
            f"/api/v1/production-orders/from-meal-plan/{meal_plan_id}",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert create_response.status_code == 201
        production_order_id = create_response.json()["data"]["production_order"]["id"]

        complete_response = client.post(
            f"/api/v1/production-orders/{production_order_id}/complete",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "actual_portions": 10,
                "accepted_portions": 10,
                "rejected_portions": 0
            },
        )
        assert complete_response.status_code == 200
        assert complete_response.json()["data"]["production_order"]["status"] == "COMPLETED"

        cost_sheet_response = client.get(f"/api/v1/production-orders/{production_order_id}/cost-sheet")

    assert cost_sheet_response.status_code == 200
    assert cost_sheet_response.json()["code"] == "PRODUCTION_COST_SHEET_FOUND"


def test_create_delivery_order_and_record_proof_flow_works() -> None:
    with TestClient(app) as client:
        login_response = client.post(
            "/api/v1/identity/login",
            data={"username": "operator@example.com", "password": "mbg12345"},
        )
        access_token = login_response.json()["data"]["access_token"]
        tenant_id = client.get("/api/v1/tenants/").json()["data"][0]["id"]
        sppg_id = client.get("/api/v1/sppg/").json()["data"][0]["id"]
        recipe_id = client.get("/api/v1/recipes/").json()["data"][0]["id"]
        school_id = client.get("/api/v1/geography/schools/").json()["data"][0]["id"]

        meal_plan_response = client.post(
            "/api/v1/meal-plans/",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "tenant_id": tenant_id,
                "sppg_id": sppg_id,
                "recipe_id": recipe_id,
                "plan_date": "2026-07-25",
                "meal_type": "LUNCH",
                "status": "DRAFT",
                "planned_portions": 5,
                "budget_cost_per_portion": 15000,
                "notes": "Delivery flow test"
            },
        )
        meal_plan_id = meal_plan_response.json()["data"]["id"]
        client.post(f"/api/v1/meal-plans/{meal_plan_id}/submit", headers={"Authorization": f"Bearer {access_token}"})
        client.post(f"/api/v1/meal-plans/{meal_plan_id}/approve", headers={"Authorization": f"Bearer {access_token}"})
        client.post(f"/api/v1/meal-plans/{meal_plan_id}/reserve-materials", headers={"Authorization": f"Bearer {access_token}"})

        production_order_response = client.post(
            f"/api/v1/production-orders/from-meal-plan/{meal_plan_id}",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        production_order_id = production_order_response.json()["data"]["production_order"]["id"]
        client.post(
            f"/api/v1/production-orders/{production_order_id}/complete",
            headers={"Authorization": f"Bearer {access_token}"},
            json={"actual_portions": 5, "accepted_portions": 5, "rejected_portions": 0},
        )

        create_delivery_response = client.post(
            f"/api/v1/delivery-orders/from-production-order/{production_order_id}",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "school_id": school_id,
                "planned_departure": "2026-07-25T07:00:00Z",
                "planned_arrival": "2026-07-25T08:00:00Z",
                "receiver_name": "Petugas Sekolah"
            },
        )
        assert create_delivery_response.status_code == 201
        delivery_order_id = create_delivery_response.json()["data"]["delivery_order"]["id"]

        proof_response = client.post(
            f"/api/v1/delivery-orders/{delivery_order_id}/proof",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "received_at": "2026-07-25T08:05:00Z",
                "receiver_name": "Petugas Sekolah",
                "receiver_gps": "-6.1702,106.8283",
                "received_portions": 5,
                "rejected_portions": 0,
                "temperature_celsius": 62.5,
                "condition_notes": "Diterima baik"
            },
        )

    assert proof_response.status_code == 201
    payload = proof_response.json()
    assert payload["code"] == "DELIVERY_PROOF_RECORDED"
    assert payload["data"]["delivery_order"]["status"] == "RECEIVED"


def test_warehouse_endpoint_returns_items() -> None:
    with TestClient(app) as client:
        response = client.get("/api/v1/inventory/warehouses/")

    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload["data"], list)


def test_inventory_balance_endpoint_returns_items() -> None:
    with TestClient(app) as client:
        response = client.get("/api/v1/inventory/balances/")

    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload["data"], list)


def test_create_inventory_transaction_requires_authorized_role() -> None:
    with TestClient(app) as client:
        admin_login_response = client.post(
            "/api/v1/identity/login",
            data={"username": "operator@example.com", "password": "mbg12345"},
        )
        admin_access_token = admin_login_response.json()["data"]["access_token"]
        login_response = client.post(
            "/api/v1/identity/login",
            data={"username": "viewer@example.com", "password": "viewer123"},
        )
        access_token = login_response.json()["data"]["access_token"]
        warehouses = client.get("/api/v1/inventory/warehouses/").json()["data"]
        products = client.get("/api/v1/products/").json()["data"]
        uoms = client.get("/api/v1/uoms/").json()["data"]
        tenant_id = client.get("/api/v1/tenants/").json()["data"][0]["id"]
        sppg_id = client.get("/api/v1/sppg/").json()["data"][0]["id"]
        if not warehouses:
            create_warehouse_response = client.post(
                "/api/v1/inventory/warehouses/",
                headers={"Authorization": f"Bearer {admin_access_token}"},
                json={
                    "tenant_id": tenant_id,
                    "sppg_id": sppg_id,
                    "code": "WH-TEST-01",
                    "name": "Warehouse Test 01",
                    "warehouse_type": "MAIN",
                    "location": "Gudang Test",
                    "is_active": True,
                },
            )
            assert create_warehouse_response.status_code == 201
            warehouses = client.get("/api/v1/inventory/warehouses/").json()["data"]
        response = client.post(
            "/api/v1/inventory/transactions/",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "tenant_id": tenant_id,
                "sppg_id": sppg_id,
                "transaction_type": "RECEIPT",
                "product_id": products[0]["id"],
                "destination_warehouse_id": warehouses[0]["id"],
                "quantity": 1,
                "uom_id": uoms[0]["id"],
                "unit_cost": 1000,
                "transaction_at": "2026-07-19T16:30:00Z"
            },
        )

    assert response.status_code == 403
    assert response.json()["code"] == "INSUFFICIENT_ROLE"
