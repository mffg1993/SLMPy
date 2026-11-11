"""Launch the local SLMPy browser interface."""
import argparse
import webbrowser


def main():
    parser = argparse.ArgumentParser(description="Start the SLMPy local browser GUI")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args()
    if not (1024 <= args.port <= 65535):
        parser.error("Port must be between 1024 and 65535")
    if not args.no_browser:
        import threading
        threading.Timer(1.2, lambda: webbrowser.open("http://127.0.0.1:%d" % args.port)).start()
    import uvicorn
    uvicorn.run("slmpy_browser.server:app", host="127.0.0.1", port=args.port, reload=False, workers=1)


if __name__ == "__main__":
    main()
