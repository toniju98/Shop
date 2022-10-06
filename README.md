# Shop


I built an E commerce shop where the payment works exclusively with MetaMask. The reason, why I built it, was, that I was part of a team which planned to bring out a shop where people can only buy with our own ERC20-Token. My foundation therefore was a almost ready e commerce shop, which you can find here: 

I didn't change very much on the style. I simplified it more. I deleted all the classic payment stuff and some other extra features. The goal was to have an absolutely basic merch shop. I won't explain the whole structure of the shop because there is already the repo for it. I will talk more detailed about how I implemented the Meta mask payment and login process. The login is similar like in OpenSea e.g. But it is a bit more complicated. Inspiration therefore was: https://www.quicknode.com/guides/web3-sdks/how-to-build-a-one-click-sign-in-using-metamask-with-phps-laravel

The process:

1. You click the login button

2. You login with metamassk

3. You give your signature to backend

4. backend gives back signature

5. ...

The payment process was simpler. Of course you can't order completely anonymous, even if you pay with crypto, so after you type in your personal informations you checkout and
pay similar like paying for an NFT on OpenSea e.g. But in this case you pay with ERC20-Tokens.


Code based on: https://github.com/justdjango/django-ecommerce/tree/master/djecommerce

.env needs to be filled by email
