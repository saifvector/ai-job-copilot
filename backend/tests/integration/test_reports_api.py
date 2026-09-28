"""
Integration tests for Reporting & Export Center REST API (Phase 9).
Validates endpoints under /api/v1/reports:
- POST /api/v1/reports/generate
- GET /api/v1/reports
- GET /api/v1/reports/{id}
- GET /api/v1/reports/{id}/download
- DELETE /api/v1/reports/{id}
"""
import uuid
import pytest
from httpx import AsyncClient


@pytest.fixture
def mock_user_id() -> uuid.UUID:
    return uuid.UUID("a0000000-0000-0000-0000-000000000001")


@pytest.mark.asyncio
async def test_reports_api_full_flow(client: AsyncClient, mock_user_id):
    """Test full report generation, listing, downloading, and deletion via REST API."""
    headers = {"X-User-Id": str(mock_user_id)}

    # 1. Generate Application Report as PDF
    pdf_payload = {
        "report_type": "APPLICATION_REPORT",
        "format": "PDF",
        "title": "Application Performance Q3",
        "date_range_days": 30,
    }
    res_pdf = await client.post("/api/v1/reports/generate", json=pdf_payload, headers=headers)
    assert res_pdf.status_code == 201
    data_pdf = res_pdf.json()
    assert data_pdf["success"] is True
    report_pdf_id = data_pdf["data"]["id"]
    assert data_pdf["data"]["format"] == "PDF"
    assert data_pdf["data"]["reportType"] == "APPLICATION_REPORT"
    assert data_pdf["data"]["fileSize"] > 0
    assert data_pdf["data"]["downloadUrl"] == f"/api/v1/reports/{report_pdf_id}/download"

    # 2. Generate Match Report as CSV
    csv_payload = {
        "report_type": "MATCH_REPORT",
        "format": "CSV",
    }
    res_csv = await client.post("/api/v1/reports/generate", json=csv_payload, headers=headers)
    assert res_csv.status_code == 201
    data_csv = res_csv.json()
    assert data_csv["data"]["format"] == "CSV"

    # 3. Generate Skill Report as XLSX
    xlsx_payload = {
        "report_type": "SKILL_REPORT",
        "format": "XLSX",
    }
    res_xlsx = await client.post("/api/v1/reports/generate", json=xlsx_payload, headers=headers)
    assert res_xlsx.status_code == 201
    data_xlsx = res_xlsx.json()
    assert data_xlsx["data"]["format"] == "XLSX"

    # 4. Generate Career Report as JSON
    json_payload = {
        "report_type": "CAREER_REPORT",
        "format": "JSON",
    }
    res_json = await client.post("/api/v1/reports/generate", json=json_payload, headers=headers)
    assert res_json.status_code == 201
    data_json = res_json.json()
    assert data_json["data"]["format"] == "JSON"

    # 5. GET /api/v1/reports - List Reports and aggregate stats
    list_res = await client.get("/api/v1/reports", headers=headers)
    assert list_res.status_code == 200
    list_data = list_res.json()["data"]
    assert len(list_data["reports"]) >= 4
    assert list_data["stats"]["totalReports"] >= 4
    assert list_data["stats"]["storageUsedBytes"] > 0

    # 6. GET /api/v1/reports/{id} - Get by ID
    get_res = await client.get(f"/api/v1/reports/{report_pdf_id}", headers=headers)
    assert get_res.status_code == 200
    assert get_res.json()["data"]["id"] == report_pdf_id

    # 7. GET /api/v1/reports/{id}/download - Download file
    dl_res = await client.get(f"/api/v1/reports/{report_pdf_id}/download", headers=headers)
    assert dl_res.status_code == 200
    assert "attachment" in dl_res.headers.get("content-disposition", "")
    assert len(dl_res.content) > 1000

    # Verify download count incremented
    get_res2 = await client.get(f"/api/v1/reports/{report_pdf_id}", headers=headers)
    assert get_res2.json()["data"]["downloadCount"] >= 1

    # 8. DELETE /api/v1/reports/{id} - Delete report
    del_res = await client.delete(f"/api/v1/reports/{report_pdf_id}", headers=headers)
    assert del_res.status_code == 200
    assert del_res.json()["data"] is True

    # 9. Verify 404 after deletion
    get_res3 = await client.get(f"/api/v1/reports/{report_pdf_id}", headers=headers)
    assert get_res3.status_code == 404
