from database import init_db, save_article_db
from iaRecap import resumer_et_categoriser_article, trier_articles_ia
from mailReader import connect_to_imap, delete_email, fetch_one_email_articles


def run_pipeline():
    init_db()
    mail_conn = connect_to_imap()

    mail_conn.select('"[Gmail]/Tous les messages"', readonly=False)

    status, messages = mail_conn.search(
        None, 'FROM "googlealerts-noreply@google.com"'
    )

    if status == "OK" and messages[0]:
        email_ids = messages[0].split()
        print(f"📧 {len(email_ids)} mail(s) à traiter...")

        for uid in email_ids:
            uid_str = uid.decode() if isinstance(uid, bytes) else str(uid)
            print(f"\n--- Traitement du mail UID {uid_str} ---")

            raw_articles = fetch_one_email_articles(mail_conn, uid_str)

            if raw_articles:
                selected = trier_articles_ia(raw_articles)

                for art in selected:
                    article_orm = resumer_et_categoriser_article(art)
                    if article_orm:
                        inserted = save_article_db(article_orm)
                        if inserted:
                            print(
                                f" [{article_orm.category.value}] : {article_orm.title}"
                            )

            delete_email(mail_conn, uid_str)

    mail_conn.logout()


if __name__ == "__main__":
    run_pipeline()