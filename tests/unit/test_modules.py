from uuid import uuid4

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
    assert payload["data"]["active_sppg_id"] is not None
    assert len(payload["data"]["accessible_sppg_ids"]) >= 1


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
    assert payload["data"]["active_sppg_id"] is not None


def test_identity_switch_active_sppg_returns_new_token() -> None:
    with TestClient(app) as client:
        login_response = client.post(
            "/api/v1/identity/login",
            data={"username": "operator@example.com", "password": "mbg12345"},
        )
        access_token = login_response.json()["data"]["access_token"]
        current_user = client.get(
            "/api/v1/identity/me",
            headers={"Authorization": f"Bearer {access_token}"},
        ).json()["data"]
        active_sppg_id = current_user["active_sppg_id"]

        response = client.post(
            "/api/v1/identity/switch-active-sppg",
            headers={"Authorization": f"Bearer {access_token}"},
            json={"sppg_id": active_sppg_id},
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["code"] == "IDENTITY_ACTIVE_SPPG_SWITCHED"
    assert payload["data"]["token_type"] == "bearer"
    assert payload["data"]["active_sppg_id"] == active_sppg_id


def test_identity_user_sppg_access_admin_endpoints_work() -> None:
    with TestClient(app) as client:
        login_response = client.post(
            "/api/v1/identity/login",
            data={"username": "operator@example.com", "password": "mbg12345"},
        )
        access_token = login_response.json()["data"]["access_token"]
        current_user = client.get(
            "/api/v1/identity/me",
            headers={"Authorization": f"Bearer {access_token}"},
        ).json()["data"]
        user_id = current_user["id"]
        accessible_sppg_ids = current_user["accessible_sppg_ids"]
        active_sppg_id = current_user["active_sppg_id"]

        get_response = client.get(
            f"/api/v1/identity/users/{user_id}/sppg-access",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        put_response = client.put(
            f"/api/v1/identity/users/{user_id}/sppg-access",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "accessible_sppg_ids": accessible_sppg_ids,
                "active_sppg_id": active_sppg_id,
            },
        )

    assert get_response.status_code == 200
    get_payload = get_response.json()
    assert get_payload["code"] == "IDENTITY_USER_SPPG_ACCESS_FOUND"
    assert get_payload["data"]["user_id"] == user_id
    assert active_sppg_id in get_payload["data"]["accessible_sppg_ids"]

    assert put_response.status_code == 200
    put_payload = put_response.json()
    assert put_payload["code"] == "IDENTITY_USER_SPPG_ACCESS_UPDATED"
    assert put_payload["data"]["user_id"] == user_id
    assert put_payload["data"]["active_sppg_id"] == active_sppg_id


def test_identity_admin_user_management_endpoints_work() -> None:
    with TestClient(app) as client:
        login_response = client.post(
            "/api/v1/identity/login",
            data={"username": "operator@example.com", "password": "mbg12345"},
        )
        access_token = login_response.json()["data"]["access_token"]
        tenant_id = client.get("/api/v1/tenants/").json()["data"][0]["id"]
        sppg_id = client.get("/api/v1/sppg/").json()["data"][0]["id"]
        user_email = f"qa-admin-{uuid4()}@example.com"

        list_response = client.get(
            "/api/v1/identity/users",
            headers={"Authorization": f"Bearer {access_token}", "X-Tenant-ID": tenant_id},
        )
        create_response = client.post(
            "/api/v1/identity/users",
            headers={"Authorization": f"Bearer {access_token}", "X-Tenant-ID": tenant_id},
            json={
                "tenant_id": tenant_id,
                "full_name": "QA Admin User",
                "email": user_email,
                "password": "qa12345",
                "role_names": ["tenant_admin"],
                "is_active": True,
                "accessible_sppg_ids": [sppg_id],
                "active_sppg_id": sppg_id,
            },
        )
        created_user_id = create_response.json()["data"]["id"]
        get_response = client.get(
            f"/api/v1/identity/users/{created_user_id}",
            headers={"Authorization": f"Bearer {access_token}", "X-Tenant-ID": tenant_id},
        )
        update_response = client.put(
            f"/api/v1/identity/users/{created_user_id}",
            headers={"Authorization": f"Bearer {access_token}", "X-Tenant-ID": tenant_id},
            json={
                "full_name": "QA Admin User Updated",
                "role_names": ["operations_manager"],
                "is_active": True,
                "password": None,
                "accessible_sppg_ids": [sppg_id],
                "active_sppg_id": sppg_id,
            },
        )

    assert list_response.status_code == 200
    list_payload = list_response.json()
    assert list_payload["code"] == "IDENTITY_USER_LIST_FOUND"
    assert all(item["tenant_id"] == tenant_id for item in list_payload["data"])

    assert create_response.status_code == 200
    create_payload = create_response.json()
    assert create_payload["code"] == "IDENTITY_USER_CREATED"
    assert create_payload["data"]["email"] == user_email
    assert create_payload["data"]["active_sppg_id"] == sppg_id

    assert get_response.status_code == 200
    get_payload = get_response.json()
    assert get_payload["code"] == "IDENTITY_USER_FOUND"
    assert get_payload["data"]["id"] == created_user_id

    assert update_response.status_code == 200
    update_payload = update_response.json()
    assert update_payload["code"] == "IDENTITY_USER_UPDATED"
    assert update_payload["data"]["full_name"] == "QA Admin User Updated"
    assert update_payload["data"]["role_names"] == ["operations_manager"]


def test_sppg_endpoint_supports_tenant_context_filter() -> None:
    with TestClient(app) as client:
        first_tenant_id = client.get("/api/v1/tenants/").json()["data"][0]["id"]
        first_sppg_id = client.get("/api/v1/sppg/").json()["data"][0]["id"]

        response = client.get(
            "/api/v1/sppg/",
            headers={"X-Tenant-ID": first_tenant_id, "X-SPPG-ID": first_sppg_id},
        )

    assert response.status_code == 200
    assert response.headers["X-Tenant-ID"] == first_tenant_id
    assert response.headers["X-SPPG-ID"] == first_sppg_id
    payload = response.json()
    assert payload["success"] is True
    assert len(payload["data"]) >= 1
    assert all(item["tenant_id"] == first_tenant_id for item in payload["data"])


def test_procurement_purchase_request_list_supports_scope_headers() -> None:
    with TestClient(app) as client:
        login_response = client.post(
            "/api/v1/identity/login",
            data={"username": "operator@example.com", "password": "mbg12345"},
        )
        access_token = login_response.json()["data"]["access_token"]
        tenant_id = client.get("/api/v1/tenants/").json()["data"][0]["id"]
        sppg_id = client.get("/api/v1/sppg/").json()["data"][0]["id"]
        recipe_id = client.get("/api/v1/recipes/").json()["data"][0]["id"]

        probe_meal_plan = client.post(
            "/api/v1/meal-plans/",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "tenant_id": tenant_id,
                "sppg_id": sppg_id,
                "recipe_id": recipe_id,
                "plan_date": "2026-07-28",
                "meal_type": "LUNCH",
                "status": "DRAFT",
                "planned_portions": 100,
                "budget_cost_per_portion": 15000,
                "notes": "Procurement scope test",
            },
        )
        assert probe_meal_plan.status_code == 201
        probe_meal_plan_id = probe_meal_plan.json()["data"]["id"]
        requirement_resp = client.post(
            f"/api/v1/meal-plans/{probe_meal_plan_id}/calculate-requirements",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert requirement_resp.status_code == 200
        requirement_line = requirement_resp.json()["data"][0]
        component_product_id = requirement_line["component_product_id"]
        gross_quantity_for_100 = float(requirement_line["gross_quantity"])
        balances = client.get("/api/v1/inventory/balances/").json()["data"]
        available_stock = sum(
            balance["quantity_available"]
            for balance in balances
            if balance["product_id"] == component_product_id and balance["sppg_id"] == sppg_id
        )
        planned_portions = int(((available_stock + gross_quantity_for_100) / gross_quantity_for_100) * 100) + 100

        meal_plan_response = client.post(
            "/api/v1/meal-plans/",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "tenant_id": tenant_id,
                "sppg_id": sppg_id,
                "recipe_id": recipe_id,
                "plan_date": "2026-07-29",
                "meal_type": "LUNCH",
                "status": "DRAFT",
                "planned_portions": planned_portions,
                "budget_cost_per_portion": 15000,
                "notes": "Procurement scope shortage test",
            },
        )
        assert meal_plan_response.status_code == 201
        meal_plan_id = meal_plan_response.json()["data"]["id"]

        create_pr_response = client.post(
            f"/api/v1/procurement/purchase-requests/from-meal-plan/{meal_plan_id}",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert create_pr_response.status_code == 201

        response = client.get(
            "/api/v1/procurement/purchase-requests/",
            headers={"X-Tenant-ID": tenant_id, "X-SPPG-ID": sppg_id},
        )

    assert response.status_code == 200
    assert response.headers["X-Tenant-ID"] == tenant_id
    assert response.headers["X-SPPG-ID"] == sppg_id
    payload = response.json()
    assert payload["success"] is True
    assert len(payload["data"]) >= 1
    assert all(item["tenant_id"] == tenant_id for item in payload["data"])
    assert all(item["sppg_id"] == sppg_id for item in payload["data"])


def test_production_order_list_supports_scope_headers() -> None:
    with TestClient(app) as client:
        tenant_id = client.get("/api/v1/tenants/").json()["data"][0]["id"]
        sppg_id = client.get("/api/v1/sppg/").json()["data"][0]["id"]

        response = client.get(
            "/api/v1/production-orders/",
            headers={"X-Tenant-ID": tenant_id, "X-SPPG-ID": sppg_id},
        )

    assert response.status_code == 200
    assert response.headers["X-Tenant-ID"] == tenant_id
    assert response.headers["X-SPPG-ID"] == sppg_id
    payload = response.json()
    assert payload["success"] is True
    assert all(item["tenant_id"] == tenant_id for item in payload["data"])
    assert all(item["sppg_id"] == sppg_id for item in payload["data"])


def test_delivery_order_list_supports_scope_headers() -> None:
    with TestClient(app) as client:
        tenant_id = client.get("/api/v1/tenants/").json()["data"][0]["id"]
        sppg_id = client.get("/api/v1/sppg/").json()["data"][0]["id"]

        response = client.get(
            "/api/v1/delivery-orders/",
            headers={"X-Tenant-ID": tenant_id, "X-SPPG-ID": sppg_id},
        )

    assert response.status_code == 200
    assert response.headers["X-Tenant-ID"] == tenant_id
    assert response.headers["X-SPPG-ID"] == sppg_id
    payload = response.json()
    assert payload["success"] is True
    assert all(item["tenant_id"] == tenant_id for item in payload["data"])
    assert all(item["sppg_id"] == sppg_id for item in payload["data"])


def test_account_list_supports_tenant_scope_header() -> None:
    with TestClient(app) as client:
        tenant_id = client.get("/api/v1/tenants/").json()["data"][0]["id"]
        response = client.get("/api/v1/accounts", headers={"X-Tenant-ID": tenant_id})

    assert response.status_code == 200
    assert response.headers["X-Tenant-ID"] == tenant_id
    payload = response.json()
    assert payload["success"] is True
    assert all(item["tenant_id"] == tenant_id for item in payload["data"])


def test_journal_entry_list_supports_tenant_scope_header() -> None:
    with TestClient(app) as client:
        tenant_id = client.get("/api/v1/tenants/").json()["data"][0]["id"]
        response = client.get("/api/v1/journal-entries", headers={"X-Tenant-ID": tenant_id})

    assert response.status_code == 200
    assert response.headers["X-Tenant-ID"] == tenant_id
    payload = response.json()
    assert payload["success"] is True
    assert all(item["tenant_id"] == tenant_id for item in payload["data"])


def test_budget_list_supports_tenant_scope_header() -> None:
    with TestClient(app) as client:
        tenant_id = client.get("/api/v1/tenants/").json()["data"][0]["id"]
        response = client.get("/api/v1/budgets", headers={"X-Tenant-ID": tenant_id})

    assert response.status_code == 200
    assert response.headers["X-Tenant-ID"] == tenant_id
    payload = response.json()
    assert payload["success"] is True
    assert all(item["tenant_id"] == tenant_id for item in payload["data"])


def test_program_endpoint_returns_items() -> None:
    with TestClient(app) as client:
        response = client.get("/api/v1/programs/")

    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload["data"], list)
    assert "total" in payload["meta"]


def test_program_create_and_assignment_flow_works() -> None:
    with TestClient(app) as client:
        login_response = client.post(
            "/api/v1/identity/login",
            data={"username": "operator@example.com", "password": "mbg12345"},
        )
        access_token = login_response.json()["data"]["access_token"]
        tenant_id = client.get("/api/v1/tenants/").json()["data"][0]["id"]
        sppg_id = client.get("/api/v1/sppg/").json()["data"][0]["id"]
        code_suffix = str(uuid4()).split("-")[0].upper()

        create_response = client.post(
            "/api/v1/programs/",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "code": f"PRG-{code_suffix}",
                "name": "Program MBG APBD Test",
                "description": "Program uji otomatis",
                "program_type": "PUBLIC",
                "funding_source_name": "APBD Provinsi",
                "start_date": "2026-07-19",
                "end_date": "2026-12-31",
                "status": "DRAFT",
                "is_active": True,
            },
        )
        assert create_response.status_code == 201, create_response.json()
        program_id = create_response.json()["data"]["id"]

        tenant_assignment_response = client.post(
            f"/api/v1/programs/{program_id}/tenants",
            headers={"Authorization": f"Bearer {access_token}", "X-Tenant-ID": tenant_id},
            json={
                "tenant_id": tenant_id,
                "start_date": "2026-07-19",
                "end_date": "2026-12-31",
                "is_active": True,
                "notes": "Tenant assignment test",
            },
        )
        period_response = client.post(
            f"/api/v1/programs/{program_id}/periods",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "code": "2026-H2",
                "name": "Semester 2 2026",
                "date_start": "2026-07-19",
                "date_end": "2026-12-31",
                "status": "OPEN",
                "notes": "Periode semester 2",
            },
        )
        sppg_assignment_response = client.post(
            f"/api/v1/programs/{program_id}/sppg",
            headers={
                "Authorization": f"Bearer {access_token}",
                "X-Tenant-ID": tenant_id,
                "X-SPPG-ID": sppg_id,
            },
            json={
                "tenant_id": tenant_id,
                "sppg_id": sppg_id,
                "start_date": "2026-07-19",
                "end_date": "2026-12-31",
                "is_active": True,
                "notes": "SPPG assignment test",
            },
        )
        detail_response = client.get(
            f"/api/v1/programs/{program_id}",
            headers={"X-Tenant-ID": tenant_id, "X-SPPG-ID": sppg_id},
        )
        scoped_list_response = client.get(
            "/api/v1/programs/",
            headers={"X-Tenant-ID": tenant_id, "X-SPPG-ID": sppg_id},
        )

    assert tenant_assignment_response.status_code == 201, tenant_assignment_response.json()
    assert tenant_assignment_response.json()["code"] == "PROGRAM_TENANT_ASSIGNED"

    assert period_response.status_code == 201, period_response.json()
    assert period_response.json()["code"] == "PROGRAM_PERIOD_CREATED"

    assert sppg_assignment_response.status_code == 201, sppg_assignment_response.json()
    assert sppg_assignment_response.json()["code"] == "PROGRAM_SPPG_ASSIGNED"

    assert detail_response.status_code == 200, detail_response.json()
    detail_payload = detail_response.json()
    assert detail_payload["code"] == "PROGRAM_FOUND"
    assert detail_payload["data"]["program"]["id"] == program_id
    assert len(detail_payload["data"]["periods"]) == 1
    assert len(detail_payload["data"]["tenant_assignments"]) == 1
    assert len(detail_payload["data"]["sppg_assignments"]) == 1

    assert scoped_list_response.status_code == 200, scoped_list_response.json()
    scoped_items = scoped_list_response.json()["data"]
    assert any(item["id"] == program_id for item in scoped_items)


def test_uom_create_rejects_tenant_write_scope_violation() -> None:
    with TestClient(app) as client:
        login_response = client.post(
            "/api/v1/identity/login",
            data={"username": "operator@example.com", "password": "mbg12345"},
        )
        access_token = login_response.json()["data"]["access_token"]
        response = client.post(
            "/api/v1/uoms/",
            headers={
                "Authorization": f"Bearer {access_token}",
                "X-Tenant-ID": str(uuid4()),
            },
            json={
                "tenant_id": client.get("/api/v1/tenants/").json()["data"][0]["id"],
                "code": "CTX-UOM-01",
                "name": "Context UOM",
                "symbol": "ctx",
                "dimension": "UNIT",
                "factor_to_base": 1.0,
                "is_active": True,
            },
        )

    assert response.status_code == 403
    payload = response.json()
    assert payload["code"] == "TENANT_WRITE_SCOPE_VIOLATION"


def test_meal_plan_create_rejects_sppg_write_scope_violation() -> None:
    with TestClient(app) as client:
        login_response = client.post(
            "/api/v1/identity/login",
            data={"username": "operator@example.com", "password": "mbg12345"},
        )
        access_token = login_response.json()["data"]["access_token"]
        tenant_id = client.get("/api/v1/tenants/").json()["data"][0]["id"]
        sppg_id = client.get("/api/v1/sppg/").json()["data"][0]["id"]
        recipe_id = client.get("/api/v1/recipes/").json()["data"][0]["id"]
        response = client.post(
            "/api/v1/meal-plans/",
            headers={
                "Authorization": f"Bearer {access_token}",
                "X-SPPG-ID": sppg_id,
            },
            json={
                "tenant_id": tenant_id,
                "sppg_id": str(uuid4()),
                "recipe_id": recipe_id,
                "plan_date": "2026-07-30",
                "meal_type": "LUNCH",
                "status": "DRAFT",
                "planned_portions": 10,
                "budget_cost_per_portion": 15000,
                "notes": "Scope violation test",
            },
        )

    assert response.status_code == 403
    payload = response.json()
    assert payload["code"] == "SPPG_WRITE_SCOPE_VIOLATION"


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
        probe_meal_plan = client.post(
            "/api/v1/meal-plans/",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "tenant_id": tenant_id,
                "sppg_id": sppg_id,
                "recipe_id": recipe_id,
                "plan_date": "2026-07-21",
                "meal_type": "LUNCH",
                "status": "DRAFT",
                "planned_portions": 100,
                "budget_cost_per_portion": 15000,
                "notes": "Shortage probe",
            },
        )
        assert probe_meal_plan.status_code == 201
        probe_meal_plan_id = probe_meal_plan.json()["data"]["id"]
        requirement_resp = client.post(
            f"/api/v1/meal-plans/{probe_meal_plan_id}/calculate-requirements",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert requirement_resp.status_code == 200
        requirement_line = requirement_resp.json()["data"][0]
        component_product_id = requirement_line["component_product_id"]
        gross_quantity_for_100 = float(requirement_line["gross_quantity"])
        balances = client.get("/api/v1/inventory/balances/").json()["data"]
        available_stock = sum(
            balance["quantity_available"]
            for balance in balances
            if balance["product_id"] == component_product_id and balance["sppg_id"] == sppg_id
        )
        planned_portions = int(((available_stock + gross_quantity_for_100) / gross_quantity_for_100) * 100) + 100
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
                "planned_portions": planned_portions,
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
        accounts = client.get("/api/v1/accounts").json()["data"]
        account_codes = {a["code"] for a in accounts}
        needed = [
            ("130000", "Persediaan Bahan", "ASSET", "DEBIT"),
            ("240000", "Barang Diterima Belum Ditagih", "LIABILITY", "CREDIT"),
        ]
        for code, name, category, normal_balance in needed:
            if code not in account_codes:
                resp = client.post(
                    "/api/v1/accounts",
                    headers={"Authorization": f"Bearer {access_token}"},
                    json={
                        "tenant_id": tenant_id,
                        "code": code,
                        "name": name,
                        "category": category,
                        "normal_balance": normal_balance,
                    },
                )
                assert resp.status_code == 201
        sppg_id = client.get("/api/v1/sppg/").json()["data"][0]["id"]
        recipe_id = client.get("/api/v1/recipes/").json()["data"][0]["id"]
        warehouse_id = client.get("/api/v1/inventory/warehouses/").json()["data"][0]["id"]
        probe_meal_plan = client.post(
            "/api/v1/meal-plans/",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "tenant_id": tenant_id,
                "sppg_id": sppg_id,
                "recipe_id": recipe_id,
                "plan_date": "2026-07-22",
                "meal_type": "LUNCH",
                "status": "DRAFT",
                "planned_portions": 100,
                "budget_cost_per_portion": 15000,
                "notes": "Goods receipt probe",
            },
        )
        assert probe_meal_plan.status_code == 201
        probe_meal_plan_id = probe_meal_plan.json()["data"]["id"]
        requirement_resp = client.post(
            f"/api/v1/meal-plans/{probe_meal_plan_id}/calculate-requirements",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert requirement_resp.status_code == 200
        requirement_line = requirement_resp.json()["data"][0]
        component_product_id = requirement_line["component_product_id"]
        gross_quantity_for_100 = float(requirement_line["gross_quantity"])
        balances = client.get("/api/v1/inventory/balances/").json()["data"]
        available_stock = sum(
            balance["quantity_available"]
            for balance in balances
            if balance["product_id"] == component_product_id and balance["sppg_id"] == sppg_id
        )
        planned_portions = int(((available_stock + gross_quantity_for_100) / gross_quantity_for_100) * 100) + 100
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
                "planned_portions": planned_portions,
                "budget_cost_per_portion": 15000,
                "notes": "Goods receipt test",
            },
        )
        meal_plan_id = create_meal_plan_response.json()["data"]["id"]
        purchase_request_response = client.post(
            f"/api/v1/procurement/purchase-requests/from-meal-plan/{meal_plan_id}",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert purchase_request_response.status_code == 201, purchase_request_response.json()
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


def test_create_purchase_request_reserves_budget_amount() -> None:
    with TestClient(app) as client:
        login_response = client.post(
            "/api/v1/identity/login",
            data={"username": "operator@example.com", "password": "mbg12345"},
        )
        access_token = login_response.json()["data"]["access_token"]
        tenant_id = client.get("/api/v1/tenants/").json()["data"][0]["id"]
        accounts = client.get("/api/v1/accounts").json()["data"]
        account_by_code = {a["code"]: a for a in accounts}
        if "510000" not in account_by_code:
            resp = client.post(
                "/api/v1/accounts",
                headers={"Authorization": f"Bearer {access_token}"},
                json={
                    "tenant_id": tenant_id,
                    "code": "510000",
                    "name": "Biaya Bahan",
                    "category": "COST_OF_SERVICE",
                    "normal_balance": "DEBIT",
                },
            )
            assert resp.status_code == 201
            accounts = client.get("/api/v1/accounts").json()["data"]
            account_by_code = {a["code"]: a for a in accounts}
        material_expense_account_id = account_by_code["510000"]["id"]

        budget_resp = client.post(
            "/api/v1/budgets",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "tenant_id": tenant_id,
                "name": "Budget Reservation Test",
                "date_start": "2026-07-01",
                "date_end": "2026-07-31",
                "version_number": 1,
                "notes": "Budget reserve from purchase request",
                "lines": [
                    {
                        "category_name": "BAHAN_BAKU",
                        "account_id": material_expense_account_id,
                        "planned_amount": 100000000,
                        "control_mode": "WARNING",
                        "tolerance_percentage": 0,
                    }
                ],
            },
        )
        assert budget_resp.status_code == 201
        budget_id = budget_resp.json()["data"]["budget"]["id"]
        submit_resp = client.post(
            f"/api/v1/budgets/{budget_id}/submit",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert submit_resp.status_code == 200
        approve_resp = client.post(
            f"/api/v1/budgets/{budget_id}/approve",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert approve_resp.status_code == 200

        sppg_id = client.get("/api/v1/sppg/").json()["data"][0]["id"]
        recipe_id = client.get("/api/v1/recipes/").json()["data"][0]["id"]
        probe_meal_plan = client.post(
            "/api/v1/meal-plans/",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "tenant_id": tenant_id,
                "sppg_id": sppg_id,
                "recipe_id": recipe_id,
                "plan_date": "2026-07-27",
                "meal_type": "LUNCH",
                "status": "DRAFT",
                "planned_portions": 100,
                "budget_cost_per_portion": 15000,
                "notes": "Budget reservation probe",
            },
        )
        assert probe_meal_plan.status_code == 201
        probe_meal_plan_id = probe_meal_plan.json()["data"]["id"]
        requirement_resp = client.post(
            f"/api/v1/meal-plans/{probe_meal_plan_id}/calculate-requirements",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert requirement_resp.status_code == 200
        requirement_line = requirement_resp.json()["data"][0]
        component_product_id = requirement_line["component_product_id"]
        gross_quantity_for_100 = float(requirement_line["gross_quantity"])
        balances = client.get("/api/v1/inventory/balances/").json()["data"]
        available_stock = sum(
            balance["quantity_available"]
            for balance in balances
            if balance["product_id"] == component_product_id and balance["sppg_id"] == sppg_id
        )
        planned_portions = int(((available_stock + gross_quantity_for_100) / gross_quantity_for_100) * 100) + 100
        meal_plan = client.post(
            "/api/v1/meal-plans/",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "tenant_id": tenant_id,
                "sppg_id": sppg_id,
                "recipe_id": recipe_id,
                "plan_date": "2026-07-28",
                "meal_type": "LUNCH",
                "status": "DRAFT",
                "planned_portions": planned_portions,
                "budget_cost_per_portion": 15000,
                "notes": "Budget reservation flow test",
            },
        )
        assert meal_plan.status_code == 201
        meal_plan_id = meal_plan.json()["data"]["id"]
        pr_resp = client.post(
            f"/api/v1/procurement/purchase-requests/from-meal-plan/{meal_plan_id}",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        availability_resp = client.get(f"/api/v1/budgets/{budget_id}/availability")

    assert pr_resp.status_code == 201, pr_resp.json()
    assert availability_resp.status_code == 200
    assert availability_resp.json()["data"]["lines"][0]["reserved_amount"] > 0


def test_goods_receipt_moves_budget_from_reserved_to_committed() -> None:
    with TestClient(app) as client:
        login_response = client.post(
            "/api/v1/identity/login",
            data={"username": "operator@example.com", "password": "mbg12345"},
        )
        access_token = login_response.json()["data"]["access_token"]
        tenant_id = client.get("/api/v1/tenants/").json()["data"][0]["id"]
        accounts = client.get("/api/v1/accounts").json()["data"]
        account_by_code = {a["code"]: a for a in accounts}
        needed = [
            ("130000", "Persediaan Bahan", "ASSET", "DEBIT"),
            ("240000", "Barang Diterima Belum Ditagih", "LIABILITY", "CREDIT"),
            ("510000", "Biaya Bahan", "COST_OF_SERVICE", "DEBIT"),
        ]
        for code, name, category, normal_balance in needed:
            if code not in account_by_code:
                resp = client.post(
                    "/api/v1/accounts",
                    headers={"Authorization": f"Bearer {access_token}"},
                    json={
                        "tenant_id": tenant_id,
                        "code": code,
                        "name": name,
                        "category": category,
                        "normal_balance": normal_balance,
                    },
                )
                assert resp.status_code == 201
        accounts = client.get("/api/v1/accounts").json()["data"]
        account_by_code = {a["code"]: a for a in accounts}
        material_expense_account_id = account_by_code["510000"]["id"]

        budget_resp = client.post(
            "/api/v1/budgets",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "tenant_id": tenant_id,
                "name": "Budget Commitment Test",
                "date_start": "2026-07-01",
                "date_end": "2026-07-31",
                "version_number": 1,
                "notes": "Budget commitment from goods receipt",
                "lines": [
                    {
                        "category_name": "BAHAN_BAKU",
                        "account_id": material_expense_account_id,
                        "planned_amount": 100000000,
                        "control_mode": "WARNING",
                        "tolerance_percentage": 0,
                    }
                ],
            },
        )
        assert budget_resp.status_code == 201
        budget_id = budget_resp.json()["data"]["budget"]["id"]
        client.post(f"/api/v1/budgets/{budget_id}/submit", headers={"Authorization": f"Bearer {access_token}"})
        client.post(f"/api/v1/budgets/{budget_id}/approve", headers={"Authorization": f"Bearer {access_token}"})

        sppg_id = client.get("/api/v1/sppg/").json()["data"][0]["id"]
        recipe_id = client.get("/api/v1/recipes/").json()["data"][0]["id"]
        warehouse_id = client.get("/api/v1/inventory/warehouses/").json()["data"][0]["id"]
        probe_meal_plan = client.post(
            "/api/v1/meal-plans/",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "tenant_id": tenant_id,
                "sppg_id": sppg_id,
                "recipe_id": recipe_id,
                "plan_date": "2026-07-27",
                "meal_type": "LUNCH",
                "status": "DRAFT",
                "planned_portions": 100,
                "budget_cost_per_portion": 15000,
                "notes": "Budget commitment probe",
            },
        )
        probe_meal_plan_id = probe_meal_plan.json()["data"]["id"]
        requirement_resp = client.post(
            f"/api/v1/meal-plans/{probe_meal_plan_id}/calculate-requirements",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        requirement_line = requirement_resp.json()["data"][0]
        component_product_id = requirement_line["component_product_id"]
        gross_quantity_for_100 = float(requirement_line["gross_quantity"])
        balances = client.get("/api/v1/inventory/balances/").json()["data"]
        available_stock = sum(
            balance["quantity_available"]
            for balance in balances
            if balance["product_id"] == component_product_id and balance["sppg_id"] == sppg_id
        )
        planned_portions = int(((available_stock + gross_quantity_for_100) / gross_quantity_for_100) * 100) + 100
        meal_plan = client.post(
            "/api/v1/meal-plans/",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "tenant_id": tenant_id,
                "sppg_id": sppg_id,
                "recipe_id": recipe_id,
                "plan_date": "2026-07-28",
                "meal_type": "LUNCH",
                "status": "DRAFT",
                "planned_portions": planned_portions,
                "budget_cost_per_portion": 15000,
                "notes": "Budget commitment flow test",
            },
        )
        meal_plan_id = meal_plan.json()["data"]["id"]
        pr_resp = client.post(
            f"/api/v1/procurement/purchase-requests/from-meal-plan/{meal_plan_id}",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert pr_resp.status_code == 201, pr_resp.json()
        purchase_request_id = pr_resp.json()["data"]["purchase_request"]["id"]
        availability_after_pr = client.get(f"/api/v1/budgets/{budget_id}/availability").json()["data"]["lines"][0]
        gr_resp = client.post(
            f"/api/v1/procurement/purchase-requests/goods-receipts/from-purchase-request/{purchase_request_id}",
            headers={"Authorization": f"Bearer {access_token}"},
            json={"warehouse_id": warehouse_id, "receipt_date": "2026-07-19", "notes": "Budget commitment GR"},
        )
        availability_after_gr = client.get(f"/api/v1/budgets/{budget_id}/availability").json()["data"]["lines"][0]

    assert gr_resp.status_code == 201, gr_resp.json()
    assert availability_after_pr["reserved_amount"] > 0
    assert availability_after_gr["reserved_amount"] < availability_after_pr["reserved_amount"]
    assert availability_after_gr["committed_amount"] > 0


def test_create_and_complete_production_order_flow_works() -> None:
    with TestClient(app) as client:
        login_response = client.post(
            "/api/v1/identity/login",
            data={"username": "operator@example.com", "password": "mbg12345"},
        )
        access_token = login_response.json()["data"]["access_token"]
        tenant_id = client.get("/api/v1/tenants/").json()["data"][0]["id"]
        accounts = client.get("/api/v1/accounts").json()["data"]
        account_codes = {a["code"] for a in accounts}
        needed = [
            ("130000", "Persediaan Bahan", "ASSET", "DEBIT"),
            ("510000", "Biaya Bahan", "COST_OF_SERVICE", "DEBIT"),
        ]
        for code, name, category, normal_balance in needed:
            if code not in account_codes:
                resp = client.post(
                    "/api/v1/accounts",
                    headers={"Authorization": f"Bearer {access_token}"},
                    json={
                        "tenant_id": tenant_id,
                        "code": code,
                        "name": name,
                        "category": category,
                        "normal_balance": normal_balance,
                    },
                )
                assert resp.status_code == 201
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


def test_accounting_account_and_journal_flow_works() -> None:
    with TestClient(app) as client:
        login_response = client.post(
            "/api/v1/identity/login",
            data={"username": "operator@example.com", "password": "mbg12345"},
        )
        access_token = login_response.json()["data"]["access_token"]
        tenant_id = client.get("/api/v1/tenants/").json()["data"][0]["id"]
        accounts = client.get("/api/v1/accounts").json()["data"]
        if len(accounts) < 2:
            create_account_1 = client.post(
                "/api/v1/accounts",
                headers={"Authorization": f"Bearer {access_token}"},
                json={
                    "tenant_id": tenant_id,
                    "code": "110000",
                    "name": "Kas dan Bank",
                    "category": "ASSET",
                    "normal_balance": "DEBIT",
                    "allow_posting": True,
                    "is_active": True,
                },
            )
            assert create_account_1.status_code == 201
            create_account_2 = client.post(
                "/api/v1/accounts",
                headers={"Authorization": f"Bearer {access_token}"},
                json={
                    "tenant_id": tenant_id,
                    "code": "510000",
                    "name": "Biaya Bahan",
                    "category": "COST_OF_SERVICE",
                    "normal_balance": "DEBIT",
                    "allow_posting": True,
                    "is_active": True,
                },
            )
            assert create_account_2.status_code == 201
            accounts = client.get("/api/v1/accounts").json()["data"]
        assert len(accounts) >= 2
        response = client.post(
            "/api/v1/journal-entries",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "tenant_id": tenant_id,
                "entry_date": "2026-07-19",
                "reference": "TEST-JE-01",
                "description": "Jurnal test",
                "source_module": "manual",
                "source_document_type": "manual_entry",
                "source_document_id": None,
                "lines": [
                    {"account_id": accounts[0]["id"], "line_type": "DEBIT", "amount": 100000, "description": "Debit"},
                    {"account_id": accounts[1]["id"], "line_type": "CREDIT", "amount": 100000, "description": "Credit"}
                ]
            },
        )
        assert response.status_code == 201
        journal_entry_id = response.json()["data"]["journal_entry"]["id"]
        post_response = client.post(
            f"/api/v1/journal-entries/{journal_entry_id}/post",
            headers={"Authorization": f"Bearer {access_token}"},
        )

    assert post_response.status_code == 200
    assert post_response.json()["data"]["journal_entry"]["status"] == "POSTED"


def test_goods_receipt_creates_posted_inventory_journal() -> None:
    with TestClient(app) as client:
        login_response = client.post(
            "/api/v1/identity/login",
            data={"username": "operator@example.com", "password": "mbg12345"},
        )
        access_token = login_response.json()["data"]["access_token"]
        tenant_id = client.get("/api/v1/tenants/").json()["data"][0]["id"]
        accounts = client.get("/api/v1/accounts").json()["data"]
        account_codes = {a["code"] for a in accounts}
        needed = [
            ("130000", "Persediaan Bahan", "ASSET", "DEBIT"),
            ("240000", "Barang Diterima Belum Ditagih", "LIABILITY", "CREDIT"),
        ]
        for code, name, category, normal_balance in needed:
            if code not in account_codes:
                resp = client.post(
                    "/api/v1/accounts",
                    headers={"Authorization": f"Bearer {access_token}"},
                    json={
                        "tenant_id": tenant_id,
                        "code": code,
                        "name": name,
                        "category": category,
                        "normal_balance": normal_balance,
                    },
                )
                assert resp.status_code == 201
        sppg_id = client.get("/api/v1/sppg/").json()["data"][0]["id"]
        recipe_id = client.get("/api/v1/recipes/").json()["data"][0]["id"]
        warehouse_id = client.get("/api/v1/inventory/warehouses/").json()["data"][0]["id"]
        probe_meal_plan = client.post(
            "/api/v1/meal-plans/",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "tenant_id": tenant_id,
                "sppg_id": sppg_id,
                "recipe_id": recipe_id,
                "plan_date": "2026-07-25",
                "meal_type": "LUNCH",
                "status": "DRAFT",
                "planned_portions": 100,
                "budget_cost_per_portion": 15000,
                "notes": "Journal goods receipt probe",
            },
        )
        assert probe_meal_plan.status_code == 201
        probe_meal_plan_id = probe_meal_plan.json()["data"]["id"]
        requirement_resp = client.post(
            f"/api/v1/meal-plans/{probe_meal_plan_id}/calculate-requirements",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert requirement_resp.status_code == 200
        requirement_line = requirement_resp.json()["data"][0]
        component_product_id = requirement_line["component_product_id"]
        gross_quantity_for_100 = float(requirement_line["gross_quantity"])
        balances = client.get("/api/v1/inventory/balances/").json()["data"]
        available_stock = sum(
            balance["quantity_available"]
            for balance in balances
            if balance["product_id"] == component_product_id and balance["sppg_id"] == sppg_id
        )
        planned_portions = int(((available_stock + gross_quantity_for_100) / gross_quantity_for_100) * 100) + 100
        meal_plan = client.post(
            "/api/v1/meal-plans/",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "tenant_id": tenant_id,
                "sppg_id": sppg_id,
                "recipe_id": recipe_id,
                "plan_date": "2026-07-26",
                "meal_type": "LUNCH",
                "status": "DRAFT",
                "planned_portions": planned_portions,
                "budget_cost_per_portion": 15000,
                "notes": "Journal goods receipt test",
            },
        )
        meal_plan_id = meal_plan.json()["data"]["id"]
        pr_resp = client.post(
            f"/api/v1/procurement/purchase-requests/from-meal-plan/{meal_plan_id}",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        purchase_request_id = pr_resp.json()["data"]["purchase_request"]["id"]
        je_before = len(client.get("/api/v1/journal-entries").json()["data"])
        gr_resp = client.post(
            f"/api/v1/procurement/purchase-requests/goods-receipts/from-purchase-request/{purchase_request_id}",
            headers={"Authorization": f"Bearer {access_token}"},
            json={"warehouse_id": warehouse_id, "receipt_date": "2026-07-19", "notes": "GR journal"},
        )
        je_after = len(client.get("/api/v1/journal-entries").json()["data"])

    assert gr_resp.status_code == 201
    assert je_after > je_before


def test_create_supplier_invoice_posts_payable_and_actualizes_budget() -> None:
    with TestClient(app) as client:
        login_response = client.post(
            "/api/v1/identity/login",
            data={"username": "operator@example.com", "password": "mbg12345"},
        )
        access_token = login_response.json()["data"]["access_token"]
        tenant_id = client.get("/api/v1/tenants/").json()["data"][0]["id"]
        accounts = client.get("/api/v1/accounts").json()["data"]
        account_by_code = {a["code"]: a for a in accounts}
        needed = [
            ("130000", "Persediaan Bahan", "ASSET", "DEBIT"),
            ("210000", "Hutang Supplier", "LIABILITY", "CREDIT"),
            ("240000", "Barang Diterima Belum Ditagih", "LIABILITY", "CREDIT"),
            ("510000", "Biaya Bahan", "COST_OF_SERVICE", "DEBIT"),
        ]
        for code, name, category, normal_balance in needed:
            if code not in account_by_code:
                resp = client.post(
                    "/api/v1/accounts",
                    headers={"Authorization": f"Bearer {access_token}"},
                    json={
                        "tenant_id": tenant_id,
                        "code": code,
                        "name": name,
                        "category": category,
                        "normal_balance": normal_balance,
                    },
                )
                assert resp.status_code == 201
        accounts = client.get("/api/v1/accounts").json()["data"]
        account_by_code = {a["code"]: a for a in accounts}
        material_expense_account_id = account_by_code["510000"]["id"]

        budget_resp = client.post(
            "/api/v1/budgets",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "tenant_id": tenant_id,
                "name": "Budget Invoice Actual Test",
                "date_start": "2026-07-01",
                "date_end": "2026-07-31",
                "version_number": 1,
                "notes": "Budget actualization from supplier invoice",
                "lines": [
                    {
                        "category_name": "BAHAN_BAKU",
                        "account_id": material_expense_account_id,
                        "planned_amount": 100000000,
                        "control_mode": "WARNING",
                        "tolerance_percentage": 0,
                    }
                ],
            },
        )
        assert budget_resp.status_code == 201
        budget_id = budget_resp.json()["data"]["budget"]["id"]
        submit_resp = client.post(
            f"/api/v1/budgets/{budget_id}/submit",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert submit_resp.status_code == 200
        approve_resp = client.post(
            f"/api/v1/budgets/{budget_id}/approve",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert approve_resp.status_code == 200

        sppg_id = client.get("/api/v1/sppg/").json()["data"][0]["id"]
        recipe_id = client.get("/api/v1/recipes/").json()["data"][0]["id"]
        warehouse_id = client.get("/api/v1/inventory/warehouses/").json()["data"][0]["id"]
        probe_meal_plan = client.post(
            "/api/v1/meal-plans/",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "tenant_id": tenant_id,
                "sppg_id": sppg_id,
                "recipe_id": recipe_id,
                "plan_date": "2026-07-27",
                "meal_type": "LUNCH",
                "status": "DRAFT",
                "planned_portions": 100,
                "budget_cost_per_portion": 15000,
                "notes": "Supplier invoice probe",
            },
        )
        assert probe_meal_plan.status_code == 201
        probe_meal_plan_id = probe_meal_plan.json()["data"]["id"]
        requirement_resp = client.post(
            f"/api/v1/meal-plans/{probe_meal_plan_id}/calculate-requirements",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert requirement_resp.status_code == 200
        requirement_line = requirement_resp.json()["data"][0]
        component_product_id = requirement_line["component_product_id"]
        gross_quantity_for_100 = float(requirement_line["gross_quantity"])
        balances = client.get("/api/v1/inventory/balances/").json()["data"]
        available_stock = sum(
            balance["quantity_available"]
            for balance in balances
            if balance["product_id"] == component_product_id and balance["sppg_id"] == sppg_id
        )
        planned_portions = int(((available_stock + gross_quantity_for_100) / gross_quantity_for_100) * 100) + 100

        meal_plan = client.post(
            "/api/v1/meal-plans/",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "tenant_id": tenant_id,
                "sppg_id": sppg_id,
                "recipe_id": recipe_id,
                "plan_date": "2026-07-28",
                "meal_type": "LUNCH",
                "status": "DRAFT",
                "planned_portions": planned_portions,
                "budget_cost_per_portion": 15000,
                "notes": "Supplier invoice flow test",
            },
        )
        assert meal_plan.status_code == 201
        meal_plan_id = meal_plan.json()["data"]["id"]
        pr_resp = client.post(
            f"/api/v1/procurement/purchase-requests/from-meal-plan/{meal_plan_id}",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert pr_resp.status_code == 201, pr_resp.json()
        purchase_request_id = pr_resp.json()["data"]["purchase_request"]["id"]
        gr_resp = client.post(
            f"/api/v1/procurement/purchase-requests/goods-receipts/from-purchase-request/{purchase_request_id}",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "warehouse_id": warehouse_id,
                "receipt_date": "2026-07-19",
                "notes": "GR for supplier invoice",
            },
        )
        assert gr_resp.status_code == 201
        goods_receipt_id = gr_resp.json()["data"]["goods_receipt"]["id"]

        je_before = len(client.get("/api/v1/journal-entries").json()["data"])
        invoice_resp = client.post(
            f"/api/v1/procurement/purchase-requests/supplier-invoices/from-goods-receipt/{goods_receipt_id}",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "invoice_date": "2026-07-19",
                "due_date": "2026-07-26",
                "budget_account_id": material_expense_account_id,
                "notes": "Invoice supplier posted",
            },
        )
        je_after = len(client.get("/api/v1/journal-entries").json()["data"])
        availability_resp = client.get(f"/api/v1/budgets/{budget_id}/availability")

    assert invoice_resp.status_code == 201, invoice_resp.json()
    assert invoice_resp.json()["code"] == "SUPPLIER_INVOICE_CREATED"
    assert len(invoice_resp.json()["data"]["lines"]) > 0
    assert je_after > je_before
    assert availability_resp.status_code == 200
    assert availability_resp.json()["data"]["lines"][0]["committed_amount"] == 0
    assert availability_resp.json()["data"]["lines"][0]["actual_amount"] > 0


def test_create_supplier_payment_posts_cash_journal_and_marks_invoice_paid() -> None:
    with TestClient(app) as client:
        login_response = client.post(
            "/api/v1/identity/login",
            data={"username": "operator@example.com", "password": "mbg12345"},
        )
        access_token = login_response.json()["data"]["access_token"]
        tenant_id = client.get("/api/v1/tenants/").json()["data"][0]["id"]
        accounts = client.get("/api/v1/accounts").json()["data"]
        account_by_code = {a["code"]: a for a in accounts}
        needed = [
            ("110000", "Kas dan Bank", "ASSET", "DEBIT"),
            ("130000", "Persediaan Bahan", "ASSET", "DEBIT"),
            ("210000", "Hutang Supplier", "LIABILITY", "CREDIT"),
            ("240000", "Barang Diterima Belum Ditagih", "LIABILITY", "CREDIT"),
            ("510000", "Biaya Bahan", "COST_OF_SERVICE", "DEBIT"),
        ]
        for code, name, category, normal_balance in needed:
            if code not in account_by_code:
                resp = client.post(
                    "/api/v1/accounts",
                    headers={"Authorization": f"Bearer {access_token}"},
                    json={
                        "tenant_id": tenant_id,
                        "code": code,
                        "name": name,
                        "category": category,
                        "normal_balance": normal_balance,
                    },
                )
                assert resp.status_code == 201
        accounts = client.get("/api/v1/accounts").json()["data"]
        account_by_code = {a["code"]: a for a in accounts}
        material_expense_account_id = account_by_code["510000"]["id"]
        cash_bank_account_id = account_by_code["110000"]["id"]

        budget_resp = client.post(
            "/api/v1/budgets",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "tenant_id": tenant_id,
                "name": "Budget Payment Test",
                "date_start": "2026-07-01",
                "date_end": "2026-07-31",
                "version_number": 1,
                "notes": "Budget payment flow",
                "lines": [
                    {
                        "category_name": "BAHAN_BAKU",
                        "account_id": material_expense_account_id,
                        "planned_amount": 100000000,
                        "control_mode": "WARNING",
                        "tolerance_percentage": 0,
                    }
                ],
            },
        )
        assert budget_resp.status_code == 201
        budget_id = budget_resp.json()["data"]["budget"]["id"]
        client.post(f"/api/v1/budgets/{budget_id}/submit", headers={"Authorization": f"Bearer {access_token}"})
        client.post(f"/api/v1/budgets/{budget_id}/approve", headers={"Authorization": f"Bearer {access_token}"})

        sppg_id = client.get("/api/v1/sppg/").json()["data"][0]["id"]
        recipe_id = client.get("/api/v1/recipes/").json()["data"][0]["id"]
        warehouse_id = client.get("/api/v1/inventory/warehouses/").json()["data"][0]["id"]
        probe_meal_plan = client.post(
            "/api/v1/meal-plans/",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "tenant_id": tenant_id,
                "sppg_id": sppg_id,
                "recipe_id": recipe_id,
                "plan_date": "2026-07-27",
                "meal_type": "LUNCH",
                "status": "DRAFT",
                "planned_portions": 100,
                "budget_cost_per_portion": 15000,
                "notes": "Payment probe",
            },
        )
        probe_meal_plan_id = probe_meal_plan.json()["data"]["id"]
        requirement_resp = client.post(
            f"/api/v1/meal-plans/{probe_meal_plan_id}/calculate-requirements",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        requirement_line = requirement_resp.json()["data"][0]
        component_product_id = requirement_line["component_product_id"]
        gross_quantity_for_100 = float(requirement_line["gross_quantity"])
        balances = client.get("/api/v1/inventory/balances/").json()["data"]
        available_stock = sum(
            balance["quantity_available"]
            for balance in balances
            if balance["product_id"] == component_product_id and balance["sppg_id"] == sppg_id
        )
        planned_portions = int(((available_stock + gross_quantity_for_100) / gross_quantity_for_100) * 100) + 100
        meal_plan = client.post(
            "/api/v1/meal-plans/",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "tenant_id": tenant_id,
                "sppg_id": sppg_id,
                "recipe_id": recipe_id,
                "plan_date": "2026-07-28",
                "meal_type": "LUNCH",
                "status": "DRAFT",
                "planned_portions": planned_portions,
                "budget_cost_per_portion": 15000,
                "notes": "Payment flow test",
            },
        )
        meal_plan_id = meal_plan.json()["data"]["id"]
        pr_resp = client.post(
            f"/api/v1/procurement/purchase-requests/from-meal-plan/{meal_plan_id}",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        purchase_request_id = pr_resp.json()["data"]["purchase_request"]["id"]
        gr_resp = client.post(
            f"/api/v1/procurement/purchase-requests/goods-receipts/from-purchase-request/{purchase_request_id}",
            headers={"Authorization": f"Bearer {access_token}"},
            json={"warehouse_id": warehouse_id, "receipt_date": "2026-07-19", "notes": "Payment GR"},
        )
        goods_receipt_id = gr_resp.json()["data"]["goods_receipt"]["id"]
        inv_resp = client.post(
            f"/api/v1/procurement/purchase-requests/supplier-invoices/from-goods-receipt/{goods_receipt_id}",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "invoice_date": "2026-07-19",
                "due_date": "2026-07-26",
                "budget_account_id": material_expense_account_id,
                "notes": "Payment invoice",
            },
        )
        supplier_invoice_id = inv_resp.json()["data"]["supplier_invoice"]["id"]
        je_before = len(client.get("/api/v1/journal-entries").json()["data"])
        payment_resp = client.post(
            f"/api/v1/procurement/purchase-requests/supplier-payments/from-supplier-invoice/{supplier_invoice_id}",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "payment_date": "2026-07-19",
                "bank_account_id": cash_bank_account_id,
                "notes": "Supplier payment posted",
            },
        )
        je_after = len(client.get("/api/v1/journal-entries").json()["data"])
        invoice_detail_resp = client.get(
            f"/api/v1/procurement/purchase-requests/supplier-invoices/{supplier_invoice_id}"
        )

    assert payment_resp.status_code == 201, payment_resp.json()
    assert payment_resp.json()["code"] == "SUPPLIER_PAYMENT_CREATED"
    assert je_after > je_before
    assert invoice_detail_resp.status_code == 200
    assert invoice_detail_resp.json()["data"]["supplier_invoice"]["status"] == "PAID"


def test_production_complete_creates_posted_production_journal() -> None:
    with TestClient(app) as client:
        login_response = client.post(
            "/api/v1/identity/login",
            data={"username": "operator@example.com", "password": "mbg12345"},
        )
        access_token = login_response.json()["data"]["access_token"]
        tenant_id = client.get("/api/v1/tenants/").json()["data"][0]["id"]
        accounts = client.get("/api/v1/accounts").json()["data"]
        account_codes = {a["code"] for a in accounts}
        needed = [
            ("130000", "Persediaan Bahan", "ASSET", "DEBIT"),
            ("510000", "Biaya Bahan", "COST_OF_SERVICE", "DEBIT"),
        ]
        for code, name, category, normal_balance in needed:
            if code not in account_codes:
                resp = client.post(
                    "/api/v1/accounts",
                    headers={"Authorization": f"Bearer {access_token}"},
                    json={
                        "tenant_id": tenant_id,
                        "code": code,
                        "name": name,
                        "category": category,
                        "normal_balance": normal_balance,
                    },
                )
                assert resp.status_code == 201
        sppg_id = client.get("/api/v1/sppg/").json()["data"][0]["id"]
        recipe_id = client.get("/api/v1/recipes/").json()["data"][0]["id"]
        meal_plan_response = client.post(
            "/api/v1/meal-plans/",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "tenant_id": tenant_id,
                "sppg_id": sppg_id,
                "recipe_id": recipe_id,
                "plan_date": "2026-07-27",
                "meal_type": "LUNCH",
                "status": "DRAFT",
                "planned_portions": 8,
                "budget_cost_per_portion": 15000,
                "notes": "Production journal test",
            },
        )
        meal_plan_id = meal_plan_response.json()["data"]["id"]
        client.post(f"/api/v1/meal-plans/{meal_plan_id}/submit", headers={"Authorization": f"Bearer {access_token}"})
        client.post(f"/api/v1/meal-plans/{meal_plan_id}/approve", headers={"Authorization": f"Bearer {access_token}"})
        reserve_response = client.post(f"/api/v1/meal-plans/{meal_plan_id}/reserve-materials", headers={"Authorization": f"Bearer {access_token}"})
        assert reserve_response.status_code == 200
        create_po = client.post(
            f"/api/v1/production-orders/from-meal-plan/{meal_plan_id}",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        production_order_id = create_po.json()["data"]["production_order"]["id"]
        je_before = len(client.get("/api/v1/journal-entries").json()["data"])
        complete_resp = client.post(
            f"/api/v1/production-orders/{production_order_id}/complete",
            headers={"Authorization": f"Bearer {access_token}"},
            json={"actual_portions": 8, "accepted_portions": 8, "rejected_portions": 0},
        )
        je_after = len(client.get("/api/v1/journal-entries").json()["data"])

    assert complete_resp.status_code == 200
    assert je_after > je_before


def test_budget_create_submit_approve_and_availability_works() -> None:
    with TestClient(app) as client:
        login_response = client.post(
            "/api/v1/identity/login",
            data={"username": "operator@example.com", "password": "mbg12345"},
        )
        access_token = login_response.json()["data"]["access_token"]
        tenant_id = client.get("/api/v1/tenants/").json()["data"][0]["id"]
        accounts = client.get("/api/v1/accounts").json()["data"]
        if not accounts:
            create_account = client.post(
                "/api/v1/accounts",
                headers={"Authorization": f"Bearer {access_token}"},
                json={
                    "tenant_id": tenant_id,
                    "code": "520000",
                    "name": "Biaya Operasional",
                    "category": "EXPENSE",
                    "normal_balance": "DEBIT",
                    "allow_posting": True,
                    "is_active": True,
                },
            )
            assert create_account.status_code == 201
            accounts = client.get("/api/v1/accounts").json()["data"]
        account_id = accounts[0]["id"]
        create_response = client.post(
            "/api/v1/budgets",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "tenant_id": tenant_id,
                "name": "Budget Test",
                "date_start": "2026-07-01",
                "date_end": "2026-07-31",
                "version_number": 1,
                "notes": "Budget test",
                "lines": [
                    {
                        "category_name": "OPERASIONAL",
                        "account_id": account_id,
                        "planned_amount": 1000000,
                        "control_mode": "WARNING",
                        "tolerance_percentage": 0
                    }
                ]
            },
        )
        assert create_response.status_code == 201
        budget_id = create_response.json()["data"]["budget"]["id"]
        submit_response = client.post(
            f"/api/v1/budgets/{budget_id}/submit",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert submit_response.status_code == 200
        approve_response = client.post(
            f"/api/v1/budgets/{budget_id}/approve",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert approve_response.status_code == 200
        availability_response = client.get(f"/api/v1/budgets/{budget_id}/availability")

    assert availability_response.status_code == 200
    assert availability_response.json()["code"] == "BUDGET_AVAILABILITY_FOUND"


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
