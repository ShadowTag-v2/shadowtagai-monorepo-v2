# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
from datetime import date, datetime


def calculate_age(birth_date_str):
  try:
    birth_date = datetime.strptime(birth_date_str, "%Y-%m-%d").date()
  except ValueError:
    raise ValueError("Invalid birth date format. Use YYYY-MM-DD.")

  today = date.today()

  if birth_date > today:
    raise ValueError("Birth date cannot be in the future.")

  if (today.month, today.day) == (birth_date.month, birth_date.day):
    print("Happy birthday!")

  age = today.year - birth_date.year

  if (today.month, today.day) < (birth_date.month, birth_date.day):
    age -= 1

  return age
