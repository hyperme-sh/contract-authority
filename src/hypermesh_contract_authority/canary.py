"""Inactive owner observation contract; deployment routes and credentials are Infra-owned."""
from dataclasses import dataclass
from datetime import datetime, timedelta
import re
from uuid import UUID

from . import Fulfill, POLICY, POLICY_REVISION, PROTOCOL, SIGNER


class Unavailable(ValueError):
    pass


def require(condition, reason):
    if not condition:
        raise Unavailable(reason)


@dataclass(frozen=True)
class Binding:
    source_revision: str
    policy_revision: str = POLICY_REVISION
    enabled: bool = False

    def __post_init__(self):
        require(isinstance(self.source_revision, str) and
                re.fullmatch('[0-9a-f]{40}', self.source_revision), 'Exact source revision required')
        require(self.policy_revision == POLICY_REVISION, 'Unsupported self-use policy')

    def metadata(self, value):
        require(self.enabled is True, 'Authority canary binding disabled')
        require(isinstance(value, dict) and value.get('source_revision') == self.source_revision
                and value.get('policy_revision') == self.policy_revision
                and value.get('policy') == POLICY and value.get('protocol') == PROTOCOL
                and value.get('writer') == 'self-use' and value.get('financial') is False,
                'Authority policy or build attribution unavailable')

    def decision(self, value, *, tenant: UUID, terms: Fulfill, now: datetime, original=None):
        require(self.enabled is True, 'Authority canary binding disabled')
        require(now.tzinfo is not None, 'Timezone-aware observation required')
        require(set(terms.meters) == {'wall_time', 'capacity_block'} and terms.reserved_hours == 1,
                'Unsupported requested terms')
        require(isinstance(value, dict), 'Contract decision unavailable')
        try:
            start, end = (datetime.fromisoformat(value[k]) for k in ('signed_at', 'until'))
            identity = UUID(value['id'])
            require(identity.int != 0 and str(identity) == value['id'], 'Invalid contract identity')
            require(start.tzinfo is not None and end.tzinfo is not None and
                    end-start == timedelta(hours=1) and start <= now < end,
                    'Contract time unavailable or expired')
            expected = {'id':str(identity), 'tenant_id':str(tenant), 'lease_id':str(terms.lease_id),
                'parties':[{'role':'renter','subject':str(terms.renter_subject)},
                           {'role':'host','subject':str(terms.host_subject)}],
                'meters':['capacity_block','wall_time'], 'rail':'self-use', 'status':'signed',
                'signed_by':SIGNER, 'signed_at':value['signed_at'], 'until':value['until'],
                'protocol':PROTOCOL}
            require(value == expected, 'Contract terms or authority differ')
            require(terms.contract_id is None or terms.contract_id == identity, 'Claimed contract differs')
            require(original is None or original == value, 'Replay changed original contract')
        except (KeyError, TypeError, ValueError) as exc:
            if isinstance(exc, Unavailable): raise
            raise Unavailable('Malformed contract decision') from None
        return {'decision':'self-use', 'expiry_preserved':original is not None}


def refusal(status, expected):
    require(type(status) is int and expected in (401, 404, 409, 422, 503) and status == expected,
            'Expected authority refusal was not observed')
    return {'refusal': expected}
