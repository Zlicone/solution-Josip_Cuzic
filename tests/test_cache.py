"""Test cachiranja /stats: rezultat se pamti, a write čisti cache."""

from app.db.models import Ticket, TicketPriority, TicketStatus


async def test_stats_cached_until_write(client, session):
    base = (await client.get("/stats")).json()["total"]

    # Direktan upis u bazu (zaobilazi API pa ne čisti cache).
    session.add(
        Ticket(
            id=500, title="direktni", status=TicketStatus.open,
            priority=TicketPriority.low,
        )
    )
    await session.commit()

    # Još uvijek se poslužuje iz cachea - stara vrijednost.
    assert (await client.get("/stats")).json()["total"] == base

    # Write kroz API čisti cache.
    await client.post("/tickets", json={"title": "preko API-ja"})

    # Sad su vidljiva oba nova ticketa.
    assert (await client.get("/stats")).json()["total"] == base + 2
