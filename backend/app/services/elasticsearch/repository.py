from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from elasticsearch import Elasticsearch

from app.core.config import settings


class AttendanceElasticRepository:
    def __init__(self, client: Elasticsearch | None = None) -> None:
        self.client = client or Elasticsearch(
            settings.elasticsearch_url,
            basic_auth=(settings.elasticsearch_username, settings.elasticsearch_password)
            if settings.elasticsearch_username and settings.elasticsearch_password
            else None,
            verify_certs=settings.elasticsearch_verify_certs,
            request_timeout=settings.elasticsearch_request_timeout,
        )
        self.index_pattern = settings.elasticsearch_index_pattern
        self.field_mapping = {
            'timestamp': settings.es_field_timestamp,
            'event_time': settings.es_field_event_time,
            'user_id': settings.es_field_user_id,
            'user_name': settings.es_field_user_name,
            'device_name': settings.es_field_device_name,
            'device_id': settings.es_field_device_id,
            'outcome': 'event.outcome',
        }

    def build_recent_events_query(self, minutes: int, size: int = 100, sort_order: str = 'asc') -> dict[str, Any]:
        return {
            'size': size,
            'sort': [{self.field_mapping['timestamp']: {'order': sort_order}}],
            'query': {
                'bool': {
                    'filter': [
                        {'range': {self.field_mapping['timestamp']: {'gte': f'now-{minutes}m', 'lte': 'now'}}},
                        {'exists': {'field': self.field_mapping['user_id']}},
                    ]
                }
            },
        }

    def recent_events(self, minutes: int = 10, size: int = 100, sort_order: str = 'asc') -> list[dict[str, Any]]:
        response = self.client.search(index=self.index_pattern, body=self.build_recent_events_query(minutes, size, sort_order))
        return [item['_source'] for item in response['hits']['hits']]

    def checked_in_users(self, start_time: str, end_time: str, user_ids: Iterable[str]) -> set[str]:
        ids = list(user_ids)
        aggregation_query = {
            'size': 0,
            'query': {
                'bool': {
                    'filter': [
                        {'range': {self.field_mapping['timestamp']: {'gte': start_time, 'lte': end_time}}},
                        {'terms': {self.field_mapping['user_id']: ids}},
                    ]
                }
            },
            'aggs': {'users': {'terms': {'field': self.field_mapping['user_id'], 'size': len(ids) or 1000}}},
        }
        try:
            response = self.client.search(index=self.index_pattern, body=aggregation_query)
            return {bucket['key'] for bucket in response['aggregations']['users']['buckets']}
        except Exception:
            fallback_query = {
                'size': max(len(ids), 100),
                '_source': [self.field_mapping['user_id']],
                'query': aggregation_query['query'],
            }
            response = self.client.search(index=self.index_pattern, body=fallback_query)
            found: set[str] = set()
            for item in response['hits']['hits']:
                value = self._dig_value(item['_source'], self.field_mapping['user_id'])
                if value:
                    found.add(str(value))
            return found

    def report_summary(self, start_time: str, end_time: str) -> dict[str, Any]:
        query = {
            'size': 0,
            'query': {'bool': {'filter': [{'range': {self.field_mapping['timestamp']: {'gte': start_time, 'lte': end_time}}}]}},
            'aggs': {
                'present_users': {'cardinality': {'field': self.field_mapping['user_id']}},
                'event_outcomes': {'terms': {'field': self.field_mapping['outcome'], 'size': 10}},
            },
        }
        response = self.client.search(index=self.index_pattern, body=query)
        return {
            'total_events': response['hits']['total']['value'],
            'present_users': response['aggregations']['present_users']['value'],
            'outcomes': response['aggregations']['event_outcomes']['buckets'],
        }

    def health(self) -> str:
        health = self.client.cluster.health()
        return str(health.get('status', 'unknown'))

    def _dig_value(self, data: dict[str, Any], path: str) -> Any:
        current: Any = data
        for part in path.split('.'):
            if not isinstance(current, dict):
                return None
            current = current.get(part)
        return current
