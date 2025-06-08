import asyncio

import asyncpg


async def main():
    conn = await asyncpg.connect(
        host="172.17.0.1",
        port=5432,
        user="postgres",
        password="S3cur3Str0ngP@ss",
        database="chocomax",
    )


asyncio.run(main())
