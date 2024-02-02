# vibinator

This is a complementary app to my [plugmon app](https://github.com/jcostom/plugmon). I'm using plugmon to monitor the Etekcity smart plug that our washer is plugged into. This enables me to tell when the washer is done.

Ordinarily, I'd just recycle the code and use the same to keep an eye on the dryer, but there's a problem. You see, we've got an electric dryer, and nobody makes a smart plug for a 240V 30A appliance like a dryer. If we got a gas dryer, this would be easy, but I'm not dropping that kind of cash just to get this done.

So, instead of monitoring voltage, we'll look at vibration. When the dryer is running, it's vibrating.

Update - March 2022 - I'm in the process of refactoring this code to run under Docker. It's only ever going to be built as armv7 and arm64 images, as it just doesn't make sense to build as amd64 images ever.

Check out the example docker-compose file for how you should be launching this thing. Environment variables, with their default values follow:

* TZ: Your Time Zone, default is America/New_York*
* INTERVAL: your polling interval, default is 120s (internally, this is carved into 4 slices)
* SENSOR_PIN: which GPIO pin you're using for the sensor, default is pin 14
* AVG_THRESHOLD: above this value, you declare the dryer as being "on", used to prevent false positives if you're in a "noisy" environment. Default is 0.2
* LOGALL: logs more data during monitoring - useful for debugging monitor intervals and threshold levels, default is False. Set to True if you want more logs. Don't leave this on forever if you use a Pi with a flash card, as flash cards have a finite number of write ops.

You should map the /dev/gpiomem device into the container as well. I believe you can also do a volume mount of /sys:/sys, but I wouldn't advise that for security reasons. Similarly, you could invoke the container as priviliged, but again, I wouldn't do that for security reasons.

As of v2.5 of the container, multiple notification types are supported. Yes, you can do multiple notification types simultaneously too!

## Setting up Telegram

There are a ton of tutorials out there to teach you how to create a Telegram Bot. Follow one and come back with your Chat ID and Token values. Set the USE_TELEGRAM variable to 1, and set the TELEGRAM_CHATID and TELEGRAM_TOKEN variables and you're set. The old variables of CHATID and MYTOKEN still work as well, but be a good citizen and update to the new variable names please.

## Setting up Pushover

1. Sign up for an account at the [Pushover](https://pushover.net/) website and install the app on your device(s). Make note of your User Key in the app. It's easy to find it in the settings.

2. Follow their [API Docs](https://pushover.net/api) to create yourself an app you intend to use.

3. Pass the variables USE_PUSHOVER (set this to 1!), PUSHOVER_APP_TOKEN, and PUSHOVER_USER_KEY into the container and magic will happen.

## Setting up Pushbullet

1. Sign up for an account at the Pushbullet website.

2. In the Settings > Account page, setup an API key.

3. Pass the variables USE_PUSHBULLET and PUSHBULLET_APIKEY to the container and wait for magic.

## Setting up Alexa Notifications

1. Add the "Notify Me" skill to your Alexa account

2. Note the accessCode value from the email you got from the skill.

3. Pass the variables USE_ALEXA and ALEXA_ACCESSCODE to the container, and wait for the glowing ring on your Echo!