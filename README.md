# jazkarta.easyformplugin.salesforce

This is a Plone addon for [collective.easyform](https://github.com/collective/collective.easyform)
which uses the Salesforce REST API to create records in Salesforce when a form is submitted.

It is a successor to [Products.salesforcepfgadapter](https://pypi.org/project/Products.salesforcepfgadapter/),
but has a more basic UI and doesn't have all the same features.

## Features

- Create a new record in Salesforce
- Map field values from the form to Salesforce fields
- Calculate values from TALES expressions and map them to Salesforce fields

## Installation

To install jazkarta.easyformplugin.salesforce, first add it to your buildout::

```
    [buildout]

    ...

    eggs =
        jazkarta.easyformplugin.salesforce
```

and then run `bin/buildout`

You must also make sure the following environment variables are set while running Zope:

* SALESFORCE_USERNAME
* SALESFORCE_PASSWORD
* SALESFORCE_TOKEN (if needed)
* SALESFORCE_DOMAIN: the subdomain to use for authentication to Salesforce,
  e.g. `login` for production orgs or `test` for sandboxes.

## Usage

1. Create an Easyform.
2. Open the Actions menu and choose "Define form actions"
3. Click the "Add New Action" button
4. Enter a Title and Short Name for the action. Choose "Send to Salesforce" as the "Action type". Click the "Add" button.
5. Close the modal.
6. Click the "Settings" button for the new action.
7. Edit the "Salesforce Operations" field to specify the field mapping in JSON.
8. Click the "Save" button.
9. Test submitting the form.

## Migration from PloneFormGen & salesforcepfgadapter

This addon integrates with Easyform's tool for migrating from PloneFormGen.
This will happen automatically as long as `jazkarta.easyformplugins.salesforce` is installed
when you use the `/@@migrate-ploneformgen` view.
It will try to migrate every `salesforcepfgadapter`, but will throw an exception if the
adapter uses settings that are not supported by `jazkarta.easyformplugins.salesforce`
(such as chained adapters to write to multiple Salesforce records).

## Contribute

- Report Bugs: https://github.com/collective/jazkarta.easyformplugin.salesforce/issues
- Source Code: https://github.com/collective/jazkarta.easyformplugin.salesforce

## Support

This package is offered as open source but without any guarantee of free support.
If you are interested in paid support, please contact david at glicksoftware.com

## License

The project is licensed under the GPLv2.
