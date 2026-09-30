import ctypes
import ctypes.wintypes
import os


user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

FOCUS_OS_PID = os.getpid()

last_external_application = "Unknown"


def get_active_window():

    global last_external_application

    hwnd = user32.GetForegroundWindow()

    if not hwnd:
        return last_external_application

    process_id = ctypes.wintypes.DWORD()

    user32.GetWindowThreadProcessId(
        hwnd,
        ctypes.byref(process_id)
    )

    current_pid = process_id.value

    # Ignore Focus OS itself
    if current_pid == FOCUS_OS_PID:
        return last_external_application

    PROCESS_QUERY_LIMITED_INFORMATION = 0x1000

    process_handle = kernel32.OpenProcess(
        PROCESS_QUERY_LIMITED_INFORMATION,
        False,
        current_pid
    )

    if not process_handle:
        return last_external_application

    buffer_size = ctypes.wintypes.DWORD(1024)

    executable_path = ctypes.create_unicode_buffer(
        buffer_size.value
    )

    success = kernel32.QueryFullProcessImageNameW(
        process_handle,
        0,
        executable_path,
        ctypes.byref(buffer_size)
    )

    kernel32.CloseHandle(process_handle)

    if not success:
        return last_external_application

    application = os.path.basename(
        executable_path.value
    )

    if application.lower().endswith(".exe"):
        application = application[:-4]

    # Store the actual external application
    last_external_application = application

    return application