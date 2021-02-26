# currys-pc-order-bot
To hit back against the woes I encountered trying to get a GPU in this "trying times".
<br>
> Use this software at YOUR OWN RISK. This software offers no guarantee. I do not assume any risk you might incure from using this software.

### Getting Started

To use the bot, confirm that you have chrome, python-pip. It would be ideal to install virtualenv or similar too.

Install the python dependencies using:
```pip install -r requirements.txt```

<br/>
Next, you will need to get chrome drivers. Confirm your version of Chrome or Chromium (Other chromium based browsers should work too) using the command or gui method.

For Chrome
```google-chrome --version```

You can then get the Chrome driver corresponding to your chrome version and Operating System from here: [https://chromedriver.chromium.org]()

> The Chrome driver should be named ```chromedriver``` and placed in the project root folder.

<br/>
You're about ready to get your item from Curry's PC.

<br/>

Rename the file ```secrets-template.yaml``` to ```secrets.yaml``` and fill in your personal details. 

> Ensure that you have set up a Currys account and address info before use

### To run the bot:
```python3 buy-bot3.py <currys_pc_product_link>```

Replacing ```<currys_pc_product_link>``` with the link to the product you wish to buy.

Good luck!

<br/>

Notice:
- Items with add-on packages before placing in basket will cause program to fail. Fix this by changing the key ```checkout_addon``` in ```conf.yaml``` to ```True```


