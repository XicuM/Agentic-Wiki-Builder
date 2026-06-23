import asyncio
import sys
import logging
sys.path.insert(0, ".")
from importlib.machinery import SourceFileLoader

server = SourceFileLoader("server", ".agents/mcp/research/server.py").load_module()

class MockContext:
    def info(self, msg):
        print("INFO:", msg)
    def error(self, msg):
        print("ERROR:", msg)
    async def report_progress(self, *args, **kwargs):
        pass

async def main():
    ctx = MockContext()
    
    print("Downloading Leproult 2011...")
    try:
        res1 = await server.download_paper(ctx, "e384bbd6f4574958ec1732087a2f11f03de4802a", "leproult_2011_sleep_testosterone", "physiology")
        print("Success:", res1)
    except Exception as e:
        print("Failed:", e)
        import traceback
        traceback.print_exc()

    print("\nDownloading Dote-Montero 2021...")
    try:
        res2 = await server.download_paper(ctx, "59b4869b037b4cece82000fd776c6e7d05a2f262", "dote_montero_2021_hiit_testosterone", "physiology")
        print("Success:", res2)
    except Exception as e:
        print("Failed:", e)
        import traceback
        traceback.print_exc()

asyncio.run(main())
