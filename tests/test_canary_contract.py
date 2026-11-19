"""Offline policy observations and an explicitly substituted store; no sockets/database."""
from datetime import UTC, datetime, timedelta
from uuid import uuid4
from unittest.mock import Mock

from fastapi.testclient import TestClient
import psycopg
import pytest

import hypermesh_contract_authority as owner
from hypermesh_contract_authority.canary import Binding, Unavailable, refusal


def sample():
    tenant=uuid4(); terms=owner.Fulfill(lease_id=uuid4(),reserved_hours=1,
        renter_subject=uuid4(),host_subject=uuid4(),meters=['wall_time','capacity_block'])
    now=datetime.now(UTC)
    record={'id':str(uuid4()),'tenant_id':str(tenant),'lease_id':str(terms.lease_id),
        'parties':[{'role':'renter','subject':str(terms.renter_subject)},
                   {'role':'host','subject':str(terms.host_subject)}],
        'meters':['capacity_block','wall_time'],'rail':'self-use','status':'signed',
        'signed_by':owner.SIGNER,'signed_at':now.isoformat(),
        'until':(now+timedelta(hours=1)).isoformat(),'protocol':owner.PROTOCOL}
    return tenant, terms, now, record


def test_disabled_and_unattributed_observations_refuse():
    with pytest.raises(Unavailable):Binding('a'*40).metadata({})
    with pytest.raises(Unavailable):Binding('a'*40,enabled=True).metadata({})
    with pytest.raises(Unavailable):Binding('branch')
    with pytest.raises(Unavailable):Binding('a'*40,policy_revision='unknown')


def test_original_decision_and_expiry():
    tenant,terms,now,record=sample(); binding=Binding('a'*40,enabled=True)
    assert binding.decision(record,tenant=tenant,terms=terms,now=now,original=record)['expiry_preserved']
    with pytest.raises(Unavailable):binding.decision(record,tenant=tenant,terms=terms,now=now+timedelta(hours=1))
    with pytest.raises(Unavailable):binding.decision(record,tenant=uuid4(),terms=terms,now=now)
    with pytest.raises(Unavailable):binding.decision(record,tenant=tenant,terms=terms,now=now,original={})


@pytest.mark.parametrize('patch',[{'rail':'stripe'},{'gross_cents':1},{'signed_by':'other'},
    {'meters':['token_digest_count']},{'until':'bad'},{'id':'bad'},{'status':'pending'}])
def test_wrong_decisions_refuse(patch):
    tenant,terms,now,record=sample()
    with pytest.raises(Unavailable):Binding('a'*40,enabled=True).decision(record|patch,tenant=tenant,terms=terms,now=now)


def test_exact_refusals():
    for status in (401,404,409,422,503):assert refusal(status,status)=={'refusal':status}
    for status in (None,200,500,True):
        with pytest.raises(Unavailable):refusal(status,503)


def test_attributed_metadata_and_store_failure(monkeypatch):
    # Only persistence is substituted. FastAPI authentication and error handling are real.
    ledger=Mock();ledger.fulfill.side_effect=psycopg.OperationalError('private connection detail')
    ledger.connect.side_effect=psycopg.OperationalError('private connection detail')
    monkeypatch.setattr(owner,'Ledger',lambda dsn:ledger)
    monkeypatch.setenv('CONTRACT_AUTHORITY_SOURCE_REVISION','a'*40)
    token='fixture-private-token-'+'x'*32
    client=TestClient(owner.create_app(dsn='fixture',token=token))
    assert client.get('/v1/meta').status_code==401
    meta=client.get('/v1/meta',headers={'X-Internal-Token':token}).json()
    Binding('a'*40,enabled=True).metadata(meta)
    with pytest.raises(Unavailable):Binding('b'*40,enabled=True).metadata(meta)
    tenant,terms,_,_=sample()
    response=client.post('/v1/contracts/fulfill',headers={'X-Internal-Token':token,'X-Tenant-ID':str(tenant)},json=terms.model_dump(mode='json'))
    refusal(response.status_code,503)
    assert 'private' not in response.text and token not in response.text
    assert client.get('/health').status_code==503


def test_no_original_comparison_is_not_reported_as_preserved():
    tenant,terms,now,record=sample();binding=Binding('a'*40,enabled=True)
    assert binding.decision(record,tenant=tenant,terms=terms,now=now)['expiry_preserved'] is False
    with pytest.raises(Unavailable):
        binding.decision(record,tenant=tenant,terms=terms.model_copy(update={'meters':['wall_time','wall_time']}),now=now)
