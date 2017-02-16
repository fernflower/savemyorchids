import daemon
import fetch_data

pidfile = daemon.pidlockfile.PIDLockFile("/var/run/orchids.pid")
with daemon.DaemonContext(pidfile=pidfile):
    fetch_data.main()
