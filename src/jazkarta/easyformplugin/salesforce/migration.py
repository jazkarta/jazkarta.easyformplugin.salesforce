from collective.easyform.migration.actions import (
    TYPES_MAPPING,
    Type,
    append_field,
    append_node,
)
import json


def append_sf_action(schema, type_, name, properties):
    node = append_field(schema, type_, name, properties)

    # process SF adapter properties
    creation_mode = properties["creationMode"]
    if creation_mode not in ("create", "update"):
        raise NotImplementedError("Unsupported creationMode: {}".format(creation_mode))
    fields = {}
    for item in properties["fieldMap"]:
        if "/" in item["field_path"]:
            raise NotImplementedError("Fields in fieldset folders not supported yet.")
        fields[item["sf_field"]] = "form:" + item["field_path"]
    for item in properties["presetValueMap"]:
        fields[item["sf_field"]] = item["value"]
    op = {
        "operation": creation_mode,
        "sobject": properties["SFObjectType"],
        "fields": fields,
    }
    if creation_mode == "update":
        op["match_expression"] = properties["updateMatchExpression"]
        if properties["actionIfNoExistingObject"] not in ("abort", "create"):
            raise NotImplementedError(
                "Unsupported actionIfNoExistingObject: {}".format(
                    properties["actionIfNoExistingObject"]
                )
            )
        op["action_if_no_existing_object"] = properties["actionIfNoExistingObject"]
    if properties["dependencyMap"]:
        raise NotImplementedError(
            "Unsupported: dependencyMap (jazkarta.easyformplugins.salesforce "
            "does not support chained adapters at this time)."
        )

    append_node(node, "operations", json.dumps([op]))
    return node


TYPES_MAPPING["SalesforcePFGAdapter"] = Type(
    "jazkarta.easyformplugin.salesforce.action.SendToSalesforce",
    append_sf_action,
)
