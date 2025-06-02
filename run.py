from waitress import serve
from eco_community.wsgi import application

if __name__ == "__main__":
    print("🚀 正在启动 Waitress 服务器...")
    print("🌐 监听地址：http://0.0.0.0:8000")
    serve(application, host='0.0.0.0', port=8000)
