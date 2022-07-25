# Rivadm client

HTML client for Rivadm dialogue manager 


## Usage
You have to specify which bot you want to interact with by URL parameter ``bot=[bot name]`` or by attaching bot name as path to address like:

    http://127.0.0.1:5000/[bot_name]/

You can change endpoint's address of Rivadm dialogue manager by URL paramater ``e=[Rivadm endpoint]``.

The default endpoint's value is ``http://localhost:5000/``.

Example: 

    http://localhost:63342/rivadm-client/index.html?e=http://localhost:5000/&bot=demo_tel
    