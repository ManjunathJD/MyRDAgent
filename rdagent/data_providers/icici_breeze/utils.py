from datetime import datetime

def format_date(date_obj):
  """Formats a date object to 'YYYY-MM-DD HH:MM:SS'."""
  return date_obj.strftime('%Y-%m-%d %H:%M:%S')