import os
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'  # 国内镜像
os.environ['HF_HUB_OFFLINE'] = '0'  # 允许在线下载

import uvicorn

if __name__ == "__main__":
    # 检测环境：HF Spaces 用 7860，本地用 8000
    port = int(os.environ.get("PORT", "8000"))
    
    print("=" * 50)
    print("🐱🐶 PetCare AI - 宠物护理助手")
    print("=" * 50)
    print(f"访问地址: http://localhost:{port}")
    print(f"Web界面: http://localhost:{port}/static/index.html")
    print("=" * 50)
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=False)