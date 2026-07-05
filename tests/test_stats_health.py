"""Testovi za /stats i /health endpointe."""


async def test_stats_aggregates(client, sample_tickets):
    r = await client.get("/stats")
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 3
    assert body["by_status"] == {"open": 2, "closed": 1}
    assert body["by_priority"] == {"medium": 1, "high": 1, "low": 1}
    # emilys i noahh imaju po jedan ticket
    assignees = {row["assignee"]: row["count"] for row in body["top_assignees"]}
    assert assignees == {"emilys": 1, "noahh": 1}


async def test_health_ok(client):
    r = await client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}
