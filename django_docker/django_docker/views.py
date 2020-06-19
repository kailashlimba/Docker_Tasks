from rest_framework.views import APIView
from typing import List, Dict, Tuple

from rest_framework.response import Response
from rest_framework.views import APIView


class ValidateFiniteValueEntity(APIView):
    SlotValidationResult = Tuple[bool, bool, str, Dict]

    def validate_finite_values_entity(self, values: List[Dict], supported_values: List[str] = None,
                                      invalid_trigger: str = None, key: str = None,
                                      support_multiple: bool = True, pick_first: bool = False,
                                      **kwargs) -> SlotValidationResult:
        """
        Validate an entity on the basis of its value extracted.
        The method will check if the values extracted("values" arg) lies within the finite list of
        supported values(arg "supported_values").
        :param pick_first: Set to true if the first value is to be picked up
        :param support_multiple: Set to true if multiple utterances of an entity are supported
        :param values: Values extracted by NLU
        :param supported_values: List of supported values for the slot
        :param invalid_trigger: Trigger to use if the extracted value is not supported
        :param key: Dict key to use in the params returned
        :return: a tuple o
        """
        # initialize values need to be returned
        filled = False
        partially_filled = False
        trigger = ""
        parameters = {key: []}

        # Edge case if values are empty
        if len(values) == 0:
            return False, False, invalid_trigger, {}

        for dict_value in values:
            current_value = dict_value["value"]
            if current_value in supported_values:
                parameters[key].append(current_value.upper())
            else:
                trigger = invalid_trigger

        if trigger != invalid_trigger:
            filled = True
            partially_filled = False
        else:
            parameters = {}
        if pick_first or support_multiple is False:
            parameters[key] = str(values[0]["value"].upper())
        return filled, partially_filled, trigger, parameters

    def post(self, request):
        request_data = request.data
        values = request_data["values"]
        supported_values = request_data["supported_values"]
        invalid_trigger = request_data["invalid_trigger"]
        key = request_data["key"]
        pick_first = False
        if "pick_first" in request_data:
            pick_first = request_data["pick_first"]
        supported_multiple = False
        if "supported_multiple" in request_data:
            supported_multiple = request_data["supported_multiple"]

        validate_result = self.validate_finite_values_entity(values, supported_values, invalid_trigger, key,
                                                             supported_multiple, pick_first)

        return Response(
            {"filled": validate_result[0],
             "partially_filled": validate_result[1],
             "trigger": validate_result[2],
             "parameters": validate_result[3]
             })


class ValidateNumericValueEntity(APIView):
    SlotValidationResult = Tuple[bool, bool, str, Dict]

    def validate_numeric_entity(self, values: List[Dict], invalid_trigger: str = None, key: str = None,
                                support_multiple: bool = True, pick_first: bool = False, constraint=None,
                                var_name=None, **kwargs) -> SlotValidationResult:
        """
        Validate an entity on the basis of its value extracted.
        The method will check if that value satisfies the numeric constraints put on it.
        If there are no numeric constraints, it will simply assume the value is valid.
        If there are numeric constraints, then it will only consider a value valid if it satisfies the
        numeric constraints.
        In case of multiple values being extracted and the support_multiple flag being set to true, the
        extracted values
        will be filtered so that only those values are used to fill the slot which satisfy the numeric
        constraint.
        If multiple values are supported and even 1 value does not satisfy the numeric constraint, the
        slot is assumed to be
        partially filled.
        :param pick_first: Set to true if the first value is to be picked up
        :param support_multiple: Set to true if multiple utterances of an entity are supported
        :param values: Values extracted by NLU
        :param invalid_trigger: Trigger to use if the extracted value is not supported
        :param key: Dict key to use in the params returned
        :param constraint: Conditional expression for constraints on the numeric values extracted
        :param var_name: Name of the var used to express the numeric constraint
        :return: a tuple of (filled, partially_filled, trigger, params)
        """

        filled = False
        partially_filled = False
        trigger = ""
        parameters = {key: []}

        # No Values Edge case
        if len(values) == 0:
            return (False, False, invalid_trigger, {})

        # No Constraints Edge case
        if constraint == '':
            filled = True
            if pick_first:
                parameters[key] = values[0]["value"]
                return (filled, partially_filled, trigger, parameters)
            for dict_value in values:
                parameters[key].append(dict_value["value"])
            return (filled, partially_filled, trigger, parameters)

        for dict_value in values:
            expression = constraint.replace(var_name, str(dict_value["value"]))
            if eval(expression):
                parameters[key].append(dict_value["value"])
            else:
                trigger = invalid_trigger

        if trigger != invalid_trigger:
            filled = True
            partially_filled = False
        else:
            parameters = {}

        if pick_first or support_multiple is False:
            parameters[key] = values[0]["value"]

        return ([filled, partially_filled, trigger, parameters])

    def post(self, request):
        request_data = request.data
        values = request_data["values"]
        invalid_trig = request_data["invalid_trigger"]
        key = request_data["key"]
        constraint = request_data["constraint"]
        var_name = request_data["var_name"]

        pick_first = False
        supported_multiple = False
        if "pick_first" in request_data:
            pick_first = request_data["pick_first"]
        if "supported_multiple" in request_data:
            supported_multiple = request_data["supported_multiple"]

        numeric_result = self.validate_numeric_entity(values, invalid_trig, key, supported_multiple, pick_first,
                                                      constraint,
                                                      var_name)

        return Response({"filled": numeric_result[0],
                         "partially_filled": numeric_result[1],
                         "trigger": numeric_result[2],
                         "parameters": numeric_result[3]
                         })
