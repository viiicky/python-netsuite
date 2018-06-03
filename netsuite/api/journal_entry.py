from netsuite.service import RecordRef, JournalEntry, JournalEntryLineList, JournalEntryLine
from netsuite.client import client, passport, app_info


def prepare_journal_entry(data):
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
        'externalId': data.external_id,
        'subsidiary': RecordRef(internalId=data.subsidiary_internal_id, type='subsidiary'),
        'lineList': journal_entry_line_list
    }

    # prepare JournalEntry from the assembled data
    return JournalEntry(**journal_entry_data)


def create_journal_entries(journal_entries_data):
    journal_entries = [prepare_journal_entry(d) for d in journal_entries_data]

    response = client.service.addList(journal_entries, _soapheaders={'passport': passport, 'applicationInfo': app_info})
    # Note: Above call will fail with newer WSDL. Newer WSDLs are strict on not passing the passport in these calls.
    # If using newer WSDL just do `response = client.service.addList(journal_entries)`,
    # else you will get ambiguous authentication exception.
    # Same applies on the call inside the utils#get_record_by_type()

    r_list = response.body.writeResponseList
    if r_list.status.isSuccess:
        result = []
        for je, r in zip(journal_entries, r_list.writeResponse):
            # TODO: Instead of returning True/False with external_id, return Record/None with external_id
            # making use of utils#get_records()
            if r.status.isSuccess:
                result.append((je.externalId, True))
            else:
                print('Exception occurred while posting journal entry: {}'.format(r))
                result.append((je.externalId, False))
        return result
    else:
        print('Exception occurred while posting journal entries: {}'.format(r_list.status.statusDetail.message))
        raise Exception(r_list)
