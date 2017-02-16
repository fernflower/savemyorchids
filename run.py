import daemon
import fetch_data

with daemon.DaemonContext():
    fetch_data.main()
