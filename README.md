# vibinator

This is a complementary app to my [plugmon app](https://github.com/jcostom/plugmon). I'm using plugmon to monitor the Etekcity smart plug that our washer is plugged into. This enables me to tell when the washer is done.

Ordinarily, I'd just recycle the code and use the same to keep an eye on the dryer, but there's a problem. You see, we've got an electric dryer, and nobody makes a smart plug for a 240V 30A appliance like a dryer. If we got a gas dryer, this would be easy, but I'm not dropping that kind of cash just to get this done.

So, instead of monitoring voltage, we'll look at vibration. When the dryer is running, it's vibrating. So now, I sit, waiting for my movement sensors to come from China. More updates when those get here...

Update - March 2022 - I'm in the process of refactoring this code to run under Docker. It's only ever going to be built as armv7 and arm64 images, as it just doesn't make sense to build as amd64 images ever.

Check out the example docker-compose file for how you should be launching this thing. Environment variables, with their default values follow:

* IFTTTKEY: your webhook key value from IFTTT
* IFTTTWEBHOOK: your webhook name from IFTTT
* TZ: Your Time Zone, default is America/New_York*
* INTERVAL: your polling interval, default is 120s (internally, this is carved into 4 slices)
* SENSOR_PIN: which GPIO pin you're using for the sensor, default is pin 14
* AVG_THRESHOLD: above this value, you declare the dryer as being "on", used to prevent false positives if you're in a "noisy" environment. Default is 0.2

Only IFTTTKEY and IFTTTWEBHOOK are required, the rest have sane defaults.

You should map the /dev/gpiomem device into the container as well. I believe you can also do a volume mount of /sys:/sys, but I wouldn't advise that for security reasons. Similarly, you could invoke the container as priviliged, but again, I wouldn't do that for security reasons.
