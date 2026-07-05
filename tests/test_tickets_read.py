"""Integracijski testovi read endpointa (preko HTTP klijenta i test baze)."""


async def test_list_returns_all(client, sample_tickets):
    r = await client.get("/tickets")
    assert r.status_code == 200
    assert r.json()["total"] == 3


async def test_filter_by_status(client, sample_tickets):
    r = await client.get("/tickets", params={"status": "open"})
    assert r.json()["total"] == 2


async def test_filter_by_priority(client, sample_tickets):
    r = await client.get("/tickets", params={"priority": "high"})
    assert r.json()["total"] == 1


async def test_pagination(client, sample_tickets):
    r = await client.get("/tickets", params={"limit": 1, "offset": 1})
    body = r.json()
    assert len(body["items"]) == 1
    assert body["items"][0]["id"] == 2


async def test_search_is_case_insensitive(client, sample_tickets):
    r = await client.get("/tickets/search", params={"q": "fix"})
    assert r.json()["total"] == 2


async def test_detail_includes_source_payload(client, sample_tickets):
    r = await client.get("/tickets/1")
    assert r.status_code == 200
    assert r.json()["source_payload"] is not None


async def test_detail_not_found(client, sample_tickets):
    assert (await client.get("/tickets/999")).status_code == 404


async def test_description_truncated_to_100(client, sample_tickets):
    r = await client.get("/tickets", params={"priority": "low"})
    description = r.json()["items"][0]["description"]
    assert len(description) == 100
