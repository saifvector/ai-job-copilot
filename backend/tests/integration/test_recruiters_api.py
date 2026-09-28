"""
Integration tests for Recruiter CRM & Networking Intelligence REST API (Phase 10).
Validates endpoints under:
- /api/v1/recruiters
- /api/v1/referrals
"""
import uuid
import pytest
from httpx import AsyncClient


@pytest.fixture
def mock_user_id() -> uuid.UUID:
    return uuid.UUID("a0000000-0000-0000-0000-000000000001")


@pytest.mark.asyncio
async def test_recruiter_crm_api_full_flow(client: AsyncClient, mock_user_id: uuid.UUID):
    """Test full recruiter creation, interaction logging, referral lifecycle, analytics, and deletion."""
    headers = {"X-User-Id": str(mock_user_id)}

    # 1. Create Recruiter
    recruiter_payload = {
        "name": "Rachel Zane",
        "company": "Pearson Specter",
        "title": "Principal Talent Partner",
        "email": "rachel.zane@lawfirm.com",
        "linkedinUrl": "https://linkedin.com/in/rachel-zane",
        "notes": "Key connection for in-house Legal Tech engineering roles.",
    }
    create_res = await client.post("/api/v1/recruiters", json=recruiter_payload, headers=headers)
    assert create_res.status_code == 201
    recruiter_data = create_res.json()["data"]
    recruiter_id = recruiter_data["id"]
    assert recruiter_data["name"] == "Rachel Zane"
    assert recruiter_data["company"] == "Pearson Specter"
    assert recruiter_data["title"] == "Principal Talent Partner"

    # 2. List Recruiters
    list_res = await client.get("/api/v1/recruiters", headers=headers)
    assert list_res.status_code == 200
    list_data = list_res.json()["data"]
    assert list_data["total"] >= 1
    assert any(r["id"] == recruiter_id for r in list_data["recruiters"])

    # 3. Get Recruiter Detail
    detail_res = await client.get(f"/api/v1/recruiters/{recruiter_id}", headers=headers)
    assert detail_res.status_code == 200
    detail_data = detail_res.json()["data"]
    assert detail_data["id"] == recruiter_id
    assert "interactions" in detail_data
    assert "referrals" in detail_data

    # 4. Patch Recruiter
    patch_res = await client.patch(
        f"/api/v1/recruiters/{recruiter_id}",
        json={"title": "Managing Director of Talent"},
        headers=headers,
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["data"]["title"] == "Managing Director of Talent"

    # 5. Log Interaction (Message)
    msg_payload = {
        "interactionType": "Message",
        "summary": "Reached out via LinkedIn message to inquire about senior roles.",
    }
    interact_res = await client.post(
        f"/api/v1/recruiters/{recruiter_id}/interactions",
        json=msg_payload,
        headers=headers,
    )
    assert interact_res.status_code == 201
    assert interact_res.json()["data"]["interactionType"] == "Message"

    # 6. Log Interaction (Call)
    call_payload = {
        "interactionType": "Call",
        "summary": "Completed 30-minute culture and technical alignment call.",
    }
    call_res = await client.post(
        f"/api/v1/recruiters/{recruiter_id}/interactions",
        json=call_payload,
        headers=headers,
    )
    assert call_res.status_code == 201

    # 7. Get Interaction History
    hist_res = await client.get(f"/api/v1/recruiters/{recruiter_id}/history", headers=headers)
    assert hist_res.status_code == 200
    history = hist_res.json()["data"]
    assert len(history) >= 2

    # 8. Add Referral
    ref_payload = {
        "company": "Pearson Specter",
        "role": "Principal Software Architect",
        "status": "Requested",
        "notes": "Submitted internal referral link",
    }
    ref_res = await client.post(
        f"/api/v1/recruiters/{recruiter_id}/referrals",
        json=ref_payload,
        headers=headers,
    )
    assert ref_res.status_code == 201
    ref_data = ref_res.json()["data"]
    ref_id = ref_data["id"]
    assert ref_data["status"] == "Requested"
    assert ref_data["role"] == "Principal Software Architect"

    # 9. List Referrals
    refs_list_res = await client.get("/api/v1/referrals", headers=headers)
    assert refs_list_res.status_code == 200
    refs = refs_list_res.json()["data"]
    assert any(r["id"] == ref_id for r in refs)

    # 10. Update Referral Status to Received
    patch_ref_res = await client.patch(
        f"/api/v1/referrals/{ref_id}",
        json={"status": "Received", "notes": "Referral submitted in portal"},
        headers=headers,
    )
    assert patch_ref_res.status_code == 200
    assert patch_ref_res.json()["data"]["status"] == "Received"

    # 11. Get Networking Analytics
    analytics_res = await client.get("/api/v1/recruiters/analytics", headers=headers)
    assert analytics_res.status_code == 200
    analytics = analytics_res.json()["data"]
    assert analytics["recruitersContacted"] >= 1
    assert analytics["companiesReached"] >= 1
    assert analytics["messagesSent"] >= 1
    assert analytics["responsesReceived"] >= 1
    assert analytics["referralsReceived"] >= 1

    # 12. Delete Referral
    del_ref_res = await client.delete(f"/api/v1/referrals/{ref_id}", headers=headers)
    assert del_ref_res.status_code == 200

    # 13. Delete Recruiter
    del_rec_res = await client.delete(f"/api/v1/recruiters/{recruiter_id}", headers=headers)
    assert del_rec_res.status_code == 200
