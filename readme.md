Add on has more features are done.

#

# Blackjack -- my version of the course: 100days of python.

#

- Make a user register. (done)
- Login for registerd users.
- Login menu:

  print(f"welcome back {user}")
  print("last login from,.......")

  - Go to Blackjack.
  - Account details.
    - Change details [role=user]
    - Change password.
    - Change 2FA.
  - View login locations.
    - Lock locations.
  - Logout. (done)
  - Exit. (done)
  - Delete account.

- Admin:

  - Only needs to input name for login. (Im lazy)

    - Admin menu:
      - See users.
        - Get user details.
        - Change user data[role=admin].
        - Delete user.
    - Reset password.
    - View login locations
      - Lock locations
    - Logout. (done)
    - Exit. (done)

#

- Register email confirmation (done)
- Add data change for user account[role=user]
- Add reset password via mail/phone?
- 2FA. (choice = phone/email)
- Last login from {"date": "UTC", "location": location, "earth":{"long":"longditude, "lat":latitude"}}
  - If not recognized.
    - Give secoundairy password and email/sms confimation.
      - Lock location (yes/no)
- Check login credentials and MAC-addres. If no match: send accept message to,.

  - Check for harddrive(s), motherboard serial, MAC-addres(s) combination (done)
  - If already used combination: Skip.

- Lock out Admin account if wrong input or MAC-addres or serial combination(send email/sms to,.)

- Lock out User account if wrong input \*3 (send email/sms)

  - If user credentials and MAC-address do not match:
    - Proseed login but show (\*) for every usefull data.
    - Remove reset password.
    - Remove email / phone data.

#

- Main game:
  - Blackjack.
  - View top-3 highscore.

#

LEARNING POITNS :

#

- Get better at coding.
- Work on functions.
- Use of folder system
- Refine coding style,. . . .... . . .. . . . .......
- Refine boiler plate
- CRUD-operations.
- Auth

#

Next BIG-project:

- Use reg/log system.

- Add on if found something nice ;-D

- Collect 13F's.

  - Only use top 20 / 30 companies

    - Check corresponding Balance sheet data
    - Check for Names (authoritarian names? No bullshit names like: 23435, 324235 stuff like that)

  - Use due diligence. (Sort out balance sheet data)
    - Sort on Peter Lynch system. (adjusted)
    - Sort on Joal greenbalt system. (adjusted)
    - Sort on Warren's system.
    - Sort on my own system.
      - Check for overlapping data.
        - If overlapping found?!
          - Scrape for shareholders.(partculier / institutional)
          - Insider trade's
          - Scrape for news items.
            - Sentiment checker.
          - Scrape for economic events data and dates.
            - Check historical data and trendlines. (5-10year max? (That's a lot of data!))
            - Check if companie x,y,z is just started to make money in the last year or something. (Use eval of Due diligence)

- Display all major futures?
- Display all major FOREX-pairs
- Display VIX vs Bonds.
- Display Materials goods

  - Show notification if intrest is found with PDF-summary. (open / ignore)

Use redis for collection, sorting, processing data.
Use MongoDB for long term

- Start looking into machine / deep learning.
  - Algorithmic trading.
  - Load balancers (If needed)
