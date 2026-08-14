import email
from email.utils import parsedate_to_datetime
import imaplib
import os
import re
from typing import List
from urllib.parse import parse_qs, urlparse
from bs4 import BeautifulSoup

from dotenv import load_dotenv
from models import ArticleRaw

load_dotenv()

IMAP_SERVER = os.getenv("IMAP_SERVER")
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
PASSWORD = os.getenv("APP_PASSWORD")


def connect_to_imap() -> imaplib.IMAP4_SSL:
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(EMAIL_ADDRESS, PASSWORD)
    return mail


def clean_google_url(raw_url: str) -> str:
    parsed = urlparse(raw_url)
    if "google.com" in parsed.netloc and "/url" in parsed.path:
        query_params = parse_qs(parsed.query)
        if "url" in query_params:
            return query_params["url"][0]
        if "q" in query_params:
            return query_params["q"][0]
    return raw_url

def parse_email_for_content(raw_email: bytes, email_date: str) -> list[ArticleRaw]:
    msg = email.message_from_bytes(raw_email)
    html_body = ""

    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/html":
                charset = part.get_content_charset() or "utf-8"
                html_body = part.get_payload(decode=True).decode(charset, errors="replace")
                break
    else:
        if msg.get_content_type() == "text/html":
            charset = msg.get_content_charset() or "utf-8"
            html_body = msg.get_payload(decode=True).decode(charset, errors="replace")

    if not html_body:
        return []

    soup = BeautifulSoup(html_body, "html.parser")
    articles = []
    article_id = 0

    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"]
        title = a_tag.get_text(strip=True)

        if "/url?" in href and "alerts/remove" not in href and "alerts?" not in href:
            if not title or len(title) < 5 or "alerte" in title.lower():
                continue

            clean_link = clean_google_url(href)

            articles.append(
                ArticleRaw(
                    id=article_id,
                    title=title,
                    link=clean_link,
                    date=email_date,
                )
            )
            article_id += 1

    return articles


def fetch_one_email_articles(
    mail: imaplib.IMAP4_SSL, uid: str
) -> List[ArticleRaw]:
    status, msg_data = mail.fetch(uid, "(RFC822)")
    if status != "OK":
        return []

    raw_email = msg_data[0][1]
    msg = email.message_from_bytes(raw_email)
    email_date_obj = parsedate_to_datetime(msg["Date"])
    email_date_str = email_date_obj.isoformat() if email_date_obj else None

    return parse_email_for_content(raw_email, email_date_str)


def delete_email(mail: imaplib.IMAP4_SSL, uid: str):
    try:
        uid_str = uid.decode() if isinstance(uid, bytes) else str(uid)

        res = mail.uid('COPY', uid_str, '[Gmail]/Corbeille')
        if res[0] != 'OK':
            mail.uid('COPY', uid_str, '[Gmail]/Trash')

        mail.uid('STORE', uid_str, '+FLAGS', '(\\Deleted)')

        mail.expunge()

        print(f"🗑️ Mail UID {uid_str} supprimé de la boîte.")
    except Exception as e:
        print(f"Erreur lors de la suppression du mail UID {uid} : {e}")