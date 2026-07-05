"""Integracijski testovi write endpointa (create, patch, validacija, perzistencija)."""

from app.db.models import Ticket


async def test_create_ticket(client):
    r = await client.post(
        "/tickets", json={"title": "Novi", "priority": "high", "assignee": "emilys"}
    )
    assert r.status_code == 201
    body = r.json()
    assert body["title"] == "Novi"
    assert body["priority"] == "high"
    assert isinstance(body["id"], int)


async def test_create_validation_rejects_empty_title(client):
    assert (await client.post("/tickets", json={"title": ""})).status_code == 422


async def test_patch_updates_only_sent_fields(client, sample_tickets):
    r = await client.patch("/tickets/1", json={"status": "closed"})
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "closed"
    assert body["assignee"] == "emilys"  # netaknuto


async def test_patch_not_found(client):
    assert (await client.patch("/tickets/999", json={"status": "open"})).status_code == 404


async def test_patch_without_fields_is_rejected(client, sample_tickets):
    assert (await client.patch("/tickets/1", json={})).status_code == 400


async def test_patch_survives_restart(client, sample_tickets, session_factory):
    """Promjena mora preživjeti restart - čitamo iz nove, nezavisne sesije."""
    await client.patch("/tickets/1", json={"status": "closed"})
    async with session_factory() as fresh:
        ticket = await fresh.get(Ticket, 1)
        assert ticket.status.value == "closed"
