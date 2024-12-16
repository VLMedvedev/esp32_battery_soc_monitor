import asyncio
from asyncio import Event

async def waiter(event):
    print('Waiting for event')
    await event.wait()  # Pause here until event is set
    print('Waiter got event.')
    event.clear()  # Flag caller and enable re-use of the event

async def main():
    event = Event()
    task = asyncio.create_task(waiter(event))
    await asyncio.sleep(2)
    print('Setting event')
    event.set()
    await asyncio.sleep(1)
    # Caller can check if event has been cleared
    print('Event is {}'.format('set' if event.is_set() else 'clear'))

asyncio.run(main())