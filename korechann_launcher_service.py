import win32serviceutil
import win32service
import win32event
import subprocess
import os
import time

# --- Log launcher events --- #
def log_event(message):
    timestamp = time.strftime("[%Y-%m-%d %H:%M:%S]")
    with open('korechann_launcher.log', 'a', encoding='utf-8') as f:
        f.write(f"{timestamp} {message}\n")

class KorechannService(win32serviceutil.ServiceFramework):
    _svc_name_ = "KorechannService"
    _svc_display_name_ = "Korechann Background Service"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        executable_path = os.path.join(os.path.dirname(__file__), "korechann_service.exe")

        while True:
            # Check if stop is requested before starting new worker
            if win32event.WaitForSingleObject(self.hWaitStop, 0) == win32event.WAIT_OBJECT_0:
                log_event("Service stop signal received before starting new worker.")
                break

            try:
                process = subprocess.Popen(executable_path)
                log_event(f"Started korechann_service.exe with PID {process.pid}")

                while True:
                    # Check stop signal periodically
                    if win32event.WaitForSingleObject(self.hWaitStop, 1000) == win32event.WAIT_OBJECT_0:
                        log_event("Service stop signal received. Terminating worker...")
                        process.terminate()
                        process.wait()
                        break

                    # Otherwise, check if process already exited naturally
                    retcode = process.poll()
                    if retcode is not None:
                        log_event(f"korechann_service.exe exited with code {retcode}. Restarting in 10 seconds...")
                        time.sleep(10)
                        break

            except Exception as e:
                log_event(f"Error in launcher while managing korechann_service.exe: {e}")
                break


if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(KorechannService)