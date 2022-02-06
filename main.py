import uvicorn


if __name__ == "__main__":
    uvicorn.run("api_v2:app", port=8080, reload=True, reload_dirs=["/home/mj/apps/OpenCentralHeating/api_v2"])
