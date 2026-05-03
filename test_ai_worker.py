import asyncio
import httpx
import websockets
import json

API_URL = "http://127.0.0.1:8000/api/v1"
WS_URL = "ws://127.0.0.1:8000"

async def test_flow():
    async with httpx.AsyncClient() as client:
        # 1. Đăng nhập để lấy token
        print("1. Đang đăng nhập...")
        login_res = await client.post(f"{API_URL}/auth/login", data={
            "username": "test@example.com",
            "password": "password"
        })
        
        # Nếu chưa có user thì tự động đăng ký
        if login_res.status_code != 200:
            print("   -> Tài khoản chưa tồn tại, tự động đăng ký mới...")
            await client.post(f"{API_URL}/auth/register", json={
                "email": "test@example.com",
                "password": "password",
                "full_name": "Test User"
            })
            login_res = await client.post(f"{API_URL}/auth/login", data={
                "username": "test@example.com",
                "password": "password"
            })
            
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("   -> Lấy token thành công!")

        # 2. Tạo một tài liệu mới
        print("\n2. Đang tạo tài liệu...")
        doc_res = await client.post(f"{API_URL}/documents/", json={
            "title": "Tài liệu test AI",
            "content": "Đây là nội dung tài liệu mẫu cần AI tóm tắt."
        }, headers=headers)
        document_id = doc_res.json()["id"]
        print(f"   -> Đã tạo tài liệu ID: {document_id}")

        # 3. Kết nối WebSocket
        print("\n3. Đang mở kết nối WebSocket (chờ kết quả từ AI Worker)...")
        ws_endpoint = f"{WS_URL}/ws/chat/{document_id}?token={token}"
        
        async with websockets.connect(ws_endpoint) as websocket:
            print("   -> Đã kết nối WebSocket thành công!")
            
            # 4. Gửi Request gọi AI
            print("\n4. Gửi HTTP Request yêu cầu AI tóm tắt...")
            ai_res = await client.post(f"{API_URL}/ai/request", json={
                "document_id": document_id,
                "type": "summarize",
                "prompt": "Hãy tóm tắt tài liệu này bằng 2 câu."
            }, headers=headers)
            print(f"   -> API phản hồi ngay lập tức (không bị treo): {ai_res.json()}")
            
            # 5. Lắng nghe WebSocket
            print("\n5. Đang lắng nghe kênh WebSocket (Dự kiến chờ 3 giây Celery xử lý)...")
            while True:
                msg = await websocket.recv()
                data = json.loads(msg)
                
                # Bỏ qua các tin nhắn hệ thống hoặc chat thông thường, chỉ in kết quả AI
                if data.get("type") == "ai_result":
                    print("\n🎉 NHẬN ĐƯỢC KẾT QUẢ TỪ AI (Bắn trực tiếp qua Redis Pub/Sub) 🎉")
                    print(f"Status: {data.get('status')}")
                    print(f"Nội dung: {data.get('content')}")
                    break

if __name__ == "__main__":
    asyncio.run(test_flow())
