#!/usr/bin/python3

import asyncio
import websockets
import json

async def getPoolEnergyLogs():
    """
    Get pool.energy logs from websocket and print them to console.
    """
    async with websockets.connect("wss://pool.energy/ws/log/") as websocket:
        await websocket.send(json.dumps(['partials', 'payments']))
        while True:
            log_recv = await websocket.recv()
            log_json = json.loads(log_recv)
            for log_msg in log_json['data']:
                log_temp = log_msg['message']
                del log_msg['message']
                log_out = log_temp.replace("'", "").replace("\"", "")
                log_msg['message'] = log_out
                print(log_msg)

if __name__ in "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(getPoolEnergyLogs())
    loop.close()
