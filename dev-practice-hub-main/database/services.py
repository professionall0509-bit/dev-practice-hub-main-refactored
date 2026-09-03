from database.models import (
    application_exists,
    application_exists_by_gmail_id,
    get_all_applications,
    get_by_status,
    get_total_count,
    save_application,
)


class DatabaseService:

    def save(self, application):
        save_application(application)

    def get_all(self):
        return get_all_applications()

    def get_status(self, status):
        return get_by_status(status)

    def total(self):
        return get_total_count()

    def exists(self, sender, subject):
        return application_exists(sender, subject)

    def exists_by_gmail_id(self, gmail_id):
        return application_exists_by_gmail_id(gmail_id)
