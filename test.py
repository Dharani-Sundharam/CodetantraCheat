from email_validator import validate_email, EmailNotValidError

email = "0000.cd@gmail.com"

try:
    email_info = validate_email(email)
    valid_email = email_info.normalized
    print(f"{valid_email} is valid")
except EmailNotValidError as e:
    print(f"{email} is not valid: {str(e)}")
