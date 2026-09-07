from vega.router.wakeword_detector import WakeWordDetector

if __name__ == "__main__":
    detector = WakeWordDetector()
    print(detector.search_wakewords("ало клод ало вега"))
