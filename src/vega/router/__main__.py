import uvicorn


def main():
    uvicorn.run("vega.router.app:app", host="0.0.0.0", port=8000)


main()
