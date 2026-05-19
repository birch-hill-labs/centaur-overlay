from tools.acme_crm.client import get_account, health_summary, list_accounts


def test_list_accounts_returns_sample_accounts():
    accounts = list_accounts()

    assert {account["name"] for account in accounts} == {"Globex", "Initech"}


def test_get_account_is_case_insensitive():
    assert get_account("GLOBEX")["owner"] == "Avery Chen"


def test_health_summary_marks_sample_data():
    summary = health_summary()

    assert summary["sample_data"] is True
    assert summary["open_tickets"] == 4
