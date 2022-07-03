import schedule
import time

# Functions setup
def check_for_emails():
	print("Checking for emails")

def dispatch_to_site():
	print("dispatching to site")

# Task scheduling
# After every 10mins geeks() is called.
schedule.every(1).minutes.do(check_for_emails)
schedule.every(2).minutes.do(dispatch_to_site)

# After every hour geeks() is called.
schedule.every().hour.do(dispatch_to_site)

# Loop so that the scheduling task
# keeps on running all time.
while True:

	# Checks whether a scheduled task
	# is pending to run or not
	schedule.run_pending()
	time.sleep(1)
