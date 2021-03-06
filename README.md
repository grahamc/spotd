# SpotD

Stop before your server does. A generic tool for detecting your AWS
EC2 spot instance will be terminated.

## Usage

```
 $ python spotd.py
```

and then it won't exit until AWS indicates your spot price bid has run
out.

Note: When it _does_ exit, it will output a log line like:

```
Received notice to shut-down at <datetime>
```

## Why

AWS recommends you take heed of their shutdown warning and begin
cleaning up after yourself. You may start gracefully shutting down
your services.

## Example systemd Units


```
[Unit]
After=network.target
Description=Trigger shutdown when AWS indicates our spot bid is too low.

[Service]
ExecStart=/opt/spotd.py
```

A unit for spotd

```
[Unit]
After=network.target
BindsTo=spotd.service
Description=Test spotd

[Service]
ExecStart=/opt/spotd-test-start

```

and the test service is:

```bash
#!/bin/bash -e
while true; do
  date
  sleep 15
done
```

Use BindsTo to trigger a shut-down of your service when spotd exits.


systemd output:

```
Mar 20 14:55:00 myserver spotd[5550]: WARNING:spotd:Received notice to shut-down at 2016-03-20T14:56:57Z
Mar 20 14:55:00 myserver systemd[1]: spotd.service: Main process exited, code=exited, status=1/FAILURE
Mar 20 14:55:00 myserver systemd[1]: spotd.service: Unit entered failed state.
Mar 20 14:55:00 myserver audit[1]: SERVICE_STOP pid=1 uid=0 auid=4294967295 ses=4294967295 msg='unit=spotd comm="systemd" exe="/nix/store/90rnxknf63kj3z9krqqdsld3k4451asb-systemd-229/lib/systemd/systemd" hostname=? addr=? terminal=? res=failed'
Mar 20 14:55:00 myserver systemd[1]: spotd.service: Failed with result 'exit-code'.
Mar 20 14:55:00 myserver systemd[1]: Stopping Test spotd...
Mar 20 14:55:00 myserver kernel: audit: type=1131 audit(1458485700.570:99): pid=1 uid=0 auid=4294967295 ses=4294967295 msg='unit=spotd comm="systemd" exe="/nix/store/90rnxknf63kj3z9krqqdsld3k4451asb-systemd-229/lib/systemd/systemd" hostname=? addr=? terminal=? res=failed'
Mar 20 14:55:00 myserver systemd[1]: Stopped Test spotd.
Mar 20 14:55:00 myserver audit[1]: SERVICE_STOP pid=1 uid=0 auid=4294967295 ses=4294967295 msg='unit=spotd-test comm="systemd" exe="/nix/store/90rnxknf63kj3z9krqqdsld3k4451asb-systemd-229/lib/systemd/systemd" hostname=? addr=? terminal=? res=success'
Mar 20 14:55:00 myserver kernel: audit: type=1131 audit(1458485700.571:100): pid=1 uid=0 auid=4294967295 ses=4294967295 msg='unit=spotd-test comm="systemd" exe="/nix/store/90rnxknf63kj3z9krqqdsld3k4451asb-systemd-229/lib/systemd/systemd" hostname=? addr=? terminal=? res=success'
```

## Notes

### Dependencies

Python 2.7, no other python packages.

I _despise_ Python 2.7, and hate to make a new project use it. However,
its availability on my target instances is undeniable.

### Can I use it on non-spot instances? Outside of AWS?

Yes. Any and all errors are considered to be proof the server is _not_
about to be terminated, so it should be OK to make a standard machine
image using spotd and deploy it to AWS on-demand instances, or even
non-AWS computers.

### Implementation Notes

1. Poll http://169.254.169.254/latest/meta-data/spot/termination-time
   and `exit 1` when that URL returns a date.
2. Loops, checking every 5 seconds (per [documentation][5-second-rule])
3. Any HTTP body which contains a valid-looking date (YYYY-MM-DDTHH:MM:SSZ)
   will be used as evidence we're about to shut down.
4. Any network errors (like socket timeouts) are ignored.


[5-second-rule]: http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/spot-interruptions.html#spot-instance-termination-notices
