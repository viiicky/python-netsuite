from netsuite.utils import get_record_by_type

from netsuite.service import RecordRef, JournalEntry, JournalEntryLineList, JournalEntryLine
from netsuite.client import client, passport, app_info


def create_journal_entry(data):
    # prepare lineList for JournalEntry
    journal_entry_line_list = JournalEntryLineList(line=[])
    for line_entry in data.line_entries:
        journal_entry_line = JournalEntryLine(
            account=RecordRef(internalId=line_entry.account_internal_id, type='account'), memo=line_entry.memo)
        if line_entry.entry_type in 'cC':
            journal_entry_line.credit = line_entry.amount
        elif line_entry.entry_type in 'dD':
            journal_entry_line.debit = line_entry.amount
        else:
            raise Exception('Line entry is neither of credit type nor of debit.')
        journal_entry_line_list.line.append(journal_entry_line)

    # assemble data for JournalEntry at one place
    journal_entry_data = {
        'subsidiary': RecordRef(internalId=data.subsidiary_internal_id, type='subsidiary'),
        'lineList': journal_entry_line_list
    }

    # prepare JournalEntry from the assembled data
    journal_entry = JournalEntry(**journal_entry_data)

    # post JournalEntry and return the same with True by fetching it in case of successful post,
    # else return the returned error response with False
    response = client.service.add(journal_entry, _soapheaders={'passport': passport, 'applicationInfo': app_info})
    r = response.body.writeResponse
    if r.status.isSuccess:
        result = get_record_by_type('journalEntry', r.baseRef.internalId)
        return True, result
    return False, r
