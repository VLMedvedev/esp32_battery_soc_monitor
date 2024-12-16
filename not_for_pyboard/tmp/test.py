import asyncio
async def bar(x):
    count = 0
    while True:
        count += 1
        print('Instance: {} count: {}'.format(x, count))
        await asyncio.sleep(1)  # Pause 1s

async def main():
    tasks = [None] * 3  # For CPython compaibility must store a reference see 2.2 Note
    for x in range(3):
        tasks[x] = asyncio.create_task(bar(x))
    await asyncio.sleep(10)

asyncio.run(main())