Add on has more features are done.

#

# Blackjack -- my version of the course: 100days of python.

#

- Make a user register.
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
  - Logout.
  - Exit.
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

- Register confirmation (10min window)
- Add data change for user account[role=user]
- Add reset password via mail/phone?
- 2FA. (choice = phone/email)
- Last login from {"date": "UTC", "location": location, "earth":{"long":"longditude, "lat":latitude"}}
  - If not recognized.
    - Give secoundairy password and email/sms confimation.
      - Lock location (yes/no)
- Check login credentials and MAC-addres. If no match: send accept message to,.

  - Check for harddrive, motherboard serial combination
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

Next projects:

- Use reg/log system.

- Add on if found something nice.

- Collect 13F's data.

  - Sort on Peter Lynch system.
  - Joal greenbalt system.
  - Warren's system.
  - Own system

- Display Down-jones data?
- Display all major futures?
- Sentiment checker?

Use redis for collection, sorting, processing data.
Use Mongo for long term

- Start looking into machine / deep learning.
  - Algorithmic trading.
  - Load balancers (If needed)
    .
