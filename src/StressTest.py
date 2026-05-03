import asyncio
import aiohttp
import time

# Target URL for the stress test (Login endpoint)
TARGET_URL = "http://localhost:5000/login"

# Number of requests to send
# Threshold is 5 per minute, so 10 requests should trigger several 429s
REQUEST_COUNT = 10

async def send_request(session, req_id):
    """Send a single POST request to the login endpoint."""
    payload = {
        "username": "testuser",
        "password": "testpassword"
    }
    
    start_time = time.time()
    try:
        async with session.post(TARGET_URL, json=payload) as response:
            status = response.status
            resp_json = await response.json()
            latency = (time.time() - start_time) * 1000
            
            status_text = "✅ SUCCESS" if status == 200 else "🛑 RATE LIMITED" if status == 429 else f"❓ STATUS {status}"
            print(f"Request {req_id:2}: {status_text} | Latency: {latency:6.2f}ms | Message: {resp_json.get('message', 'N/A')}")
            return status
    except Exception as e:
        print(f"Request {req_id:2}: ❌ ERROR | {str(e)}")
        return None

async def main():
    print("="*60)
    print("🚀 STARTING RATE LIMIT STRESS TEST")
    print(f"Target: {TARGET_URL}")
    print(f"Sending {REQUEST_COUNT} concurrent requests...")
    print("="*60)

    async with aiohttp.ClientSession() as session:
        tasks = [send_request(session, i+1) for i in range(REQUEST_COUNT)]
        results = await asyncio.gather(*tasks)

    # Analyze results
    success_count = results.count(200) + results.count(401) # 401 is also "reached the app logic"
    limited_count = results.count(429)
    
    print("="*60)
    print("📊 TEST SUMMARY")
    print(f"Total Requests: {REQUEST_COUNT}")
    print(f"Reached Logic:  {success_count}")
    print(f"Rate Limited:   {limited_count}")
    
    if limited_count > 0:
        print("\n✅ VERIFIED: Rate limiter is working and blocking excess requests.")
    else:
        print("\n❌ FAILED: No requests were rate limited. Check backend configuration.")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(main())
