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

## Example SystemD Units


```
[Unit]
After=network-interfaces.target
Description=Trigger shutdown when AWS indicates our spot bid is too low.

[Service]
ExecStart=/opt/spotd.py
```

    A unit for spotd

```
[Unit]
BindsTo=spotd.service

...
```

    Use BindsTo to trigger a shut-down of your service when spotd exits.

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
