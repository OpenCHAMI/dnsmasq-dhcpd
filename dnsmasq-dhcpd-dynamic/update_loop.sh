while true
do
    smd.py
    #TODO we should probably only kill on smd.py finding a change
    kill -1 $(pgrep dnsmasq)
    sleep 10
done
