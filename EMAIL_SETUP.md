# Email Notifications — Setup Guide

Phase-1 email notifications are wired into the yacht booking system. Four
events trigger an email:

| Event | Recipient | Template |
|---|---|---|
| New booking submitted | Customer | `templates/emails/booking_confirmation.html` |
| New booking submitted | Admin (`ADMIN_EMAIL`) | `templates/emails/admin_new_booking.html` |
| Booking approved / rejected | Customer | `templates/emails/booking_status.html` |
| Booking cancelled (by customer or admin) | Customer **and** Admin | `templates/emails/booking_cancellation.html` |

If `MAIL_USERNAME` is empty the email helpers silently skip sending, so the
system is safe to run locally without SMTP configured.

---

## 1. Generate a Gmail App Password

Use the shared Tomorrow World Gmail account (e.g.
`bookings@tomorrowworld.com` if you have a Google Workspace domain, or a
dedicated `tomorrow.world.bookings@gmail.com` mailbox).

1. Sign in to the Google account at <https://myaccount.google.com>.
2. Open **Security** → turn on **2-Step Verification** (required before
   App Passwords are available).
3. Go to <https://myaccount.google.com/apppasswords>.
4. Choose **App = Mail**, **Device = Other (custom name)** and type
   `TW Yacht Booking`.
5. Click **Generate**. Google will show a 16-character password like
   `abcd efgh ijkl mnop`. Copy it (remove spaces).

> **Important:** You will NOT be able to see this password again. Store it
> in a password manager or paste it directly into your environment variables.

### Gmail sending limit
- Free Gmail account: **~500 emails/day**.
- Google Workspace account: **~2,000 emails/day**.

If you expect to exceed these numbers, switch to SendGrid or AWS SES.

---

## 2. Configure environment variables

Copy `.env.example` → `.env` (for local runs) and fill in:

```env
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=bookings@tomorrowworld.com
MAIL_PASSWORD=abcdefghijklmnop        # 16-char App Password, no spaces
MAIL_DEFAULT_SENDER=Tomorrow World <bookings@tomorrowworld.com>
ADMIN_EMAIL=admin@tomorrowworld.com   # where new-booking alerts are sent
```

### On Render
In your Render dashboard → the web service → **Environment** → add the same
variables. Redeploy after saving.

### On local development
Either export the variables in your shell:

```bash
export MAIL_USERNAME="bookings@tomorrowworld.com"
export MAIL_PASSWORD="abcdefghijklmnop"
export ADMIN_EMAIL="admin@tomorrowworld.com"
python app.py
```

Or load them from `.env` with `python-dotenv` (not currently required).

---

## 3. Quick test

After starting the app:

1. Submit a booking as a customer at `http://localhost:8080/booking/customer`.
2. You should receive:
   - A **confirmation email** at the customer email you entered.
   - A **"New Booking Pending Review"** email at `ADMIN_EMAIL`.
3. Log in as admin and approve / reject / cancel — each action will fire the
   corresponding email.

If emails do not arrive, check the server log for lines starting with
`Email send failed` or `Admin notification failed`.

---

## 4. Common problems

| Symptom | Likely cause | Fix |
|---|---|---|
| `SMTPAuthenticationError: Username and Password not accepted` | Using your normal Google password | You must use an **App Password** (see Step 1) |
| `SMTPAuthenticationError: Application-specific password required` | 2-Step Verification is off | Turn on 2-Step Verification first |
| Emails go to spam | `MAIL_DEFAULT_SENDER` does not match `MAIL_USERNAME` | Use the same address, ideally with a display name like `Tomorrow World <...>` |
| Customer gets confirmation but admin does not | `ADMIN_EMAIL` not set | Add `ADMIN_EMAIL` env var and redeploy |
| "Email send failed" in logs but no traceback | Gmail rate limit or network block | Wait a few minutes; consider moving to SendGrid for production |

---

## 5. When to upgrade

Gmail SMTP is fine for the first few months while volume is low. Move to a
transactional provider when any of the following is true:

- You are sending more than 300 customer-facing emails per day.
- You need delivery reports, bounce handling, or template analytics.
- You want the "From" address to be a proper domain address
  (e.g. `bookings@tomorrowworld.com`) without Gmail's quirks.

Recommended path:

1. **SendGrid** — 100 free emails/day, good reporting. Just change
   `MAIL_SERVER=smtp.sendgrid.net`, `MAIL_USERNAME=apikey`,
   `MAIL_PASSWORD=<your SendGrid API key>`.
2. **AWS SES** — cheapest at scale (~$0.10 per 1,000 emails). Requires
   domain verification and moving out of "sandbox" mode.
