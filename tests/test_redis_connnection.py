import asyncio

from redis import asyncio as aioredis


async def main():

    r = aioredis.Redis(host="localhost", port=6379, db=0)

    print("Redis Ping:", await r.ping())

    await r.set("foo", "bar")
    print("Test set:", await r.get("foo"))

    await r.setex("foo", 5, "bar")
    print("Before sleep:", await r.get("foo"))

    await asyncio.sleep(10)  # Corrected sleep
    print("After sleep:", await r.get("foo"))  # Should return None

    await r.aclose()  # Close connection properly


asyncio.run(main())
