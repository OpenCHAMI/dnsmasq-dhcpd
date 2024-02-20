while true
do
    smd.py
    rc=$?
    if [$rc -e 1]; then
        kill -1 $(pgrep dnsmasq)
    fi
    sleep 10
done
