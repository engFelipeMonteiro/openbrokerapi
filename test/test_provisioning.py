import http
import json

from werkzeug.wrappers import Response

from openbrokerapi import errors
from openbrokerapi.service_broker import ProvisionedServiceSpec, ProvisionDetails
from test import BrokerTestCase


class ProvisioningTest(BrokerTestCase):

    def test_provisining_called_with_the_right_values(self):
        self.broker.provision.return_value = ProvisionedServiceSpec(False, "dash_url", "operation_str")

        _ = self.client.put(
            "/v2/service_instances/here-instance-id?accepts_incomplete=true",
            data=json.dumps({
                "service_id": "service-guid-here",
                "plan_id": "plan-guid-here",
                "organization_guid": "org-guid-here",
                "space_guid": "space-guid-here",
                "parameters": {
                    "parameter1": 1
                }
            }),
            headers={
                'X-Broker-Api-Version': '2.00',
                'Authorization': self.auth_header
            })

        actual_instance_id, actual_details, actual_async_allowed = self.broker.provision.call_args[0]
        self.assertEqual(actual_instance_id, "here-instance-id")
        self.assertEqual(actual_async_allowed, True)

        self.assertIsInstance(actual_details, ProvisionDetails)
        self.assertEqual(actual_details.service_id, "service-guid-here")
        self.assertEqual(actual_details.plan_id, "plan-guid-here")
        self.assertEqual(actual_details.parameters, dict(parameter1=1))
        self.assertEqual(actual_details.organization_guid, "org-guid-here")
        self.assertEqual(actual_details.space_guid, "space-guid-here")

    def test_provisining_called_just_with_required_fields(self):
        self.broker.provision.return_value = ProvisionedServiceSpec(False, "dash_url", "operation_str")

        _ = self.client.put(
            "/v2/service_instances/here-instance-id",
            data=json.dumps({
                "service_id": "service-guid-here",
                "plan_id": "plan-guid-here",
                "organization_guid": "org-guid-here",
                "space_guid": "space-guid-here",
            }),
            headers={
                'X-Broker-Api-Version': '2.00',
                'Authorization': self.auth_header
            })

        actual_instance_id, actual_details, actual_async_allowed = self.broker.provision.call_args[0]
        self.assertEqual(actual_instance_id, "here-instance-id")
        self.assertEqual(actual_async_allowed, False)

        self.assertIsInstance(actual_details, ProvisionDetails)
        self.assertEqual(actual_details.service_id, "service-guid-here")
        self.assertEqual(actual_details.plan_id, "plan-guid-here")
        self.assertEqual(actual_details.organization_guid, "org-guid-here")
        self.assertEqual(actual_details.space_guid, "space-guid-here")

        self.assertIsNone(actual_details.parameters)

    def test_returns_201_if_created(self):
        self.broker.provision.return_value = ProvisionedServiceSpec(False, "dash_url", "operation_str")

        response: Response = self.client.put(
            "/v2/service_instances/abc",
            data=json.dumps({
                "service_id": "service-guid-here",
                "plan_id": "plan-guid-here",
                "organization_guid": "org-guid-here",
                "space_guid": "space-guid-here",
            }),
            headers={
                'X-Broker-Api-Version': '2.00',
                'Authorization': self.auth_header
            })

        self.assertEquals(response.status_code, http.HTTPStatus.CREATED)
        self.assertEquals(response.json, dict(
            dashboard_url="dash_url",
            operation="operation_str"
        ))

    def test_returns_202_if_provisioning_in_progress(self):
        self.broker.provision.return_value = ProvisionedServiceSpec(True, "dash_url", "operation_str")

        response: Response = self.client.put(
            "/v2/service_instances/abc",
            data=json.dumps({
                "service_id": "service-guid-here",
                "plan_id": "plan-guid-here",
                "organization_guid": "org-guid-here",
                "space_guid": "space-guid-here",
            }),
            headers={
                'X-Broker-Api-Version': '2.00',
                'Authorization': self.auth_header
            })

        self.assertEquals(response.status_code, http.HTTPStatus.ACCEPTED)
        self.assertEquals(response.json, dict(
            dashboard_url="dash_url",
            operation="operation_str"
        ))

    def test_returns_409_if_already_exists_but_is_not_equal(self):
        self.broker.provision.side_effect = errors.ErrInstanceAlreadyExists()

        response: Response = self.client.put(
            "/v2/service_instances/abc",
            data=json.dumps({
                "service_id": "service-guid-here",
                "plan_id": "plan-guid-here",
                "organization_guid": "org-guid-here",
                "space_guid": "space-guid-here",
            }),
            headers={
                'X-Broker-Api-Version': '2.00',
                'Authorization': self.auth_header
            })

        self.assertEquals(response.status_code, http.HTTPStatus.CONFLICT)
        self.assertEquals(response.json, {})

    def test_returns_422_if_async_required_but_not_supported(self):
        self.broker.provision.side_effect = errors.ErrAsyncRequired()

        response: Response = self.client.put(
            "/v2/service_instances/abc",
            data=json.dumps({
                "service_id": "service-guid-here",
                "plan_id": "plan-guid-here",
                "organization_guid": "org-guid-here",
                "space_guid": "space-guid-here",
            }),
            headers={
                'X-Broker-Api-Version': '2.00',
                'Authorization': self.auth_header
            })

        self.assertEquals(response.status_code, http.HTTPStatus.UNPROCESSABLE_ENTITY)
        self.assertEquals(response.json, dict(
            error="AsyncRequired",
            description="This service plan requires client support for asynchronous service operations."
        ))