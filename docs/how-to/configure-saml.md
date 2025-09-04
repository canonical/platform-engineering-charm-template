# Configure SAML

The NetBox charm makes use of the saml-integrator for SAML. You can find
more information in [charmhub](https://charmhub.io/saml-integrator).

SAML is configured in NetBox using the library `python-social-core` with the `SAMLAuth` backend.

To configure it, you need to know the `entidy_id` and `metadata_url` of your IdP provider. 
`entity_id` must be a valid URI. It can be configured with the following commands:
```
juju deploy saml-integrator --channel latest/edge --config entity_id=<idp_entidy_id> --config metadata_url=<idp_metadata_url>
juju integrate saml-integrator netbox-k8s
```

For NetBox to work, you may need to customise some of the following configuration options:
 - `saml-sp-entity-id`: SAML SP entity id. This is mandatory, and should be a correct URL.
 - `saml-username`: SAML attribute used for both the social `uid` and the `username` (`name_id` by default).
 - `saml-email`: SAML attribute used for the email (optional).

NetBox configuration options for SAML can be configured like:
```
juju config netbox-k8s saml-sp-entity-id=<your_sp_entity_id_url> saml-username=<saml_attribute_for_uid_and_username>
```
