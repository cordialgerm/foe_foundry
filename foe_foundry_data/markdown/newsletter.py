def create_newsletter(cta: str = "Subscribe to the Foe Foundry Newsletter") -> str:
    """Generates HTML for a newsletter subscription form."""

    return f"""<div class="email-subscribe bg-object parchment p-3 m-3">
        <div class="m-3 p-3">
            <h2>{cta}</h2>
            <p>Get the latest updates on new features, monsters, powers, and GM tips - all for free!</p>
            <form action="https://buttondown.com/api/emails/embed-subscribe/cordialgerm" method="post" target="popupwindow"
                onsubmit="window.open('https://buttondown.com/cordialgerm', 'popupwindow')" class="embeddable-buttondown-form">
                <div class="form-group row">
                <label for="bd-email" class="col-sm-3 col-form-label">Enter your email</label>
                <div class="col-sm-6">
                    <input type="email" name="email" id="bd-email" class="form-control" />
                </div>
                <div class="col-sm-3">
                    <button type="submit" class="btn btn-primary mb-2">Subscribe</button>
                </div>
                </div>
            </form>
        </div>
        </div>"""
