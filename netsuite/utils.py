from netsuite.client import client, app_info, passport
from netsuite.service import (
    RecordRef,
    SearchPreferences
)


class obj(object):
    """Dictionary to object utility.

    >>> d = {'b': {'c': 2}}
    >>> x = obj(d)
    >>> x.b.c
    2
    """
    def __init__(self, d):
        for a, b in d.items():
            if isinstance(b, (list, tuple)):
               setattr(self, a, [obj(x)
                   if isinstance(x, dict) else x for x in b])
            else:
               setattr(self, a, obj(b)
                   if isinstance(b, dict) else b)


def get_record_by_type(type, internal_id):
    record = RecordRef(internalId=internal_id, type=type)
    response = client.service.get(record,
        _soapheaders={
            'applicationInfo': app_info,
            'passport': passport,
        }
    )
    r = response.body.readResponse
    if r.status.isSuccess:
        return r.record


def get_records(types, internal_ids):
    """ Fetch all the records represented by the corresponding input type and internalId.
    zip is used on lists: types and internal_ids, thus the one which is bigger is truncated from the end.

    Note: Make sure the order of input lists: types and internalIds matches to get the expected records.

    :param types: list of type of the records to be fetched
    :param internal_ids: list of internal id of the records to be fetched
    :return: list of records fetched represented by the corresponding input type and internalId in the same order.
    If there occurs an error for a given record, None is placed at the position of that particular item.

    If there occurs any error in the root request of fetching the list, an [] is returned.
    """
    record_refs = [RecordRef(internalId=i, type=t) for t, i in zip(types, internal_ids)]
    response = client.service.getList(record_refs, _soapheaders={'applicationInfo': app_info, 'passport': passport})

    r_list = response.body.readResponseList
    return [r.record for r in r_list.readResponse] if r_list.status.isSuccess else []


def search_records_using(searchtype):
    search_preferences = SearchPreferences(
        bodyFieldsOnly=False,
        returnSearchColumns=True,
        pageSize=20
    )

    return client.service.search(
        searchRecord=searchtype,
        _soapheaders={
            'searchPreferences': search_preferences,
            'applicationInfo': app_info,
            'passport': passport,
        }
    )
