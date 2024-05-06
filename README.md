# Dynamic dnsmasq container

This container expects all configuration files to be mounted in via docker volumes.

See the [example directory](/examples/docker-compose/) for a recommended configuration file structure.

## Dynamic hosts

dnsmasq doesn't have a native facility to automatically update the configuration on changes.  It requires a SIGHUP.  However, it does have a facility that allows it to dynamically add hosts through the `--dhcp-hostsdir` option.  The behavior may not be precisely what you expect.  Here is the 

> --dhcp-hostsdir=<path>
    This is equivalent to --dhcp-hostsfile, except for the following. The path MUST be a directory, and not an individual file. Changed or new files within the directory are read automatically, without the need to send SIGHUP. If a file is deleted or changed after it has been read by dnsmasq, then the host record it contained will remain until dnsmasq receives a SIGHUP, or is restarted; ie host records are only added dynamically. The order in which the files in a directory are read is not defined.

## Manually reloading the container configuration

Docker supports sending signals to the main process in a container.  From the [docker documentation](https://docs.docker.com/reference/cli/docker/container/kill/#send-a-custom-signal--to-a-container), there are several ways to send a SIGHUP to dnsmasq.

```bash
# The following commands are all equivalent
docker kill --signal=SIGHUP dnsmasq
docker kill --signal=HUP dnsmasq
docker kill --signal=1 dnsmasq
```

